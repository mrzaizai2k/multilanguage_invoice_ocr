import sys
sys.path.append("") 

from fastapi import (FastAPI, Request, Header, 
                     status, HTTPException, Query)
from fastapi.responses import JSONResponse
from pymongo import ASCENDING, DESCENDING
from typing import Optional
from datetime import datetime, timezone

from src.ocr_reader import OcrReader
from src.invoice_extraction import OpenAIExtractor
from src.qwen2_extract import Qwen2Extractor
from src.mongo_database import MongoDatabase
from src.Utils.utils import *

app = FastAPI()
config_path='config/config.yaml'
config = read_config(path=config_path)

mongo_db = MongoDatabase(config_path=config_path)

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
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "message": "Base64 image is required",
                })
        
        # Generate invoice UUID
        current_time = datetime.now(timezone.utc)
        img = valid_base64_image(img)       
        
        invoice_document = {
            "invoice_type": None,
            "created_at": current_time,
            "created_by": user_uuid,
            "last_modified_at": None,
            "last_modified_by": None,
            "status": "not extracted",
            "invoice_image_base64": img,
            "invoice_info": {}
        }
        
        invoice_uuid = mongo_db.create_document(invoice_document)
        print('result save mongo', invoice_uuid)
        mongo_db.update_document_by_id(invoice_uuid, {"invoice_uuid": invoice_uuid})

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "invoice_uuid": invoice_uuid,
                "message": "Upload successful"
            }
        )

    except Exception as e:
        # Handle errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": str(e)
            })
    

@app.delete("/api/v1/invoices/{invoice_uuid}")
async def delete_invoice(invoice_uuid: str):
    try:
        mongo_db.delete_document_by_id(invoice_uuid)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Invoice deleted successfully"
            }
        )
    
    except Exception as e:
        # Handle errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": str(e)
            })
    

@app.put("/api/v1/invoices/{invoice_uuid}")
async def modify_invoice(invoice_uuid: str, request: Request):
    try:
        # Parse JSON body
        body = await request.json()
        user_uuid = body.get("user_uuid")
        invoice_info = body.get("invoice_info")
        
        if not invoice_info:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "message": "Invoice information is required",
                })
        

        # Prepare update fields
        update_fields = {
            "invoice_info": invoice_info,
            "last_modified_at": datetime.now(timezone.utc),
            "last_modified_by": user_uuid
        }

        # Update the document in the database
        try:
            mongo_db.update_document_by_id(invoice_uuid, update_fields)
        except:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Failed to update the invoice",
                })

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "invoice_uuid": invoice_uuid,
                "message": "Invoice information updated."
            }
        )

    except Exception as e:
        # Handle errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": str(e)
            })

@app.get("/api/v1/invoices")
async def get_invoices(
    created_at: Optional[str] = Query("asc", description="Sort by creation date (asc or desc)"),
    created_by: Optional[str] = Query(None, description="Filter by user_uuid of the invoice creator"),
    invoice_type: Optional[str] = Query(None, description="Filter by type of invoice"),
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

        # Fetch documents from MongoDB
        invoices = mongo_db.get_documents(query, page=page, limit=limit, sort=created_at.lower())
        

        for invoice in invoices:
            invoice["_id"] = str(invoice["_id"])
            if "created_at" in invoice:
                invoice["created_at"] = invoice["created_at"].isoformat()  # Convert datetime to ISO format

        print("len",len(invoices))
        print("invoice",invoices[0]['created_at'])

        # Return the invoices in the expected format
        return JSONResponse(
            status_code=200,
            content=invoices
        )

    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config['IES_host'], port=config['IES_port'])
