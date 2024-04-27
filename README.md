# OLLAMA Question-Answer Dataset Generator

This script is designed to generate a question-answer dataset from a given text, specifically from a PDF document. It uses the OLLAMA API, an OpenAI compatible API endpoint, to generate questions and answers based on the text content.

## Key Features

- **Extract Text from PDF**: The script can extract text from a PDF document using the PyPDF2 library.
- **Generate Questions and Answers**: The script uses the OLLAMA API to generate questions and answers based on the extracted text.
- **Save Results**: The generated question-answer pairs are saved in a JSON file.

## How to Use

1. **Setup OLLAMA API**: Before running the script, make sure to set up the OLLAMA API on your local machine. The API is invoked using the OpenAI format with the base URL set to 'http://localhost:11434/v1'. The API key is set to 'ollama', but it is not used in this script.

2. **Run the Script**: Run the script in your Python environment. The script will read a PDF document, extract the text, generate questions and answers, and save the results in a JSON file.

3. **Specify the PDF Document**: Specify the path to the PDF document in the `extract_text_from_pdf` function.

4. **Check the Results**: The results are saved in a file named 'responses.json'. Check this file to see the generated question-answer pairs.

## Important Note

This script uses the OLLAMA API, which is an OpenAI compatible API endpoint. The OLLAMA API is designed to work with large language models and provides a Docker Image for an OpenAI API compatible server for local LLMs. This makes it a powerful tool for generating question-answer pairs based on a given text.

## Dependencies

- OpenAI
- PyPDF2
- tqdm
- json

## Contribution

Feel free to contribute to this project by creating issues or sending pull requests. All contributions are welcome!
