import os
from importData import update_excel
from importData import copy_excel_file, rename
from config import MAIN_SHEET, PROGRESS, PROGRESS_2
from copy_data import copy_data

JSON_1  = 1
JSON_2  = 2
EXCEL_1 = 1
EXCEL_2 = 2

# Call the function
copy_excel_file()

# Process data from data1.json
# Project 1
update_excel(JSON_1, EXCEL_1, MAIN_SHEET, 'B1', 'name')
update_excel(JSON_1, EXCEL_1, PROGRESS, 'B4', 'project_number')
update_excel(JSON_1, EXCEL_1, PROGRESS, 'B5', 'customer')
update_excel(JSON_1, EXCEL_1, PROGRESS, 'B6', 'city')
update_excel(JSON_1, EXCEL_1, PROGRESS, 'B7', 'kw')
update_excel(JSON_1, EXCEL_1, PROGRESS, 'B8', 'land')
update_excel(JSON_1, EXCEL_1, PROGRESS, 'E2', 'cost_hour') # Add cost by hour

update_excel(JSON_1, EXCEL_1, PROGRESS, 'A11', 'lines')
update_excel(JSON_2, EXCEL_1, PROGRESS, '', 'service')

# Project 2
update_excel(JSON_1, EXCEL_1, MAIN_SHEET, 'B1', 'name')
update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B4', 'project_number')
update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B5', 'customer')
update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B6', 'city')
update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B7', 'kw')
update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'B8', 'land')
update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'E2', 'cost_hour') # Add cost by hour

update_excel(JSON_1, EXCEL_1, PROGRESS_2, 'A11', 'lines')
update_excel(JSON_2, EXCEL_1, PROGRESS_2, '', 'service')

# Copy data to output2
copy_data(EXCEL_1, MAIN_SHEET, EXCEL_2, 'April 24_0')

# Rename
rename()
