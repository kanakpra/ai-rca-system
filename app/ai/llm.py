import requests


def load_prompt(logs):

    with open("prompts/incident_prompt.md", "r") as file:

        prompt_template = file.read()

    return prompt_template.replace(
        "{{LOGS}}",
        logs
    )


def call_ai(logs):

    prompt = load_prompt(logs)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json().get("response", "")