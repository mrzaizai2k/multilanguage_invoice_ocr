import sys
sys.path.append("")

from functools import wraps
import time
from datetime import datetime
import os
import psutil
import yaml
import pymupdf
from PIL import Image
import cv2
import re
import base64
import numpy as np
import binascii
import pytz
from pytesseract import Output
import pytesseract
from collections import Counter
from io import BytesIO
import openpyxl
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
load_dotenv()


def convert_ms_to_hms(ms):
    seconds = ms / 1000
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    seconds = round(seconds, 2)
    
    return f"{int(hours)}:{int(minutes):02d}:{seconds:05.2f}"

def measure_memory_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info()[0]
        rt = func(*args, **kwargs)
        mem_end = process.memory_info()[0]
        diff_MB = (mem_end - mem_start) / (1024 * 1024)  # Convert bytes to megabytes
        print('Memory usage of %s: %.2f MB' % (func.__name__, diff_MB))
        return rt
    return wrapper


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        time_delta = convert_ms_to_hms(total_time*1000)

        print(f'{func.__name__.title()} Took {time_delta}')
        return result
    return timeit_wrapper

def is_file(path:str):
    return '.' in path

def check_path(path):
    # Extract the last element from the path
    last_element = os.path.basename(path)
    if is_file(last_element):
        # If it's a file, get the directory part of the path
        folder_path = os.path.dirname(path)

        # Check if the directory exists, create it if not
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Create new folder path: {folder_path}")
        return path
    else:
        # If it's not a file, it's a directory path
        # Check if the directory exists, create it if not
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Create new path: {path}")
        return path

def read_config(path = 'config/config.yaml'):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def pdf_to_images(pdf_file):
    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images


def resize_same_ratio(img: Image.Image, target_size: int = 640) -> Image.Image:
    """
    Resizes an image to maintain aspect ratio either by height or width.
    
    If the image is vertical (height > width), it resizes the image to make its height 640 pixels,
    maintaining the aspect ratio. If the image is horizontal (width > height), it resizes the image 
    to make its width 640 pixels, maintaining the aspect ratio.
    
    Args:
        img (PIL.Image.Image): The image to be resized.
        target_size (int, optional): The target size for the longest dimension of the image. 
                                     Defaults to 640.

    Returns:
        PIL.Image.Image: The resized image.
    """
    
    # Get the current dimensions of the image
    width, height = img.size
    
    # Determine whether the image is vertical or horizontal
    if height > width:
        # Calculate the new width to maintain aspect ratio
        new_width = int((width / height) * target_size)
        new_height = target_size
    else:
        # Calculate the new height to maintain aspect ratio
        new_height = int((height / width) * target_size)
        new_width = target_size

    # Resize the image
    resized_img = img.resize((new_width, new_height))
    
    return resized_img

def clean_dict(d):
    if isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items() if v not in [None, "", "None", "NULL"] and (not isinstance(v, (dict, list)) or clean_dict(v))}
    elif isinstance(d, list):
        return [clean_dict(i) for i in d if i not in [None, "", "None", "NULL"]]
    else:
        return d

def create_html_table(data):
    html = "<table>"
    for row in data:
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

def rotate_image(image, angle):
    return image.rotate(angle, expand=True)

def create_thumbnail(image, size=(500, 500)):
    thumbnail = image.copy()
    thumbnail.thumbnail(size)
    return thumbnail

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < max_retries:
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator


def is_base64(s):
    try:
        # Ensure the string length is a multiple of 4
        if len(s) % 4 != 0:
            return False

        # Attempt to decode the string
        base64.b64decode(s, validate=True)
        return True
    except (binascii.Error, ValueError):
        return False


def valid_base64_image(data_url: str) -> str:
    """
    Extracts the base64 part of a data URL string that begins with 'data:image'.
    
    :param data_url: The data URL string containing the image data.
    :return: The base64 encoded image string.
    """
    if data_url.startswith("data:image"):
        # Find the comma and return the substring after it
        return data_url.split(",")[1]
    else:
        return data_url



