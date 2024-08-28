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


if __name__ == "__main__":
    print("Has GPU?")