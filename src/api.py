import sys
sys.path.append("") 

import uvicorn
import time
import os
import json
from fastapi import (FastAPI, Request, Depends,
                     status, HTTPException, Query)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional, Literal
from contextlib import asynccontextmanager
from src.mongo_database import MongoDatabase
import threading
from src.ocr_reader import OcrReader, GoogleTranslator
from src.base_extractors import OpenAIExtractor 
# from src.qwen2_extract import Qwen2Extractor

from src.ldap_authen import (User, get_current_user, ldap_authen, 
                             Token, create_access_token)
from src.Utils.utils import (read_config, get_current_time, is_base64, 
                             valid_base64_image, convert_datetime_to_iso, convert_iso_to_string,
                             get_land_and_city_list, get_currencies_from_txt, find_pairs_of_docs)
from src.invoice_extraction import extract_invoice_info, validate_invoice
from src.Utils.logger import create_logger
from src.export_excel.main import export_json_to_excel
from src.mail import EmailSender

from dotenv import load_dotenv
load_dotenv()

config_path='config/config.yaml'
config = read_config(path=config_path)

logger = create_logger(config_path=config_path)
logger.info(msg = "Loading config")

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
SERVER_IP = os.getenv('SERVER_IP')


mongo_db = MongoDatabase(config_path=config_path, logger=logger)
change_stream = None
change_stream_thread = None

ocr_reader = OcrReader(config_path=config_path, translator=GoogleTranslator(), logger=logger)
invoice_extractor = OpenAIExtractor(config_path=config_path)

email_sender = EmailSender(config=config, logger=logger)

def process_change_stream(ocr_reader, invoice_extractor, config):
    global change_stream
    for change in change_stream:
        if change['operationType'] == 'insert':
            # Instead of processing just the inserted document, we'll fetch all unprocessed documents
            unprocessed_documents, _ = mongo_db.get_documents(filters={"status": "not extracted"})
            
            for document in unprocessed_documents:
                document_id = document['_id']
                base64_img = document['invoice_image_base64']

                try:
                    new_data = extract_invoice_info(base64_img=base64_img, ocr_reader=ocr_reader,
                                                    invoice_extractor=invoice_extractor, config=config, 
                                                    logger=logger)
                    
                    # Update the processed document
                    mongo_db.update_document_by_id(str(document_id), new_data)
                    
                except Exception as e:
                    logger.error(f"Error processing document {document_id}: {str(e)}")
                
            email_sender.send_email(email_type='modify_invoice_remind',
                                        receivers=None,
                                        )

        elif change['operationType'] == 'update':
            # Process modified documents
            doc_id = str(change['documentKey']['_id']) 
            updated_doc = mongo_db.get_document_by_id(document_id=doc_id)
            logger.info(msg = "trigger modified")

            if not ((updated_doc.get('last_modified_by') is not None) and 
                    (updated_doc.get('invoice_type') in ['invoice 1', 'invoice 2'])):
                continue

            # Get all documents modified this month
            start_of_month = get_current_time(timezone=config['timezone']).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            modified_documents, _ = mongo_db.get_documents(
                filters={
                    "last_modified_by": {"$ne": None},
                    "last_modified_at": {"$gte": start_of_month},
                    "invoice_type": {"$in": ["invoice 1", "invoice 2"]},
                    "invoice_info.name": updated_doc['invoice_info']['name'],
                    "invoice_info.project_number": updated_doc['invoice_info']['project_number']
                }
            )

            if not modified_documents or (len(modified_documents)<=1): #just have 1 doc, no partner doc there
                continue

            msg = f"modified_documents update change streams: {len(modified_documents)}"
            logger.info(msg = msg)

            msg = f"modified_documents update change streams: {len(modified_documents)}"
            logger.info(msg=msg)

            invoice_pairs = find_pairs_of_docs(modified_documents)

            if not invoice_pairs:
                logger.info(msg="No matching invoice pairs found")
                return

            logger.debug('Create pair of json')
            try:
                employee_expense_report_path, output_2_excel = export_json_to_excel(invoice_pairs=invoice_pairs, logger=logger)
                if employee_expense_report_path or output_2_excel:
                    email_sender.send_email(email_type='send_excel',
                                            receivers=None,
                                            attachment_paths=[employee_expense_report_path, output_2_excel])
                    logger.debug(f"attachment_paths: {[employee_expense_report_path, output_2_excel]}")
            except Exception as e:
                logger.debug(f"error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global change_stream, change_stream_thread
    change_stream = mongo_db.start_change_stream()
    change_stream_thread = threading.Thread(target=process_change_stream, 
                                            args=(ocr_reader, invoice_extractor, config))
    change_stream_thread.start()
    
    yield  # This is where the FastAPI app runs
    
    # Shutdown
    if change_stream:
        change_stream.close()
    if change_stream_thread:
        change_stream_thread.join()

app = FastAPI(lifespan=lifespan)

# Define allowed origins
allowed_origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:80",
]

