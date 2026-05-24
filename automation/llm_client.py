import os

from dotenv import load_dotenv

import google.generativeai as genai


load_dotenv()


API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


genai.configure(
    api_key=API_KEY
)


model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)


def call_local_llm(prompt):

    try:

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        return f"LLM Error: {str(e)}"