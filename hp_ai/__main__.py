from . import api
from . import cli
from . import io

def main():
    # Initialize components
    cli_handler = cli.CLIHandler()
    document_manager = io.DocumentManager(cli_handler.get_document_folder())
    prompt_manager = io.PromptManager(cli_handler.get_prompt_file())

    # Get available PDF files and prompts
    documents = document_manager.get_documents()

    # Get user selections
    selected_documents = cli_handler.select_documents(documents)
    selected_prompt_name = cli_handler.select_prompt(prompt_manager.get_prompt_names())
    selected_prompt = prompt_manager.get_prompt(selected_prompt_name)

    # Display selections and confirm
    print(f"Selected documents: {selected_documents}")
    print(f"Selected prompt: {selected_prompt}")

    if cli_handler.confirm_continue():
        # Process files with OpenAI
        client = api.OpenAIClient()
        for filename in selected_documents:
            client.add_file(document_manager.get_document_path(filename))

        # Generate and display result
        result = client.generate(selected_prompt)
        print(result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
