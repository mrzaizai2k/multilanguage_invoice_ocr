import sys
sys.path.append("")

import base64
import os
import cv2
import numpy as np
from typing import Union
from llama_index.llms.ollama import Ollama
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

class InvoicePostProcessing:
    def __init__(self, config_path:str):
        self.config_path = config_path
        self.config = read_config(self.config_path)['postprocessing']

        self.model_name=self.config['model_name'] 
        self.request_timeout=self.config['request_timeout'] 
        self.llm = Ollama(model=self.model_name, request_timeout= self.request_timeout, json_mode=True)
        self._load_dummy_data()

    
    def _load_dummy_data(self):
        # Dummy OCR text
        try:
            response = self.llm.complete("who are you")
            # Print the response for verification
            print(f"Dummy data processing output:{response}")
        except Exception as e:
            print(f"Error in loading dummy data: {e}")
        
    def postprocess(self, invoice_template:str,
                        ocr_text: str, model_text: str) -> str:

        # Prepare the prompt for the LLM
        prompt = f"""
        You are a helpful assistant that responds in JSON format with the invoice information in English. Don't add any annotations there. Remember to close any bracket. And just output the field that has value, don't return field that are empty.
        Use the text from the model response and the text from OCR. Describe what's in the image as the template here: 
        {invoice_template}. 
        The OCR text is: {ocr_text} 
        The model response text is: {model_text}
        """

        # Generate the response from the LLM
        response = self.llm.complete(prompt)
        return response.text
    
class OpenAIExtractor(BaseExtractor):
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__(config_path)
        self.config = self.config['openai']
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

    def extract_json(self, text: str) -> dict:
        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        json_string = text[start_index:end_index]
        json_string = json_string.replace('true', 'True').replace('false', 'False').replace('null', 'None')
        result = eval(json_string)
        return result

    @timeit
    @retry_on_failure(max_retries=3, delay=1.0)
    def extract_invoice(self, text, image: Union[str, np.ndarray]) -> dict:
        base64_image = self.encode_image(image)
        invoice_info = self._extract_invoice_llm(text, base64_image)
        invoice_info = self.extract_json(invoice_info)
        return invoice_info


def test_post_processing():
    ocr_text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"
    model_text = """- Store name: Géant Casino
    - Location: Annecy
    - Date: 28/06/2008
    - Caisse: 014
    - Phone number: 04.50.88.20.00
    - Opening hours: Monday to Saturday from 8:30 a.m. to 9:30 p.m.
    - Prices for items:
      - Glasses: 22.00€
      - Hats: 10.00€
    - Total amount: 32.00€
    - CB EMV: 32.00€
    - Loyalty card information: You had the loyalty card, you would have accumulated 11 SMILES
    - Cashier's information: Cashier number: 000148, Time: 17:46:26, Ticket number: 000130
    - Additional notes: Scan'Express is waiting for you!!! Thank you for your visit, see you soon"""

    config_path = "config/config.yaml"
    invoice_template_path = "config/invoice_template.txt"
    with open(invoice_template_path, 'r') as file:
            invoice_template = file.read()

    processor = InvoicePostProcessing(config_path)
    result_json = processor.postprocess(invoice_template, ocr_text, model_text)
    print(result_json)

def test_openai_invoice():
    config_path = "config/config.yaml"
    ocr_text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"
    image_path = "fr_1.png"

    extractor = OpenAIExtractor(config_path=config_path)
    invoice_data = extractor.extract_invoice(text=ocr_text, image=image_path)
    print(invoice_data)

if __name__ == "__main__":

    # test_openai_invoice()
    test_post_processing()
