

from openai import OpenAI
import json
from typing import List
from tqdm import tqdm
import PyPDF2



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



text = extract_text_from_pdf('PIIA - India.pdf')
responses = {"responses": process_text(text)}
