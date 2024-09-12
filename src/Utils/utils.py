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


if __name__ == "__main__":
    print("Has GPU?")