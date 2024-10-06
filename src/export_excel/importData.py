# export.py
import sys
sys.path.append("") 

import json
import openpyxl
import os
import shutil
from datetime import datetime
import glob

from src.export_excel.config import input_1_excel, output_1_excel, input_1_json
from src.export_excel.config import input_2_excel, output_2_excel, input_2_json
from src.export_excel.config import input_3_exel, output_path, MAIN_SHEET, FORMAT_NUMBER

def copy_excel_file():
    '''
    Ensure output folder exists, remove all files in it, 
    and copy 2 template files from the Example folder.
    '''
    # Check if output_path exists; if not, create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created output directory: {output_path}")
    else:
        # Remove all files in the output folder
        files = glob.glob(os.path.join(output_path, '*'))
        for file in files:
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except Exception as e:
                print(f"Error when removing {file}: {e}")

    # Copy template files
    try:
        shutil.copy(input_1_excel, output_1_excel)
        print(f"Copied: {input_1_excel} to {output_1_excel}")

        shutil.copy(input_2_excel, output_2_excel)
        print(f"Copied: {input_2_excel} to {output_2_excel}")
    except Exception as e:
        print(f"Error when copying files: {e}")


def rename_vorlagespesen_to_emp_name(excel_path:str = "output/VorlageSpesenabrechnung.xlsx"):
    '''
    Rename output file excel VorlageSpesenabrechnung to the new file name based on the employee's name
    '''
    wb = openpyxl.load_workbook(excel_path)

    # Access the specified sheet
    if MAIN_SHEET in wb.sheetnames:
        ws = wb[MAIN_SHEET]
    else:
        print(f"Sheet '{MAIN_SHEET}' not found in the Excel file.")
        return
    
    full_name = ws['B1'].value
    name_parts = full_name.split()
    initials = ''.join([part[:2] for part in name_parts])

    date = ws['E3'].value
    month_year = date.strftime("%m_%y")

    new_filename = f"{initials}_{month_year}.xlsx" 
    new_path = os.path.join(output_path, new_filename)

    # Đổi tên tệp
    os.rename(output_1_excel, new_path)
    print(f"Rename {output_1_excel} to {new_path}")
    wb.close()
    return new_path

def update_excel(json_data:dict, excel_des_path:str="output/VorlageSpesenabrechnung.xlsx", 
                 sheet_name:str="", cell:str="", value:str=""):
    '''
    Input:
        json_index: index of json - define in config.py - to set path
        excel_index: index of excel - define in config.py - to set path
        sheet_name: sheet of excel file - write data to this sheet
        cell: cell want  to write data
        value: data need to be written to cell
    '''
        
    # Access the value from the JSON
    if value == 'lines':
        handle_lines_value(json_data, sheet_name, excel_des_path)
        return
    elif value == 'cost_hour':
        handle_number_hour_value(excel_des_path, sheet_name, cell)
        return
    elif value == 'service':
        handle_add_service(json_data, excel_des_path, sheet_name)
        return
    elif value in json_data['invoice_info']:
        value_to_write = json_data['invoice_info'][value]
        # Write the existing Excel workbook
        write_data(excel_des_path, sheet_name, cell, value_to_write)
    else:
        print(f"Key '{value}' not found in the JSON data.")
        return

def write_data(excel_des_path, sheet_name, cell, value_to_write, is_money = False):
    '''
    Input:
        excel_index: index of excel - define in config.py - to set path
        sheet_name: sheet of excel file - write data to this sheet
        cell: cell want  to write data
        value_to_write: data need to be written to cell
        is_money: to convert format money
    '''
    # Load the existing Excel workbook
    excel_des = excel_des_path
    
    wb = openpyxl.load_workbook(excel_des)

    # Access the specified sheet
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        print(f"Sheet '{sheet_name}' not found in the Excel file.")
        return
    
    # Write the value to the specified cell
    ws[cell].value = value_to_write
    if is_money == True:
        ws[cell].number_format = FORMAT_NUMBER

    # Save the updated Excel workbook
    wb.save(excel_des)
    wb.close()
    print(f"Added value '{value_to_write}' from JSON to cell {cell} in sheet '{sheet_name}'.")

def conver_number_hour(time):
    '''
    Hanlde time
    '''
    # Split the time into hours, minutes, and seconds
    hours, minutes, seconds = map(int, time.split(':'))

    # Convert the time into a float (hours + minutes/60)
    return float(hours + minutes / 60 + seconds / 3600)


