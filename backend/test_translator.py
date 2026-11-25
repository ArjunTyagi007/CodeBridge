
import unittest

from app.translator.python_to_js import translate_python_to_js


class TestPythonToJavaScript(unittest.TestCase):

    def translate(self, code):
        return translate_python_to_js(code)

    def test_variable_assignment(self):
        result = self.translate("age = 20")
        self.assertIn("let age = 20;", result)

    def test_if_else(self):
        code = """
age = 20
if age >= 18:
    print("Adult")
else:
    print("Minor")
"""
        result = self.translate(code)

        self.assertIn("if ((age >= 18))", result)
        self.assertIn('console.log("Adult")', result)
        self.assertIn('console.log("Minor")', result)
        self.assertIn("else", result)

    def test_elif(self):
        code = """
score = 75
if score >= 90:
    print("A")
elif score >= 60:
    print("B")
else:
    print("C")
"""
        result = self.translate(code)

        self.assertIn("else if", result)
        self.assertIn('console.log("B")', result)

    def test_comparison_operators(self):
        code = """
a = 10
b = 20
print(a == b)
print(a != b)
print(a < b)
print(a > b)
print(a <= b)
print(a >= b)
"""
        result = self.translate(code)

        self.assertIn("===", result)
        self.assertIn("!==", result)
        self.assertIn("<", result)
        self.assertIn(">", result)
        self.assertIn("<=", result)
        self.assertIn(">=", result)

    def test_logical_operators(self):
        code = """
if age >= 18 and age <= 60:
    print("Allowed")
"""
        result = self.translate(code)

        self.assertIn("&&", result)

    def test_for_loop(self):
        code = """
for i in range(5):
    print(i)
"""
        result = self.translate(code)

        self.assertIn("for (let i = 0; i < 5; i += 1)", result)
        self.assertIn("console.log(i)", result)

    def test_while_loop(self):
        code = """
count = 0
while count < 5:
    count += 1
"""
        result = self.translate(code)

        self.assertIn("while", result)
        self.assertIn("count += 1;", result)

    def test_function(self):
        code = """
def add(a, b):
    return a + b
"""
        result = self.translate(code)

        self.assertIn("function add(a, b)", result)
        self.assertIn("return (a + b);", result)

    def test_lists_and_dictionaries(self):
        code = """
numbers = [1, 2, 3]
person = {"name": "John"}
"""
        result = self.translate(code)

        self.assertIn("[1, 2, 3]", result)
        self.assertIn('"name": "John"', result)

    def test_invalid_python(self):
        with self.assertRaises(SyntaxError):
            self.translate("if age >:")


if __name__ == "__main__":
    unittest.main(verbosity=2)
