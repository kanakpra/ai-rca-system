from automation.llm_client import (
    call_local_llm
)


def load_prompt(
    target_file,
    feature_request
):

    with open(
        "prompts/code_generation_prompt.md",
        "r"
    ) as file:

        prompt_template = file.read()

    prompt = prompt_template.replace(
        "{{TARGET_FILE}}",
        target_file
    )

    prompt = prompt.replace(
        "{{FEATURE_REQUEST}}",
        feature_request
    )

    return prompt


if __name__ == "__main__":

    target_file = input(
        "Enter target file: "
    )

    feature_request = input(
        "Enter feature request: "
    )

    prompt = load_prompt(
        target_file,
        feature_request
    )

    print("\n=== SENDING TO GEMINI ===\n")

    result = call_local_llm(
        prompt
    )

    print("\n=== GENERATED CODE ===\n")

    print(result)