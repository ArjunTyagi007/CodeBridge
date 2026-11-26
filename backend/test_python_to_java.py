import unittest

from app.translator.python_to_java import translate_python_to_java


class TestPythonToJava(unittest.TestCase):

    def translate(self, code):
        return translate_python_to_java(code)

    def test_variable_assignment(self):
        result = self.translate("age = 20")
        self.assertIn("int age = 20;", result)

    def test_string_assignment(self):
        result = self.translate('name = "John"')
        self.assertIn('String name = "John";', result)

    def test_boolean_assignment(self):
        result = self.translate("is_active = True")
        self.assertIn("boolean is_active = true;", result)

    def test_if_else(self):
        code = """
age = 20
if age >= 18:
    print("Adult")
else:
    print("Minor")
"""
        result = self.translate(code)

        self.assertIn("if (age >= 18)", result)
        self.assertIn('System.out.println("Adult")', result)
        self.assertIn('System.out.println("Minor")', result)
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
        self.assertIn('System.out.println("B")', result)

    def test_for_loop(self):
        code = """
for i in range(5):
    print(i)
"""
        result = self.translate(code)

        self.assertIn(
            "for (int i = 0; i < 5; i++)",
            result
        )
        self.assertIn("System.out.println(i)", result)

    def test_while_loop(self):
        code = """
count = 0
while count < 5:
    count += 1
"""
        result = self.translate(code)

        self.assertIn("while (count < 5)", result)
        self.assertIn("count += 1;", result)

    def test_function(self):
        code = """
def add(a, b):
    return a + b
"""
        result = self.translate(code)

        self.assertIn("public static", result)
        self.assertIn("add(", result)
        self.assertIn("return (a + b);", result)

    def test_lists(self):
        code = """
numbers = [1, 2, 3]
"""
        result = self.translate(code)

        self.assertIn("List", result)
        self.assertIn("1", result)
        self.assertIn("2", result)
        self.assertIn("3", result)

    def test_invalid_python(self):
        with self.assertRaises(SyntaxError):
            self.translate("if age >:")


if __name__ == "__main__":
    unittest.main(verbosity=2)