# Add SERVER_IP to allowed origins if it exists
if SERVER_IP:
    allowed_origins.append(f"http://{SERVER_IP}/")
    allowed_origins.append(f"https://{SERVER_IP}/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Replace with your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.debug(msg=f"allowed_origins: {allowed_origins}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user_dependency(token: str = Depends(oauth2_scheme)) -> User:
    return get_current_user(token, SECRET_KEY, ALGORITHM)

@app.get("/")
@app.post("/")
async def hello():
    return {"message": "Hello, world!"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):    
    try:
        is_valid, is_admin, username = ldap_authen(username=form_data.username, 
                                                   password=form_data.password, 
                                                   config=config)
        if is_valid:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(secret_key=SECRET_KEY, algorithm=ALGORITHM,
                data={"sub": username, "is_admin": is_admin}, expires_delta=access_token_expires
            )
            logger.debug(f"Login successful for username: {username} (is_admin: {is_admin})")
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            logger.debug(f"Login failed for username: {form_data.username} - Incorrect username or password")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
    except Exception as e:
        logger.debug(f"Error during login for username: {form_data.username} - {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user_dependency)):
    logger.info(f"Fetching user info for username: {current_user.username}")
    try:
        return current_user
    except Exception as e:
        logger.error(f"Error fetching user info for username: {current_user.username} - {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/frontend_defines")
async def get_frontend_defines():
    try:
        # Read the JSON file
        frontend_fields_define_path = config['frontend_fields_define_path']
        with open(frontend_fields_define_path, "r") as file:
            frontend_defines = json.load(file)

        # Get currencies, lands, and cities
        currencies = get_currencies_from_txt()
        lands, cities = get_land_and_city_list()

        # Update the frontend defines with the retrieved data
        for item in frontend_defines:
            if item["key"] == "currency":
                item["data"] = currencies
            elif item["key"] == "city":
                item["data"] = cities
            elif item["key"] == "land":
                item["data"] = lands

        msg={
                "frontend_defines": frontend_defines,
                "message": "Get frontend_defines successful"
            }
        logger.debug(msg=msg)
        return JSONResponse(
            status_code=200,
            content=msg
        )

    except Exception as e:
        # Handle errors
        msg = {
                "status": "error",
                "message": str(e)
            }
        logger.debug(msg = msg)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=msg)

@app.post("/api/v1/invoices/upload")
async def upload_invoice(
    request: Request,
    ):

    try:
        # Parse JSON body
        body = await request.json()
        img = body.get("img")
        user_uuid = body.get("user_uuid")
        
        if not img or not is_base64(img):
            msg = {
                    "status": "error",
                    "message": "Base64 image is required",
                }
            logger.debug(msg=msg)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=msg)
        
        # Generate invoice UUID
        img = valid_base64_image(img)       
        
        invoice_document = {
            "invoice_type": None,
            "created_at": get_current_time(timezone=config['timezone']),
            "created_by": user_uuid,
            "last_modified_at": None,
            "last_modified_by": None,
            "status": "not extracted",
            "invoice_image_base64": img,
            "invoice_info": {}
        }
        
        invoice_uuid = mongo_db.create_document(invoice_document)
        mongo_db.update_document_by_id(invoice_uuid, {"invoice_uuid": invoice_uuid})

        msg={
                "invoice_uuid": invoice_uuid,
                "message": "Upload successful"
            }
        logger.debug(msg=msg)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=msg
        )

    except Exception as e:
        # Handle errors
        msg = {
                "status": "error",
                "message": str(e)
        }
        logger.debug(msg=msg)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=msg)
    

