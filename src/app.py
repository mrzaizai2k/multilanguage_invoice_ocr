import sys
import json
sys.path.append("")

import streamlit as st
from PIL import Image
import numpy as np
from ocr_reader import OcrReader
from invoice_extraction import InvoiceExtractor
from src.Utils.utils import pdf_to_images

def clean_dict(d):
    if isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items() if v not in [None, "", "None", "NULL"] and (not isinstance(v, (dict, list)) or clean_dict(v))}
    elif isinstance(d, list):
        return [clean_dict(i) for i in d if i not in [None, "", "None", "NULL"]]
    else:
        return d
    
def rotate_image(image, angle):
    return image.rotate(angle, expand=True)

def create_thumbnail(image, size=(500, 500)):
    thumbnail = image.copy()
    thumbnail.thumbnail(size)
    return thumbnail

# Load key name dictionary
with open("config/key_name_dict.json", "r") as f:
    key_name_dict = json.load(f)

config_path = "config/config.yaml"
ocr_reader = OcrReader(config_path=config_path)
invoice_extractor = InvoiceExtractor(config_path=config_path)

st.title("Invoice Information Extractor")

uploaded_file = st.file_uploader("Choose an image or PDF file", type=["jpg", "jpeg", "png", 'pdf'])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "pdf":
        images = pdf_to_images(uploaded_file)
    else:
        images = [Image.open(uploaded_file)]

    # Sidebar with thumbnails
    st.sidebar.title("Image Selection")
    selected_index = st.sidebar.selectbox("Select an image:", range(len(images)))

    # Display thumbnails in the sidebar
    for i, img in enumerate(images):
        thumbnail = create_thumbnail(img)
        st.sidebar.image(thumbnail, caption=f"Image {i + 1}", use_column_width=True)

    # Main content
    col1, col2 = st.columns([2, 3])

    with col1:
        # Image display and manipulation
        original_image = images[selected_index]
        
        # Rotation state
        rotation = 0

        # Rotation buttons
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            if st.button("Rotate -"):
                rotation += 90
        with col1b:
            if st.button("Reset"):
                rotation = 0
        with col1c:
            if st.button("Rotate +"):
                rotation -= 90

        # Apply rotation for display only
        displayed_image = rotate_image(original_image, rotation)

        st.image(displayed_image, caption="Selected Image", use_column_width=True)

    with col2:
        # Perform OCR and invoice extraction
        st.write("Extracting text and invoice information...")
        ocr_result = ocr_reader.get_text(rotate_image(original_image, rotation))
        extracted_text = ocr_result['text']
        invoice_info = invoice_extractor.extract_invoice(extracted_text, np.array(rotate_image(original_image, rotation)))

        # Create tabs for JSON and Table views
        json_tab, table_tab = st.tabs(["JSON", "Table"])

        # Clean the dictionary
        filtered_info = clean_dict(invoice_info)

        print("filtered_info:", filtered_info)
        print("invoice_info:", invoice_info)

        # Display the cleaned information using Streamlit
        with json_tab:
            st.json(filtered_info)

        with table_tab:
            if filtered_info:
                data = []
                for key, value in filtered_info['data'].items():
                    display_name = key_name_dict.get(key, key.replace('_', ' ').title())
                    data.append({"Field": display_name, "Value": value})
                st.table(data)
            else:
                st.write("No valid data to display.")