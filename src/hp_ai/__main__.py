import json

from dotenv import load_dotenv

from . import api, cli, io

# Load environment variables
load_dotenv()


def main():
    try:
        cli_handler = cli.CLIHandler()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    document_manager = io.DocumentManager(cli_handler.get_document_folder())
    prompt_manager = io.PromptManager(cli_handler.get_prompt_file())

    documents = document_manager.get_documents()

    # Get user selections
    try:
        selected_documents = cli_handler.select_documents(documents)
        selected_prompt_name = cli_handler.select_prompt(
            prompt_manager.get_prompt_names()
        )
    except KeyboardInterrupt:
        print("\nCancelled by user\n")
        return
    selected_prompt = prompt_manager.get_prompt(selected_prompt_name)

    # Display selections and confirm
    print(f"Selected documents: {selected_documents}")
    print(f"Selected prompt: {selected_prompt}")

    if cli_handler.confirm_continue("Do you want to generate quiz questions?"):
        try:
            client = api.OpenAIClient()
        except Exception as e:
            print(f"Error initializing OpenAIClient: {e}")
            return

        for filename in selected_documents:
            client.add_file(document_manager.get_document_path(filename))

        # Generate and display result
        result = client.generate(selected_prompt)
        json_result = json.loads(result)
        pretty_result = json.dumps(json_result, indent=4, ensure_ascii=False)
        print(pretty_result)

        if cli_handler.confirm_continue(
            "Do you want to upload the quiz to the database?"
        ):
            try:
                quizClient = api.QuizAPIClient()
            except Exception as e:
                print(f"Error initializing QuizAPIClient: {e}")
                return
            quizClient.create_quiz(json_result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
