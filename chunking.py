

from openai import OpenAI
import json
from typing import List
from tqdm import tqdm
import PyPDF2
import sys
# run pip install -r requirements.txt to install the required packages
import subprocess
# run the following command in your terminal to install the required packages
# pip install -r requirements.txt
def install_requirements():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")

install_requirements()



def process_text(text: str, chunk_size: int = 40):
    text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    print(f"Created {len(text_chunks)} chunks.")



def extract_text_from_pdf(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text += page_obj.extract_text()
    pdf_file_obj.close()
    return text

# get pdf name from user in commandline input parameter
# if argv[1] is not provided, then provide an error message and exit
if len(sys.argv) < 2:
    print("Please provide the pdf file name as a commandline argument.")
    sys.exit(1)
pdf_name = sys.argv[1]
text = extract_text_from_pdf(pdf_name)
#print first few characters of the text
print(text[:1000])
responses = {"responses": process_text(text)}
