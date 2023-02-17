from element import *

# The possible operators
_ops = ("*", "/", "^", "+", "-")

# Characters that can be interpreted by the calculator
_allowed_nums = "0123456789."
_allowed_chars = _allowed_nums + "+-*/^()"

# Illegal character combinations that can be formed with allowed characters
_illegal_strs = (
    "**", "*/", "*^", "//", "/*", "/^", "^^", "^*", "^/",
    "+*", "+/", "+^", "-*", "-/", "-^",
    "+)", "-)", "*)", "/)", "^)",
    "(*", "(/", "(^",
    "()"
)


def is_calculation(calc: str):
    """
    Returns False if the calculation contains characters that can't be interpreted by the calculator
    or if there are any illegal character combinations. Returns True if the provided string is a calculation.
    :param calc: The string to be tested.
    :return: Whether the string is a calculation string or not.
    """

    calc = calc.replace(" ", "")

    # Tests if the distribution of the brackets is correct
    bracket_level = 0
    for c in calc:
        if c == "(": bracket_level += 1
        if c == ")": bracket_level -= 1
        if bracket_level < 0:
            return False
    if bracket_level > 0:
        return False

    calc = f"({calc})"

    # Checks if there are characters that can't be interpreted
    for c in calc:
        if c not in _allowed_chars:
            return False

    last_was_dot = False
    contains_dot = False
    i = 0
    while i < len(calc):
        if calc[i].isnumeric():
            last_was_dot = False
        elif calc[i] == ".":
            if contains_dot:
                return False
            contains_dot = True
            last_was_dot = True
        else:
            if last_was_dot:
                return False
            contains_dot = False
            last_was_dot = False
        i += 1

    # Checks for character combinations that can't be interpreted
    for s in _illegal_strs:
        if s in calc:
            return False

    return True


def _format_calculation(calc: str) -> str | None:
    if not is_calculation(calc):
        return None

    calc = calc.replace(" ", "")

    calc = f"({calc})"

    # Removes the redundant +/- operators ("+-1", "--19", etc.)
    change = True
    while change:
        change = False
        f_calc = calc.replace("++", "+").replace("--", "+").replace("+-", "-").replace("-+", "-")
        if calc != f_calc:
            change = True
        calc = f_calc

    calc = _add_brackets_at_double_ops(calc)

    calc = _add_power_number_brackets(calc)

    calc = calc.replace(")(", ")*(")

    return calc


# 4*-3 -> 4*(-3)
def _add_brackets_at_double_ops(calc) -> str:
    i = 0
    while i < len(calc) - 1:
        if calc[i] in _ops and calc[i + 1] in _ops:
            end_index = i + 2
            if calc[end_index] in _allowed_nums:
                while calc[end_index] in _allowed_nums:
                    end_index += 1
            elif calc[end_index] == "(":
                level = 1
                end_index += 1
                while level > 0:
                    if calc[end_index] == "(":
                        level += 1
                    elif calc[end_index] == ")":
                        level -= 1
                    end_index += 1

            calc = calc[:i + 1] + "(" + calc[i + 1:end_index] + ")" + calc[end_index:]
        i += 1

    return calc

# -3^5 -> -(3^5)
def _add_power_number_brackets(calc: str) -> str:

    i = 0
    while i < len(calc):
        if calc[i] == "^":
            start_index = i-1
            if calc[start_index] in _allowed_nums:
                while calc[start_index] in _allowed_nums:
                    start_index -= 1
            elif calc[start_index] == ")":
                level = 1
                start_index -= 1
                while level > 0:
                    if calc[start_index] == ")":
                        level += 1
                    elif calc[start_index] == "(":
                        level -= 1
                    start_index -= 1

            end_index = i+1
            if calc[end_index] in _allowed_nums:
                while calc[end_index] in _allowed_nums:
                    end_index += 1
            elif calc[end_index] == "(":
                level = 1
                end_index += 1
                while level > 0:
                    if calc[end_index] == "(":
                        level += 1
                    elif calc[end_index] == ")":
                        level -= 1
                    end_index += 1

            calc = calc[:start_index+1] + "(" + calc[start_index+1:i] + "#" + calc[i+1:end_index+1] + ")" + calc[end_index+1:]

        i += 1

    return calc.replace("#", "^")



def _parse_calculation(calc: str) -> Brackets | None:
    root, i = _parse_brackets(f"({calc})", "+", 1)
    return root


def _parse_brackets(calc: str, op: str, start: int) -> (Brackets | None, int | None):
    if start >= len(calc):
        return None, None
    if not is_calculation(calc):
        return None, None

    root = Brackets(op, [])

    current_op = "+"
    current_value = ""
    element_count = 0

    i = start
    while i < len(calc):
        if calc[i] == "(":
            bracket, new_i = _parse_brackets(calc, current_op, i + 1)
            root.elements.append(bracket)
            i = new_i
        elif calc[i] == ")":
            if current_value != "":
                root.elements.append(Number(current_op, float(current_value)))
                element_count += 1
            return root, i

        elif calc[i] in _allowed_nums:
            current_value += calc[i]
        elif calc[i] in _ops:
            if current_value != "":
                root.elements.append(Number(current_op, float(current_value)))
                element_count += 1

            current_op = calc[i]
            current_value = ""

        i += 1

    return root, len(calc) - 1


def calculate(calc: str) -> float | None:

    if is_calculation(calc):
        formatted_calc = _format_calculation(calc)
        parsed_calc = _parse_calculation(formatted_calc)
        if parsed_calc is not None:
            return parsed_calc.calculate()
        return None
    else:
        return None
