
import esprima


# ==========================================================
# EXPRESSION TRANSLATOR
# ==========================================================

def translate_expression(node):
    """Convert a JavaScript expression into Python syntax."""

    if node is None:
        return ""

    node_type = node.get("type")

    # Variable names
    if node_type == "Identifier":
        name = node["name"]

        if name == "undefined":
            return "None"

        return name

    # Constants and literals
    if node_type == "Literal":
        value = node.get("value")

        if value is True:
            return "True"

        if value is False:
            return "False"

        if value is None:
            return "None"

        return repr(value)

    # Binary operators
    if node_type == "BinaryExpression":
        left = translate_expression(node["left"])
        right = translate_expression(node["right"])
        operator = node["operator"]

        operators = {
            "===": "==",
            "!==": "!=",
            "==": "==",
            "!=": "!=",
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%",
            "<": "<",
            ">": ">",
            "<=": "<=",
            ">=": ">=",
            "**": "**"
        }

        if operator not in operators:
            raise NotImplementedError(
                f"Unsupported binary operator: {operator}"
            )

        return f"({left} {operators[operator]} {right})"

    # Logical operators
    if node_type == "LogicalExpression":
        left = translate_expression(node["left"])
        right = translate_expression(node["right"])

        operators = {
            "&&": "and",
            "||": "or"
        }

        operator = node["operator"]

        if operator not in operators:
            raise NotImplementedError(
                f"Unsupported logical operator: {operator}"
            )

        return f"({left} {operators[operator]} {right})"

    # Unary operators
    if node_type == "UnaryExpression":
        argument = translate_expression(node["argument"])
        operator = node["operator"]

        if operator == "!":
            return f"(not {argument})"

        if operator == "+":
            return f"(+{argument})"

        if operator == "-":
            return f"(-{argument})"

        raise NotImplementedError(
            f"Unsupported unary operator: {operator}"
        )

    # Assignment expressions
    if node_type == "AssignmentExpression":
        left = translate_expression(node["left"])
        right = translate_expression(node["right"])
        operator = node["operator"]

        supported = {
            "=", "+=", "-=", "*=", "/=", "%="
        }

        if operator not in supported:
            raise NotImplementedError(
                f"Unsupported assignment operator: {operator}"
            )

        return f"{left} {operator} {right}"

    # Increment and decrement
    if node_type == "UpdateExpression":
        argument = translate_expression(node["argument"])

        if node["operator"] == "++":
            return f"{argument} += 1"

        if node["operator"] == "--":
            return f"{argument} -= 1"

        raise NotImplementedError(
            f"Unsupported update operator: {node['operator']}"
        )

    # Function calls
    if node_type == "CallExpression":
        callee = node["callee"]

        arguments = [
            translate_expression(arg)
            for arg in node["arguments"]
        ]

        # console.log() becomes print()
        if (
            callee.get("type") == "MemberExpression"
            and callee.get("object", {}).get("name") == "console"
            and callee.get("property", {}).get("name") == "log"
            and not callee.get("computed")
        ):
            return f"print({', '.join(arguments)})"

        function_name = translate_expression(callee)

        return f"{function_name}({', '.join(arguments)})"

    # Object properties and array indexing
    if node_type == "MemberExpression":
        obj = translate_expression(node["object"])
        prop_node = node["property"]

        # JavaScript array/string length
        if (
            not node.get("computed")
            and prop_node.get("name") == "length"
        ):
            return f"len({obj})"

        prop = translate_expression(prop_node)

        if node.get("computed"):
            return f"{obj}[{prop}]"

        return f"{obj}.{prop}"

    # Arrays
    if node_type == "ArrayExpression":
        elements = [
            translate_expression(item)
            for item in node["elements"]
        ]

        return f"[{', '.join(elements)}]"

    # Objects
    if node_type == "ObjectExpression":
        properties = []

        for prop in node["properties"]:

            if prop.get("computed"):
                raise NotImplementedError(
                    "Computed object properties are not supported yet."
                )

            key_node = prop["key"]

            if key_node["type"] == "Identifier":
                key = repr(key_node["name"])
            else:
                key = repr(key_node.get("value"))

            value = translate_expression(prop["value"])

            properties.append(f"{key}: {value}")

        return "{" + ", ".join(properties) + "}"

    # Ternary operator
    if node_type == "ConditionalExpression":
        condition = translate_expression(node["test"])
        consequent = translate_expression(node["consequent"])
        alternate = translate_expression(node["alternate"])

        return f"({consequent} if {condition} else {alternate})"

    raise NotImplementedError(
        f"Unsupported JavaScript expression: {node_type}"
    )


# ==========================================================
# FOR LOOP HELPERS
# ==========================================================

