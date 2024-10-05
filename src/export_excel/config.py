import sys
sys.path.append("")

import os
from src.Utils.utils import read_config

config_path = "config/config.yaml"
config = read_config(path = config_path)

# Define the paths
config = config['excel']['export']
input_path = config['input_path']
output_path = config['output_path']
example_path = config['input_path']

# Define the name file
excel_1_file = config['excel_1_file']
excel_2_file = config['excel_2_file']
excel_3_file = config['excel_3_file']
json_1_file = config['json_1_file']
json_2_file = config['json_2_file']

# Create file paths
input_1_excel = os.path.join(example_path, excel_1_file)
output_1_excel = os.path.join(output_path, excel_1_file)
input_1_json = os.path.join(input_path, json_1_file)

input_2_excel = os.path.join(example_path, excel_2_file)
output_2_excel = os.path.join(output_path, excel_2_file)
input_2_json = os.path.join(input_path, json_2_file)

input_3_exel = os.path.join(input_path, excel_3_file)

# name sheets
MAIN_SHEET = config['MAIN_SHEET']
PROGRESS = config['PROGRESS']
PROGRESS_2 = config['PROGRESS_2']
FORMAT_NUMBER = config['FORMAT_NUMBER']

__all__ = [
    'input_1_excel', 'output_1_excel', 'input_1_json',
    'input_2_excel', 'output_2_excel', 'input_2_json',
    'input_3_excel', 'output_path', 
    'MAIN_SHEET', 'PROGRESS', 'PROGRESS_2', 'FORMAT_NUMBER'
]