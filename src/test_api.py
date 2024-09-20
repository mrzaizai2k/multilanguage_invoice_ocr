import sys
sys.path.append("") 

import requests
from typing import Literal, Optional
from src.Utils.utils import *


def test_upload_invoice(img_path, user_uuid):
    # Define the payload
    url = f"{root_url}/api/v1/invoices/upload"

    base64_img = convert_img_path_to_base64(img_path)

    payload = {
        "img": base64_img,
        "user_uuid": user_uuid
    }
    
    # Send the POST request
    response = requests.post(url, json=payload)

    # Print the response for debugging (optional)
    print(response.json())

def test_modify_invoice(invoice_uuid, user_uuid, new_invoice_info):
    # Define the payload and URL
    url = f"{root_url}/api/v1/invoices/{invoice_uuid}"

    payload = {
        "user_uuid": user_uuid,
        "invoice_info": new_invoice_info
    }
    
    # Send the PUT request
    response = requests.put(url, json=payload)

    # Print the response for debugging (optional)
    print(response.json())

    # Check if the request was successful
    if response.status_code == 200:
        print("Invoice modified successfully.")
    else:
        print("Failed to modify invoice.")

def test_delete_invoice(invoice_uuid, user_uuid):
    # Define the URL with query parameters
    url = f"{root_url}/api/v1/invoices/{invoice_uuid}?user_uuid={user_uuid}"

    # Send the DELETE request
    response = requests.delete(url)

    # Print the response for debugging (optional)
    print(response.json())

    # Check if the request was successful
    if response.status_code == 200:
        print("Invoice deleted successfully.")
    else:
        print("Failed to delete invoice.")


def test_get_invoices(user_uuid: Optional[str] = None, 
                      invoice_type: Optional[str] = None,
                      invoice_uuid: Optional[str] = None,
                      created_at: Literal["asc", "desc"] = "asc",
                      page: int = 1, limit: int = 10):

    # Define the endpoint URL
    url = f"{root_url}/api/v1/invoices"
    
    # Define the query parameters
    params = {
        "page": page,
        "limit": limit,
        "created_at": created_at,
    }

    if user_uuid:
        params["created_by"] = user_uuid
    if invoice_type:
        params["invoice_type"] = invoice_type
    if invoice_uuid:
        params["invoice_uuid"] = invoice_uuid

    # Send the GET request with query parameters
    response = requests.get(url, params=params)
    
    # Print the response for debugging (optional)
    print(response.status_code)
    print("len",len(response.json()))

    # Check the status code and print appropriate messages
    if response.status_code == 200:
        print("Invoices fetched successfully.")
    else:
        print(f"Failed to fetch invoices. Status code: {response.status_code}")


if __name__ == "__main__":
    config_path='config/config.yaml'
    config = read_config(path=config_path)

    # root_url = f"http://{config['IES_host']}:{config['IES_port']}"
    root_url = f"http://46.137.228.37" # aws

    img_path = "test/images/page_3.png"
    user_uuid = "2111_1111_1111_1111"
    invoice_uuid = "66ed92711cb41ac8180283e0"
    invoice_info = {"amount": "1111",} 

    test_upload_invoice(img_path=img_path, user_uuid=user_uuid)
    # test_get_invoices(user_uuid=user_uuid, invoice_type=None, created_at='desc', invoice_uuid=invoice_uuid)
    # test_get_invoices(user_uuid=user_uuid, invoice_type=None, created_at='desc')
    # test_modify_invoice(invoice_uuid=invoice_uuid, user_uuid=user_uuid, new_invoice_info=invoice_info)
    # test_delete_invoice(invoice_uuid=invoice_uuid, user_uuid=user_uuid)








