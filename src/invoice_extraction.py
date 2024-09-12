import sys
sys.path.append("") 

from src.ocr_reader import OcrReader, GoogleTranslator
from base_extractors import OpenAIExtractor, BaseExtractor
from src.qwen2_extract import Qwen2Extractor
from typing import Literal
from src.Utils.utils import timeit, read_config, convert_img_path_to_base64, get_current_time

import base64
from io import BytesIO
from PIL import Image

def base64_to_pil_image(base64_img: str) -> Image.Image:
    """
    Convert a Base64-encoded image into a PIL Image object.

    :param base64_img: The Base64-encoded image string.
    :return: A PIL Image object.
    """
    # Decode the Base64 string into bytes
    image_data = base64.b64decode(base64_img)

    # Convert the bytes data into a BytesIO object
    image_bytes = BytesIO(image_data)

    # Open the image using PIL and return the Image object
    return Image.open(image_bytes)

def get_document_type(ocr_result:dict) -> str:
    text = ocr_result['text'].lower()

    if (ocr_result['ori_language'] == 'de' and "recording of external assignments" in text) or ("erfassung externer einsatze"  in text):
        if "page 1 of 2" in text or ("seite 1 von 2" in text):
            document_type = "invoice 1"
        elif "page 2 of 2" in text or ("seite 2 von 2" in text):
            document_type = "invoice 2"
    else:
        document_type = "invoice 3"

    return document_type

def get_document_template(document_type:str, config:dict):
    invoice_dict=config['invoice_dict']
    return invoice_dict[document_type]

def extract_invoice_info(base64_img:str, ocr_reader:OcrReader, invoice_extractor:BaseExtractor, config:dict) -> dict:
    result = {}
    pil_img = base64_to_pil_image(base64_img)
    ocr_result = ocr_reader.get_text(pil_img)

    invoice_type=get_document_type(ocr_result)
    invoice_template = get_document_template(invoice_type, config=config)

    invoice_info = invoice_extractor.extract_invoice(ocr_text=ocr_result['text'],image=base64_img, 
                                                        invoice_template=invoice_template)
    result['translator'] = ocr_reader['translator']
    result['ocr_detector'] = ocr_reader['ocr_detector']
    result['invoice_info'] = invoice_info
    result['invoice_type'] = invoice_type
    result['ocr_info'] = ocr_result
    result['llm_extractor'] = invoice_extractor['llm_extractor']
    result['post_processor'] = invoice_extractor['post_processor']

    return result


if __name__ == "__main__":
    config_path = "config/config.yaml"
    config = read_config(config_path)

    ocr_reader = OcrReader(config_path=config_path, translator=GoogleTranslator())
    invoice_extractor = OpenAIExtractor(config_path=config_path)
    img_path = "test/images/fr_1.png"
    base64_img = convert_img_path_to_base64(img_path)
    print(get_document_template('invoice 1', config))
    result = extract_invoice_info(base64_img=base64_img, ocr_reader=ocr_reader,
                                        invoice_extractor=invoice_extractor, config=config)
    print("info", result)