@app.delete("/api/v1/invoices/{invoice_uuid}")
async def delete_invoice(invoice_uuid: str):
    try:
        mongo_db.delete_document_by_id(invoice_uuid)
        msg = {
                "message": "Invoice deleted successfully"
            }
        logger.debug(msg=msg)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=msg
        )
    
    except Exception as e:
        # Handle errors
        msg = {
                "status": "error",
                "message": str(e)
            }
        logger.debug(msg=msg)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=msg)
    

@app.put("/api/v1/invoices/{invoice_uuid}")
async def modify_invoice(invoice_uuid: str, request: Request):
    try:
        # Parse JSON body
        body = await request.json()
        user_uuid = body.get("user_uuid")
        invoice_info = body.get("invoice_info")
        
        if not invoice_info:
            msg = {
                    "status": "error",
                    "message": "Invoice information is required",
                }
            logger.debug(msg=msg)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=msg)
        
        logger.debug(msg = f"invoice_info.keys {invoice_info.keys()}")

        invoice_info['invoice_info'] = convert_iso_to_string(invoice_info['invoice_info'], format='%d/%m/%Y')

        invoice_dict = validate_invoice(invoice_info=invoice_info, 
                                             invoice_type=invoice_info['invoice_type'], 
                                             config=config)
        
        logger.debug(msg = f"invoice_dict['invoice_info']: {invoice_dict['invoice_info']}")


        # Prepare update fields
        update_fields = {
            "invoice_info": invoice_dict['invoice_info'],
            "last_modified_at": get_current_time(timezone=config['timezone']),
            "last_modified_by": user_uuid
        }

        # Update the document in the database
        try:
            mongo_db.update_document_by_id(invoice_uuid, update_fields)
        except:
            msg = {
                    "status": "error",
                    "message": "Failed to update the invoice",
                }
            logger.debug(msg = msg)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=msg)

        msg = {
                "invoice_uuid": invoice_uuid,
                "message": "Invoice information updated."
            }
        logger.debug(msg=msg)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=msg
        )

    except Exception as e:
        # Handle errors
        msg = {
                "status": "error",
                "message": str(e)
            }
        logger.debug(msg = msg)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=msg)


@app.get("/api/v1/invoices")
async def get_invoices(
    created_at: Optional[str] = Query("asc", description="Sort by creation date (asc or desc)"),
    created_by: Optional[str] = Query(None, description="Filter by user_uuid of the invoice creator"),
    invoice_type: Optional[str] = Query(None, description="Filter by type of invoice"),
    invoice_uuid: Optional[str] = Query(None, description="Filter by id of invoice"),
    invoice_status: Optional[Literal['not extracted', 'completed']] = Query(None, description="Filter by invoice invoicestatus"),
    page: int = Query(1, description="Page number for pagination", gt=0),
    limit: int = Query(10, description="Number of invoices per page", gt=0),
):
    try:
        # Build the query object
        query = {}
        if created_by:
            query["created_by"] = created_by
        if invoice_type:
            query["invoice_type"] = invoice_type
        if invoice_uuid:
            query["invoice_uuid"] = invoice_uuid
        if invoice_status:
            query["status"] = invoice_status

        logger.debug(msg=f"query:{query}")
        
        # Fetch documents from MongoDB
        invoices, total_matching_docs = mongo_db.get_documents(filters=query, page=page, limit=limit, sort=created_at.lower())
        logger.debug(msg=f"Number of docs:{len(invoices)}")
        logger.debug(msg=f"Number of docs matching filters:{total_matching_docs}")
        
        if not invoices:
            msg = "There are no invoices that meet requirements"
            logger.debug(msg=msg)
            return JSONResponse(
                status_code=200,
                content={
                    "invoices": [],
                    "total": 0
                }
            )

        for invoice in invoices:
            invoice["_id"] = str(invoice["_id"])
            convert_datetime_to_iso(invoice)

        logger.debug(msg=f"Sample invoice keys: {invoices[0].keys()}")

        # Return the invoices in the expected format
        return JSONResponse(
            status_code=200,
            content={
                    "invoices": invoices,
                    "total": total_matching_docs
                }
        )

    except Exception as e:
        # Handle errors
        msg = {
                "status": "error",
                "message": str(e)
            }
        logger.debug(msg = msg)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=msg)
    

if __name__ == "__main__":

    while True:
        try:
            logger.info("Starting the server...")
            uvicorn.run(app, host=config['IES_host'], port=config['IES_port'])
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.info("Restarting the server in 5 seconds...")
            time.sleep(5)
