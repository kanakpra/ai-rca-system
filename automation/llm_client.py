import requests


def call_local_llm(prompt):

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        return response.json().get(
            "response",
            "No response"
        )

    except Exception as e:

        return f"LLM Error: {str(e)}"