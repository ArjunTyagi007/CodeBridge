
import ast
import json


class PythonToJavaScript:

    def translate(self, source_code):
        tree = ast.parse(source_code)
        return self.generate_module(tree)

    def generate_module(self, tree):
        output = []

        for node in tree.body:
            output.append(self.generate_statement(node))

        return "\n\n".join(output)

    def generate_statement(self, node):

        if isinstance(node, ast.FunctionDef):
            arguments = ", ".join(
                arg.arg for arg in node.args.args
            )

            body = []

            for statement in node.body:
                body.append(
                    "    " + self.generate_statement(statement)
                )

            return (
                f"function {node.name}({arguments}) {{\n"
                + "\n".join(body)
                + "\n}"
            )

        elif isinstance(node, ast.Expr):
            return self.generate_expression(node.value) + ";"

        elif isinstance(node, ast.Return):
            if node.value:
                return "return " + self.generate_expression(node.value) + ";"
            return "return;"

        elif isinstance(node, ast.Assign):
            value = self.generate_expression(node.value)
            targets = ", ".join(
                self.generate_expression(target)
                for target in node.targets
            )
            return f"let {targets} = {value};"

        elif isinstance(node, ast.Pass):
            return ""

        else:
            raise NotImplementedError(
                f"Unsupported Python statement: {type(node).__name__}"
            )

    def generate_expression(self, node):

        if isinstance(node, ast.Call):
            function_name = self.generate_expression(node.func)

            arguments = ", ".join(
                self.generate_expression(arg)
                for arg in node.args
            )

            if function_name == "print":
                return f"console.log({arguments})"

            return f"{function_name}({arguments})"

        elif isinstance(node, ast.Name):
            return node.id

        elif isinstance(node, ast.Constant):
            if node.value is None:
                return "null"
            if node.value is True:
                return "true"
            if node.value is False:
                return "false"
            if isinstance(node.value, str):
                return json.dumps(node.value)
            return str(node.value)

        elif isinstance(node, ast.BinOp):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)

            operators = {
                ast.Add: "+",
                ast.Sub: "-",
                ast.Mult: "*",
                ast.Div: "/",
                ast.Mod: "%",
            }

            operator = operators.get(type(node.op))

            if operator is None:
                raise NotImplementedError("Unsupported operator")

            return f"({left} {operator} {right})"

        else:
            raise NotImplementedError(
                f"Unsupported Python expression: {type(node).__name__}"
            )


def translate_python_to_js(source_code):
    translator = PythonToJavaScript()
    return translator.translate(source_code)
