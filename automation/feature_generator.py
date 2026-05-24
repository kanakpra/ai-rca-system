from automation.llm_client import (
    call_local_llm
)

from automation.parser import (
    extract_json
)

from automation.validator import (
    validate_plan
)


def load_prompt(feature_request):

    with open(
        "prompts/feature_generation_prompt.md",
        "r"
    ) as file:

        prompt_template = file.read()

    return prompt_template.replace(
        "{{FEATURE_REQUEST}}",
        feature_request
    )


def retry_prompt(raw_output):

    return f"""
Your previous response was invalid.

You MUST return ONLY valid JSON.

Only use files from this project:

- app/reasoning/parser.py
- app/reasoning/severity.py
- app/reasoning/correlation.py
- app/api/routes.py
- tests/test_parser.py
- tests/test_severity.py

No explanations.
No markdown.
No extra text.

Previous invalid response:
{raw_output}

Return ONLY this JSON format:

{{
  "files_to_modify": [],
  "logic_changes": [],
  "tests_required": [],
  "possible_risks": []
}}
"""


if __name__ == "__main__":

    request = input(
        "Enter feature request: "
    )

    prompt = load_prompt(request)

    print("\n=== FIRST AI CALL ===\n")

    raw_output = call_local_llm(prompt)

    parsed = extract_json(raw_output)

    # Retry if invalid JSON
    if not parsed:

        print("\n=== INVALID JSON DETECTED ===\n")

        retry = retry_prompt(raw_output)

        raw_output = call_local_llm(retry)

        parsed = extract_json(raw_output)

    print("\n=== FINAL RAW OUTPUT ===\n")

    print(raw_output)

    print("\n=== FINAL PARSED OUTPUT ===\n")

    print(parsed)

    # Validate project files
    if parsed:

        invalid = validate_plan(parsed)

        print("\n=== INVALID FILES ===\n")

        print(invalid)

        if not invalid:

            print(
                "\nPlan passed validation."
            )

        else:

            print(
                "\nPlan rejected due to invalid files."
            )