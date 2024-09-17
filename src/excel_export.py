import sys
sys.path.append("")

import openpyxl
from fuzzywuzzy import fuzz, process

from src.Utils.utils import read_config

class ExcelProcessor:
    def __init__(self, config_path:str = None, config:dict = None):
        # Load configuration from the YAML file
        if (config_path is None and config is None) or (config_path and config):
            raise ValueError("Either 'config_path' or 'config' must be provided, but not both or neither.")

        if config_path:
            self.config_path = config_path
            self.config = read_config(path=self.config_path)['excel']
        elif config:
            self.config = config['excel']

        # Load the Excel file and sheet
        self.workbook = openpyxl.load_workbook(self.config['excel_file_path'], keep_vba=True)
        self.sheet = self.workbook[self.config['sheet_name']]
        self.nachname_position = None
        self.vorname_position = None

    def _find_nachname_vorname_positions(self):
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

    def get_user_names(self):
        """Returns a list of tuples (nachname, vorname) starting from the row after the header."""
        self._find_nachname_vorname_positions()  # Ensure the positions are set
        
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
    
    def get_user_email(self, nachname: str, vorname: str) -> str:
        """
        Generate the user email based on the first two characters of the last and first names.
        :param nachname: Last name of the user.
        :param vorname: First name of the user.
        :return: Email address as a string.
        """
        # Get the first two characters from each name, ensuring they are not None
        nachname_part = nachname[:2].lower() if nachname else ''
        vorname_part = vorname[:2].lower() if vorname else ''
        return f"{nachname_part}{vorname_part}@gmail.com"

    def get_user_info(self):
        """
        Returns a list of dictionaries, each containing user information:
        {'name': (nachname, vorname), 'email': email}
        """
        # Get the list of user names
        user_names = self.get_user_names()
        user_info_list = []

        # Generate user info with names and emails
        for nachname, vorname in user_names:
            email = self.get_user_email(nachname, vorname)
            user_info_list.append({
                'name': (nachname, vorname),
                'email': email
            })

        return user_info_list
    
    def get_sheet_names(self):
        return self.workbook.sheetnames



class FuzzyNameMatcher:
    def __init__(self, names):
        """
        Initialize the matcher with the list of names.
        :param names: List of tuples (nachname, vorname)
        """
        self.names = names
        # Preprocess names into canonical form and create a mapping for unique names
        self.canonical_names = self._preprocess_names()

    def _preprocess_names(self):
        """
        Preprocess the names by creating both first-last and last-first formats.
        :return: List of unique preprocessed names as strings.
        """
        corpus = []
        for idx, (last_name, first_name) in enumerate(self.names):
            last_first = f"{last_name.lower()} {first_name.lower()}"
            first_last = f"{first_name.lower()} {last_name.lower()}"
            # Store both last-first and first-last with the index of the name
            corpus.append((last_first, idx))
            corpus.append((first_last, idx))
        return corpus

    def find_best_match(self, ocr_output):
        """
        Find the closest match to the OCR output using fuzzy matching.
        :param ocr_output: OCR string (possibly incorrect)
        :return: Position of best matching name in the original list, best matching name, and highest similarity score.
        """
        # Preprocess the OCR output
        ocr_output = ocr_output.lower()

        # Extract the closest match using fuzzy matching (search over both last-first and first-last formats)
        best_match, best_score = None, 0
        best_idx = None

        for name, idx in self.canonical_names:
            score = fuzz.ratio(ocr_output, name)
            if score > best_score:
                best_match = name
                best_score = score
                best_idx = idx

        # Return the index of the original name in the list, the best match, and the score
        if best_match is not None:
            original_name = self.names[best_idx]
            return best_idx, original_name, best_score
        else:
            return None, None, 0

def get_full_name(name_tuple):
    """
    Convert a tuple into a full name string.
    :param name_tuple: Tuple containing parts of a name (e.g., last_name, first_name, etc.)
    :return: Full name as a single string with space-separated values.
    """
    return ' '.join(f"{part}" for part in name_tuple)




if __name__ == "__main__":
    # Example usage:
    config_path = 'config/config.yaml'
    config = read_config(config_path)
    processor = ExcelProcessor(config=config)
    names = processor.get_user_names()

    print(names)
    user_info = processor.get_user_info()
    for info in user_info:
        print(info)
        
    print(processor.get_sheet_names())

    # Example usage:

    matcher = FuzzyNameMatcher(names)

    # OCR output (potentially with errors and mixed order)
    ocr_output = ["Téuuley Divl", "Tuuulev Dirk", "Tümmeler Dirk", "Dirk Tuuulev", "Divl Téuuley"]

    for ocr_name in ocr_output:
        best_idx, best_match, best_score = matcher.find_best_match(ocr_name)
        print(f"OCR Output: {ocr_name}")
        if best_match:
            print(f"Best Match: {best_match} at index {best_idx} with score {best_score}")
            full_name = get_full_name(best_match)
            print(full_name)
        else:
            print("No match found")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        