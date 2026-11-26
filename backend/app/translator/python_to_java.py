
import ast


class PythonToJava:

    def __init__(self):
        self.variables = {}
        self.indent_level = 0

    def indent(self):
        return "    " * self.indent_level

    def infer_type(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "boolean"
            if isinstance(node.value, int):
                return "int"
            if isinstance(node.value, float):
                return "double"
            if isinstance(node.value, str):
                return "String"

        if isinstance(node, (ast.List, ast.Tuple)):
            return "List<Object>"

        if isinstance(node, ast.Dict):
            return "Map<Object, Object>"

        if isinstance(node, (ast.Compare, ast.BoolOp)):
            return "boolean"

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return "boolean"

        if isinstance(node, ast.BinOp):
            left_type = self.infer_type(node.left)
            right_type = self.infer_type(node.right)

            if "String" in (left_type, right_type):
                return "String"

            if "double" in (left_type, right_type):
                return "double"

            return "int"

        return "Object"

    def expression(self, node):

        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Constant):
            if node.value is True:
                return "true"
            if node.value is False:
                return "false"
            if node.value is None:
                return "null"
            if isinstance(node.value, str):
                return '"' + node.value.replace("\\", "\\\\").replace('"', '\\"') + '"'
            return str(node.value)

        if isinstance(node, ast.BinOp):
            left = self.expression(node.left)
            right = self.expression(node.right)

            if isinstance(node.op, ast.Pow):
                return f"Math.pow({left}, {right})"

            operator = self.binary_operator(node.op)
            return f"({left} {operator} {right})"

        if isinstance(node, ast.UnaryOp):
            operand = self.expression(node.operand)

            if isinstance(node.op, ast.Not):
                return f"(!{operand})"

            if isinstance(node.op, ast.USub):
                return f"(-{operand})"

            if isinstance(node.op, ast.UAdd):
                return f"(+{operand})"

        if isinstance(node, ast.BoolOp):
            operator = "&&" if isinstance(node.op, ast.And) else "||"
            values = [
                self.expression(value)
                for value in node.values
            ]
            return f"({f' {operator} '.join(values)})"

        if isinstance(node, ast.Compare):
            left = self.expression(node.left)
            right = self.expression(node.comparators[0])
            operator = self.comparison_operator(node.ops[0])

            return f"{left} {operator} {right}"

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id == "print":
                    args = ", ".join(
                        self.expression(arg)
                        for arg in node.args
                    )
                    return f"System.out.println({args})"

                if node.func.id == "len":
                    value = self.expression(node.args[0])
                    return f"{value}.size()"

                args = ", ".join(
                    self.expression(arg)
                    for arg in node.args
                )
                return f"{node.func.id}({args})"

        if isinstance(node, (ast.List, ast.Tuple)):
            values = ", ".join(
                self.expression(item)
                for item in node.elts
            )
            return (
                "new ArrayList<Object>("
                f"Arrays.<Object>asList({values}))"
            )

        if isinstance(node, ast.Dict):
            if not node.keys:
                return "new HashMap<Object, Object>()"

            pairs = []

            for key, value in zip(node.keys, node.values):
                pairs.append(
                    f"{self.expression(key)}, "
                    f"{self.expression(value)}"
                )

            return (
                "new HashMap<Object, Object>("
                f"Map.of({', '.join(pairs)}))"
            )

        if isinstance(node, ast.Subscript):
            value = self.expression(node.value)
            index = self.expression(node.slice)
            return f"{value}.get({index})"

        if isinstance(node, ast.Attribute):
            return (
                f"{self.expression(node.value)}."
                f"{node.attr}"
            )

        if isinstance(node, ast.IfExp):
            condition = self.expression(node.test)
            body = self.expression(node.body)
            other = self.expression(node.orelse)

            return f"({condition} ? {body} : {other})"

        raise NotImplementedError(
            f"Unsupported expression: {type(node).__name__}"
        )

    def binary_operator(self, operator):
        operators = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "/",
            ast.Mod: "%",
        }

        for operator_type, symbol in operators.items():
            if isinstance(operator, operator_type):
                return symbol

        raise NotImplementedError(
            f"Unsupported operator: {type(operator).__name__}"
        )

    def comparison_operator(self, operator):
        operators = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
        }

        for operator_type, symbol in operators.items():
            if isinstance(operator, operator_type):
                return symbol

        raise NotImplementedError(
            f"Unsupported comparison: {type(operator).__name__}"
        )

    def generate_block(self, statements):
        self.indent_level += 1

        result = ""

        for statement in statements:
            result += self.generate_statement(statement)

        self.indent_level -= 1

        return result

    def generate_statement(self, node):

        if isinstance(node, ast.Assign):
            value = self.expression(node.value)
            lines = ""

            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id

                    if name in self.variables:
                        lines += (
                            f"{self.indent()}{name} = {value};\n"
                        )
                    else:
                        variable_type = self.infer_type(node.value)

                        self.variables[name] = variable_type

                        lines += (
                            f"{self.indent()}{variable_type} "
                            f"{name} = {value};\n"
                        )

            return lines

        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                name = node.target.id
                value = (
                    self.expression(node.value)
                    if node.value is not None
                    else "null"
                )

                variable_type = self.infer_type(node.value)

                self.variables[name] = variable_type

                return (
                    f"{self.indent()}{variable_type} "
                    f"{name} = {value};\n"
                )

        if isinstance(node, ast.AugAssign):
            name = self.expression(node.target)
            value = self.expression(node.value)
            operator = self.binary_operator(node.op)

            return (
                f"{self.indent()}{name} "
                f"{operator}= {value};\n"
            )

        if isinstance(node, ast.Expr):
            return (
                f"{self.indent()}"
                f"{self.expression(node.value)};\n"
            )

        if isinstance(node, ast.If):
            condition = self.expression(node.test)

            result = (
                f"{self.indent()}if ({condition}) {{\n"
            )

            result += self.generate_block(node.body)

            if node.orelse:
                if (
                    len(node.orelse) == 1
                    and isinstance(node.orelse[0], ast.If)
                ):
                    result += (
                        f"{self.indent()}}} else "
                    )
                    nested = self.generate_statement(
                        node.orelse[0]
                    )
                    result += nested.lstrip()
                    return result

                result += f"{self.indent()}}} else {{\n"
                result += self.generate_block(node.orelse)

            result += f"{self.indent()}}}\n"

            return result

        if isinstance(node, ast.For):
            if (
                isinstance(node.target, ast.Name)
                and isinstance(node.iter, ast.Call)
                and isinstance(node.iter.func, ast.Name)
                and node.iter.func.id == "range"
            ):
                args = node.iter.args

                if len(args) == 1:
                    start = "0"
                    stop = self.expression(args[0])
                    step = "1"

                elif len(args) == 2:
                    start = self.expression(args[0])
                    stop = self.expression(args[1])
                    step = "1"

                elif len(args) == 3:
                    start = self.expression(args[0])
                    stop = self.expression(args[1])
                    step = self.expression(args[2])

                else:
                    raise NotImplementedError(
                        "Unsupported range arguments"
                    )

                variable = node.target.id

                if step == "1":
                    update = f"{variable}++"
                elif step == "-1":
                    update = f"{variable}--"
                else:
                    update = f"{variable} += {step}"

                self.variables[variable] = "int"

                result = (
                    f"{self.indent()}for (int {variable} = "
                    f"{start}; {variable} < {stop}; "
                    f"{update}) {{\n"
                )

                result += self.generate_block(node.body)
                result += f"{self.indent()}}}\n"

                return result

        if isinstance(node, ast.While):
            condition = self.expression(node.test)

            result = (
                f"{self.indent()}while ({condition}) {{\n"
            )

            result += self.generate_block(node.body)
            result += f"{self.indent()}}}\n"

            return result

        if isinstance(node, ast.Return):
            if node.value is None:
                return f"{self.indent()}return;\n"

            return (
                f"{self.indent()}return "
                f"{self.expression(node.value)};\n"
            )

        if isinstance(node, ast.Break):
            return f"{self.indent()}break;\n"

        if isinstance(node, ast.Continue):
            return f"{self.indent()}continue;\n"

        if isinstance(node, ast.Pass):
            return ""

        raise NotImplementedError(
            f"Unsupported statement: {type(node).__name__}"
        )

    def generate_function(self, node):
        previous_variables = self.variables.copy()
        self.variables = {}

        parameters = ", ".join(
            f"Object {arg.arg}"
            for arg in node.args.args
        )

        self.indent_level = 1

        result = (
            f"    public static Object {node.name}"
            f"({parameters}) {{\n"
        )

        result += self.generate_block(node.body)
        result += "    }\n\n"

        self.variables = previous_variables
        self.indent_level = 0

        return result

    def translate(self, source_code):
        tree = ast.parse(source_code)

        functions = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
        ]

        statements = [
            node for node in tree.body
            if not isinstance(node, ast.FunctionDef)
        ]

        function_code = ""

        for function in functions:
            function_code += self.generate_function(function)

        self.variables = {}
        self.indent_level = 2

        main_code = self.generate_block(statements)

        return (
            "import java.util.*;\n\n"
            "public class Main {\n"
            f"{function_code}"
            "    public static void main(String[] args) {\n"
            f"{main_code}"
            "    }\n"
            "}\n"
        )


def translate_python_to_java(source_code):
    translator = PythonToJava()
    return translator.translate(source_code)
