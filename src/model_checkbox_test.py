import sys
sys.path.append("")

import base64
import os
import cv2
import numpy as np
from typing import Union
from PIL import Image
from src.Utils.utils import read_config, valid_base64_image

from dotenv import load_dotenv
load_dotenv()

config_path = "config/config.yaml"
config = read_config(path = config_path)
config = config['llm_extract']['openai']
model = config['model_name']
temperature = config['temperature']
max_tokens = config['max_tokens']

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


import cv2
import numpy as np
import base64
from PIL import Image


def encode_image(image_input: Union[str, np.ndarray, Image.Image]) -> str:
        if isinstance(image_input, str):
            try:  # Check if it's a local file path
                with open(image_input, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            except:  # If not, assume it's a base64 string and validate it
                image_input = valid_base64_image(data_url=image_input)
                return image_input

        elif isinstance(image_input, np.ndarray):
            # Convert NumPy array to PNG format and encode to base64
            _, buffer = cv2.imencode('.png', image_input)
            return base64.b64encode(buffer).decode("utf-8")
        
        elif isinstance(image_input, Image.Image):
            # Convert PIL image to bytes, then encode to base64
            buffer = np.array(image_input)
            _, buffer = cv2.imencode('.png', cv2.cvtColor(buffer, cv2.COLOR_RGB2BGR))
            return base64.b64encode(buffer).decode("utf-8")

def extract_invoice_llm(ocr_text, base64_image:str, invoice_template:str):
        response = client.chat.completions.create(
            model= model,
            messages=[
                {"role": "system", "content": """You are a helpful assistant that responds in JSON format with the invoice information in English. 
                                            Don't add any annotations there. Remember to close any bracket. And just output the field that has value, 
                                            don't return field that are empty. number, price and amount should be number, date should be convert to dd/mm/yyyy, 
                                            time should be convert to HH:mm:ss, currency should be 3 chracters like VND, USD, EUR"""},
                {"role": "user", "content": [
                    # {"type": "text", "text": f"From the image of the bill and the text from OCR, extract the information. The ocr text is: {ocr_text} \n. Return the key names as in the template is a MUST. The invoice template: \n {invoice_template}"},
                    {"type": "text", "text": f"From the image of the bill, which items has handwritten check box symbol in the column zahlungsart and same row, and what is the check box saying, the boxes can be setzt gebahrlt, mit Visa gezahlt, and kostenuebernahme"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

if __name__ == "__main__":
        
    ocr_text = """Recording of external assignments - Confidential - Tuuulev Divl Last name, first name: transaction number: 24 0o4 s Timesheet created in the EGW Actually paid and proven additional travel costs (attach receipts): Version 2.1 Description* Individual amounts Payment method Hotel without breakfast with breakfast E 4125o paid by yourself with Paid Visa can you book again? Yes, costs covered, invoice paid to the company for refueling t 98 paid by yourself with Visa paid for costs taken over, invoice paid to the company Parking fees C paid by yourself paid with Visa Costs taken over, invoice paid to the company Rental car paid by itself E 15620 paid with Visa Covered costs , invoice to the company toll € 20 paid by yourself paid with Visa, cost assumption, invoice paid to the company os'hZ D self paid with Visa paid railway hcket cost assumption, invoice to the company E 9 so self paid with Visa paid f4001171t cost assumption, invoice in the Company paid by itself, paid with Visa, cost assumption, invoice paid to the company itself, paid with Visa, cost assumption, invoice to the company observe!!! The following applies to overnight stays: These must also be stated if payment was made directly via a3Ds. In this case, the sum O,-f must be stated. For overnight stays, it must always be stated whether breakfast was offered with or without. For the accuracy of the date and signature of the employee: This template is used to record external assignments, is the basis for the expense report and must be submitted to the administration upon return. This template can be found at D:UsersPublicDocumentsa3Dsa3Ds_QMVorlagen_Templates Page 2 of 2"""
    image_path = "test/images/005_2.png"

    config_path = "config/config.yaml"
    config = read_config(path = config_path)
    invoice_template_path = config['invoice_dict']['invoice 2']
    
    with open(invoice_template_path, 'r') as file:
        invoice_template = file.read()

    
    base64_image = encode_image(image_path)


    invoice_data = extract_invoice_llm(ocr_text=ocr_text, base64_image=base64_image, 
                                             invoice_template=invoice_template)
    print(invoice_data)
