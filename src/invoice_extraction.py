import sys
sys.path.append("") 
import re
import numpy as np
import asyncio

from copy import deepcopy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional

from src.ocr_reader import OcrReader, GoogleTranslator
from src.base_extractors import OpenAIExtractor, BaseExtractor
# from src.qwen2_extract import Qwen2Extractor
from src.Utils.utils import (timeit, read_config, convert_img_path_to_base64, 
                             get_current_time, convert_base64_to_pil_image, read_txt_file)
from src.validate_invoice import (validate_invoice_3, validate_invoice_1,validate_invoice_2,
                                    Invoice3, Invoice2, Invoice1)

def preprocess_text(text: str) -> str:
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase and remove extra whitespace
    return ' '.join(text.lower().split())


def compare_with_templates(input_text: str, 
                        invoice_txt_template: dict, 
                        threshold: float = 0.3) -> Optional[str]:
    """
    Compares the input text with templates and returns the key of the most similar template if it meets the threshold.

    Args:
        input_text (str): The input text to compare.
        invoice_txt_template (dict): Dictionary mapping invoice names to template paths.
        threshold (float): Cosine similarity threshold for determining if the template is a good match.

    Returns:
        Optional[str]: The key of the most similar template if it meets the threshold, otherwise None.
    """
    
    # Extract template paths from the dictionary
    template_paths = list(invoice_txt_template.values())
    template_keys = list(invoice_txt_template.keys())
    
    # Read and preprocess templates
    templates = [read_txt_file(path) for path in template_paths]
    preprocessed_templates = [preprocess_text(template) for template in templates]
    preprocessed_input = preprocess_text(input_text)

    # TF-IDF with cosine similarity
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_templates + [preprocessed_input])
    cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]

    # Find the index of the most similar template
    max_score_index = np.argmax(cosine_similarities)
    max_cosine_similarity = cosine_similarities[max_score_index]

    # Check if the most similar template meets the threshold
    if max_cosine_similarity < threshold:
        return None
    else:
        return template_keys[max_score_index]


def get_document_type(ocr_result: dict, config: dict) -> str:
    """
    Determines the document type based on OCR results and configured templates.
    
    Args:
        ocr_result (dict): Dictionary containing OCR results, including 'ori_text' and 'ori_language'.
        config (dict): Configuration dictionary containing template paths and other settings.

    Returns:
        str: The determined document type.
    """

    # Extract the necessary information from OCR results
    text = ocr_result['ori_text'].lower()
    language = ocr_result['ori_language']
    invoice_txt_template = config.get('invoice_txt_template', {})

    # Check if the language is German ('de')
    if language == 'de':
        # Compare the OCR text with the templates using the provided function
        document_type = compare_with_templates(input_text=text, 
                                               invoice_txt_template=invoice_txt_template, 
                                               threshold=config['invoice_txt_template_thresh'])
        # If no similar template is found, default to "invoice 3"
        if not document_type:
            return "invoice 3"
        else:
            return document_type
    else:
        # If the language is not German, default to "invoice 3"
        return "invoice 3"


def get_document_template(document_type:str, config:dict):
    invoice_dict=config['invoice_dict']
    invoice_template = read_txt_file(invoice_dict[document_type])
    return invoice_template

async def extract_invoice_info(base64_img:str, ocr_reader:OcrReader, 
                         invoice_extractor:BaseExtractor, config:dict, logger = None) -> dict:
    result = {}
    pil_img = convert_base64_to_pil_image(base64_img)
    ocr_result = ocr_reader.get_text(pil_img)

    invoice_type=get_document_type(ocr_result, config = config)
    invoice_template = get_document_template(invoice_type, config=config)

    rotate_image = ocr_reader.get_rotated_image(pil_img)
    invoice_info = await invoice_extractor.extract_invoice(ocr_text=ocr_result['text'], image=rotate_image, 
                                                        invoice_template=invoice_template)
    print('\ninvoice_info-1', invoice_info)
    invoice_info = validate_invoice(invoice_info=invoice_info, 
                                    invoice_type=invoice_type, config=config)
    
    result['translator'] = ocr_reader['translator']
    result['ocr_detector'] = ocr_reader['ocr_detector']
    result['invoice_info'] = invoice_info["invoice_info"]
    result['invoice_type'] = invoice_type
    result['ocr_info'] = ocr_result
    result['llm_extractor'] = invoice_extractor['llm_extractor']
    result['post_processor'] = invoice_extractor['post_processor']

    result["last_modified_at"] = get_current_time(timezone=config['timezone'])
    result["status"] = "completed"

    print("\ninvoice_info", invoice_info)
    if logger:
        logger.debug(f"Final invoice info: {invoice_info}")

    return result

def validate_invoice(invoice_info: dict, invoice_type: str, config: dict) -> dict:
    # Create a deep copy of the invoice_info to avoid modifying the original
    invoice_info_copy = deepcopy(invoice_info)

    invoice_types = {
        "invoice 1": (validate_invoice_1, Invoice1),
        "invoice 2": (validate_invoice_2, Invoice2),
        "invoice 3": (validate_invoice_3, Invoice3)
    }

    if invoice_type not in invoice_types:
        raise ValueError(f"Invalid invoice type: {invoice_type}")

    validate_func, invoice_class = invoice_types[invoice_type]

    valid_invoice = validate_func(invoice_data=invoice_info_copy, config=config)
    full_invoice = invoice_class(invoice_info=valid_invoice['invoice_info'])
    
    return full_invoice.model_dump(exclude_unset=False)

async def main():
    config_path = "config/config.yaml"
    config = read_config(config_path)

    ocr_reader = OcrReader(config_path=config_path, translator=GoogleTranslator())
    invoice_extractor = OpenAIExtractor(config_path=config_path)
    
    # Image path setup
    img_path = "test/images/007_1.png"
    import os
    if not os.path.exists(img_path):
        print(f"Image path {img_path} not found! Using alternative path.")
        img_path = "fr_1.png"

    # Convert image path to base64 string
    base64_img = convert_img_path_to_base64(img_path)

    # Run the invoice extraction asynchronously
    result = await extract_invoice_info(base64_img=base64_img, 
                                        ocr_reader=ocr_reader,
                                        invoice_extractor=invoice_extractor, 
                                        config=config)

    print("\ninfo", result['invoice_info'])
    print("\nresult", result)


if __name__ == "__main__":
    asyncio.run(main())




