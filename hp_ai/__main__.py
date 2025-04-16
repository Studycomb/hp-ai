import questionary
import argparse
import os
import tomllib

from openai_client import OpenAIClient

parser = argparse.ArgumentParser(description="")
parser.add_argument("--pdf-folder", help="Path to folder containing PDF files", default="./pdfs", type=str)
parser.add_argument("--prompt-file", help="Path to file with prompts", default="./prompts.toml", type=str)
args = parser.parse_args()

pdf_files = os.listdir(args.pdf_folder)
pdf_files = [f for f in pdf_files if f.endswith(".pdf")]

prompts = []
with open(args.prompt_file, "rb") as prompt_file:
    prompts = tomllib.load(prompt_file)

selected_files = questionary.checkbox(
    "Select PDF files to process",
    choices=pdf_files,
).ask()

selected_prompt = questionary.select(
    f"Select a prompt to use, prompt are defined in \"{args.prompt_file}\"",
    choices=prompts,
).ask()

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
