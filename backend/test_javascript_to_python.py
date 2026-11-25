
import unittest

from app.translator.javascript_to_python import (
    translate_javascript_to_python
)


class TestJavaScriptToPython(unittest.TestCase):

    def test_variable_declaration(self):
        result = translate_javascript_to_python(
            "let age = 20;"
        )
        self.assertIn("age = 20", result)

    def test_console_log(self):
        result = translate_javascript_to_python(
            'console.log("Hello");'
        )
        self.assertIn("print(", result)
        self.assertIn("Hello", result)

    def test_arithmetic(self):
        result = translate_javascript_to_python(
            "let total = 10 + 5;"
        )
        self.assertIn("(10 + 5)", result)

    def test_comparison(self):
        result = translate_javascript_to_python(
            "let result = age >= 18;"
        )
        self.assertIn("(age >= 18)", result)

    def test_logical_operators(self):
        result = translate_javascript_to_python(
            "let result = age >= 18 && age <= 60;"
        )
        self.assertIn("and", result)

    def test_if_else(self):
        result = translate_javascript_to_python(
            """
            if (age >= 18) {
                console.log("Adult");
            } else {
                console.log("Minor");
            }
            """
        )
        self.assertIn("if (age >= 18):", result)
        self.assertIn("else:", result)

    def test_elif(self):
        result = translate_javascript_to_python(
            """
            if (marks >= 90) {
                console.log("A");
            } else if (marks >= 70) {
                console.log("B");
            } else {
                console.log("C");
            }
            """
        )
        self.assertIn("elif", result)

    def test_while_loop(self):
        result = translate_javascript_to_python(
            """
            let i = 0;
            while (i < 5) {
                i++;
            }
            """
        )
        self.assertIn("while (i < 5):", result)
        self.assertIn("i += 1", result)

    def test_for_loop(self):
        result = translate_javascript_to_python(
            """
            for (let i = 0; i < 5; i++) {
                console.log(i);
            }
            """
        )
        self.assertIn("for i in range(0, 5):", result)

    def test_function(self):
        result = translate_javascript_to_python(
            """
            function add(a, b) {
                return a + b;
            }
            """
        )
        self.assertIn("def add(a, b):", result)
        self.assertIn("return (a + b)", result)

    def test_arrays(self):
        result = translate_javascript_to_python(
            "let numbers = [10, 20, 30];"
        )
        self.assertIn("[10, 20, 30]", result)

    def test_objects(self):
        result = translate_javascript_to_python(
            'let person = {name: "John", age: 25};'
        )
        self.assertIn("'name': 'John'", result)
        self.assertIn("'age': 25", result)

    def test_array_length(self):
        result = translate_javascript_to_python(
            "let size = numbers.length;"
        )
        self.assertIn("len(numbers)", result)

    def test_invalid_javascript(self):
        with self.assertRaises(SyntaxError):
            translate_javascript_to_python(
                "if (age >) {"
            )


if __name__ == "__main__":
    unittest.main()
