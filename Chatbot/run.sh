pip install --upgrade pip setuptools wheel
BLIS_ARCH="generic"
pip install spacy --no-binary=blis
pip install -r requirements.txt -U
python -m spacy download en_core_web_md
python ChatBot/main.py