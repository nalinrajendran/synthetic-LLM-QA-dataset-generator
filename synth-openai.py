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
        model="gemma:2b",
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

import json

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

# Example usage
corrupted_json_str = '''{
  "question": "What is AI/ML?",
  "answer": "Artificial Intelligence (AI) and Machine Learning (ML) are a set of technologies that have revolutionized how we live and work. AI has led to new types of applications, such as facial recognition, machine learning, and neural networks, while ML is a subfield of AI that uses data and algorithms to train models that can make predictions or decisions on new data."
'''

corrected_json = correct_corrupted_json(corrupted_json_str)
print(json.dumps(corrected_json, indent=2))



def generate_questions_answers(text_chunk):

    messages = [
    {'role': 'system', 'content': 'You are an API that converts bodies of text into a single question and answer into a valid JSON format. Each JSON " \
    "should contain a single question with a single answer. Only respond with valid JSON and no additional text. Test the JSON for validity before returning it. I will be very disappinted with any errors in the JSON\n.'},
    {'role': 'user', 'content': 'Text: ' + text_chunk}
    ]


    response = client.chat.completions.create(
        model="gemma:2b",
        messages=messages,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,

    )


    response_text = response.choices[0].message.content.strip()
    try:
        correct_corrupted_json(response_text)

        json_data = json.loads(response_text)
        print(json_data)
        return json_data
    except json.JSONDecodeError as e:
        print(str(e))
        print("Error: Response is not valid JSON.... Trying to fix the JSON.")
        correct_corrupted_json(response_text)
        fix_json(json.loads(response_text))
        return []




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


text = extract_text_from_pdf(pdf_name)
responses = {"responses": process_text(text)}


with open('responses.json', 'w') as f:
    json.dump(responses, f, indent=2)


