import sys
sys.path.append("") 

import pandas as pd
from datetime import datetime, timedelta

def create_egw_filename() -> str:
    """
    Create a filename like egw_export_timesheet-YYYY-mm-dd.csv based on the current date.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"egw_export_timesheet-{current_date}.csv"
    return filename

def handle_project_and_title(invoice_info: dict) -> str:
    """
    Create the 'Projekt' and 'Titel' content as '<project_number>: <customer>'.
    """
    return f"{invoice_info['project_number']}: {invoice_info['customer']}"

def handle_start(line: dict) -> str:
    """
    Convert 'date' and 'start_time' into format 'dd.mm.YYYY HH:mm:ss'.
    """
    date_str = line['date']
    start_time_str = line['start_time']
    start_datetime = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S")
    return start_datetime.strftime("%d.%m.%Y %H:%M:%S")

def preprocess_end_time(end_time: str) -> str:
    """
    Adjust '24:00:00' to '00:00:00' of the next day for parsing compatibility.
    """
    if end_time == "24:00:00":
        return "00:00:00"
    return end_time

def handle_dauer(line: dict) -> int:
    """
    Calculate 'Dauer' in minutes as (end_time - start_time - break_time).
    """
    start_time = datetime.strptime(line['start_time'], "%H:%M:%S")
    end_time_str = preprocess_end_time(line['end_time'])
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")
    
    if line['end_time'] == "24:00:00":
        end_time += timedelta(days=1)  # add one day if end_time was '24:00:00'
        
    break_duration = timedelta(hours=line['break_time'])
    work_duration = end_time - start_time - break_duration
    return int(work_duration.total_seconds() // 60)  # Dauer in minutes

def handle_menge(dauer: int) -> float:
    """
    Calculate 'Menge' in hours as dauer/60 and round to 1 decimal place.
    """
    return round(dauer / 60, 1)

def handle_besitzer(invoice_info: dict) -> str:
    """
    Return the name of the 'Besitzer' from the invoice info.
    """
    return invoice_info["name"]

def handle_kategorie(invoice_info: dict) -> str:
    """
    Determine 'Kategorie' based on 'is_without_measuring_technology'.
    """
    return (
        "Auftragsarbeit ohne Messtechnik" 
        if invoice_info.get("is_without_measuring_technology", False)
        else "Auftragsarbeit mit Messtechnik"
    )

def export_egw_file(config: dict, invoice_lists: list) -> str:
    """
    Exports invoice data into a CSV file with specified columns.
    """
    # Prepare the filename and output path
    file_name = create_egw_filename()
    output_egw_file_path = f"{config['output_path']}/{file_name}"
    
    # List to store all rows for DataFrame creation
    rows = []
    
    # Process each invoice in invoice_lists once
    for invoice in invoice_lists:
        invoice_info = invoice["invoice_info"]
        
        # Shared fields
        project_and_title = handle_project_and_title(invoice_info)
        besitzer = handle_besitzer(invoice_info)
        kategorie = handle_kategorie(invoice_info)
        
        # Process each line and add the structured data to rows
        for line in invoice_info["lines"]:
            dauer = handle_dauer(line)
            row = {
                "Stundenzettel ID": None,
                "Projekt": project_and_title,
                "Titel": project_and_title,
                "Kategorie": kategorie,
                "Beschreibung": None,
                "Start": handle_start(line),
                "Dauer": dauer,
                "Menge": handle_menge(dauer),
                "Preis pro Einheit": None,
                "Besitzer": besitzer,
                "Geändert von": None,
                "Status": None,
                "Projectid": None,
                "Geändert": None
            }
            rows.append(row)
    
    # Create DataFrame and remove duplicates
    df = pd.DataFrame(rows)
    df = df.drop_duplicates()
    
    # Save to CSV
    df.to_csv(output_egw_file_path, index=False, sep=";")
    
    print(f"File saved as {output_egw_file_path}")
    return output_egw_file_path


if __name__ == "__main__":
    import json
    from src.Utils.utils import read_config

    with open("config/data1.json", 'r') as file:
        invoice_1 = json.load(file)  

    with open("config/data3.json", 'r') as file:
        invoice_1_b = json.load(file)  

    config = read_config(path = 'config/config.yaml')['egw']
    # from src.mongo_database import MongoDatabase
    # config_path='config/config.yaml'
    # mongo_db = MongoDatabase(config_path=config_path)
    # invoice_1 = mongo_db.get_document_by_id(document_id='6702803020af02d7f38e4238')
    # invoice_2 = mongo_db.get_document_by_id(document_id='67028a752d2ad07517a0c286')
    # print(invoice_1['invoice_type'])
    # print(invoice_2['invoice_type'])

    # print(invoice_1['invoice_info'])
    # print(invoice_2['invoice_info'])
    
    output_egw_file_path = export_egw_file(config, invoice_lists =[invoice_1, invoice_1_b])

