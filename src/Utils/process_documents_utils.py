import sys
sys.path.append("")


from typing import Dict
import os
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
            },
            limit = 500,
        )

        if not invoice_1_documents:
            logger.info("No invoice 1 documents found for the month.")
            return output_egw_file_path

        invoice_1_ids = [str(doc['_id']) for doc in invoice_1_documents]
        logger.debug(f"Invoice 1 document IDs: {invoice_1_ids}")

        # Generate the EGW file and update the path
        output_egw_file_path = export_egw_file(config['egw'], invoice_lists=invoice_1_documents)
        logger.debug(f"EGW file created: {output_egw_file_path}")
        
    except Exception as e:
        logger.error(f"Error creating or sending EGW file: {e}")
    
    return output_egw_file_path

def get_excel_files(mongo_db, start_of_month, logger):
    """
    Generate Excel files for invoice pairs and return the output folder path.
    
    Args:
        mongo_db: MongoDB connection object
        start_of_month (datetime): Start of the month for filtering documents
        logger: Logger instance for logging
        
    Returns:
        str: Path to the folder containing Excel files, or None if no files generated
    """
    output_folder = None

    try:
        # Filter all invoice 1 and 2 documents modified in the same month
        modified_documents, _ = mongo_db.get_documents(
            filters={
                "last_modified_at": {"$gte": start_of_month},
                "invoice_type": {"$in": ["invoice 1", "invoice 2"]}
            },
            limit = 500,

        )

        if not modified_documents:
            logger.info(f"No modified documents found for the month starting {start_of_month.strftime('%Y-%m-%d')}")
            return output_folder

        logger.info(f"Found {len(modified_documents)} modified documents for the month")

        # Find pairs of documents
        invoice_pairs = find_pairs_of_docs(modified_documents)
        if not invoice_pairs:
            logger.info("No matching invoice pairs found")
            return output_folder

        logger.info(f"Found {len(invoice_pairs)} invoice pairs")

        # Process each pair individually and log UUID
        for i in range(len(invoice_pairs)):
            pair = invoice_pairs[i]
            invoice = pair[0]
            logger.debug(f"Processing pair with invoice UUID: {invoice['invoice_uuid']}")
            employee_expense_report_path, output_2_excel = export_json_to_excel(
                invoice_pairs=[pair], logger=logger
            )
            logger.debug(f"Generated files - Employee report: {employee_expense_report_path}, Output 2: {output_2_excel}")
            # Set output_folder based on output_2_excel path
            if output_2_excel:
                output_folder = os.path.dirname(output_2_excel)

    except Exception as e:
        logger.error(f"Error generating Excel files: {str(e)}")
        return None

    return output_folder


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
    
