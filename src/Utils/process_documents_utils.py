import sys
sys.path.append("")


from typing import Dict
from src.egw_export import export_egw_file
from src.export_excel.main import export_json_to_excel
from src.Utils.utils import find_pairs_of_docs
from src.invoice_extraction import extract_invoice_info


def get_egw_file(mongo_db, start_of_month, config, logger):
    output_egw_file_path = None

    try:
        invoice_1_documents, _ = mongo_db.get_documents(
            filters={
                "last_modified_at": {"$gte": start_of_month},
                "invoice_type": "invoice 1"
            }
        )

        if not invoice_1_documents:
            logger.info("No invoice 1 documents found for the month.")
            return output_egw_file_path

        invoice_1_ids = [str(doc['_id']) for doc in invoice_1_documents]
        logger.debug(f"Invoice 1 document IDs: {invoice_1_ids}")

        # Generate the EGW file and update the path
        output_egw_file_path = export_egw_file(config['egw'], invoice_lists=invoice_1_documents)
        logger.debug(f"EGW file created and emailed: {output_egw_file_path}")
        
    except Exception as e:
        logger.error(f"Error creating or sending EGW file: {e}")
    
    return output_egw_file_path

def get_excel_files(mongo_db, start_of_month, logger):
    employee_expense_report_path, output_2_excel = None, None

    try:
        # Filter all invoice 1 and 2 documents modified in the same month
        modified_documents, _ = mongo_db.get_documents(
            filters={
                "last_modified_at": {"$gte": start_of_month},
                "invoice_type": {"$in": ["invoice 1", "invoice 2"]}
            }
        )

        if not modified_documents:
            logger.info("No modified documents found for the month.")
            return employee_expense_report_path, output_2_excel

        logger.info(f"Modified documents found: {len(modified_documents)}")

        # Find pairs of documents based on file_name (handled in find_pairs_of_docs)
        invoice_pairs = find_pairs_of_docs(modified_documents)
        if not invoice_pairs:
            logger.info("No matching invoice pairs found.")
            return employee_expense_report_path, output_2_excel

        # Export pairs to Excel and JSON
        logger.debug("Creating paired JSON for export.")
        employee_expense_report_path, output_2_excel = export_json_to_excel(
            invoice_pairs=invoice_pairs, logger=logger
        )
        logger.debug(f"Attachment paths: {[employee_expense_report_path, output_2_excel]}")

    except Exception as e:
        logger.error(f"Error exporting to Excel or JSON: {e}")

    return employee_expense_report_path, output_2_excel


def process_single_document(ocr_reader, invoice_extractor, 
                            config, mongo_db, logger, document: dict):
    try:
        document_id = document['_id']
        base64_img = document['invoice_image_base64']
        file_name = document['file_name']

        new_data = extract_invoice_info(
            base64_img=base64_img,
            ocr_reader=ocr_reader,
            invoice_extractor=invoice_extractor,
            config=config,
            logger=logger,
            file_name=file_name
        )

        mongo_db.update_document_by_id(str(document_id), new_data)

    except Exception as e:
        msg = f"Error processing document {document_id}: {str(e)}"
        print(msg)
        if logger:
            logger.error(msg = msg)
    
