install:
# python3 -m venv venv
	pip install --no-cache-dir -r requirements.txt

unit_test:
	python src/excel_export.py
	python src/export_excel/main.py
	python src/ldap_authen.py
	python src/mail.py
	python src/validate_invoice.py
	python src/base_extractors.py
	python src/ocr_reader.py
	python src/invoice_extraction.py
	python src/qwen2_extract.py
	python src/mongo_database.py