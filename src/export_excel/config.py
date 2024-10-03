import os

# Define the paths
input_path = 'Input/'
output_path = 'Output/'
example_path = 'Example/'

# Define the name file
excel_1_file = 'VorlageSpesenabrechnung.xlsx'
excel_2_file = '1.4437_10578_A3DS GmbH_04_2024.xlsm'
excel_3_file = 'travel_expenses_2024.xlsx'
json_1_file = 'data1.json'
json_2_file = 'data2.json'

# Create file paths
input_1_excel = os.path.join(example_path, excel_1_file)
output_1_excel = os.path.join(output_path, excel_1_file)
input_1_json = os.path.join(input_path, json_1_file)

input_2_excel = os.path.join(example_path, excel_2_file)
output_2_excel = os.path.join(output_path, excel_2_file)
input_2_json = os.path.join(input_path, json_2_file)

input_3_exel = os.path.join(input_path, excel_3_file)

# name sheets
MAIN_SHEET = 'Auszahlung'
PROGRESS = 'Vorgang 1'
PROGRESS_2 = 'Vorgang 2'
FORMAT_NUMBER = '_-* #,##0.00\ "€"_-;\-* #,##0.00\ "€"_-;_-* "-"??\ "€"_-;_-@_-'

