# OLLAMA Question-Answer Dataset Generator

This project provides a suite of Python scripts to automatically generate question-answer datasets from PDF documents. It leverages locally run Ollama models to analyze text from PDFs and create corresponding questions and answers. The generated datasets can be useful for training and fine-tuning large language models (LLMs) or for other NLP tasks.

Key technologies used include Python, the Ollama API, and various text processing libraries.

## Key Features

*   **Comprehensive PDF Text Extraction**: Utilizes libraries to accurately extract textual content from your PDF documents.
*   **Flexible Question-Answer Generation**: Connects with your local Ollama instance to generate relevant questions and answers based on the extracted text.
*   **Local Ollama Model Selection**: Prompts you to choose from your available local Ollama models, allowing you to experiment with different LLMs.
*   **Batch Processing**: Capable of processing multiple PDF files placed in the `source_documents` directory in a single run.
*   **Dual Format Output**: Saves the generated question-answer pairs in both JSON (`<pdf_name>.json`) and CSV (`<pdf_name>.csv`) formats in the `output_datasets` directory.
*   **Text Chunking**: Intelligently divides long texts into smaller, manageable chunks to fit the context window of the LLMs, ensuring thorough coverage of the document.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Python**: Version 3.7 or higher is recommended.
*   **Ollama**:
    *   Ollama must be installed and running on your local machine. You can download it from [https://ollama.ai/](https://ollama.ai/).
    *   Ensure the Ollama API server is accessible (default: `http://localhost:11434`).
    *   You need to have at least one model pulled using Ollama (e.g., `ollama pull llama2`). You can see available models with `ollama list`.

## Dependencies

The project relies on the following Python libraries:

*   `openai`
*   `tqdm`
*   `PyPDF2`
*   `ollama`
*   `prompt_toolkit`

These can be installed by running `pip install -r requirements.txt` as described in the Installation section.

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```
    *(Replace `https://github.com/your-username/your-repository-name.git` with the actual URL of this repository if you know it, otherwise leave as a placeholder for the user to fill in)*

2.  **Create a Virtual Environment and Install Dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Install the required packages using the `requirements.txt` file (see Dependencies section for a list):
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

1.  **Prepare Your Documents**:
    *   Place all the PDF files you want to process into the `source_documents/` directory. If this directory doesn't exist, please create it at the root of the project.

2.  **Run the Dataset Generation Script**:
    *   Execute the main script from the root directory of the project:
        ```bash
        python generate-dataset-from-pdfs.py
        ```

3.  **Select an Ollama Model**:
    *   Upon running the script, you will be presented with a list of your locally available Ollama models.
    *   Enter the number corresponding to the model you wish to use for generating questions and answers. This selection is handled by `ollama_models.py`.

4.  **Processing**:
    *   The script will then process each PDF file one by one.
    *   Text is extracted, chunked (as managed by `chunking.py`), and then questions and answers are generated using the selected Ollama model.
    *   Progress will be displayed in the console.

5.  **Check Your Datasets**:
    *   Once the script finishes, you will find the generated datasets in the `output_datasets/` directory.
    *   For each input PDF (e.g., `my_document.pdf`), two files will be created:
        *   A JSON file: `output_datasets/my_document.json`
        *   A CSV file: `output_datasets/my_document.csv` (This conversion is handled automatically by `json_to_csv.py` after the JSON generation).

## Project Structure

```
.
├── .gitignore
├── README.md
├── chunking.py                 # Handles text splitting for LLM processing
├── generate-dataset-from-pdfs.py # Main script for dataset generation
├── json_to_csv.py              # Converts JSON output to CSV
├── ollama_models.py            # Manages listing and selection of Ollama models
├── requirements.txt            # Python dependencies
├── source_documents/           # Directory for your input PDF files
│   └── example.pdf
└── output_datasets/            # Directory for generated JSON and CSV datasets
    ├── example.json
    └── example.csv
```

## Scripts Overview

*   `generate-dataset-from-pdfs.py`: This is the main executable script. It orchestrates the entire process:
    *   Scans the `source_documents/` directory for PDF files.
    *   Prompts the user to select an Ollama model (using functionality from `ollama_models.py`).
    *   For each PDF:
        *   Extracts text.
        *   Splits text into manageable chunks (using `chunking.py`).
        *   Generates question-answer pairs via the Ollama API.
        *   Saves the results as a JSON file in `output_datasets/`.
    *   Automatically invokes `json_to_csv.py` to convert the generated JSON to CSV format.

*   `json_to_csv.py`: A utility script that takes a JSON file (as generated by the main script) and converts its contents into a CSV file. It's called automatically by `generate-dataset-from-pdfs.py`.

*   `ollama_models.py`: This script handles interaction with your local Ollama installation to:
    *   Fetch the list of locally available models.
    *   Present this list to the user for selection.
    *   Return the chosen model to the main script.

*   `chunking.py`: Contains the logic for dividing large pieces of text extracted from PDFs into smaller segments. This is crucial for fitting the text within the context window limitations of most language models and ensuring the entire document can be processed effectively.

## Acknowledgements

This project is based on and inspired by the work of others in the open-source community. We would like to acknowledge the following projects:

*   The original version by [nalinrajendran/synthetic-LLM-QA-dataset-generator](https://github.com/nalinrajendran/synthetic-LLM-QA-dataset-generator).
*   Concepts incorporated from [TraoreMorike/synthetic-LLM-QA-dataset-generator](https://github.com/TraoreMorike/synthetic-LLM-QA-dataset-generator/tree/main).

This version aims to address certain issues, such as those related to JSON handling, and introduces features like LLM model selection from local Ollama instances and the capability to process multiple PDFs from a directory.
