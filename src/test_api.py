import sys
sys.path.append("") 

import requests
from typing import Literal, Optional
from src.Utils.utils import *
from dotenv import load_dotenv
load_dotenv()


def test_excel():
    url = f"{root_url}/api/v1/excel"
    response = requests.get(url, params={})
    
    # Print the response for debugging (optional)
    print(f"Status code: {response.status_code}")
  


def test_upload_invoice(img_path, user_uuid, file_name:str=None):
    # Define the payload
    url = f"{root_url}/api/v1/invoices/upload"

    base64_img = convert_img_path_to_base64(img_path)

    payload = {
        "img": base64_img,
        "user_uuid": user_uuid,
        "file_name": file_name
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

@timeit
def test_get_invoices(user_uuid: Optional[str] = None, 
                      invoice_type: Optional[str] = None,
                      invoice_uuid: Optional[str] = None,
                      invoice_status: Optional[Literal['not extracted', 'completed']] = None,
                      created_at: Literal["asc", "desc"] = "asc",
                      page: int = 1, limit: int = 10):

    # Define the endpoint URL
    url = f"{root_url}/api/v1/invoices"
    
    # Define the query parameters with corrected names
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
    if invoice_status:
        params["invoice_status"] = invoice_status  # Corrected key here

    print("params", params)
    # Send the GET request with query parameters
    response = requests.get(url, params=params)
    
    # Print the response for debugging (optional)
    print(f"Status code: {response.status_code}")
    invoices = response.json()["invoices"]
    print('len(invoices)', len(invoices))
    print("\nkey",response.json()["invoices"][0].keys())

    invoice = response.json()["invoices"][0]
    print('file_name', invoice['file_name'])

    # Print all data excluding 'invoice_image_base64'
    for key, value in invoice.items():
        if key in ['last_modified_by', 'last_modified_at']:
            print(f"{key}: {value}")


    invoice_ids = [invoice['_id'] for invoice in invoices]
    print(f"Number of invoices: {len(invoices)}")
    print(f"Number of matching docs: {response.json()['total']}")

    
    if invoices:
        for invoice in invoices:
            print(f"Invoice status: {invoice.get('status', 'N/A')}")

    # Check the status code and print appropriate messages
    if response.status_code == 200:
        print("Invoices fetched successfully.")
    else:
        print(f"Failed to fetch invoices. Status code: {response.status_code}")

    return response, invoice_ids


def test_get_frontend_defines(root_url):
    # Define the base URL of the API
    url = f"{root_url}/api/v1/frontend_defines"

    # Send the GET request
    response = requests.get(url)

    # Print the response for debugging (optional)
    print(response.json())

    # Check if the request was successful
    if response.status_code == 200:
        print("Successfully retrieved frontend defines.")
        frontend_defines = response.json().get("frontend_defines", [])
        
        # Additional checks (optional)
        assert isinstance(frontend_defines, list), "Frontend defines should be a list"
        assert len(frontend_defines) > 0, "Frontend defines should not be empty"
        # Add more assertions based on your expected data structure
    else:
        print(f"Failed to retrieve frontend defines: {response.status_code} - {response.text}")


if __name__ == "__main__":
    config_path='config/config.yaml'
    config = read_config(path=config_path)

    SERVER_IP = "52.76.178.14"

    root_url = f"https://mrzaizai2k.xyz/api" # aws
    # root_url = f"http://{SERVER_IP}/api" # aws

    # root_url = f"http://{config['IES_host']}:{config['IES_port']}" #localhost


    img_path = "test/images/007_2.png"
    user_uuid = "gauss"
    # user_uuid = "2111_1111_1111_1111"
    invoice_uuid = "67283754c979f87afe6711f9"
    invoice_info = {"land": "Laos",} 

    # test_excel()
    file_name = os.path.basename(img_path)

    # for i in range(5):
    #     test_upload_invoice(img_path=img_path, user_uuid=user_uuid, file_name=file_name)

    # test_get_invoices(user_uuid=user_uuid, invoice_type=None, created_at='desc', invoice_uuid=invoice_uuid)
    _, invoice_ids = test_get_invoices(user_uuid=None, invoice_type=None, created_at='desc', invoice_status='not extracted',)
    # test_modify_invoice(invoice_uuid=invoice_uuid, user_uuid=user_uuid, new_invoice_info=invoice_info)
    # test_delete_invoice(invoice_uuid=invoice_uuid, user_uuid=user_uuid)
    # test_get_frontend_defines(root_url=root_url)

    # print(invoice_ids)
    # for invoice in invoice_ids:
    #     test_delete_invoice(invoice_uuid=invoice, user_uuid=user_uuid)









