import sys
sys.path.append("") 

import base64
import os
import cv2
import numpy as np
from openai import OpenAI
from src.Utils.utils import read_config, timeit
from typing import Literal, Union

from dotenv import load_dotenv
load_dotenv()


class InvoiceExtractor:
    def __init__(self, config_path:str = "config/config.yaml", ):
        # Load environment variables

        self.config_path = config_path
        self.config = read_config(path = self.config_path)['llm_extract']

        self.invoice_template_path = self.config['invoice_template_path']
        self.model = self.config['model']
        self.temperature = self.config['temperature']
        self.max_tokens = self.config['max_tokens']

        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
        
        # Load the invoice template prompt
        with open(self.invoice_template_path, 'r') as file:
            self.invoice_template = file.read()


    def get_invoice_info(self, text: str) -> dict:
        # Find the substring that represents the JSON object
        start_index = text.find('{')
        end_index = text.rfind('}') + 1  # Ensures we capture the closing brace of the JSON object
        
        # Extract the JSON string from the given text
        json_string = text[start_index:end_index]
        
        # Replace any non-standard JSON elements with standard ones (if needed)
        json_string = json_string.replace('true', 'True').replace('false', 'False').replace('null', 'None')
        
        # Parse the string safely as a dictionary
        result = eval(json_string)
        return result

    def encode_image(self, image_input: Union[str, np.ndarray]):
        # Encode the image input (path, NumPy array, OpenCV image, or base64 string) to a base64 string
        if isinstance(image_input, str):
            if image_input.startswith("data:image"):  # Check if the input is already a base64 string
                return image_input.split(",")[1]  # Extract the base64 part after the "data:image/png;base64,"
            else:
                # Assume the input is a file path
                with open(image_input, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
        elif isinstance(image_input, np.ndarray):
            # Handle OpenCV image (NumPy array)
            _, buffer = cv2.imencode('.png', image_input)
            return base64.b64encode(buffer).decode("utf-8")
        else:
            raise ValueError("Unsupported image input type. Please provide a file path, base64 string, or NumPy array.")

        
    def _extract_invoice_llm(self, text, base64_image):
        # Encode the image        
        # Create the chat completion request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in JSON format with the invoice information in English. Don't add any annotations there"},
                {"role": "user", "content": [
                    {"type": "text", "text": f"From the image of the bill and the text from OCR, extract the information. The text is: {text} \n The invoice template: \n {self.invoice_template}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        # Extract the invoice information from the response
        invoice_data = response.choices[0].message.content
        return invoice_data

    @timeit
    def extract_invoice(self, text, image: Union[str, np.ndarray]) -> dict:
        base64_image = self.encode_image(image)
        invoice_info = self._extract_invoice_llm(text, base64_image)
        invoice_info = self.get_invoice_info(invoice_info)
        return invoice_info


# Example usage
if __name__ == "__main__":
    # Initialize the invoice extractor
    config_path = "config/config.yaml"
    # OCR text from the invoice
    ocr_text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"

    # Path to the invoice image
    image_path = "test_images/fr_1.png"
    image = cv2.imread(image_path)

    extractor = InvoiceExtractor(config_path=config_path)
    # Extract the invoice information
    invoice_data = extractor.extract_invoice(text=ocr_text, image=image)
    print(invoice_data)
