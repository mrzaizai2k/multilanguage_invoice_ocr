import sys
sys.path.append("") 

import uvicorn
import time
import os
import json
import random
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
                             get_land_and_city_list, get_currencies_from_txt)
from src.invoice_extraction import validate_invoice
from src.Utils.logger import create_logger
from src.mail import EmailSender
from src.Utils.process_documents_utils import get_egw_file, get_excel_files, BatchProcessor

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

batch_processor = BatchProcessor(
    ocr_reader=ocr_reader,
    invoice_extractor=invoice_extractor,
    config=config,
    email_sender=email_sender,
    mongo_db=mongo_db,
    logger=logger,
)

def process_change_stream(config):
    global change_stream
    batch_processor.start()
    
    for change in change_stream:
        if change['operationType'] == 'insert':
            # Only process the newly inserted document
            document_id = change['documentKey']['_id']
            document = mongo_db.get_document_by_id(document_id)
            
            if document and document.get('status') == 'not extracted':
                # Try to add to queue, log if queue is full
                if not batch_processor.add_to_queue(document):
                    logger.warning(f"Could not add document {document_id} to queue - queue full or document already queued")

            # Optionally, check for any missed documents periodically
            if random.random() < 0.1:  # 10% chance to check for missed documents
                unprocessed_docs, _ = mongo_db.get_documents(
                    filters={
                        "status": "not extracted",
                        "_id": {"$nin": list(batch_processor.queued_documents.union(batch_processor.currently_processing))}
                    },
                    limit=5
                )
                
                for doc in unprocessed_docs:
                    batch_processor.add_to_queue(doc)


        elif change['operationType'] == 'update':
            try:
                # Process modified documents
                doc_id = str(change['documentKey']['_id'])
                updated_doc = mongo_db.get_document_by_id(document_id=doc_id)

                if not updated_doc:
                    logger.warning(f"Document with ID {doc_id} not found.")
                    continue

                # Check document properties before processing
                if (updated_doc.get('last_modified_by') is None or 
                        updated_doc.get('invoice_type') not in ['invoice 1', 'invoice 2']):
                    continue

                # Define the start of the month timestamp
                start_of_month = get_current_time(timezone=config['timezone']).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )

                # Process Invoice 1 EGW file if applicable
                if updated_doc['invoice_type'] == "invoice 1":
                    output_egw_file_path = get_egw_file(
                        mongo_db=mongo_db, start_of_month=start_of_month, config=config, logger=logger
                    )

                # Process Excel files for paired invoices
                employee_expense_report_path, output_2_excel = get_excel_files(
                    mongo_db=mongo_db, start_of_month=start_of_month, updated_doc=updated_doc, logger=logger
                )

                # Send email with attachments if any
                attachment_paths = [employee_expense_report_path, output_2_excel, output_egw_file_path]
                if attachment_paths:
                    email_sender.send_email(
                        email_type='send_excel',
                        receivers=None,
                        attachment_paths=attachment_paths
                    )
                    logger.debug(f"Sent email with attachments: {attachment_paths}")
                else:
                    logger.info("No attachments to send for this update.")

            except Exception as e:
                logger.error(f"Error in change stream processing: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global change_stream, change_stream_thread
    change_stream = mongo_db.start_change_stream()
    change_stream_thread = threading.Thread(target=process_change_stream, 
                                            args=(config,))
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
       
        queue = batch_processor.process_queue.qsize()
        logger.debug(f'number of docs in queue {queue}')
        if batch_processor.process_queue.qsize() >= config['batch_processor']['queue_size']:  # Adjust queue size limit as needed
            msg = {
                "status": "error",
                "message": "Server is currently processing too many documents. Please try again later."
            }
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=msg
            )
        
        # Parse JSON body
        body = await request.json()
        img = body.get("img")
        user_uuid = body.get("user_uuid")
        file_name = body.get("file_name", None)
        
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
            "file_name": file_name,
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
            uvicorn.run(app, host=config['IES_host'], port=config['IES_port'],)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.info("Restarting the server in 5 seconds...")
            time.sleep(5)
