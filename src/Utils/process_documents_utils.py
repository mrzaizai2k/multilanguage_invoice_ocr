import sys
sys.path.append("")

import queue
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
import concurrent.futures
from src.egw_export import export_egw_file
from src.export_excel.main import export_json_to_excel
from src.Utils.utils import find_pairs_of_docs
from src.invoice_extraction import extract_invoice_info


def get_egw_file(mongo_db, start_of_month, config, logger):
    output_egw_file_path = None

    try:
        invoice_1_documents, _ = mongo_db.get_documents(
            filters={
                "last_modified_by": {"$ne": None},
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


def get_excel_files(mongo_db, start_of_month, updated_doc, logger):
    employee_expense_report_path, output_2_excel = None, None

    try:
        modified_documents, _ = mongo_db.get_documents(
            filters={
                "last_modified_by": {"$ne": None},
                "last_modified_at": {"$gte": start_of_month},
                "invoice_type": {"$in": ["invoice 1", "invoice 2"]},
                "invoice_info.name": updated_doc['invoice_info']['name'],
                "invoice_info.project_number": updated_doc['invoice_info']['project_number']
            }
        )

        if not modified_documents or len(modified_documents) <= 1:
            logger.info("Not enough modified documents to find pairs.")
            return employee_expense_report_path, output_2_excel

        logger.info(f"Modified documents found in change streams: {len(modified_documents)}")

        # Find pairs of documents
        invoice_pairs = find_pairs_of_docs(modified_documents)
        if not invoice_pairs:
            logger.info("No matching invoice pairs found.")
            return employee_expense_report_path, output_2_excel

        # Export pairs to Excel and JSON
        logger.debug("Creating paired JSON for export.")
        employee_expense_report_path, output_2_excel = export_json_to_excel(invoice_pairs=invoice_pairs, logger=logger)
        logger.debug(f"Attachment paths: {[employee_expense_report_path, output_2_excel]}")
        
    except Exception as e:
        logger.error(f"Error exporting to Excel or JSON: {e}")

    return employee_expense_report_path, output_2_excel

class BatchProcessor:
    def __init__(self, ocr_reader, invoice_extractor, 
                 mongo_db, config: dict, email_sender, logger=None):
        
        self.ocr_reader = ocr_reader
        self.invoice_extractor = invoice_extractor
        self.mongo_db = mongo_db
        self.config = config
        self.email_sender = email_sender  # Added email_sender
        self.logger = logger
        
        self.process_queue = queue.Queue()
        self.batch_size = self.config['batch_processor']["batch_size"]
        self.processing_interval = self.config['batch_processor']["processing_interval"]  # in seconds
        self.processing_thread = None
        self.is_running = False
        self.last_processed_time = datetime.now()
        self.currently_processing = set()
        self.lock = threading.Lock()

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._process_queue)
            self.processing_thread.daemon = True
            self.processing_thread.start()

    def stop(self):
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join()

    def add_to_queue(self, document: Dict):
        self.process_queue.put(document)

    def _process_queue(self):
        while self.is_running:
            try:
                batch = []
                # Collect up to batch_size items or wait for processing_interval
                while len(batch) < self.batch_size and self.is_running:
                    try:
                        # Wait for 1 second for new items
                        item = self.process_queue.get(timeout=1)
                        batch.append(item)
                    except queue.Empty:
                        # If we have any items and enough time has passed, process them
                        if batch and (datetime.now() - self.last_processed_time).seconds >= self.processing_interval:
                            break
                        continue

                if batch:
                    self._process_batch(batch)
                    self.last_processed_time = datetime.now()

                # Check if queue is empty after processing
                if self.process_queue.empty():
                    # Send email notification
                    self.email_sender.send_email(
                        email_type='modify_invoice_remind',
                        receivers=None
                    )

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in batch processing: {str(e)}")
                time.sleep(5)  # Wait before retrying

    def _process_batch(self, batch: List[Dict]):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.batch_size) as executor:
            futures = []
            for document in batch:
                if document['_id'] not in self.currently_processing:
                    with self.lock:
                        self.currently_processing.add(document['_id'])
                    futures.append(
                        executor.submit(
                            self._process_single_document,
                            document
                        )
                    )
            
            # Wait for all futures to complete
            concurrent.futures.wait(futures)

    def _process_single_document(self, document: Dict):
        try:
            document_id = document['_id']
            base64_img = document['invoice_image_base64']
            file_name = document['file_name']

            new_data = extract_invoice_info(
                base64_img=base64_img,
                ocr_reader=self.ocr_reader,
                invoice_extractor=self.invoice_extractor,
                config=self.config,
                logger=self.logger,
                file_name=file_name
            )

            self.mongo_db.update_document_by_id(str(document_id), new_data)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing document {document_id}: {str(e)}")
        finally:
            with self.lock:
                self.currently_processing.remove(document_id)

