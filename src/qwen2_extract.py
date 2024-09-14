import sys
sys.path.append("")

import numpy as np
from typing import Union
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from base_extractors import BaseExtractor, InvoicePostProcessing
from src.Utils.utils import read_config, timeit, retry_on_failure


class Qwen2Extractor(BaseExtractor):
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__(config_path)

        self.post_processor = InvoicePostProcessing(config_path=self.config_path)
        # Load the Qwen2 model and processor
        self.config = self.config['qwen2']
        self._initialize_model()
        self._load_dummy_data()
    
    def _initialize_model(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Device used: {self.device}")

        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.config['model_name'],
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        
        self.processor = AutoProcessor.from_pretrained(
            self.config['model_name'],
            min_pixels=self.config['min_pixels'],
            max_pixels=self.config['max_pixels']
        )

    def _load_dummy_data(self):
        """Load or generate dummy data for testing the model during initialization."""
        # Dummy text
        dummy_text = "This is a dummy invoice text for testing purposes."

        # Dummy image: Create a simple black square as a dummy image
        dummy_image = np.zeros((224, 224, 3), dtype=np.uint8)
        dummy_image_base64 = f"data:image;base64,{self.encode_image(dummy_image)}"

        # Perform a dummy extraction
        print("Performing dummy extraction to verify model initialization...")
        try:
            dummy_output = self._extract_invoice_llm(dummy_text, dummy_image_base64)
            print("Dummy extraction output:", dummy_output)
        except Exception as e:
            print("Error during dummy extraction:", e)

    @timeit
    def _extract_invoice_llm(self, text, image: Union[str, np.ndarray]):
        # Prepare the messages for Qwen2
        messages = [
            {"role": "system", "content": "You are a helpful assistant that help me with invoice"},
            {"role": "user", "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": f"From the image of the bill and the text from OCR, extract the useful information on the invoice. The text is: {text}"}
            ]}
        ]

        # Preparation for inference
        text_inputs = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text_inputs],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        inputs = inputs.to(self.device)

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=self.config['max_new_tokens'],
                                            temperature=self.config['temperature'],  # Add temperature parameter
                                            top_p=self.config['top_p'],              # Add top_p parameter
                                            top_k=self.config['top_k'],           # Add top_k parameter)
                                            )
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text[0]
    
    @timeit
    def post_process(self, ocr_text:str, model_text:str, invoice_template:str) -> str:
        response = self.post_processor.postprocess(invoice_template=invoice_template, 
                                                   ocr_text=ocr_text, model_text=model_text)
        return response

    def extract_json(self, text: str) -> dict:
        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        json_string = text[start_index:end_index]
        json_string = json_string.replace('true', 'True').replace('false', 'False').replace('null', 'None')
        result = eval(json_string)
        return result
 
    
    @timeit
    @retry_on_failure(max_retries=3, delay=1.0)
    def extract_invoice(self, ocr_text: str, image: Union[str, np.ndarray], 
                        invoice_template:str) -> dict:
        
        base64_image = self.encode_image(image)  # Assuming encode_image is still applicable
        base64_image = f"data:image;base64,{base64_image}"
        model_text = self._extract_invoice_llm(ocr_text, base64_image)
        pre_invoice_info = self.post_process(ocr_text=ocr_text, model_text=model_text, 
                                             invoice_template = invoice_template)
        invoice_info = self.extract_json(pre_invoice_info)
        return invoice_info
    
    def __getitem__(self, item):
        if item == "llm_extractor":
            return self.config['model_name']
        elif item == "post_processor":
            if self.post_processor:
                return self.post_processor['post_processor']
            else:
                return None
        else:
            raise KeyError(f"No such key: {item}")

# Note: Integrate the Qwen2Extractor into the main script as needed.

if __name__ == "__main__":
    config_path = "config/config.yaml"
    ocr_text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"
    image_path = "fr_1.png"

    invoice_template_path = "config/invoice_template.txt"
    with open(invoice_template_path, 'r') as file:
        invoice_template = file.read()
    # Test Qwen2Extractor
    qwen2_extractor = Qwen2Extractor(config_path=config_path)
    qwen2_invoice_data = qwen2_extractor.extract_invoice(ocr_text=ocr_text, image=image_path, 
                                                         invoice_template =invoice_template)
    print("\nQwen2 Extractor Output:")
    print(qwen2_invoice_data)
    print(qwen2_extractor['post_processor'], qwen2_extractor['llm_extractor'])