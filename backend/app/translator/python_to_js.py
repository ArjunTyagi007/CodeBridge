
import ast
import json


class PythonToJavaScript:

    def translate(self, source_code):
        try:
            tree = ast.parse(source_code)
            return self.generate_module(tree)
        except SyntaxError:
            raise

    def indent(self, code, level=1):
        prefix = "    " * level
        return "\n".join(
            prefix + line if line else ""
            for line in code.splitlines()
        )

    def generate_module(self, tree):
        output = []

        for node in tree.body:
            result = self.generate_statement(node)
            if result:
                output.append(result)

        return "\n\n".join(output)

    def generate_block(self, statements):
        output = []

        for statement in statements:
            result = self.generate_statement(statement)
            if result:
                output.append(result)

        if not output:
            return "     // Empty block"

        return self.indent("\n".join(output))

    # ---------------- STATEMENTS ----------------

    def generate_statement(self, node):

        if isinstance(node, ast.FunctionDef):
            arguments = ", ".join(
                arg.arg for arg in node.args.args
            )

            body = self.generate_block(node.body)

            return (
                f"function {node.name}({arguments}) {{\n"
                f"{body}\n"
                "}"
            )

        elif isinstance(node, ast.If):
            condition = self.generate_expression(node.test)
            body = self.generate_block(node.body)

            result = (
                f"if ({condition}) {{\n"
                f"{body}\n"
                "}"
            )

            if node.orelse:
                if (
                    len(node.orelse) == 1
                    and isinstance(node.orelse[0], ast.If)
                ):
                    result += " else " + self.generate_statement(
                        node.orelse[0]
                    )
                else:
                    else_body = self.generate_block(node.orelse)
                    result += (
                        " else {\n"
                        f"{else_body}\n"
                        "}"
                    )

            return result

        elif isinstance(node, ast.For):
            body = self.generate_block(node.body)
            target = self.generate_expression(node.target)

            if isinstance(node.iter, ast.Call):
                if (
                    isinstance(node.iter.func, ast.Name)
                    and node.iter.func.id == "range"
                ):
                    return self.generate_range_loop(
                        target, node.iter, body
                    )

            iterable = self.generate_expression(node.iter)

            return (
                f"for (const {target} of {iterable}) {{\n"
                f"{body}\n"
                "}"
            )

        elif isinstance(node, ast.While):
            condition = self.generate_expression(node.test)
            body = self.generate_block(node.body)

            return (
                f"while ({condition}) {{\n"
                f"{body}\n"
                "}"
            )

        elif isinstance(node, ast.Return):
            if node.value:
                return (
                    "return "
                    + self.generate_expression(node.value)
                    + ";"
                )
            return "return;"

        elif isinstance(node, ast.Assign):
            value = self.generate_expression(node.value)
            output = []

            for target in node.targets:
                output.append(
                    f"let {self.generate_expression(target)} = {value};"
                )

            return "\n".join(output)

        elif isinstance(node, ast.AnnAssign):
            if node.value is None:
                return ""

            target = self.generate_expression(node.target)
            value = self.generate_expression(node.value)

            return f"let {target} = {value};"

        elif isinstance(node, ast.AugAssign):
            target = self.generate_expression(node.target)
            value = self.generate_expression(node.value)
            operator = self.generate_operator(node.op)

            return f"{target} {operator}= {value};"

        elif isinstance(node, ast.Expr):
            return self.generate_expression(node.value) + ";"

        elif isinstance(node, ast.Break):
            return "break;"

        elif isinstance(node, ast.Continue):
            return "continue;"

        elif isinstance(node, ast.Pass):
            return ""

        else:
            raise NotImplementedError(
                f"Unsupported statement: {type(node).__name__}"
            )

    # ---------------- RANGE LOOPS ----------------

    def generate_range_loop(self, target, call, body):
        args = call.args

        if not 1 <= len(args) <= 3:
            raise NotImplementedError(
                "range() supports one, two, or three arguments"
            )

        if len(args) == 1:
            start = "0"
            stop = self.generate_expression(args[0])
            step = "1"

        elif len(args) == 2:
            start = self.generate_expression(args[0])
            stop = self.generate_expression(args[1])
            step = "1"

        else:
            start = self.generate_expression(args[0])
            stop = self.generate_expression(args[1])
            step = self.generate_expression(args[2])

        if step == "0":
            raise ValueError("range() step cannot be zero")

        if step.startswith("-"):
            condition = f"{target} > {stop}"
        else:
            condition = f"{target} < {stop}"

        return (
            f"for (let {target} = {start}; "
            f"{condition}; {target} += {step}) {{\n"
            f"{body}\n"
            "}"
        )

    # ---------------- EXPRESSIONS ----------------

    def generate_expression(self, node):

        if isinstance(node, ast.Name):
            return node.id

        elif isinstance(node, ast.Constant):
            if node.value is None:
                return "null"
            if node.value is True:
                return "true"
            if node.value is False:
                return "false"
            return json.dumps(node.value)

        elif isinstance(node, ast.BinOp):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)
            operator = self.generate_operator(node.op)

            if isinstance(node.op, ast.FloorDiv):
                return f"Math.floor({left} / {right})"

            return f"({left} {operator} {right})"

        elif isinstance(node, ast.UnaryOp):
            operator = {
                ast.Not: "!",
                ast.USub: "-",
                ast.UAdd: "+",
                ast.Invert: "~",
            }.get(type(node.op))

            if operator is None:
                raise NotImplementedError("Unsupported unary operator")

            return operator + self.generate_expression(node.operand)

        elif isinstance(node, ast.BoolOp):
            operator = {
                ast.And: "&&",
                ast.Or: "||",
            }.get(type(node.op))

            if operator is None:
                raise NotImplementedError("Unsupported logical operator")

            values = [
                self.generate_expression(value)
                for value in node.values
            ]

            return "(" + f" {operator} ".join(values) + ")"

        elif isinstance(node, ast.Compare):
            left = self.generate_expression(node.left)
            comparisons = []

            for operator, comparator in zip(
                node.ops, node.comparators
            ):
                right = self.generate_expression(comparator)

                if isinstance(operator, ast.In):
                    comparison = f"{right}.includes({left})"
                elif isinstance(operator, ast.NotIn):
                    comparison = f"!{right}.includes({left})"
                else:
                    symbol = self.generate_comparison(operator)
                    comparison = f"({left} {symbol} {right})"

                comparisons.append(comparison)
                left = right

            return " && ".join(comparisons)

        elif isinstance(node, ast.Call):
            function_name = self.generate_expression(node.func)

            arguments = ", ".join(
                self.generate_expression(arg)
                for arg in node.args
            )

            if function_name == "print":
                return f"console.log({arguments})"

            if function_name == "len":
                if len(node.args) != 1:
                    raise NotImplementedError(
                        "len() requires exactly one argument"
                    )
                return (
                    self.generate_expression(node.args[0])
                    + ".length"
                )

            return f"{function_name}({arguments})"

        elif isinstance(node, ast.List):
            elements = ", ".join(
                self.generate_expression(element)
                for element in node.elts
            )
            return f"[{elements}]"

        elif isinstance(node, ast.Tuple):
            elements = ", ".join(
                self.generate_expression(element)
                for element in node.elts
            )
            return f"[{elements}]"

        elif isinstance(node, ast.Dict):
            elements = []

            for key, value in zip(node.keys, node.values):
                if key is None:
                    raise NotImplementedError(
                        "Dictionary unpacking is not supported"
                    )

                elements.append(
                    f"{self.generate_expression(key)}: "
                    f"{self.generate_expression(value)}"
                )

            return "{" + ", ".join(elements) + "}"

        elif isinstance(node, ast.Subscript):
            value = self.generate_expression(node.value)
            index = self.generate_expression(node.slice)
            return f"{value}[{index}]"

        elif isinstance(node, ast.Attribute):
            value = self.generate_expression(node.value)
            return f"{value}.{node.attr}"

        elif isinstance(node, ast.IfExp):
            condition = self.generate_expression(node.test)
            body = self.generate_expression(node.body)
            alternative = self.generate_expression(node.orelse)

            return f"({condition} ? {body} : {alternative})"

        elif isinstance(node, ast.JoinedStr):
            parts = []

            for value in node.values:
                if isinstance(value, ast.Constant):
                    parts.append(str(value.value))
                elif isinstance(value, ast.FormattedValue):
                    parts.append(
                        "${"
                        + self.generate_expression(value.value)
                        + "}"
                    )

            return "`" + "".join(parts) + "`"

        elif isinstance(node, ast.Slice):
            raise NotImplementedError(
                "Python slicing is not supported yet"
            )

        else:
            raise NotImplementedError(
                f"Unsupported expression: {type(node).__name__}"
            )

    # ---------------- OPERATORS ----------------

    def generate_operator(self, operator):
        operators = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "//",
            ast.Mod: "%",
            ast.Pow: "**",
        }

        result = operators.get(type(operator))

        if result is None:
            raise NotImplementedError("Unsupported arithmetic operator")

        return result

    def generate_comparison(self, operator):
        operators = {
            ast.Eq: "===",
            ast.NotEq: "!==",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
            ast.Is: "===",
            ast.IsNot: "!==",
        }

        result = operators.get(type(operator))

        if result is None:
            raise NotImplementedError("Unsupported comparison operator")

        return result


def translate_python_to_js(source_code):
    translator = PythonToJavaScript()
    return translator.translate(source_code)
