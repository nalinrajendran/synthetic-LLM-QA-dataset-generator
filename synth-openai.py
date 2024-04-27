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
      "question": "What are the Intellectual Property Rights in the scope of this Agreement?",
      "answer": "The Intellectual Property Rights in the scope of this Agreement include rights associated with works of authorship, including exclusive exploitation rights, copyrights, design rights, moral rights, and mask work rights; trademark, service marks and trade name rights and similar rights; trade secret rights; patent and industrial property rights; other proprietary rights in intellectual property of every kind and nature."
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
    try:
        json_data = json.loads(response_text)
        print(json_data)
        return json_data
    except json.JSONDecodeError:
        print("The JSON is not valid, reformatting again.")
        # fix_json (crptd_json)
        return []


def generate_questions_answers(text_chunk):

    messages = [
    {'role': 'system', 'content': 'You are an API that converts bodies of text into a single question and answer into a JSON format. Each JSON " \
    "should contain a single question with a single answer. Only respond with the JSON and no additional text. \n.'},
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
        json_data = json.loads(response_text)
        print(json_data)
        return json_data
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON.... Trying to fix the JSON.")
        # fix_json(json.loads(response_text))
        return []




def extract_text_from_pdf(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text += page_obj.extract_text()
    pdf_file_obj.close()
    return text




def process_text(text: str, chunk_size: int = 4000) -> List[dict]:
    text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    all_responses = []
    for chunk in tqdm(text_chunks, desc="Processing chunks", unit="chunk"):
        response = generate_questions_answers(chunk)
        if 'question' in response and 'answer' in response:
            all_responses.append({'question': response['question'], 'answer': response['answer']})
    return all_responses




text = extract_text_from_pdf('PIIA - India.pdf')
responses = {"responses": process_text(text)}


with open('responses.json', 'w') as f:
    json.dump(responses, f, indent=2)


