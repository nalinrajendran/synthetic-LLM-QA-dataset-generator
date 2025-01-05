# Run the script with the following command:
# python json_to_csv.py --dir ./source_documents --output ./output_datasets
# This will process all JSON files in the source_documents directory and save the CSV files in the output_datasets directory.
# You can also process a single JSON file by specifying the --file argument with the path to the JSON file.
# python json_to_csv.py --file ./source_documents/example.json --output ./output_datasets
# This will process the example.json file and save the CSV file in the output_datasets directory.
# The CSV file will contain the prompt, question, and answer columns for each response in the JSON file.
# You can customize the fieldnames and other parameters in the script to suit your specific requirements.

import json
import csv
import os
import sys
import argparse
import shutil
# Set up argument parser
parser = argparse.ArgumentParser(description='Process JSON files to CSV')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--file', help='Path to single JSON file', default=None)
group.add_argument('--dir', help='Path to directory containing PDF files',default='./source_documents')
parser.add_argument('--output', help='Path to output directory',default='./output_datasets')
args = parser.parse_args()

# Create output directory if it doesn't exist
os.makedirs(args.output, exist_ok=True)

if args.file:
    # Single PDF file
    pdf_path = args.file
    print(pdf_path)
    pdfs = [os.path.splitext(pdf_path)[0]]  # Remove extension
elif args.dir:
    # Directory of PDFs
    pdf_dir = args.dir
    print(pdf_dir)
    pdfs = [os.path.splitext(f)[0] for f in os.listdir(pdf_dir) 
            if f.endswith('.pdf')]
    if not pdfs:
        print(f"No PDF files found in directory '{pdf_dir}'.")
        sys.exit(1) 

instruction = "You are a helpful assistant who can answer questions about the topic in the dataset."

# Process each PDF's JSON file
for pdf in pdfs:
    if args.file:
        json_file = os.path.splitext(pdf_path)[0] + '.json'
        csv_file = os.path.join(args.output, os.path.basename(os.path.splitext(pdf_path)[0]) + '.csv')
    else:
        json_file = os.path.join(pdf_dir, pdf + '.json')
        csv_file = os.path.join(args.output, pdf + '.csv')
    print("Processing:", json_file)
    try:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            responses = json.load(f)

        # Write to CSV file
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['prompt', 'question', 'answer']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for response in responses['responses']:
                if 'question' in response and 'answer' in response:
                    writer.writerow({
                        'prompt': instruction,
                        'question': response['question'],
                        'answer': response['answer']
                    })
        print(f"Created CSV file: {csv_file}")
        # Move JSON files to output directory if CSV was created successfully
        if os.path.exists(csv_file):
            output_json = os.path.join(args.output, os.path.basename(json_file))
            try:
                shutil.move(json_file, output_json)
                print(f"Moved JSON file to: {output_json}")
            except Exception as e:
                print(f"Error moving JSON file {json_file}: {str(e)}")
    except Exception as e:
        print(f"Error processing {json_file}: {str(e)}")
print("All JSONs processed successfully.")

