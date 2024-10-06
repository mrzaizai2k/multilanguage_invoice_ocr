import sys
sys.path.append("") 

import os
import datetime
from src.export_excel.importData import update_excel
from src.export_excel.importData import copy_excel_file, rename_vorlagespesen_to_emp_name
from src.export_excel.copy_data import copy_data_individual_to_group
from src.export_excel.config import (MAIN_SHEET, PROGRESS, PROGRESS_2, 
                                    output_2_excel, output_1_excel)
from src.Utils.utils import convert_datetime_to_string


def get_start_date(data):
    """Get start_dat from invoice 1 lines"""
    if "invoice_info" in data and "lines" in data["invoice_info"]:
        lines = data["invoice_info"]["lines"]
        if lines:
            return lines[0]["date"]
    return None

def export_json_to_excel(invoice_1:dict, invoice_2:dict, logger = None):
    try:
        from src.export_excel.config import MAIN_SHEET, PROGRESS, PROGRESS_2
        # invoice_1  = 1
        # invoice_2  = 2
        # excel_des_path = 1
        invoice_1['invoice_info'] = convert_datetime_to_string(invoice_1['invoice_info'])
        print("invoice_1['invoice_info']",invoice_1['invoice_info'])
        invoice_2['invoice_info'] = convert_datetime_to_string(invoice_2['invoice_info'])

        excel_des_path = output_1_excel

        # Call the function
        copy_excel_file()
        if logger:
            logger.debug(msg = 'Done copy excel')

        # Process data from data1.json
        # Project 1
        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=MAIN_SHEET, cell='B1', value = 'name')
        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='B4', value = 'project_number')
        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='B5', value = 'customer')
        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='B6', value = 'city')
        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='B7', value = 'kw')
        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='B8', value = 'land')
        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='E2', value = 'cost_hour')  # Add cost by hour

        update_excel(json_data=invoice_1, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='A11', value = 'lines')

        invoice_2['invoice_info']['sign_date'] = get_start_date(data=invoice_1)
        update_excel(json_data=invoice_2, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='', value = 'service')

        if logger:
            logger.debug(msg = 'Done update json')

        # Project 2
        # update_excel(JSON_1, EXCEL_1, MAIN_SHEET, 'B1', 'name')
        # update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B4', 'project_number')
        # update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B5', 'customer')
        # update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B6', 'city')
        # update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B7', 'kw')
        # update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B8', 'land')
        # update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'E2', 'cost_hour') # Add cost by hour

        # update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'A11', 'lines')
        # update_excel(JSON_2, EXCEL_1, PROGRESS_2, '', 'service')

        # Rename the output_1_excel to new name path based on teh employee name
        rename_path = rename_vorlagespesen_to_emp_name(excel_path=output_1_excel)

        # Copy data to output2
        copy_data_individual_to_group(src_file_path=rename_path, src_sheet=MAIN_SHEET, 
                                    des_file_path=output_2_excel, des_sheet='April 24_0')

        if logger:
            logger.debug(msg = 'run Done')
    except Exception as e:
        print("error", e)
        if logger:
            logger.debug(msg = f'error:{e}')
    

if __name__ == "__main__":
    import json
    with open("config/data1.json", 'r') as file:
        invoice_1 = json.load(file)  

    with open("config/data2.json", 'r') as file:
        invoice_2 = json.load(file)  
    
    # from src.mongo_database import MongoDatabase
    # config_path='config/config.yaml'
    # mongo_db = MongoDatabase(config_path=config_path)
    # invoice_1 = mongo_db.get_document_by_id(document_id='6702803020af02d7f38e4238')
    # invoice_2 = mongo_db.get_document_by_id(document_id='67028a752d2ad07517a0c286')
    # print(invoice_1['invoice_type'])
    # print(invoice_2['invoice_type'])

    print(invoice_1['invoice_info'])
    print(invoice_2['invoice_info'])

    export_json_to_excel(invoice_1, invoice_2)