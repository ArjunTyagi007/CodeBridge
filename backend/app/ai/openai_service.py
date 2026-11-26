
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Read API key securely
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Check your backend/.env file."
    )

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Select the AI model
MODEL = os.getenv("OPENAI_MODEL", "gpt-6.2-astra")


def explain_code(
    original_code: str,
    translated_code: str,
    source_language: str,
    target_language: str
):
    """
    Generate an explanation of the original and translated code.
    """

    if not original_code.strip() or not translated_code.strip():
        raise ValueError("Both original and translated code are required.")

    prompt = f"""
You are CodeBridge, an expert programming tutor.

Explain the following code in simple language suitable for beginners.

Source language: {source_language}
Target language: {target_language}

Original code:
{original_code}

Translated code:
{translated_code}

Provide your explanation using these sections:

1. Overall Purpose
   Explain what the program does.

2. Step-by-Step Explanation
   Explain the important statements in order.

3. Important Programming Concepts
   Explain the functions, variables, loops, and conditions used.

4. Translation Comparison
   Explain how the original code was converted into the target language.

5. Key Differences
   Mention important differences between the two languages
   that are relevant to this code.

Use clear language and small examples where helpful.
Do not invent functionality that is not present in the code.
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text
