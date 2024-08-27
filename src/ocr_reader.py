import sys
sys.path.append("") 

import json
import sys
from paddleocr import PaddleOCR
from transformers import pipeline
from PIL import Image
import torch
import cv2
import numpy as np

class OcrReader:
    def __init__(self, json_path, 
                 device=None, 
                 language_detector:str = "facebook/metaclip-b32-400m",
                 language_thresh:float = 0.2, ):
        # Load language dictionary from JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            self.language_dict = json.load(f)

        self.language_detector = language_detector
        self.language_thresh = language_thresh

        # Set up the device (CPU or GPU)
        if device:
            self.device = device
        else:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load zero-shot image classification model
        self.image_classifier = pipeline(task="zero-shot-image-classification", 
                                         model=self.language_detector, 
                                         device=self.device,
                                         batch_size = 8,)
    
    def get_image(self, input_data):
        if isinstance(input_data, str):  # If input_data is a path
            image = Image.open(input_data)
        elif isinstance(input_data, Image.Image):  # If input_data is a PIL image
            image = input_data
        else:
            raise ValueError("Unsupported input data type")
        return image
    
    def get_lang(self, image):
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

    def get_text(self, input_data):
        # Detect the language of the image
        image = self.get_image(input_data)
        
        lang = self.get_lang(image)

        # Initialize the PaddleOCR with the detected language
        ocr = PaddleOCR(lang=lang, show_log=False)

        # Perform OCR on the input image
        if isinstance(input_data, str):  # If input_data is a path
            result = ocr.ocr(input_data)
        elif isinstance(input_data, cv2.Mat) or isinstance(input_data, Image.Image):  # If input_data is an OpenCV image or PIL image
            result = ocr.ocr(np.array(image))

        # Combine the recognized text from the OCR result
        text = " ".join([line[1][0] for line in result[0]])
        
        data = {
            "text": text,
            "language": lang
        }
        return data

def load_image(image_path: str):
    try:
        return Image.open(image_path)
    except Exception as e:
        print(f'{image_path}: Error loading image - {e}')
        return None
        
# Example usage
if __name__ == "__main__":
    json_path = "config/language_dict.json"
    img_path = "test_images/fr_1.png"
    image = load_image(img_path)

    ocr_reader = OcrReader(json_path=json_path)
    detected_lang = ocr_reader.get_lang(image)
    print("Detected Language:", detected_lang)

    recognized_text = ocr_reader.get_text(image)

    print("Recognized Text:", recognized_text)

