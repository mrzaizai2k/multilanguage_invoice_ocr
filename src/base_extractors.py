import sys
sys.path.append("")

import base64
import os
import cv2
import numpy as np
from typing import Union
import asyncio
from openai import AsyncOpenAI
from llama_index.llms.ollama import Ollama
from PIL import Image
from src.Utils.utils import read_config, timeit, retry_on_failure, valid_base64_image

from dotenv import load_dotenv
load_dotenv()

class BaseExtractor:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = read_config(path=self.config_path)['llm_extract']

    
    def encode_image(self, image_input: Union[str, np.ndarray, Image.Image]) -> str:
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
        
        else:
            raise ValueError("Unsupported image input type. Please provide a file path, base64 string, NumPy array, or PIL Image.")


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
        You are a helpful assistant that responds in JSON format with the invoice information in English. 
        Don't add any annotations there. Remember to close any bracket. And just output the field that has value, 
        don't return field that are empty. number, price and amount should be number, date should be convert to dd/mm/yyyy, 
        time should be convert to HH:mm:ss, currency should be 3 chracters like VND, USD, EUR.
        Use the text from the model response and the text from OCR. Return the key names as in the template is a MUST. Describe what's in the image as the template here: 
        {invoice_template}. 
        The OCR text is: {ocr_text} 
        The model response text is: {model_text}
        """

        # Generate the response from the LLM
        response = self.llm.complete(prompt)
        return response.text
    
    def __getitem__(self, item):
        if item == "post_processor":
            return self.model_name
        else:
            raise KeyError(f"No such key: {item}")
    

class OpenAIExtractor(BaseExtractor):
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__(config_path)

        self.config = self.config['openai']
        self.model = self.config['model_name']
        self.temperature = self.config['temperature']
        self.max_tokens = self.config['max_tokens']

        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=self.OPENAI_API_KEY)

    async def _extract_invoice_llm(self, ocr_text, base64_image: str, invoice_template: str):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """You are a helpful assistant that responds in JSON format with the invoice information in English. 
                                            Don't add any annotations there. Remember to close any bracket. And just output the field that has value, 
                                            don't return field that are empty. number, price and amount should be number, date should be convert to dd/mm/yyyy, 
                                            time should be convert to HH:mm:ss, currency should be 3 chracters like VND, USD, EUR"""},
                {"role": "user", "content": [
                    {"type": "text", "text": f"From the image of the bill and the text from OCR, extract the information. The ocr text is: {ocr_text} \n. Return the key names as in the template is a MUST. The invoice template: \n {invoice_template}"},
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

    @retry_on_failure(max_retries=3, delay=1.0)
    async def extract_invoice(self, ocr_text, image: Union[str, np.ndarray], invoice_template: str) -> list:
        base64_image = self.encode_image(image)

        async def process_response():
            response = await self._extract_invoice_llm(ocr_text, base64_image, invoice_template=invoice_template)
            json_response = self.extract_json(response)
            print(f"Response: {json_response}")
            return json_response

        tasks = [process_response() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        # combined_result = self.combine_results(results)
        combined_result = await self.combine_results_AI(ocr_text=ocr_text, results = results)
        combined_result = self.extract_json(combined_result)
        return combined_result
    
    async def combine_results_AI(self, ocr_text, results:list[str]):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """You are a helpful assistant that responds in JSON format with the invoice information in English. 
                                            Don't add any annotations there. Remember to close any bracket. And just output the field that has value, 
                                            don't return field that are empty. number, price and amount should be number, date should be convert to dd/mm/yyyy, 
                                            time should be convert to HH:mm:ss, currency should be 3 chracters like VND, USD, EUR"""},
                {"role": "user", "content": [
                    {"type": "text", "text": f"From the image of the model answers and the text from OCR, combine the information and return only 1 final json of invoice_info, not a list. The ocr text is: {ocr_text} \n. Return the key names as in the template is a MUST. The results are: \n {str(results)}"},
                ]}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content


    def __getitem__(self, item):
        if item == "llm_extractor":
            return self.model
        elif item == "post_processor":
            return self.model
        else:
            raise KeyError(f"No such key: {item}")
    
    def combine_results(self, results: list) -> dict:
        if not results:
            return {}

        def merge_dicts(dicts):
            if not dicts:
                return {}

            merged = {}
            for key in dicts[0].keys():
                values = [d[key] for d in dicts if key in d]
                if isinstance(values[0], dict):
                    merged[key] = merge_dicts(values)
                elif isinstance(values[0], list):
                    merged[key] = merge_lists(values)
                else:
                    value_counts = {}
                    for value in values:
                        value_counts[str(value)] = value_counts.get(str(value), 0) + 1
                    most_common = max(value_counts, key=value_counts.get)
                    if len(set(values)) == len(values):
                        merged[key] = values[0]
                    else:
                        merged[key] = parse_value(most_common)
            return merged

        def merge_lists(lists):
            if not lists:
                return []

            max_length = max(len(lst) for lst in lists)
            merged = []
            for i in range(max_length):
                items = [lst[i] for lst in lists if i < len(lst)]
                if items and isinstance(items[0], dict):
                    merged.append(merge_dicts(items))
                else:
                    # Just return the first item as the merged result or None if items are empty
                    merged.append(parse_value(items[0]) if items else None)
            return merged

        def parse_value(value):
            if isinstance(value, (int, float)):
                return value
            if isinstance(value, str):
                if value.replace('.', '', 1).isdigit():  # Check if it's a valid float
                    return float(value)
                if value.isdigit():  # Check if it's a valid int
                    return int(value)
            return value  # Return as is if it's not a number

        return merge_dicts([result for result in results])

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
    config = read_config(path = config_path)
    invoice_template_path = config['invoice_dict']['invoice 3']
    with open(invoice_template_path, 'r') as file:
            invoice_template = file.read()

    processor = InvoicePostProcessing(config_path)
    result_json = processor.postprocess(invoice_template, ocr_text, model_text)
    print(result_json)


async def test_openai_invoice():
    config_path = "config/config.yaml"
    ocr_text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"
    image_path = "fr_1.png"
    config_path = "config/config.yaml"
    config = read_config(path = config_path)
    invoice_template_path = config['invoice_dict']['invoice 3']
    
    with open(invoice_template_path, 'r') as file:
        invoice_template = file.read()

    extractor = OpenAIExtractor(config_path=config_path)
    invoice_data = await extractor.extract_invoice(ocr_text=ocr_text, image=image_path, 
                                             invoice_template=invoice_template)
    print("\ninvoice_data", invoice_data)


if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(test_openai_invoice())
    end = time.time()
    print("process", end-start)

    # test_post_processing()