def convert_img_to_base64(img):
    # Encode image to base64 string
    retval, buffer = cv2.imencode('.jpg', img)  # Adjust format as needed (e.g., '.png')
    base64_img = base64.b64encode(buffer).decode('utf-8')
    return base64_img


def convert_img_path_to_base64(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"Failed to read image from {image_path}")
        base64_image = convert_img_to_base64(img)
        return base64_image

    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def bytes_to_image(image_bytes):
    """
    Converts a bytes object containing image data to an OpenCV image.

    Args:
        image_bytes (bytes): The bytes object representing the image data.

    Returns:
        numpy.ndarray: The OpenCV image as a NumPy array.

    Raises:
        ValueError: If the image data is invalid.
    """
    # Convert the bytes object to a NumPy array
    nparr = np.frombuffer(image_bytes, np.uint8)

    # Decode the image using cv2.imdecode()
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Check for decoding errors
    if img is None:
        raise ValueError("Invalid image data")

    return img


def convert_base64_to_img(base64_image:str):
    img_data = re.sub('^data:image/.+;base64,', '', base64_image)
    image_bytes = base64.b64decode(img_data)
    img = bytes_to_image(image_bytes)
    return img

def get_current_time(timezone:str = 'Europe/Berlin'):
    berlin_tz = pytz.timezone(timezone)
    # Get the current time in Berlin
    current_time = datetime.now(berlin_tz)
    return current_time

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

def get_rotation_angle(img: Image.Image) -> int:
    try:
        """
        Gets the rotation angle of the image using Tesseract's OSD.

        Args:
            img (PIL.Image.Image): The image to analyze.

        Returns:
            int: The rotation angle.
        """
        # Convert PIL image to OpenCV format
        image_cv = np.array(img)
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
        
        # Use pytesseract to get orientation information
        rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_osd(rgb, output_type=Output.DICT, config='--psm 0 -c min_characters_to_try=5')
        
        return results["rotate"]
    except Exception as e:
        return 0

def rotate_image(img: Image.Image) -> Image.Image:
    """
    Rotates an image to correct its orientation based on the detected rotation angle
    by analyzing the image at different sizes and choosing the most frequent angle.
    
    Args:
        img (PIL.Image.Image): The image to be rotated.

    Returns:
        PIL.Image.Image: The rotated image.
    """
    
    # Resize the image to different target sizes
    target_sizes = [640, 1080, 2000]
    rotation_angles = []

    for size in target_sizes:
        resized_img = resize_same_ratio(img, target_size=size)
        rotation_angle = get_rotation_angle(resized_img)
        rotation_angles.append(rotation_angle)

    # Find the most common rotation angle
    most_common_angle = Counter(rotation_angles).most_common(1)[0][0]

    if abs(most_common_angle) in [0, 180]:
        return img, 0

    # Rotate the original image using the most common angle
    image_cv = np.array(img)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
    rotated = rotate_bound(image_cv, angle=most_common_angle)
    
    # Convert the rotated image back to PIL format
    rotated_pil = Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))
    return rotated_pil, most_common_angle

def convert_base64_to_pil_image(base64_img: str) -> Image.Image:
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

def read_txt_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
def convert_datetime_to_iso(data):
    """
    Find the datetime value and convert to JSON format to send
    """
    if isinstance(data, dict):  # If the current level is a dictionary
        for key, value in data.items():
            if isinstance(value, datetime):  # Check if the value is a datetime
                data[key] = value.isoformat()  # Convert to ISO format
            elif isinstance(value, dict) or isinstance(value, list):  # If value is dict or list, recurse
                convert_datetime_to_iso(value)
    elif isinstance(data, list):  # If the current level is a list
        for item in data:
            convert_datetime_to_iso(item)

def convert_datetime_to_string(data, format: str = "%Y-%m-%d"):
    if isinstance(data, dict):
        return {key: convert_datetime_to_string(value, format) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_datetime_to_string(item, format) for item in data]
    elif isinstance(data, datetime):  # Accessing datetime correctly
        return data.strftime(format)
    else:
        return data
    
