from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import base64
import io
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from src.ocr_reader import OcrReader
from src.invoice_extraction import InvoiceExtractor

app = FastAPI()

# Initialize OCRReader and InvoiceExtractor
ocr_reader = OcrReader()
invoice_extractor = InvoiceExtractor()

class InvoiceRequest(BaseModel):
    images: List[str]

class ExtractedInvoice(BaseModel):
    text: str
    error: str = ""

class InvoiceResponse(BaseModel):
    results: List[ExtractedInvoice]

def process_image(base64_image: str) -> ExtractedInvoice:
    try:
        # Decode base64 image
        image_data = base64.b64decode(base64_image)
        original_image = Image.open(io.BytesIO(image_data))
        
        # Extract text using OCRReader
        ocr_result = ocr_reader.get_text(original_image)  # No rotation now
        extracted_text = ocr_result['text']
        
        # Extract invoice information
        invoice_info = invoice_extractor.extract_invoice(extracted_text, np.array(original_image))
        
        # You might want to format invoice_info into a string or keep it as a dict
        return ExtractedInvoice(text=str(invoice_info))
    except Exception as e:
        return ExtractedInvoice(text="", error=str(e))

@app.post("/extract-invoices/", response_model=InvoiceResponse)
async def extract_invoices(request: InvoiceRequest):
    if not request.images:
        raise HTTPException(status_code=400, detail="No images provided")

    # Process images concurrently
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, process_image, image) for image in request.images]
        results = await asyncio.gather(*tasks)

    return InvoiceResponse(results=results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
