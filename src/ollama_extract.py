from llama_index.multi_modal_llms.ollama import OllamaMultiModal
# from pathlib import Path
# from llama_index.core import Document
from pydantic import BaseModel
from typing import List, Optional
from llama_index.core.program import MultiModalLLMCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
# from PIL import Image
# import base64
# import io
from llama_index.core import SimpleDirectoryReader

# Define the path to your local image
local_image_path = ["test/images/fr_1.png"]

image_documents = SimpleDirectoryReader(input_files = local_image_path).load_data()

# Initialize the multi-modal model
mm_model = OllamaMultiModal(model="llava-llama3", request_timeout=60)


class VatItem(BaseModel):
    amount: Optional[float] = None
    amount_excl_vat: Optional[float] = None
    amount_incl_vat: Optional[float] = None
    amount_incl_excl_vat_estimated: Optional[bool] = None
    percentage: Optional[int] = None
    code: Optional[str] = None

class LineItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    amount_each: Optional[float] = None
    amount_ex_vat: Optional[float] = None
    vat_amount: Optional[float] = None
    vat_percentage: Optional[float] = None
    quantity: Optional[int] = None
    unit_of_measurement: Optional[str] = None
    sku: Optional[str] = None
    vat_code: Optional[str] = None

class Line(BaseModel):
    description: Optional[str] = None
    lineitems: Optional[List[LineItem]] = None

class Invoice(BaseModel):
    document_type: Optional[str] = None
    amount: Optional[float] = None
    amount_change: Optional[float] = None
    amount_shipping: Optional[float] = None
    vatamount: Optional[float] = None
    amountexvat: Optional[float] = None
    currency: Optional[str] = None
    date: Optional[str] = None
    purchasedate: Optional[str] = None
    purchasetime: Optional[str] = None
    # vatitems: Optional[List[VatItem]] = None
    vat_context: Optional[str] = None
    # lines: Optional[List[Line]] = None
    paymentmethod: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_type: Optional[str] = None
    receipt_number: Optional[str] = None
    order_number: Optional[str] = None
    merchant_name: Optional[str] = None
    merchant_coc_number: Optional[str] = None
    merchant_vat_number: Optional[str] = None
    merchant_website: Optional[str] = None
    merchant_email: Optional[str] = None
    merchant_address: Optional[str] = None
    merchant_zipcode: Optional[str] = None
    merchant_city: Optional[str] = None
    merchant_country_code: Optional[str] = None
    merchant_phone: Optional[str] = None
    customer_number: Optional[str] = None
    document_language: Optional[str] = None

# Define the prompt template
prompt_template_str = """

{query_str}
"""

# Initialize the multi-modal program
mm_program = MultiModalLLMCompletionProgram.from_defaults(
    output_parser=PydanticOutputParser(Invoice),
    image_documents=image_documents,
    prompt_template_str=prompt_template_str,
    multi_modal_llm=mm_model,
    verbose=True,
)

# Run the program
text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"

response = mm_program(query_str=f"USe the image and the text from OCR, Describe what's in the image. The text is: {text}")

# Print the results
print(response)

#############################################
def test_ollama():
    import base64
    import requests

    def send_image_to_ollama(image_path):
        # Read the image from the local path and convert it to base64
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare the data for the API request
        data = {
            "model": "llama3.1:8b",
            "messages": [
                {
                    "role": "user",
                    "content": "what is in this image?",
                    "images": [encoded_image]
                }
            ]
        }

        # Send the request to the Ollama API
        response = requests.post("http://localhost:11434/api/chat", json=data)

        # Print the response from the API
        print(response.text)

    # Usage example
    image_path = "test/images/fr_1.png"  # Replace with the actual path to your image
    send_image_to_ollama(image_path)

######################

