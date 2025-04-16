import questionary
import argparse
import os
import tomllib

from openai_client import OpenAIClient

parser = argparse.ArgumentParser(description="HP-AI - A tool for generating quiz questions using OpenAI")
parser.add_argument("--pdf-folder", help="Path to folder containing PDF files", default="./pdfs", type=str)
parser.add_argument("--prompt-file", help="Path to file with prompts", default="./prompts.toml", type=str)
args = parser.parse_args()

if not os.path.exists(args.pdf_folder):
    print(f"PDF folder \"{args.pdf_folder}\" does not exist")
    exit(1)
if not os.path.exists(args.prompt_file):
    print(f"Prompt file \"{args.prompt_file}\" does not exist")
    exit(1)

pdf_files = os.listdir(args.pdf_folder)
pdf_files = [f for f in pdf_files if f.endswith(".pdf")]

prompts = []
with open(args.prompt_file, "rb") as prompt_file:
    prompts = tomllib.load(prompt_file)

selected_files = questionary.checkbox(
    "Select PDF files to process",
    choices=pdf_files,
).ask()

if selected_files == None: # KeyboardInterrupt
    exit(1)

selected_prompt = questionary.select(
    f"Select a prompt to use, prompt are defined in \"{args.prompt_file}\"",
    choices=prompts,
).ask()

if selected_prompt == None: # KeyboardInterrupt
    exit(1)

print(f"Selected files: {selected_files}")
print(f"Selected prompt: {prompts[selected_prompt]}")

if not questionary.confirm(
    "Do you want to continue?",
).ask():
    print("Aborting...")
    exit(0)

client = OpenAIClient()
for f in selected_files:
    client.add_file(os.path.join(args.pdf_folder, f))
result = client.generate(prompts[selected_prompt])
print(result)
