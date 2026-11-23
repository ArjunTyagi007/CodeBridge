
from app.translator.python_to_js import translate_python_to_js

python_code = """
def greet(name):
    print("Hello", name)

greet("World")
"""

javascript_code = translate_python_to_js(python_code)

print("Translated JavaScript:")
print("----------------------")
print(javascript_code)