def convert_iso_to_string(data, format:str = '%d/%m/%Y'):
    """
    Convert ISO format datetime strings or datetime objects to 'dd/MM/YYYY' format
    """
    def convert_single_value(value):
        if isinstance(value, str):
            try:
                # Try to parse the string as an ISO format datetime
                dt = datetime.fromisoformat(value)
                return dt.strftime(format)
            except ValueError:
                # If it's not a valid ISO format, return the original string
                return value
        elif isinstance(value, datetime):
            # If it's already a datetime object, just format it
            return value.strftime(format)
        else:
            # For any other type, return as is
            return value

    if isinstance(data, dict):
        return {key: convert_iso_to_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_iso_to_string(item) for item in data]
    else:
        return convert_single_value(data)

def get_currencies_from_txt(file_path:str ="config/currencies.txt"):
    # Read the file and return a list of currency codes
    with open(file_path, 'r') as f:
        currencies = [line.strip() for line in f.readlines() if line.strip()]
    return list(set(currencies))

def get_land_and_city_list(file_path:str = "config/travel_expenses-2024.xlsx", 
                              sheet_name=None):
    # Load the Excel workbook
    workbook = openpyxl.load_workbook(file_path, keep_vba=True)
    
    # Get the sheet (use the first one if no sheet name is provided)
    if sheet_name is None:
        sheet = workbook.active
    else:
        sheet = workbook[sheet_name]

    cities = set()  # Use set to store unique cities
    lands = set()  # Use set to store unique countries

    # Iterate through rows and extract city/country names
    for row in sheet.iter_rows(min_row=4, min_col=1, max_col=1):
        cell_value = row[0].value
        if cell_value:
            cell_value = cell_value.strip()
            if cell_value.startswith('–'):  # Check for em dash (city)
                city = cell_value[1:].strip()  # Remove em dash and spaces
                if city == "im Übrigen":  # Replace city name if it's 'im Übrigen'
                    city = 'Other'
                cities.add(city)  # Add to set to ensure uniqueness
            else:
                lands.add(cell_value)  # Add to set to ensure uniqueness

    workbook.close()
    
    # Convert sets back to lists before returning
    return list(lands), list(cities) 

def find_best_match_fuzzy(string_list: list[str], text:str):
    """
    Find the closest match to text using fuzzy matching.
    :param text: string text (possibly incorrect)
    :param list: List of string to find
    :return: Position of best matching name in the original list, best matching name, and highest similarity score.
    """
    # Preprocess the OCR output
    text = text.lower()

    # Extract the closest match using fuzzy matching (search over both last-first and first-last formats)
    best_idx, best_score = None, 0

    for idx, item in enumerate(string_list):
        score = fuzz.ratio(text, item.lower())
        if score > best_score:
            best_score = score
            best_idx = idx

    # Return the index of the original name in the list, the best match, and the score
    original_name = string_list[best_idx]
    return best_idx, original_name, best_score

def is_partner_document(partner_doc, reference_doc):
    """Find the partner doc that has same sign_date but diffent invoice_type
    partner_doc: the doc to check if it's parter with the reference_doc or not
    """
    if partner_doc['invoice_info']['sign_date'] == reference_doc['invoice_info']['sign_date']:
        if reference_doc['invoice_type'] == 'invoice 1' and partner_doc['invoice_type'] == 'invoice 2':
            return True
        elif reference_doc['invoice_type'] == 'invoice 2' and partner_doc['invoice_type'] == 'invoice 1':
            return True
    return False

if __name__ == "__main__":
    config_path = "config/config.yaml"
    config = read_config(config_path)

    print(get_current_time(timezone=config['timezone']))
    # Define the Berlin time zone
    # Get the list of all currencies
    currencies = get_currencies_from_txt(file_path=config['currencies_path'])
    print(currencies)
    lands, cities = get_land_and_city_list(file_path=config['country_and_city']['file_path'],
                                                  sheet_name=config['country_and_city']['sheet_name'])
    # print("countries",lands)
    # print("cities",cities)

    print(find_best_match_fuzzy(string_list=cities, text = "Tokioo"))
        