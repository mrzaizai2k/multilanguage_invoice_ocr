import sys
sys.path.append("")

import numpy as np
from typing import Union
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from PIL import Image
import io
import base64
from src.invoice_extraction import BaseExtractor
from src.Utils.utils import read_config, timeit, retry_on_failure

class Qwen2Extractor(BaseExtractor):
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__(config_path)
        # Load the Qwen2 model and processor
        self.config = self.config['qwen2']
        self.model_name = self.config['model_name']
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Device used:", self.device)

        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.model_name, torch_dtype=torch.bfloat16, device_map="auto"
        )
        
        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
            min_pixels=self.config['min_pixels'],
            max_pixels=self.config['max_pixels']
        )
        self._load_dummy_data()
    
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

    def _extract_invoice_llm(self, text, image: Union[str, np.ndarray]):
        # Prepare the messages for Qwen2
        messages = [
            {"role": "system", "content": "You are a helpful assistant that help me with invoice"},
            {"role": "user", "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": f"responds in JSON format with the invoice information in English. Don't add any annotations there. Remember to close any bracket. And just output the field that has value, don't return field that are empty or null. From the image of the bill and the text from OCR, extract the information. The text is: {text} \n The invoice template: \n {self.invoice_template}"}
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
                                            temperature=self.config.get('temperature', 0.7),  # Add temperature parameter
                                            top_p=self.config.get('top_p', 0.8),              # Add top_p parameter
                                            top_k=self.config.get('top_k', 20),           # Add top_k parameter)
                                            )
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        print('raw', output_text[0])
        return output_text[0]

    def extract_json(self, text: str) -> dict:
        start_index = text.find('{')
        end_index = text.rfind('}')
        json_string = text[start_index:end_index]
        json_string = json_string.replace('true', 'True').replace('false', 'False').replace('null', 'None')
        result = eval(json_string)
        return result
    
    @timeit
    @retry_on_failure(max_retries=3, delay=1.0)
    def extract_invoice(self, text: str, image: Union[str, np.ndarray]) -> dict:
        base64_image = self.encode_image(image)  # Assuming encode_image is still applicable
        base64_image = f"data:image;base64,{base64_image}"
        invoice_info = self._extract_invoice_llm(text, base64_image)
        invoice_info = self.extract_json(invoice_info)
        return invoice_info

# Note: Integrate the Qwen2Extractor into the main script as needed.

if __name__ == "__main__":
    config_path = "config/config.yaml"
    ocr_text = "Géant Casino Annecy Welcome to our Caisse014 Date28/06/28 store, your store welcomes you Monday to Saturday from 8:30 a.m. to 9:30 pm Tel.04.50.88.20.00 Glasses 22.00e Hats 10.00e = Total (2) 32.00E CB EMV 32.00E you had the loyalty card, you would have accumulated 11SMILES Cashier000148/Time 17:46:26 Ticket number: 000130 Speed, comfort of purchase bude and controlled.. Scan'Express is waiting for you!!! Thank you for your visit See you soon"
    image_path = "fr_1.png"

    # Test Qwen2Extractor
    qwen2_extractor = Qwen2Extractor(config_path=config_path)
    qwen2_invoice_data = qwen2_extractor.extract_invoice(text=ocr_text, image=image_path)
    print("\nQwen2 Extractor Output:")
    print(qwen2_invoice_data)