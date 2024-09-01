import sys
sys.path.append("") 

import json
import sys
from paddleocr import PaddleOCR
from transformers import pipeline
from PIL import Image
import torch
import numpy as np
import requests
from src.Utils.utils import timeit, read_config, resize_same_ratio

class GoogleTranslator:
    def __init__(self):
        pass

    def translate(self, text, to_lang, max_input_length=4900):
        url = 'https://translate.googleapis.com/translate_a/single'
        src_language = None

        def get_translation_chunk(chunk):
            nonlocal src_language  # Allow modification of src_language within this function
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': to_lang,
                'dt': ['t', 'bd'],
                'dj': '1',
                'source': 'popup5',
                'q': chunk
            }
            response = requests.get(url, params=params, verify=False).json()
            sentences = response.get('sentences', [])
            translated_chunk = ""
            for sentence in sentences:
                translated_chunk += sentence.get('trans', "")
            
            # Get the source language only once, during the first chunk
            if src_language is None:
                src_language = response.get('src', 'unknown')
            
            return translated_chunk
        
        # Perform the translation in chunks if the text exceeds the max input length
        translated_text = ""
        for i in range(0, len(text), max_input_length):
            chunk = text[i:i + max_input_length]
            translated_text += get_translation_chunk(chunk) + "\n"
        
        return translated_text.strip(), src_language
    
class OcrReader:
    def __init__(self,  
                 device=None, 
                 translator=None,
                 config_path:str = "config/config.yaml"
                 ):
        
        self.config_path = config_path
        self.config = read_config(path = self.config_path)['ocr']

        self.language_dict_path = self.config['language_dict_path']
        self.language_detector = self.config['language_detector']
        self.language_thresh = self.config['language_thresh']
        self.target_language = self.config['target_language']
        self.resize_size = self.config['resize_size']


        # Load language dictionary from JSON file
        with open(self.language_dict_path, 'r', encoding='utf-8') as f:
            self.language_dict = json.load(f)

        device = self.config.get('device', None)
        # Set up the device (CPU or GPU)
        if device:
            self.device = device
        else:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print("Device", self.device)

        self.translator = translator

        # Load zero-shot image classification model
        self.initialize_language_detector()
        
    def initialize_language_detector(self):
        # Create a dummy image for model initialization
        dummy_image = Image.new("RGB", (224, 224), color=(255, 255, 255))  # White image
        candidate_labels = ["en", "fr"]  # Example labels

        # Initialize the zero-shot image classification model
        self.image_classifier = pipeline(task="zero-shot-image-classification", 
                                         model=self.language_detector, 
                                         device=self.device,
                                         batch_size=8)

        # Perform a dummy inference to warm up the model
        self.image_classifier(dummy_image, candidate_labels=candidate_labels)
        print("Model pipeline initialized with dummy data.")

    def get_image(self, input_data:any) -> Image:
        if isinstance(input_data, str):  # If input_data is a path
            image = Image.open(input_data)
        elif isinstance(input_data, Image.Image):  # If input_data is a PIL image
            image = input_data
        else:
            raise ValueError("Unsupported input data type")
        
        image = resize_same_ratio(image, target_size=self.resize_size)
        return image
    
    @timeit
    def _get_lang(self, image: Image.Image) -> str:
        # Define candidate labels for language classification
        candidate_labels = [f"language {key}" for key in self.language_dict]

        # Perform inference to classify the language
        outputs = self.image_classifier(image, candidate_labels=candidate_labels)
        outputs = [{"score": round(output["score"], 4), "label": output["label"] } for output in outputs]
        
        # Extract the language with the highest score
        language_names = [entry['label'].replace('language ', '') for entry in outputs]
        scores = [entry['score'] for entry in outputs]
        abbreviations = [self.language_dict.get(language) for language in language_names]
        
        first_abbreviation = abbreviations[0]
        lang = 'en'  # Default to English
        
        if scores[0] > self.language_thresh:
            lang = first_abbreviation

        return lang

    @timeit
    def get_text(self, input_data):
        # Detect the language of the image
        image = self.get_image(input_data)
        
        src_language = self._get_lang(image)

        # Initialize the PaddleOCR with the detected language
        ocr = PaddleOCR(lang=src_language, show_log=False, use_angle_cls=True)

        result = ocr.ocr(np.array(image))

        # Combine the recognized text from the OCR result
        text = " ".join([line[1][0] for line in result[0]])

        # Handle translation if a translator and target language are provided
        if self.translator and self.target_language:
            trans_text, src_language = self.translator.translate(text=text, to_lang=self.target_language)

            data = {
                "ori_text": text,
                "ori_language": src_language,
                "text": trans_text,
                "language": self.target_language,
            }
        else:
            # If translation is not required, use the original text and language
            trans_text, src_language = text, src_language
            data = {
                "ori_text": text,
                "ori_language": src_language,
                "text": trans_text,
                "language": src_language,
            }

        
        return data
    
def load_image(image_path: str):
    try:
        # Check if the path is a URL
        if image_path.startswith(('http://', 'https://')):
            image = Image.open(requests.get(image_path, stream=True).raw)
        else:
            image = Image.open(image_path)  # Load image from local path
        return image
    except Exception as e:
        print(f'{image_path}: Error loading image - {e}')
        return None
    
# Example usage
if __name__ == "__main__":
    # img_path = "test/images/fr_1.png"
    config_path = "config/config.yaml"
    
    img_path = "https://i.etsystatic.com/25406056/r/il/f891ca/2576207654/il_fullxfull.2576207654_l7av.jpg"

    image = load_image(img_path)

    ocr_reader = OcrReader(config_path=config_path, 
                           translator=GoogleTranslator())

    recognized_text = ocr_reader.get_text(image)
    print("Recognized Text:", recognized_text)
