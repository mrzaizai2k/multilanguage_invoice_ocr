install:
# python3 -m venv venv
	pip install --no-cache-dir -r requirements.txt

run:
	streamlit run app.py