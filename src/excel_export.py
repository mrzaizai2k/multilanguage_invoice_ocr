import sys
sys.path.append("")

import openpyxl
from src.Utils.utils import read_config

class ExcelProcessor:
    def __init__(self, config_path):
        # Load configuration from the YAML file
        self.config_path = config_path
        self.config = read_config(path=self.config_path)['excel']
        
        # Load the Excel file and sheet
        self.workbook = openpyxl.load_workbook(self.config['excel_file_path'], keep_vba=True)
        self.sheet = self.workbook[self.config['sheet_name']]
        self.nachname_position = None
        self.vorname_position = None

    def find_positions(self):
        """Find the row and column positions of 'nachname' and 'vorname'."""
        nachname_key = self.config['nachname_key'].lower()
        vorname_key = self.config['vorname_key'].lower()
        
        for row in self.sheet.iter_rows():
            for cell in row:
                if cell.value is not None:
                    if isinstance(cell.value, str):
                        if cell.value.lower() == nachname_key:
                            self.nachname_position = (cell.row, cell.column)
                        elif cell.value.lower() == vorname_key:
                            self.vorname_position = (cell.row, cell.column)
                    
                if self.nachname_position and self.vorname_position:
                    break
            if self.nachname_position and self.vorname_position:
                break

        # Check if the positions are valid
        if not (self.nachname_position and self.vorname_position):
            raise ValueError(f"Either '{nachname_key}' or '{vorname_key}' not found in the sheet.")
        if self.nachname_position[1] >= self.vorname_position[1]:
            raise ValueError(f"'{nachname_key}' must be in a column less than '{vorname_key}'.")

    def get_user_name(self):
        """Returns a list of tuples (nachname, vorname) starting from the row after the header."""
        self.find_positions()  # Ensure the positions are set
        
        row_num = self.nachname_position[0] + 1
        values_nachname_and_vorname = []

        while True:
            # Get values from the nachname and vorname columns
            nachname_value = self.sheet.cell(row=row_num, column=self.nachname_position[1]).value
            vorname_value = self.sheet.cell(row=row_num, column=self.vorname_position[1]).value
            
            # Break the loop if both are None (assumes end of data)
            if nachname_value is None and vorname_value is None:
                break

            # Append the values (even if one is None)
            values_nachname_and_vorname.append((nachname_value, vorname_value))
            
            # Move to the next row
            row_num += 1

        return values_nachname_and_vorname
    
    def get_sheet_names(self):
        return self.workbook.sheetnames

if __name__ == "__main__":
    # Example usage:
    processor = ExcelProcessor('config/config.yaml')
    names = processor.get_user_name()

    print(names)
    print(processor.get_sheet_names())
