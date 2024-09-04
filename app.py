import sys
sys.path.append("")

import json
import streamlit as st
from PIL import Image
import numpy as np
from src.ocr_reader import OcrReader
from src.invoice_extraction import OpenAIExtractor
from src.Utils.utils import *

def main():
    config_path = "config/config.yaml"
    ocr_reader = OcrReader(config_path=config_path)
    invoice_extractor = OpenAIExtractor(config_path=config_path)

    config = read_config(config_path)
    with open(config['key_name_dict_path'], "r") as f:
        key_name_dict = json.load(f)

    st.set_page_config(page_title="Invoice Information Extractor", layout="wide", initial_sidebar_state="expanded")

    st.title("Invoice Information Extractor")

    # Add custom CSS for fonts and clickable images
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP&family=Noto+Sans+KR&family=Noto+Sans&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans', 'Noto Sans JP', 'Noto Sans KR', 'Meiryo', 'Hiragino Kaku Gothic Pro', 'Hiragino Sans', 'Yu Gothic', 'YuGothic', sans-serif;
        }
        .clickable-image {
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        .clickable-image:hover {
            transform: scale(1.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Allow uploading multiple files
    uploaded_files = st.file_uploader("Choose images or PDF files", type=["jpg", "jpeg", "png", 'pdf'], accept_multiple_files=True)

    if uploaded_files:
        images = []
        for uploaded_file in uploaded_files:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "pdf":
                images.extend(pdf_to_images(uploaded_file))  # Extend the list for multiple pages
            else:
                images.append(Image.open(uploaded_file))

        # Use session state to store the selected image index
        if 'selected_index' not in st.session_state:
            st.session_state.selected_index = 0

        # Sidebar with clickable thumbnails
        st.sidebar.title("Image Selection")
        
        # Display thumbnails in the sidebar
        for i, img in enumerate(images):
            thumbnail = create_thumbnail(img)
            col1, col2 = st.sidebar.columns([1, 4])
            with col1:
                if st.button(f"📄", key=f"btn_{i}", help=f"Select Image {i + 1}"):
                    st.session_state.selected_index = i
            with col2:
                st.image(thumbnail, caption=f"Image {i + 1}", use_column_width=True)

        # Main content
        col1, col2 = st.columns([2, 3])

        with col1:
            # Image display and manipulation
            original_image = images[st.session_state.selected_index]

            # Rotation state
            if 'rotation' not in st.session_state:
                st.session_state.rotation = 0

            # Rotation buttons
            col1a, col1b, col1c = st.columns(3)
            with col1a:
                if st.button("Rotate -"):
                    st.session_state.rotation += 90
            with col1b:
                if st.button("Reset"):
                    st.session_state.rotation = 0
            with col1c:
                if st.button("Rotate +"):
                    st.session_state.rotation -= 90

            # Apply rotation for display only
            displayed_image = rotate_image(original_image, st.session_state.rotation)

            st.image(displayed_image, caption="Selected Image", use_column_width=True)

        with col2:
            # Perform OCR and invoice extraction
            st.write("Extracting text and invoice information...")
            ocr_result = ocr_reader.get_text(rotate_image(original_image, st.session_state.rotation))
            extracted_text = ocr_result['text']
            invoice_info = invoice_extractor.extract_invoice(extracted_text, np.array(rotate_image(original_image, st.session_state.rotation)))

            # Create tabs for JSON and Table views
            json_tab, table_tab = st.tabs(["JSON", "Table"])

            # Clean the dictionary
            filtered_info = clean_dict(invoice_info)

            # Display the cleaned information using Streamlit
            with json_tab:
                # When writing to JSON
                json_str = json.dumps(filtered_info, ensure_ascii=False)

                # When displaying JSON
                st.json(json_str)

            with table_tab:
                if filtered_info:
                    filtered_info = flatten_dict(filtered_info)
                    data = []
                    for key, value in filtered_info.items():
                        display_name = key_name_dict.get(key, key.replace('_', ' ').title())
                        data.append({"Field": display_name, "Value": value})
                    html_table = create_html_table([[row['Field'], row['Value']] for row in data])
                    st.markdown(html_table, unsafe_allow_html=True)
                else:
                    st.write("No valid data to display.")

if __name__ == "__main__":
    main()