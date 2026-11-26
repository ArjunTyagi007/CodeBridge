
import ast
import re
import operator


def infer_type(value):
    """Infer the type of a simple literal value."""

    value = value.strip()

    if re.fullmatch(r"-?\d+", value):
        return "integer (int)"

    if re.fullmatch(r"-?\d+\.\d+", value):
        return "float"

    if value in ("True", "False", "true", "false"):
        return "boolean (bool)"

    if value.startswith(("'", '"')):
        return "string (str)"

    if value.startswith("["):
        return "list"

    if value.startswith("{"):
        return "dictionary (dict)"

    if value.startswith("("):
        return "tuple"

    return "unknown or expression"


def evaluate_condition(condition, variables):
    """Evaluate simple comparison conditions safely."""

    operators = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne
    }

    match = re.fullmatch(
        r"\s*(\w+|\d+(?:\.\d+)?)\s*(>=|<=|==|!=|>|<)\s*(\w+|\d+(?:\.\d+)?)\s*",
        condition
    )

    if not match:
        return None

    left, symbol, right = match.groups()

    def get_value(item):
        if item in variables:
            return variables[item]

        try:
            return ast.literal_eval(item)
        except (ValueError, SyntaxError):
            return None

    left_value = get_value(left)
    right_value = get_value(right)

    if left_value is None or right_value is None:
        return None

    try:
        return operators[symbol](left_value, right_value)
    except (TypeError, ValueError):
        return None


def explain_code(
    original_code: str,
    translated_code: str,
    source_language: str,
    target_language: str
) -> dict:

    if not original_code.strip():
        raise ValueError("Please provide code to explain.")

    source_language = source_language.lower()
    target_language = target_language.lower()

    explanations = []
    variables = {}
    functions = {}

    lines = original_code.splitlines()

    # Detect variable assignments.
    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        match = re.match(
            r"^(?:(?:let|const|var)\s+)?([a-zA-Z_]\w*)\s*=\s*(?!=)(.+?)\s*;?$",
            stripped
        )

        if match:
            name, value = match.groups()

            if value.strip() not in ("",):
                try:
                    variables[name] = ast.literal_eval(value.rstrip(";"))
                except (ValueError, SyntaxError):
                    pass

    # Detect function definitions.
    for line in lines:
        stripped = line.strip()

        match = re.match(
            r"^(?:def|function)\s+([a-zA-Z_]\w*)\s*\((.*?)\)",
            stripped
        )

        if match:
            name, parameters = match.groups()
            parameter_list = [
                p.strip()
                for p in parameters.split(",")
                if p.strip()
            ]
            functions[name] = parameter_list

    # Explain each non-empty source line.
    for line_number, line in enumerate(lines, start=1):

        code = line.strip()

        if not code:
            continue

        explanation = (
            "This statement is part of the program's execution."
        )

        # Comments
        if code.startswith(("#", "//")):
            explanation = (
                "This is a comment. It provides information to readers "
                "and is not executed."
            )

        # Function definitions
        elif re.match(r"^(def|function)\s+", code):
            match = re.match(
                r"^(?:def|function)\s+(\w+)\s*\((.*?)\)",
                code
            )

            if match:
                name, parameters = match.groups()
                explanation = (
                    f"This defines the function '{name}'. "
                    f"Its parameters are: {parameters or 'none'}. "
                    "Functions allow code to be reused."
                )

        # Return statements
        elif re.match(r"^return\b", code):
            value = code[6:].strip()

            explanation = (
                f"This returns '{value}' from the current function."
                if value else
                "This returns control from the current function."
            )

        # Conditions
        elif re.match(r"^(if|elif|else)\b", code):
            match = re.match(r"^(if|elif)\s+(.+?):?$", code)

            if match:
                condition = match.group(2)
                result = evaluate_condition(condition, variables)

                explanation = (
                    f"This checks the condition '{condition}'. "
                )

                if result is True:
                    explanation += "The condition evaluates to True."
                elif result is False:
                    explanation += "The condition evaluates to False."
                else:
                    explanation += (
                        "The condition determines which code block runs."
                    )
            else:
                explanation = (
                    "This is an else branch. It runs when the preceding "
                    "conditions are not satisfied."
                )

        # Loops
        elif re.match(r"^(for|while)\b", code):
            explanation = (
                "This is a loop. It repeatedly executes a block of code "
                "according to its iteration or condition."
            )

        # Variable declarations and assignments
        elif re.match(
            r"^(?:(?:let|const|var)\s+)?[a-zA-Z_]\w*\s*=\s*(?!=)",
            code
        ):
            match = re.match(
                r"^(?:(?:let|const|var)\s+)?([a-zA-Z_]\w*)\s*=\s*(.+?);?$",
                code
            )

            if match:
                name, value = match.groups()
                value = value.rstrip(";").strip()
                data_type = infer_type(value)

                explanation = (
                    f"This assigns a value to the variable '{name}'. "
                    f"The assigned expression is '{value}'. "
                    f"Its inferred data type is {data_type}."
                )

        # Output statements
        elif re.match(r"^(print|console\.log)\s*\(", code):
            explanation = (
                "This displays information on the screen. "
                "It sends the supplied value to the program output."
            )

        # Function calls
        elif re.match(r"^([a-zA-Z_]\w*)\s*\(", code):
            match = re.match(
                r"^([a-zA-Z_]\w*)\s*\((.*?)\)",
                code
            )

            if match:
                name, arguments = match.groups()

                if name in functions:
                    explanation = (
                        f"This calls the function '{name}' "
                        f"with arguments: {arguments or 'none'}. "
                        f"The function has parameters: "
                        f"{', '.join(functions[name]) or 'none'}."
                    )
                else:
                    explanation = (
                        f"This calls the function '{name}' "
                        f"with arguments: {arguments or 'none'}."
                    )

        # Break and continue
        elif code.startswith("break"):
            explanation = "This immediately stops the current loop."

        elif code.startswith("continue"):
            explanation = (
                "This skips the current loop iteration and moves "
                "to the next one."
            )

        explanations.append({
            "line": line_number,
            "code": code,
            "explanation": explanation
        })

    # Compare common language constructs.
    comparison = []

    language_pairs = {
        ("python", "javascript"): [
            ("print()", "console.log()"),
            ("def", "function"),
            ("None", "null"),
            ("True / False", "true / false"),
            ("elif", "else if"),
            ("Indentation", "Curly braces {}")
        ],
        ("javascript", "python"): [
            ("console.log()", "print()"),
            ("function", "def"),
            ("null", "None"),
            ("true / false", "True / False"),
            ("else if", "elif"),
            ("Curly braces {}", "Indentation")
        ]
    }

    comparison_pairs = language_pairs.get(
        (source_language, target_language),
        []
    )

    for source_construct, target_construct in comparison_pairs:
        comparison.append({
            "source_construct": source_construct,
            "target_construct": target_construct
        })

    return {
        "method": "rule_based",
        "language": source_language,
        "target_language": target_language,
        "summary": (
            f"Analyzed {len(explanations)} non-empty lines of "
            f"{source_language} code. "
            f"Detected {len(variables)} variable assignments "
            f"and {len(functions)} function definitions."
        ),
        "variables": [
            {
                "name": name,
                "value": str(value),
                "data_type": infer_type(repr(value))
            }
            for name, value in variables.items()
        ],
        "functions": [
            {
                "name": name,
                "parameters": parameters
            }
            for name, parameters in functions.items()
        ],
        "explanations": explanations,
        "translation_comparison": comparison
    }
