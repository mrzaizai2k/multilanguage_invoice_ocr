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

   https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/connection-targets/#replica-sets

   https://www.mongodb.com/resources/products/compatibilities/deploying-a-mongodb-cluster-with-docker#:~:text=Create%20a%20Docker%20network.%20Start%20three%20instances%20of,you%20will%20be%20able%20to%20experiment%20with%20it.?msockid=34c38bc4da6f68c918d898c8db6e69e0

   create network
   ```shell
      docker network create app-network
   ```

   run mongo
   ```shell
      mkdir -p data/test-change-streams

      docker run -d \
         --name mongodb \
         -v /data/test-change-streams:/data/db \
         -p 27017:27017 \
         --network app-network \
         mongo:latest \
         mongod --replSet test-change-streams --logpath /data/db/mongodb.log --dbpath /data/db --port 27017

      docker exec -it mongodb mongosh --eval "rs.initiate()"
      
      docker exec -it mongodb mongosh --eval "rs.reconfig({_id: 'test-change-streams', members: [{ _id : 0, host : 'mongodb:27017'}]}, {force: true})"

      docker exec -it mongodb mongosh --eval "rs.status()"

   ```

   run backend

   ```shell

   docker build -t multilanguage_invoice_ocr-fastapi .

   docker run --env-file .env \
    -v $(pwd)/config:/app/config \
    -v $(pwd)/src:/app/src \
    -p 8149:8149 \
    --network app-network \
    multilanguage_invoice_ocr-fastapi:latest
    ```
   run front end
   ```shell

   cd jwt-auth-frontend/

   docker build -t jwt-auth-frontend .
   
   docker run -d \
   --name jwt-frontend-container \
   --network app-network \
   -p 3000:3000 \
   -v $(pwd)/src:/app/src \
   jwt-auth-frontend

   ```
   set up NGINX
   
   https://dev.to/theinfosecguy/how-to-deploy-a-fastapi-application-using-docker-on-aws-4m61

   setup mongo for testing
   ```shell
   mkdir -p /data/test-streams
   
   docker run -d --rm -p 27018:27017 --name mongo1 -v /data/test-streams:/data/db --network app-network mongo:latest mongod --replSet test-streams --bind_ip localhost,mongo1

   docker exec -it mongo1 mongosh --eval "rs.initiate({
   _id: \"test-streams\",
   members: [
      {_id: 0, host: \"mongo1\"}
   ]
   })"

   docker exec -it mongo1 mongosh --eval "rs.status()"
   ```

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

