import sys
sys.path.append("")

import os
import pymupdf
import streamlit as st
from PIL import Image
import numpy as np
from ocr_reader import OcrReader
from invoice_extraction import InvoiceExtractor
import io

def preprocess_pdf(pdf_file):
    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

config_path = "config/config.yaml"
ocr_reader = OcrReader(config_path=config_path)
invoice_extractor = InvoiceExtractor(config_path=config_path)

st.title("Invoice Information Extractor")

uploaded_file = st.file_uploader("Choose an image or PDF file", type=["jpg", "jpeg", "png", 'pdf'])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "pdf":
        images = preprocess_pdf(uploaded_file)
        st.session_state.current_page = st.session_state.get('current_page', 0)
        
        if st.button("Next Page") and st.session_state.current_page < len(images) - 1:
            st.session_state.current_page += 1
        if st.button("Previous Page") and st.session_state.current_page > 0:
            st.session_state.current_page -= 1
        
        image = images[st.session_state.current_page]
    else:
        image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Image", use_column_width=True)

    with col2:
        st.write("Extracting text from image...")
        ocr_result = ocr_reader.get_text(image)
        extracted_text = ocr_result['text']

        st.write("Extracted Text:")
        st.write(extracted_text)

        st.write("Extracting invoice information...")
        invoice_info = invoice_extractor.extract_invoice(extracted_text, np.array(image))

        st.write("Extracted Invoice Information:")
        for key, value in invoice_info.items():
            st.write(f"{key}: {value}")