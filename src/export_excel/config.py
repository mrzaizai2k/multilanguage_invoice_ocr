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

# Create file paths
input_1_excel = os.path.join(example_path, excel_1_file)
output_1_excel = os.path.join(output_path, excel_1_file)

input_2_excel = os.path.join(example_path, excel_2_file)
output_2_excel = os.path.join(output_path, excel_2_file)

input_3_exel = os.path.join(input_path, excel_3_file)
 
# name sheets
MAIN_SHEET = config['MAIN_SHEET']
FORMAT_NUMBER = config['FORMAT_NUMBER']

__all__ = [
    'input_1_excel', 'output_1_excel', 
    'input_2_excel', 'output_2_excel',
    'input_3_excel', 'output_path', 
    'MAIN_SHEET','FORMAT_NUMBER'
]