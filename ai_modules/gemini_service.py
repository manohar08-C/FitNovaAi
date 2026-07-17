import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_response(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        if hasattr(response, "text"):
            return response.text

        return "No response generated."

    except Exception as e:
        print("Gemini Error:", e)
        return "Sorry, an AI error occurred."