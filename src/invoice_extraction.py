import sys
sys.path.append("")

import base64
import os
import cv2
import numpy as np
from typing import Union
from src.Utils.utils import read_config, timeit, retry_on_failure

from dotenv import load_dotenv
load_dotenv()

class BaseExtractor:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = read_config(path=self.config_path)['llm_extract']
        self.invoice_template_path = self.config['invoice_template_path']
        
        # Load the invoice template prompt
        with open(self.invoice_template_path, 'r') as file:
            self.invoice_template = file.read()

    def extract_json(self, text: str) -> dict:
        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        json_string = text[start_index:end_index]
        json_string = json_string.replace('true', 'True').replace('false', 'False').replace('null', 'None')
        result = eval(json_string)
        return result

    def encode_image(self, image_input: Union[str, np.ndarray]):
        if isinstance(image_input, str):
            if image_input.startswith("data:image"):
                return image_input.split(",")[1]
            else:
                with open(image_input, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
        elif isinstance(image_input, np.ndarray):
            _, buffer = cv2.imencode('.png', image_input)
            return base64.b64encode(buffer).decode("utf-8")
        else:
            raise ValueError("Unsupported image input type. Please provide a file path, base64 string, or NumPy array.")

    @timeit
    @retry_on_failure(max_retries=3, delay=1.0)
    def extract_invoice(self, text, image: Union[str, np.ndarray]) -> dict:
        raise NotImplementedError("This method should be implemented by subclasses")

class OpenAIExtractor(BaseExtractor):
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__(config_path)
        self.model = self.config['model']
        self.temperature = self.config['temperature']
        self.max_tokens = self.config['max_tokens']

        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        from openai import OpenAI
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)

    def _extract_invoice_llm(self, text, base64_image):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in JSON format with the invoice information in English. Don't add any annotations there. Remember to close any bracket. And just output the field that has value, don't return field that are empty."},
                {"role": "user", "content": [
                    {"type": "text", "text": f"From the image of the bill and the text from OCR, extract the information. The text is: {text} \n The invoice template: \n {self.invoice_template}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content

    @timeit
    @retry_on_failure(max_retries=3, delay=1.0)
    def extract_invoice(self, text, image: Union[str, np.ndarray]) -> dict:
        base64_image = self.encode_image(image)
        invoice_info = self._extract_invoice_llm(text, base64_image)
        invoice_info = self.extract_json(invoice_info)
        return invoice_info

# You can create other extractor classes here, e.g., OllamaExtractor

if __name__ == "__main__":
    config_path = "config/config.yaml"
    ocr_text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"
    image_path = "fr_1.png"

    extractor = OpenAIExtractor(config_path=config_path)
    invoice_data = extractor.extract_invoice(text=ocr_text, image=image_path)
    print(invoice_data)
