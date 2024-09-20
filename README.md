# Invoice Information Extractor

## Introduction

The **Invoice Information Extractor** is a web application built using Streamlit that allows users to upload images or PDF files containing invoices and extract relevant information from them using Optical Character Recognition (OCR) and natural language processing techniques. It provides an easy-to-use interface for visualizing extracted data in both JSON and table formats.

## Features

- Upload single or multiple images and PDF files.
- Rotate images for better OCR accuracy.
- Extract invoice data such as names, dates, amounts, etc.
- Display extracted information in structured formats (JSON or table).
- Dynamically create thumbnails for uploaded images.

## Requirements

To run this application, you need the following libraries:

- Python 3.x
- Streamlit
- Pillow
- NumPy
- Additional dependencies (OCR and invoice extraction libraries)


Make sure you have the following files in the `config` directory:

- `key_name_dict.json`: A JSON file that maps keys to human-readable field names.
- `config.yaml`: A YAML configuration file for the OCR and invoice extraction setup.

## Getting Started

Follow these steps to run the application:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/invoice-information-extractor.git
   cd invoice-information-extractor
   ```

2. **Install the required packages:**

   If you haven't already done so, set up a virtual environment and install the dependencies:

   ```bash
   # Create a virtual environment (optional)
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   
   # Install requirements
   pip install --no-cache-dir -r requirements.txt
   ```

3. **Run the app:**

   Start the Streamlit application:

   ```bash
   streamlit run app.py
   ```
   
   Replace `app.py` with the name of your main Python file if it's different.

4. **Access the application:**

   Open your browser and go to `http://localhost:8501` to interact with the Invoice Information Extractor.

5. **Set up Mongo Database**

   You can set up mongo database by docker as this [official link](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-community-with-docker/?msockid=12d1fdc9a4da62680b18e9ffa5036390)

   Donwload the [Mongo Compass](https://www.mongodb.com/try/download/compass) for GUI management

   https://www.mongodb.com/developer/languages/python/python-change-streams/#how-to-set-up-a-local-cluster

   run mongo
   ```shell
      docker run -d \
         --name mongodb \
         -v /data/test-change-streams:/data/db \
         -p 27017:27017 \
         --network app-network \
         mongo:latest \
         mongod --replSet test-change-streams --logpath /data/db/mongodb.log --dbpath /data/db --port 27017
      
      docker exec -it mongodb mongosh --eval "rs.reconfig({_id: 'test-change-streams', members: [{ _id : 0, host : 'mongodb:27017'}]}, {force: true})"

      docker exec -it mongodb mongosh --eval "rs.status()"

   ```

      docker run --env-file .env \
    -v $(pwd)/config:/app/config \
    -v $(pwd)/src:/app/src \
    -p 8149:8149 \
    --network app-network \
    multilanguage_invoice_ocr-fastapi:latest

5. **Sending Email**

   https://viblo.asia/p/gui-mail-voi-python-bWrZn7Mrlxw

   Set up an App Password in Gmail:

   - Go to your Google Account.
   - Select "Security" on the left-hand side.
   - If you use 2-Step Verification, under "Signing in to Google," select "App Passwords" and create one.
   - Use this App Password instead of your regular Gmail password in the script.

6. **LDAP authen**
   
   https://github.com/RetributionByRevenue/LDAP3-fastapi-auth-simple
   
   https://www.forumsys.com/2022/05/10/online-ldap-test-server/

- No space on aws
https://stackoverflow.com/questions/74515846/error-could-not-install-packages-due-to-an-oserror-errno-28-no-space-left-on
https://github.com/pypa/pip/issues/7745#issuecomment-587296318

## Usage

1. Upload one or more invoice images or PDF files using the file uploader interface.
2. Select an image from the uploaded files to view it in the main display area.
3. Use the rotation buttons to adjust the image for optimal OCR results.
4. Wait for the extraction process to complete, after which you can view the extracted information in JSON format or as a table.

- ollama: https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image

