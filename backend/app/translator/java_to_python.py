
import re


TOKEN_PATTERN = re.compile(
    r'"(?:\\.|[^"\\])*"|'
    r"'(?:\\.|[^'\\])*'|"
    r'//[^\n]*|'
    r'/\*[\s\S]*?\*/|'
    r'[A-Za-z_]\w*|'
    r'\d+(?:\.\d+)?|'
    r'\+\+|--|'
    r'\+=|-=|\*=|/=|'
    r'==|!=|<=|>=|&&|\|\||'
    r'[{}()\[\];,.=+\-*/%<>!]'
)


class JavaToPython:

    def __init__(self, source):
        self.source = source
        self.tokens = self.tokenize(source)

    # ---------------- TOKENIZER ----------------

    def tokenize(self, source):
        tokens = []
        position = 0

        for match in TOKEN_PATTERN.finditer(source):
            skipped = source[position:match.start()]

            if skipped.strip():
                raise SyntaxError(
                    f"Invalid Java syntax near: {skipped.strip()}"
                )

            token = match.group()
            position = match.end()

            if token.startswith("//") or token.startswith("/*"):
                continue

            tokens.append(token)

        if source[position:].strip():
            raise SyntaxError(
                f"Invalid Java syntax near: {source[position:].strip()}"
            )

        return tokens

    # ---------------- TOKEN FORMATTING ----------------

    def tokens_to_text(self, tokens):
        text = " ".join(tokens)

        text = re.sub(r'\s*\.\s*', '.', text)
        text = re.sub(r'\s*\(\s*', '(', text)
        text = re.sub(r'\s*\)', ')', text)
        text = re.sub(r'\s*\[\s*', '[', text)
        text = re.sub(r'\s*\]', ']', text)
        text = re.sub(r'\s*,\s*', ', ', text)

        text = re.sub(
            r'\s*(==|!=|<=|>=|\+=|-=|\*=|/=|&&|\|\||[=+\-*/%<>])\s*',
            r' \1 ',
            text
        )

        return re.sub(r'\s+', ' ', text).strip()

    # ---------------- EXPRESSIONS ----------------

    def translate_expression(self, expression):
        expression = expression.strip()

        expression = re.sub(r'\btrue\b', 'True', expression)
        expression = re.sub(r'\bfalse\b', 'False', expression)
        expression = re.sub(r'\bnull\b', 'None', expression)

        expression = re.sub(
            r'System\s*\.\s*out\s*\.\s*println\s*\(',
            'print(',
            expression
        )

        expression = re.sub(
            r'System\s*\.\s*out\s*\.\s*print\s*\(',
            'print(',
            expression
        )

        expression = expression.replace("&&", " and ")
        expression = expression.replace("||", " or ")

        expression = re.sub(r'!(?!=)', 'not ', expression)

        return expression.strip()

    # ---------------- PARENTHESES AND BLOCKS ----------------

    def read_parentheses(self, tokens, start):
        if start >= len(tokens) or tokens[start] != "(":
            raise SyntaxError("Expected '('")

        depth = 0
        content = []

        for index in range(start, len(tokens)):
            token = tokens[index]

            if token == "(":
                depth += 1

                if depth > 1:
                    content.append(token)

            elif token == ")":
                depth -= 1

                if depth == 0:
                    return self.tokens_to_text(content), index + 1

                content.append(token)

            else:
                content.append(token)

        raise SyntaxError("Unmatched parentheses")

    def read_block(self, tokens, start):
        if start >= len(tokens) or tokens[start] != "{":
            raise SyntaxError("Expected '{'")

        body, next_index = self.translate_block(
            tokens,
            start + 1,
            stop_at_brace=True
        )

        return body, next_index

    def read_statement(self, tokens, start):
        result = []
        parentheses = 0
        brackets = 0

        for index in range(start, len(tokens)):
            token = tokens[index]

            if token == "(":
                parentheses += 1
            elif token == ")":
                parentheses -= 1
            elif token == "[":
                brackets += 1
            elif token == "]":
                brackets -= 1

            if parentheses < 0 or brackets < 0:
                raise SyntaxError("Unmatched closing bracket")

            if (
                token == ";"
                and parentheses == 0
                and brackets == 0
            ):
                if not result:
                    return "", index + 1

                return self.tokens_to_text(result), index + 1

            result.append(token)

        if result:
            raise SyntaxError("Missing semicolon")

        return "", len(tokens)

    def indent_lines(self, lines):
        if not lines:
            return ["    pass"]

        return ["    " + line for line in lines]

    # ---------------- ASSIGNMENTS ----------------

    def translate_assignment(self, statement):
        statement = statement.strip()

        if not statement:
            return []

        statement = re.sub(
            r'^(int|long|double|float|boolean|String|char|var)\s+',
            '',
            statement
        )

        if re.match(r'^\w+\s*=\s*$', statement):
            raise SyntaxError("Assignment is missing a value")

        increment = re.match(
            r'^(\w+)\s*(\+=|-=|\*=|/=)\s*(.+)$',
            statement
        )

        if increment:
            variable, operator, value = increment.groups()

            return [
                f"{variable} {operator} "
                f"{self.translate_expression(value)}"
            ]

        assignment = re.match(
            r'^(\w+)\s*=\s*(.+)$',
            statement
        )

        if assignment:
            variable, value = assignment.groups()

            return [
                f"{variable} = "
                f"{self.translate_expression(value)}"
            ]

        return [self.translate_expression(statement)]

    # ---------------- BLOCK TRANSLATOR ----------------

    def translate_block(self, tokens, start=0, stop_at_brace=False):
        result = []
        index = start

        while index < len(tokens):
            token = tokens[index]

            if token == "}":
                if stop_at_brace:
                    return result, index + 1

                raise SyntaxError("Unexpected closing brace")

            if token == ";":
                index += 1
                continue

            # IF / ELSE
            if token == "if":
                index += 1

                condition, index = self.read_parentheses(
                    tokens, index
                )

                body, index = self.read_block(tokens, index)

                result.append(
                    f"if {self.translate_expression(condition)}:"
                )

                result.extend(self.indent_lines(body))

                if index < len(tokens) and tokens[index] == "else":
                    index += 1

                    if index < len(tokens) and tokens[index] == "if":
                        nested, index = self.translate_block(
                            tokens, index
                        )
                        result.extend(nested)
                        continue

                    else_body, index = self.read_block(
                        tokens, index
                    )

                    result.append("else:")
                    result.extend(self.indent_lines(else_body))

                continue

            # WHILE
            if token == "while":
                index += 1

                condition, index = self.read_parentheses(
                    tokens, index
                )

                body, index = self.read_block(tokens, index)

                result.append(
                    f"while {self.translate_expression(condition)}:"
                )

                result.extend(self.indent_lines(body))
                continue

            # FOR
            if token == "for":
                index += 1

                header, index = self.read_parentheses(
                    tokens, index
                )

                parts = header.split(";")

                if len(parts) != 3:
                    raise NotImplementedError(
                        "Only traditional Java for loops are supported"
                    )

                initialization = parts[0].strip()
                condition = parts[1].strip()
                update = re.sub(r'\s+', '', parts[2])

                initialization = re.sub(
                    r'^(int|long|double|float|var)\s+',
                    '',
                    initialization
                )

                match = re.match(
                    r'(\w+)\s*=\s*(.+)',
                    initialization
                )

                if not match:
                    raise NotImplementedError(
                        "Unsupported for-loop initialization"
                    )

                variable, start_value = match.groups()

                condition_match = re.match(
                    rf'{re.escape(variable)}\s*<\s*(.+)',
                    condition
                )

                if not condition_match:
                    raise NotImplementedError(
                        "Only less-than for-loop conditions are supported"
                    )

                stop_value = condition_match.group(1)

                if update == f"{variable}++":
                    step = "1"
                elif update == f"{variable}--":
                    step = "-1"
                elif update.startswith(variable + "+="):
                    step = update.split("+=", 1)[1]
                elif update.startswith(variable + "-="):
                    step = "-" + update.split("-=", 1)[1]
                else:
                    raise NotImplementedError(
                        "Unsupported for-loop update"
                    )

                body, index = self.read_block(tokens, index)

                if step == "1":
                    range_expression = (
                        f"range({start_value}, {stop_value})"
                    )
                else:
                    range_expression = (
                        f"range({start_value}, {stop_value}, {step})"
                    )

                result.append(
                    f"for {variable} in {range_expression}:"
                )

                result.extend(self.indent_lines(body))
                continue

            # VARIABLE DECLARATIONS
            if token in (
                "int", "long", "double", "float",
                "boolean", "String", "char", "var"
            ):
                declaration, index = self.read_statement(
                    tokens, index
                )

                result.extend(
                    self.translate_assignment(declaration)
                )
                continue

            # PRINT
            if (
                token == "System"
                and index + 3 < len(tokens)
                and tokens[index + 1:index + 4]
                == [".", "out", "."]
            ):
                statement, index = self.read_statement(
                    tokens, index
                )

                result.append(
                    self.translate_expression(statement)
                )
                continue

            # RETURN
            if token == "return":
                statement, index = self.read_statement(
                    tokens, index
                )

                expression = statement[6:].strip()

                if expression:
                    result.append(
                        "return " +
                        self.translate_expression(expression)
                    )
                else:
                    result.append("return")

                continue

            # INCREMENT / DECREMENT
            if (
                index + 1 < len(tokens)
                and tokens[index + 1] in ("++", "--")
            ):
                variable = token
                operator = tokens[index + 1]

                result.append(
                    f"{variable} += 1"
                    if operator == "++"
                    else f"{variable} -= 1"
                )

                index += 2

                if index < len(tokens) and tokens[index] == ";":
                    index += 1

                continue

            # BREAK / CONTINUE
            if token in ("break", "continue"):
                result.append(token)
                index += 1

                if index < len(tokens) and tokens[index] == ";":
                    index += 1

                continue

            # OTHER STATEMENTS
            statement, index = self.read_statement(tokens, index)

            if statement:
                result.extend(
                    self.translate_assignment(statement)
                )

        if stop_at_brace:
            raise SyntaxError("Missing closing brace")

        return result, index

    # ---------------- METHOD EXTRACTION ----------------

    def extract_methods(self):
        methods = []
        main_body = None

        pattern = re.compile(
            r'(?:public\s+|private\s+|protected\s+)?'
            r'(?:static\s+)?'
            r'(?:final\s+)?'
            r'(?:void|int|double|float|long|boolean|String|char|'
            r'[A-Za-z_]\w*(?:<[^>]+>)?)\s+'
            r'([A-Za-z_]\w*)\s*'
            r'\(([^)]*)\)\s*\{'
        )

        for match in pattern.finditer(self.source):
            method_name = match.group(1)
            parameters_text = match.group(2)

            open_brace = match.end() - 1
            depth = 1
            close_brace = -1

            in_string = None
            escaped = False

            for index in range(open_brace + 1, len(self.source)):
                char = self.source[index]

                if in_string:
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == in_string:
                        in_string = None

                    continue

                if char in ('"', "'"):
                    in_string = char
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1

                    if depth == 0:
                        close_brace = index
                        break

            if close_brace == -1:
                raise SyntaxError("Unmatched method brace")

            body = self.source[open_brace + 1:close_brace]

            parameters = []

            for parameter in parameters_text.split(","):
                parameter = parameter.strip()

                if parameter:
                    parts = parameter.split()
                    parameters.append(parts[-1])

            if method_name == "main":
                main_body = body
            else:
                methods.append((method_name, parameters, body))

        return methods, main_body

    # ---------------- FINAL TRANSLATION ----------------

    def translate(self):
        methods, main_body = self.extract_methods()

        output = []

        # Translate methods other than main.
        for name, parameters, body in methods:
            tokens = self.tokenize(body)
            translated, _ = self.translate_block(tokens)

            output.append(
                f"def {name}({', '.join(parameters)}):"
            )

            output.extend(self.indent_lines(translated))
            output.append("")

        # Translate main method.
        if main_body is not None:
            tokens = self.tokenize(main_body)
            translated, _ = self.translate_block(tokens)

            output.extend(translated)

        else:
            # Remove method definitions from source.
            source = self.source

            method_pattern = re.compile(
                r'(?:public\s+|private\s+|protected\s+)?'
                r'(?:static\s+)?'
                r'(?:final\s+)?'
                r'(?:void|int|double|float|long|boolean|String|char|'
                r'[A-Za-z_]\w*(?:<[^>]+>)?)\s+'
                r'[A-Za-z_]\w*\s*'
                r'\([^)]*\)\s*\{'
            )

            matches = list(method_pattern.finditer(source))

            for match in reversed(matches):
                open_brace = match.end() - 1
                depth = 1
                close_brace = -1

                for index in range(open_brace + 1, len(source)):
                    if source[index] == "{":
                        depth += 1
                    elif source[index] == "}":
                        depth -= 1

                        if depth == 0:
                            close_brace = index
                            break

                if close_brace == -1:
                    raise SyntaxError("Unmatched method brace")

                source = (
                    source[:match.start()]
                    + source[close_brace + 1:]
                )

            source = re.sub(
                r'\bpublic\s+class\s+\w+\s*\{',
                '',
                source
            )

            source = re.sub(
                r'\bclass\s+\w+\s*\{',
                '',
                source
            )

            source = source.replace("}", "")

            tokens = self.tokenize(source)
            translated, _ = self.translate_block(tokens)

            output.extend(translated)

        return "\n".join(output).strip() + "\n"


def translate_java_to_python(source_code):
    translator = JavaToPython(source_code)
    return translator.translate()