def translate_for_loop(node, indent=0):
    """Translate a standard numeric JavaScript for loop."""

    prefix = "    " * indent

    init = node.get("init")
    test = node.get("test")
    update = node.get("update")

    # Require a numeric-style loop with a declared variable.
    if not init or not test or not update:
        raise NotImplementedError(
            "Only standard numeric for loops are supported."
        )

    if init.get("type") != "VariableDeclaration":
        raise NotImplementedError(
            "For loops must initialize a variable using let, const, or var."
        )

    declarations = init["declarations"]

    if len(declarations) != 1:
        raise NotImplementedError(
            "For loops must declare exactly one variable."
        )

    declaration = declarations[0]
    variable = declaration["id"]["name"]

    start = translate_expression(declaration.get("init"))

    # Handle the loop condition.
    if test.get("type") != "BinaryExpression":
        raise NotImplementedError(
            "For loop condition must use a comparison operator."
        )

    if test["left"].get("name") != variable:
        raise NotImplementedError(
            "For loop condition must compare its loop variable."
        )

    operator = test["operator"]
    stop = translate_expression(test["right"])

    # Determine loop increment/decrement.
    step = None

    if update.get("type") == "UpdateExpression":
        if update["argument"].get("name") != variable:
            raise NotImplementedError("Invalid for loop update.")

        step = 1 if update["operator"] == "++" else -1

    elif update.get("type") == "AssignmentExpression":
        if update["left"].get("name") != variable:
            raise NotImplementedError("Invalid for loop update.")

        amount = update["right"]

        if amount.get("type") != "Literal":
            raise NotImplementedError(
                "For loop step must be a numeric literal."
            )

        if update["operator"] == "+=":
            step = amount["value"]

        elif update["operator"] == "-=":
            step = -amount["value"]

    if not isinstance(step, (int, float)) or step == 0:
        raise NotImplementedError("Invalid for loop step.")

    # Convert JavaScript comparison into Python range boundaries.
    if operator in ("<", "<=") and step > 0:
        range_stop = stop

        if operator == "<=":
            range_stop = f"({stop}) + 1"

    elif operator in (">", ">=") and step < 0:
        range_stop = stop

        if operator == ">=":
            range_stop = f"({stop}) - 1"

    else:
        raise NotImplementedError(
            "For loop condition and step direction are incompatible."
        )

    range_step = str(step)

    if step == 1:
        range_code = f"range({start}, {range_stop})"

    elif step == -1:
        range_code = f"range({start}, {range_stop}, -1)"

    else:
        range_code = (
            f"range({start}, {range_stop}, {range_step})"
        )

    lines = [
        f"{prefix}for {variable} in {range_code}:"
    ]

    lines.extend(
        translate_statement(node["body"], indent + 1)
    )

    return lines


# ==========================================================
# STATEMENT TRANSLATOR
# ==========================================================

def translate_statement(node, indent=0):
    """Convert a JavaScript statement into Python lines."""

    prefix = "    " * indent
    node_type = node.get("type")

    # Variable declarations
    if node_type == "VariableDeclaration":
        lines = []

        for declaration in node["declarations"]:
            name = translate_expression(declaration["id"])
            value = translate_expression(declaration.get("init"))

            if value:
                lines.append(f"{prefix}{name} = {value}")
            else:
                lines.append(f"{prefix}{name} = None")

        return lines

    # Expression statements
    if node_type == "ExpressionStatement":
        expression = translate_expression(node["expression"])

        return [f"{prefix}{expression}"]

    # If / else if / else
    if node_type == "IfStatement":
        condition = translate_expression(node["test"])

        lines = [f"{prefix}if {condition}:"]

        lines.extend(
            translate_statement(node["consequent"], indent + 1)
        )

        alternate = node.get("alternate")

        if alternate:

            if alternate["type"] == "IfStatement":
                alternate_lines = translate_statement(
                    alternate, indent
                )

                alternate_lines[0] = (
                    prefix + "el" + alternate_lines[0][len(prefix):]
                    if alternate_lines[0].startswith(prefix + "if ")
                    else alternate_lines[0]
                )

                lines.extend(alternate_lines)

            else:
                lines.append(f"{prefix}else:")

                lines.extend(
                    translate_statement(alternate, indent + 1)
                )

        return lines

    # Blocks
    if node_type == "BlockStatement":
        lines = []

        for statement in node["body"]:
            lines.extend(
                translate_statement(statement, indent)
            )

        return lines or [f"{prefix}pass"]

    # While loops
    if node_type == "WhileStatement":
        condition = translate_expression(node["test"])

        lines = [f"{prefix}while {condition}:"]

        lines.extend(
            translate_statement(node["body"], indent + 1)
        )

        return lines

    # Standard for loops
    if node_type == "ForStatement":
        return translate_for_loop(node, indent)

    # Function declarations
    if node_type == "FunctionDeclaration":
        name = node["id"]["name"]

        parameters = [
            translate_expression(param)
            for param in node["params"]
        ]

        lines = [
            f"{prefix}def {name}({', '.join(parameters)}):"
        ]

        lines.extend(
            translate_statement(node["body"], indent + 1)
        )

        return lines

    # Return
    if node_type == "ReturnStatement":
        argument = translate_expression(node.get("argument"))

        if argument:
            return [f"{prefix}return {argument}"]

        return [f"{prefix}return"]

    # Break
    if node_type == "BreakStatement":
        return [f"{prefix}break"]

    # Continue
    if node_type == "ContinueStatement":
        return [f"{prefix}continue"]

    # Empty statements
    if node_type == "EmptyStatement":
        return []

    raise NotImplementedError(
        f"Unsupported JavaScript statement: {node_type}"
    )


# ==========================================================
# MAIN TRANSLATOR FUNCTION
# ==========================================================

def translate_javascript_to_python(code):
    """
    Parse JavaScript and translate supported statements
    into Python code.
    """

    if not isinstance(code, str) or not code.strip():
        raise ValueError("JavaScript code cannot be empty.")

    try:
        syntax_tree = esprima.parseScript(code)

    except Exception as error:
        raise SyntaxError(
            f"Invalid JavaScript syntax: {error}"
        ) from error

    output = []

    try:
        for statement in syntax_tree.toDict()["body"]:
            output.extend(
                translate_statement(statement)
            )

    except NotImplementedError:
        raise

    if not output:
        return "# No translatable statements found"

    return "\n".join(output)
