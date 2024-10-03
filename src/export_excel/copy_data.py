import openpyxl
from config import output_1_excel, output_2_excel
import xlwings as xw

def copy_data(src_file, src_sheet, des_file, des_sheet):
    if src_file == 1:
        source_file = output_1_excel
    if des_file == 2:
        target_file = output_2_excel

    # Load the source workbook and sheet
    source_workbook = openpyxl.load_workbook(source_file, data_only=True)
    source_sheet = source_workbook[src_sheet]
    
    # Load the target workbook and sheet
    target_workbook = openpyxl.load_workbook(target_file, keep_vba=True)
    target_sheet = target_workbook[des_sheet]

    # Get name from src file
    full_name   = source_sheet['B1'].value
    name_parts = full_name.split()
    nachname    = name_parts[0]
    vorname     = " ".join(name_parts[1:])

    # Iterate through the rows in the source file (e.g., name is in column A)
    for target_row in range(11, target_sheet.max_row + 1):
        target_nachname = target_sheet[f'E{target_row}'].value  # Name from source file (column A)
        target_vorname  = target_sheet[f'J{target_row}'].value  # Name from source file (column A)

        if target_nachname == nachname and target_vorname == vorname:
            target_sheet[f'T{target_row}'].value = get_formula_result(source_file, src_sheet, 'D5')
            target_sheet[f'V{target_row}'].value = get_formula_result(source_file, src_sheet, 'E5')
            target_sheet[f'U{target_row}'].value = get_formula_result(source_file, src_sheet, 'G5')
            print(f"Updated infomation of '{full_name}'")
            break 

    target_workbook.save(target_file)

def get_formula_result(file_path, sheet_name, cell_address):
    # Get value from func excel
    app = xw.App(visible=False)
    workbook = app.books.open(file_path)
    
    sheet = workbook.sheets[sheet_name]
    result = sheet.range(cell_address).value
    
    workbook.close()
    app.quit()
    
    return result