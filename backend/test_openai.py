
from app.ai.openai_service import explain_code

try:
    explanation = explain_code(
        original_code="age = 20\nprint(age)",
        translated_code="let age = 20;\nconsole.log(age);",
        source_language="Python",
        target_language="JavaScript"
    )

    print("\nAI EXPLANATION:\n")
    print(explanation)

except Exception as error:
    print("\nOpenAI test failed:")
    print(error)
