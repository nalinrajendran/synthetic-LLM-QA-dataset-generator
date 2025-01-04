import sys
from openai import OpenAI
import json
from typing import List
from tqdm import tqdm
import PyPDF2


client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', 
)

#to-do change template to match Llama3.1 chat response template
template =  {
    "question": " ",
    "answer": " "
}

single_shot =  {
      "question": "What is the difference between classic programming and machine learning?",
      "answer": "In contrast to programming on classic computing with fixed rules, machine learning is just like it sounds we can train/teach a computer to “learn by example” by feeding it lots and lots of examples."
    },

def fix_json (crptd_json):
    messages = [
    {'role': 'system', 'content': f'You are an API that converts the wrongly formatted JSON into a properly fomatted one by following this template : {template} . Only respond with the JSON and no additional text. \n.'},
    {'role': 'user', 'content': 'Wrong JSON: ' + crptd_json}
    ]

    response = client.chat.completions.create(
        model="llama3.1:latest", #"gemma:2b" ,
        messages=messages,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=1,

    )

    response_text = response.choices[0].message.content.strip()
    # correct corrupted json with rule-based function
    response_text = correct_corrupted_json(response_text)
    try:
        json_data = json.loads(response_text)
        print(json_data)
        return json_data
    except json.JSONDecodeError:
        print("The JSON is not valid, reformatting again.")
        fix_json (crptd_json)
        return []

import json
import re

def correct_corrupted_json(corrupted_json_str):
    # Attempt to correct common JSON issues
    try:
        # Try to parse the JSON directly
        parsed_json = json.loads(corrupted_json_str)
        return parsed_json
    except json.JSONDecodeError:
        # Handle common issues
        
        # Remove unnecessary slashes
        corrected_json_str = corrupted_json_str.replace('\/', '/').replace('\\', '')
        
        # Remove extra commas
        corrected_json_str = corrected_json_str.replace(',}', '}').replace(',]', ']')
        
        # Handle missing closing braces
        if corrected_json_str.strip().endswith('}'):
            pass
        else:
            corrected_json_str += '}'
        
        # Attempt to parse the corrected JSON
        try:
            parsed_json = json.loads(corrected_json_str)
            return parsed_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Unable to correct JSON: {e}")

def is_valid_json_structure(response_text: str) -> bool:
            """Check if the text has valid JSON structure using regex pattern matching."""
            return bool(re.match(r'^[\s]*\{.*\}[\s]*$', response_text, re.DOTALL))


def generate_questions_answers(text_chunk):

    messages = [
    {'role': 'system', 'content': 'You are an API that converts bodies of text into a single question and answer into a valid JSON format. Each JSON " \
    "should contain a single question with a single answer. Only respond with valid JSON and no additional text. Test the JSON for validity before returning it. I will be very disappinted with any errors in the JSON\n.'},
    {'role': 'user', 'content': 'Text: ' + text_chunk}
    ]

    response = client.chat.completions.create(
        model="llama3.1:latest", #"gemma:2b",
        messages=messages,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )

    response_text = response.choices[0].message.content.strip()
    try:
        #test response_text for json validity before calling json.loads and skip if invalid
       
        # Check if response_text has valid JSON structure
        if not is_valid_json_structure(response_text):
            print("Invalid JSON structure")
            return []
        if not response_text.strip().startswith('{') or not response_text.strip().endswith('}'):
            print("Invalid JSON format - missing braces")
            return []

        json_data = json.loads(response_text)
        print(json_data)
        return json_data
    except json.JSONDecodeError as e:
        print(str(e))
        print("Error: Response is not valid JSON.... Trying to fix the JSON.")
        #correct_corrupted_json(response_text)
        #fix_json(response_text)
        return []
    finally:
        #continue and skip this value
        pass

def extract_text_from_pdf(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text += page_obj.extract_text()
    pdf_file_obj.close()
    #print first few characters of the text
    print(text[:1000])
    return text

def process_text(text: str, chunk_size: int = 4000) -> List[dict]:
    text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    all_responses = []
    for chunk in tqdm(text_chunks, desc="Processing chunks", unit="chunk"):
        response = generate_questions_answers(chunk)
        if 'question' in response and 'answer' in response:
            all_responses.append({'question': response['question'], 'answer': response['answer']})
    print(f"Processed {len(all_responses)} responses.")
    #print first few responses
    print(all_responses[:3])
    return all_responses

# get pdf name from user in commandline input parameter
# if argv[1] is not provided, then provide an error message and exit
if len(sys.argv) < 2:
    print("Please provide the pdf file name as a commandline argument.")
    sys.exit(1)
pdf_name = sys.argv[1]

try:
    text = extract_text_from_pdf(pdf_name)
except FileNotFoundError:
    print(f"Error: PDF file '{pdf_name}' not found.")
    sys.exit(1)
except PyPDF2.PdfReadError:
    print(f"Error: Unable to read PDF file '{pdf_name}'. File may be corrupted or invalid.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error while reading PDF: {str(e)}")
    sys.exit(1)
responses = {"responses": process_text(text)}


with open('responses.json', 'w') as f:
    json.dump(responses, f, indent=2)


import csv

instruction = "You will answer questions about Machine Learning"

with open('responses.json', 'r', encoding='utf-8') as f:
    responses = json.load(f)

with open('responses.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['prompt', 'question', 'answer']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for response in responses['responses']:
        if 'question' in response and 'answer' in response:
            writer.writerow({'prompt': instruction, 'question': response['question'], 'answer': response['answer']})