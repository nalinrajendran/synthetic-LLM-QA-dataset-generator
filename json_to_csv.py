import json
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