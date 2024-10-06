import sys
sys.path.append("") 

import os
from src.export_excel.importData import update_excel
from src.export_excel.importData import copy_excel_file, rename_vorlagespesen_to_emp_name
from src.export_excel.copy_data import copy_data_individual_to_group
from src.export_excel.config import (MAIN_SHEET, PROGRESS, PROGRESS_2, 
                                    output_2_excel, output_1_excel)


def export_json_to_excel(invoice_1:dict, invoice_2:dict):
    from src.export_excel.config import MAIN_SHEET, PROGRESS, PROGRESS_2
    # invoice_1  = 1
    # invoice_2  = 2
    # excel_des_path = 1
    excel_des_path = output_1_excel

    # Call the function
    copy_excel_file()

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
    update_excel(json_data=invoice_2, excel_des_path=excel_des_path, sheet_name=PROGRESS, cell='', value = 'service')

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

    

if __name__ == "__main__":
    import json
    with open("config/data1.json", 'r') as file:
        invoice_1 = json.load(file)  

    with open("config/data2.json", 'r') as file:
        invoice_2 = json.load(file)  

    export_json_to_excel(invoice_1, invoice_2)