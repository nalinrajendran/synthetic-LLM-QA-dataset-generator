import os
import sys
from openai import OpenAI
import json
from typing import List
from tqdm import tqdm
import PyPDF2
from prompt_toolkit.shortcuts import radiolist_dialog
import re
import ollama
import subprocess
from json_to_csv import convert_json_to_csv

def install_requirements():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Successfully installed required packages")
    except subprocess.CalledProcessError:
        print("Failed to install required packages")
        sys.exit(1)

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


def generate_questions_answers(text_chunk, model="llama3.1:latest"):

    messages = [
    {'role': 'system', 'content': 'You are an API that converts bodies of text into a single question and answer into a valid JSON format. Each JSON " \
    "should contain a single question with a single answer. Only respond with valid JSON and no additional text. Test the JSON for validity before returning it. I will be very disappinted with any errors in the JSON\n.'},
    {'role': 'user', 'content': 'Text: ' + text_chunk}
    ]

    response = client.chat.completions.create(
        model=model,#"gemma:2b",
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


# Check if correct number of arguments are provided
if len(sys.argv) < 3:
    print("Usage: python generate-dataset-from-pdfs.py [--file <filename> | --dir <directory>]")
    sys.exit(1)
pdfs = []
arg_type = sys.argv[1]
sourcepath = sys.argv[2]

def get_pdfs():
    if arg_type == '--file':
        # Process single PDF
        if not os.path.exists(path):
            print(f"Error: PDF file '{sourcepath}' not found.")
            sys.exit(1)
        pdfs = [sourcepath]
    elif arg_type == '--dir':
        # Process all PDFs in specified directory
        if not os.path.exists(sourcepath):
            print(f"Error: Directory '{sourcepath}' not found.")
            sys.exit(1)
        pdfs = [os.path.join(sourcepath, f) for f in os.listdir(sourcepath) if f.endswith('.pdf')]
        if not pdfs:
            print(f"No PDF files found in directory '{sourcepath}'.")
            sys.exit(1)
    else:
        print("Invalid argument. Use --file or --dir.")
        sys.exit(1)
    return pdfs

def main():
    # select from available ollama models
    available_models = ollama.list()

    # Get only the name from the REST API response
    available_models=[model.model for model in available_models.models]
    print("Available models: ", available_models)
        
    # Prompt the user to select the model for Q&A generation
    qa_model = radiolist_dialog(
        title="Select Model",
        text="Please select the model to use for Q&A generation:",
        values=[(model, model) for model in available_models],
        default=available_models[0],
    ).run()
    # get pdfs from the commandline arguments
    pdfs = get_pdfs()
    # Process each PDF
    for pdf in pdfs:
        print(f"Processing PDF: {pdf}")
        try:
            text = extract_text_from_pdf(pdf)
        except FileNotFoundError:
            print(f"Error: PDF file '{pdf}' not found.")
            continue
        except PyPDF2.PdfReadError:
            print(f"Error: Unable to read PDF file '{pdf}'. File may be corrupted or invalid.")
            continue
        except Exception as e:
            print(f"Unexpected error while reading PDF: {str(e)}")
            continue
        responses = {"responses": process_text(text), "model": qa_model}
        # Save responses to JSON file
        # strip the .pdf extension from the pdf file name
        pdf = os.path.splitext(pdf)[0]
        with open(f'{pdf}.json', 'w') as f:
            json.dump(responses, f, indent=2)
            print(f"Saved responses to: {pdf}.json")
    # Convert JSON files to CSV
    convert_json_to_csv(sourcepath,output_datasets='output_datasets' )
    print("All PDFs processed successfully.")


# Install requirements when module is run
if __name__ == '__main__':
    install_requirements()
    main()