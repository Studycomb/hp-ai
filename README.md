# HP-AI

A tool for generating quiz questions using OpenAI

This tool is made to work together with [hp-web](https://github.com/Studycomb/hp-web)

## Getting Started

```
git clone git@github.com:Studycomb/hp-ai.git
cd hp-ai/
python -m pip install -e .
```

This program uses environment variables to configure API access. Check `.env.example` for details.

Environment variables can be automatically read from `.env` if present.

## Usage

```
$ hp-ai [-h] [-d DOC_FOLDER] [-p PROMPT_FILE]

HP-AI - A tool for generating quiz questions using OpenAI

options:
  -h, --help            show this help message and exit
  -d, --doc-folder DOC_FOLDER
                        Path to folder containing documents, default is current directory
  -p, --prompt-file PROMPT_FILE
                        Path to file with prompts, default is prompts.toml
```
The program runs interactively after launch. The program will:

1. Scan the specified document folder and let you select which document(s) to use as source material
2. Load prompts from the specified prompt file and allow you to choose which prompt to use for generating questions
3. Give you an overview of the selected options before generating
4. After generation the results will be displayed
5. A confirmation asking the user if they want to add the quizzes to the database
