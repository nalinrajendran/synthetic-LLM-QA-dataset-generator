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

def convert_json_to_csv(source_documents, output_datasets):
  
    # Directory of PDFs
    json_files = [os.path.splitext(f)[0] for f in os.listdir(source_documents) 
            if f.endswith('.json')]
    if not json_files:
        print(f"No JSON files found in directory '{source_documents}'.")
        sys.exit(1) 

    instruction = "You are a helpful assistant who can answer questions about the topic in the dataset."

    # Process each PDF's JSON file
    for json_file in json_files:
        # Construct full paths for input and output files
        json_file = os.path.join(source_documents, json_file + '.json')
        csv_file = os.path.join(output_datasets, os.path.splitext(os.path.basename(json_file))[0] + '.csv')
        print("Processing:", json_file)
        print("Output:", csv_file)
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
                        #to-do write in model template
                        writer.writerow({
                            'prompt': instruction,
                            'question': response['question'],
                            'answer': response['answer']
                        })
            print(f"Created CSV file: {csv_file}")
            # Move JSON files to output directory if CSV was created successfully
            if os.path.exists(csv_file):
                output_json = os.path.join(output_datasets, os.path.basename(json_file))
                try:
                    shutil.move(json_file, output_json)
                    print(f"Moved JSON file to: {output_json}")
                except Exception as e:
                    print(f"Error moving JSON file {json_file}: {str(e)}")
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    print("All JSONs processed successfully.")

if __name__ == '__main__':
    convert_json_to_csv('./source_documents', './output_datasets')
