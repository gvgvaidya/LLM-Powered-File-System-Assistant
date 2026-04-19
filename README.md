# Document Management System

A Python tool for managing and querying documents using LLM function calling capabilities.

## Features

- Read files in TXT, PDF, and DOCX formats
- List files in directories with optional filtering
- Search for keywords in documents
- Write content to files
- LLM integration for natural language queries

## Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Using the tools directly:

```python
from file_tools import read_file, list_files, search_in_file, write_file

# List files
result = list_files("resumes")
print(f"Found {result['total']} files")

# Read a file
result = read_file("resumes/michael_torres.txt")
if result['success']:
    print(result['content'])

# Search in a file
result = search_in_file("resumes/michael_torres.txt", "Python")
print(f"Found {result['count']} matches")

# Write a file
result = write_file("output/summary.txt", "Content here")
```

### Using the LLM Assistant:

```python
from document_assistant import DocumentAssistant

# Initialize with OpenAI
assistant = DocumentAssistant(llm_provider="openai")

# Ask a question
result = assistant.ask("What skills are mentioned most in the resumes?")
print(result['answer'])

# Or with Anthropic
assistant = DocumentAssistant(llm_provider="anthropic")
result = assistant.ask("Find all candidates with Python experience")
print(result['answer'])
```

## Tools Available

- **read_file(filepath)** - Extract content from TXT, PDF, DOCX
- **list_files(directory, extension)** - List files with optional filtering
- **write_file(filepath, content)** - Write content to file
- **search_in_file(filepath, keyword)** - Search for keywords

## API Keys

Set your API key as environment variable:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic  
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Sample Data

The `resumes/` directory contains 7 sample resume files for testing:
- michael_torres.txt
- sarah_martinez.txt
- james_anderson.txt
- lisa_chen.txt
- robert_williams.txt
- emily_rodriguez.txt
- david_park.txt

## Dependencies

- openai >= 1.3.0
- anthropic >= 0.7.0
- PyPDF2 >= 3.0.0
- python-docx >= 0.8.11

## Example Queries

- "List all files in resumes folder"
- "Read sarah_martinez.txt"
- "Search for Docker experience in all resumes"
- "Create a summary of top technical skills"