def handle_lines_value(json_data, sheet_name, excel_des_path):
    '''
    json_data: file json 2
    sheet_name: sheet want to write data
    excel_index: index excel - config at config.py
    '''
    number = get_last_row(excel_des_path, sheet_name, 'A', 11)
    for line in json_data['invoice_info']['lines']:
        cell_des = f'A{number}'
        value_to_write = line['date']
        date_obj = datetime.strptime(value_to_write, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d.%m.%Y')
        write_data(excel_des_path, sheet_name, cell_des, formatted_date)

        cell_des = f'B{number}'
        value_to_write = line['start_time']
        write_data(excel_des_path, sheet_name, cell_des, conver_number_hour(value_to_write))

        cell_des = f'C{number}'
        value_to_write = line['end_time']
        write_data(excel_des_path, sheet_name, cell_des, conver_number_hour(value_to_write))

        number += 1

def handle_number_hour_value(excel_des_path, sheet_name, cell):
    '''
    sheet_name: sheet want to write data
    excel_index: index excel - config at config.py
    cell: cell to write data
    '''
    # Load the existing Excel workbook
    
    target_file = excel_des_path
    
    # Load the source workbook and sheet
    source_workbook = openpyxl.load_workbook(input_3_exel)
    source_sheet = source_workbook['Table 1']
    
    # Load the target workbook and sheet
    target_workbook = openpyxl.load_workbook(target_file)
    target_sheet = target_workbook[sheet_name]

    # Find value
    land = target_sheet['B8'].value
    city = target_sheet['B6'].value
    index = 0
    for row in range(4, source_sheet.max_row + 1):
        name = source_sheet[f'A{row}'].value
        if name != None and (land == name or city in name):
            index = row
    
    if index == 0:
        print(f"Not found land and city")
        return
    
    source_workbook.close()
    target_workbook.close()

    # Set value
    value_to_write = source_sheet[f'B{index}'].value
    write_data(excel_des_path, sheet_name, 'F2', value_to_write, True)

    value_to_write = source_sheet[f'C{index}'].value
    write_data(excel_des_path, sheet_name, 'G2', value_to_write, True)

    value_to_write = source_sheet[f'D{index}'].value
    write_data(excel_des_path, sheet_name, 'H2', value_to_write, True)


def handle_add_service(json_data, excel_des_path, sheet_name):
    date = json_data['invoice_info']['sign_date']
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date = date_obj.strftime('%d.%m.%Y')
    line = get_line_from_date(excel_des_path, sheet_name, date)

    # Handle with hotel
    for fixed_line in json_data['invoice_info']['fixed_lines']:
        if fixed_line['title'] == 'Hotel':
            if fixed_line['payment_method'] == 'self paid':
                value_to_write = fixed_line['amount']
                cell = f'E{line}'
                write_data(excel_des_path, sheet_name, cell, value_to_write, True)
            elif fixed_line['with_breakfast'] == True:
                value_to_write = get_breakfas_value(excel_des_path, sheet_name)
                cell = f'F{line}'
                write_data(excel_des_path, sheet_name, cell, value_to_write, True)
            
            fix_date_with_hotel(excel_des_path, sheet_name, line)
            break

    # Handle with lines
    value = 0
    title = ''
    last_line = get_last_row(excel_des_path, sheet_name, 'H', 11)

    for row in json_data['invoice_info']['lines']:
        value = row['amount']
        title = row['title'] 

        cell = f'H{last_line}'
        write_data(excel_des_path, sheet_name, cell, value, True)
        cell = f'I{last_line}'
        write_data(excel_des_path, sheet_name, cell, title)

        last_line = last_line + 1


def get_line_from_date(excel_des_path, sheet_name, date):
    # Load the existing Excel workbook
    excel_des = excel_des_path
    wb = openpyxl.load_workbook(excel_des)
    # Access the specified sheet
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        print(f"Sheet '{sheet_name}' not found in the Excel file.")
        return
        
    start_row = 11
    for row in range(start_row, ws.max_row + 1):
        cell = ws['A' + str(row)]
        if cell.value == date:
            return row
        
    return None

def get_breakfas_value(excel_des_path, sheet_name):
    excel_des = excel_des_path

    wb = openpyxl.load_workbook(excel_des, data_only=True)
    # Access the specified sheet
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        print(f"Sheet '{sheet_name}' not found in the Excel file.")
        return 0

    money = ws['G2'].value * 0.2
    wb.close()
    return money

def get_last_row(excel_des_path, sheet_name, column, start_row):
    '''
    sheet_name: sheet want to write data
    excel_des_path: index excel - config at config.py
    column: column to get last row
    start_row:  row start

    Output: las row without data
    '''
    # Load the existing Excel workbook
    excel_des = excel_des_path
    wb = openpyxl.load_workbook(excel_des)
        # Access the specified sheet
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        print(f"Sheet '{sheet_name}' not found in the Excel file.")
        return
    
    for row in range(start_row, ws.max_row + 1):
        cell = ws[column + str(row)]
        if cell.value == None:
            return row

def fix_date_with_hotel(excel_des_path, sheet_name, line):
    '''
    Fixed date if hotel enable
    '''
    last_line = get_last_row(excel_des_path, sheet_name, 'A', line)

    value_to_write = 24
    cell = f'C{line}'
    write_data(excel_des_path, sheet_name, cell, value_to_write)

    for row in range(line + 1, last_line - 1):
        value_to_write = 0
        cell = f'B{row}'
        write_data(excel_des_path, sheet_name, cell, value_to_write)

        value_to_write = 24
        cell = f'C{row}'
        write_data(excel_des_path, sheet_name, cell, value_to_write)

    value_to_write = 0
    cell = f'B{row + 1}'
    write_data(excel_des_path, sheet_name, cell, value_to_write)