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

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            },
            timeout=10
        )

        return response.json().get(
            "response",
            "No AI response"
        )

    except Exception as e:

        return f"AI unavailable: {str(e)}"