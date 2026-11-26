
import unittest

from app.translator.java_to_python import translate_java_to_python


class TestJavaToPython(unittest.TestCase):

    def translate(self, code):
        return translate_java_to_python(code)

    def test_integer_assignment(self):
        result = self.translate("int age = 20;")
        self.assertIn("age = 20", result)

    def test_string_assignment(self):
        result = self.translate('String name = "John";')
        self.assertIn('name = "John"', result)

    def test_boolean_assignment(self):
        result = self.translate("boolean isActive = true;")
        self.assertIn("isActive = True", result)

    def test_if_else(self):
        code = """
public class Main {
    public static void main(String[] args) {
        int age = 20;
        if (age >= 18) {
            System.out.println("Adult");
        } else {
            System.out.println("Minor");
        }
    }
}
"""
        result = self.translate(code)

        self.assertIn("if age >= 18:", result)
        self.assertIn('print("Adult")', result)
        self.assertIn('print("Minor")', result)
        self.assertIn("else:", result)

    def test_for_loop(self):
        code = """
public class Main {
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {
            System.out.println(i);
        }
    }
}
"""
        result = self.translate(code)

        self.assertIn("for i in range(0, 5):", result)
        self.assertIn("print(i)", result)

    def test_while_loop(self):
        code = """
public class Main {
    public static void main(String[] args) {
        int count = 0;
        while (count < 5) {
            count++;
        }
    }
}
"""
        result = self.translate(code)

        self.assertIn("while count < 5:", result)
        self.assertIn("count += 1", result)

    def test_function(self):
        code = """
public class Main {
    public static int add(int a, int b) {
        return a + b;
    }
}
"""
        result = self.translate(code)

        self.assertIn("def add(a, b):", result)
        self.assertIn("return a + b", result)

    def test_print_statement(self):
        code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        result = self.translate(code)

        self.assertIn('print("Hello")', result)

    def test_comparison_operators(self):
        code = """
public class Main {
    public static void main(String[] args) {
        if (age != 18) {
            System.out.println("Different");
        }
    }
}
"""
        result = self.translate(code)

        self.assertIn("age != 18", result)

    def test_invalid_java(self):
        with self.assertRaises(SyntaxError):
            self.translate("if (age >) {")


if __name__ == "__main__":
    unittest.main(verbosity=2)
