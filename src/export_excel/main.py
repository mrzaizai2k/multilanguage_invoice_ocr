import sys
sys.path.append("") 

import os
import datetime
from src.export_excel.importData import update_excel
from src.export_excel.importData import prepare_excel_files, choose_sheet_to_write, clear_sheet
from src.export_excel.copy_data import copy_data_individual_to_group
from src.Utils.utils import convert_datetime_to_string

def get_start_date(data):
    """Get start_dat from invoice 1 lines"""
    lines = data["lines"]
    if lines:
        return lines[0]["date"]
    return None

def create_filename_from_dict(invoice_1: dict) -> str:
    """
    Create a file name based on the employee's name and sign date from a Python dictionary.
    
    The sign_date should be in the format 'YYYY-mm-dd', and the name should be the full name of the employee.
    The final filename will be in the format: "First2LettersOfFirstName+First2LettersOfLastName_mm_YY.xlsx"
    Example: if name is "Tummler Dirk" and sign_date is "2024-08-13", the result will be "TuDi_08_24.xlsx".
    
    If sign_date is not found, it will print an error message.
    """

    # Extract name and split into first name and last name
    if 'name' in invoice_1:
        full_name = invoice_1['name'].strip()
        name_parts = full_name.split()
        if len(name_parts) >= 2:
            initials = name_parts[0][:2] + name_parts[-1][:2]  # Take first 2 letters of first and last name
            initials = initials.capitalize()  # Capitalize the initials
        else:
            print(f"Error: Name '{full_name}' does not have enough parts.")
            return None
    else:
        print("Error: 'name' key not found in the dictionary.")
        return None

    # Extract the sign_date and format it as mm_YY
    if 'sign_date' in invoice_1:
        try:
            date_str = invoice_1['sign_date']
            sign_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            month_year = sign_date.strftime("%m_%y")  # Format as mm_YY
        except ValueError as e:
            print(f"Error: Invalid date format for sign_date '{date_str}': {e}")
            return None
    else:
        print("Error: 'sign_date' key not found in the dictionary.")
        return None

    # Combine initials and formatted date to create the final filename
    final_filename = f"{initials}_{month_year}.xlsx"
    
    return final_filename

def update_project(employee_expense_report_path:str, invoice_1:dict, invoice_2:dict, 
                   main_sheet_name:str, working_sheet_name:str):
    
    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                     sheet_name=main_sheet_name, cell='B1', value = 'name')
    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='B4', value = 'project_number')
    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='B5', value = 'customer')
    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='B6', value = 'city')
    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='B7', value = 'kw')
    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='B8', value = 'land')
    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='E2', value = 'cost_hour')  # Add cost by hour

    update_excel(json_data=invoice_1, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='A11', value = 'lines')

    invoice_2['sign_date'] = get_start_date(data=invoice_1)
    update_excel(json_data=invoice_2, excel_des_path=employee_expense_report_path, 
                    sheet_name=working_sheet_name, cell='', value = 'service')


def export_json_to_excel(invoice_pairs: list[tuple[dict, dict]], logger=None):
    """
    Process a list of invoice pairs and export them to Excel.
    
    :param invoice_pairs: List of tuples. Each tuple contains two dictionaries (invoice_1, invoice_2).
    :param logger: Logger for logging messages.
    """
    try:
        from src.export_excel.config import (MAIN_SHEET, output_path, 
                                             output_2_excel, input_1_excel)
        for idx, (invoice_1, invoice_2) in enumerate(invoice_pairs):
            
            invoice_1 = convert_datetime_to_string(invoice_1['invoice_info'])
            invoice_2 = convert_datetime_to_string(invoice_2['invoice_info'])

            if idx == 0:
                employee_expense_report_name = create_filename_from_dict(invoice_1=invoice_1)
                employee_expense_report_path = f"{output_path}/{employee_expense_report_name}"

                # Call the function
                prepare_excel_files(output_path=output_path, 
                                    employee_expense_report_path=employee_expense_report_path)  

                new_sheet_name, is_modified = choose_sheet_to_write(excel_path=employee_expense_report_path, 
                                                    invoice_1=invoice_1)
                

                if is_modified:
                
                    clear_sheet(src_file=input_1_excel, 
                                dest_file=employee_expense_report_path, 
                                sheet_name=new_sheet_name)

            update_project(employee_expense_report_path=employee_expense_report_path,
                        invoice_1=invoice_1, 
                        invoice_2=invoice_2,
                        main_sheet_name=MAIN_SHEET, 
                        working_sheet_name=new_sheet_name)
            if logger:
                logger.debug(msg = f'Done update invoice data to {employee_expense_report_path}')


            # Copy data to output2
            if idx == len(invoice_pairs) - 1: 
                copy_data_individual_to_group(src_file_path=employee_expense_report_path, src_sheet=MAIN_SHEET, 
                                            des_file_path=output_2_excel, des_sheet='April 24_0')

            if logger:
                logger.debug(msg = f'Done update invoice data from {employee_expense_report_path} to {output_2_excel}')
        
        return employee_expense_report_path, output_2_excel

    except Exception as e:
        msg = f"error: {e}"
        print(msg)
        if logger:
            logger.debug(msg =msg)
    
        return None, None

    

if __name__ == "__main__":
    import json
    with open("config/data1.json", 'r') as file:
        invoice_1 = json.load(file)  

    with open("config/data2.json", 'r') as file:
        invoice_2 = json.load(file)  

    with open("config/data3.json", 'r') as file:
        invoice_1_b = json.load(file)  

    with open("config/data4.json", 'r') as file:
        invoice_2_b = json.load(file)  

    
    # from src.mongo_database import MongoDatabase
    # config_path='config/config.yaml'
    # mongo_db = MongoDatabase(config_path=config_path)
    # invoice_1 = mongo_db.get_document_by_id(document_id='6702803020af02d7f38e4238')
    # invoice_2 = mongo_db.get_document_by_id(document_id='67028a752d2ad07517a0c286')
    # print(invoice_1['invoice_type'])
    # print(invoice_2['invoice_type'])

    # print(invoice_1['invoice_info'])
    # print(invoice_2['invoice_info'])
    for i in range(2):
        employee_expense_report_path, output_2_excel = export_json_to_excel(invoice_pairs =[(invoice_1, invoice_2), (invoice_1_b, invoice_2_b)],)
        print("employee_expense_report_path, output_2_excel", employee_expense_report_path, output_2_excel)

