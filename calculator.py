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
    "()",
    ".(", ".)", ".+", ".-", ".*", "./", ".^"  # when a number ends on a dot (which it shouldn't)
)

# ==== VALIDATAION ====
def is_calculation(calc: str):
    """
    Returns True if the provided string can be interpreted.
    :param calc: The string to be checked.
    :return: Whether the string is interpretable or not.
    """

    calc = calc.replace(" ", "")  # Trims all whitespaces from the string

    # (1) Tests if the distribution of the brackets is correct
    # (2) Checks whether there are characters that can't be interpreted
    bracket_level = 0
    for c in calc:

        if c == "(": bracket_level += 1  # (1)
        if c == ")": bracket_level -= 1  # (1)
        if bracket_level < 0: return False  # (1)

        if c not in _allowed_chars: return False  # (2)

    if bracket_level > 0:
        return False

    calc = f"({calc})"  # Surrounds the string with brackets to remove end-of-line logic (easier to program)

    # Tests if the numbers in the string are in the correct format:
    # Pass: '4', '2.6', '.5'
    # Fail: '9.', '3.8.', '4.1.6', '.6.3'
    contains_dot = False  # Tests if a dot has already been read (in case there is a 2nd one like in 1.4.5)

    # Checks if there is more than one dot in the numbers (like in '1.2.3')
    for c in calc:
        if c == ".":
            if contains_dot:
                return False
            contains_dot = True
        else:
            contains_dot = False

    # Checks for character combinations that can't be interpreted
    for s in _illegal_strs:
        if s in calc:
            return False

    return True


# ==== FORMATTER ====

def _format_calculation(calc: str) -> str | None:
    # Tests if the input can be interpreted
    if not is_calculation(calc):
        return None

    # Trims all whitespaces and pads the string with brackets
    calc = f"({calc.replace(' ', '')})"

    # Removes the redundant +/- operators ("+-1" -> "-1", "--19" -> "+19", etc.)
    # Repeats until no change has been made in the last iteration
    change = True
    while change:
        change = False
        f_calc = calc.replace("++", "+").replace("--", "+").replace("+-", "-").replace("-+", "-")
        if calc != f_calc:
            change = True
        calc = f_calc

    calc = _insert_brackets_at_double_ops(calc)
    calc = _add_power_number_brackets(calc)
    calc = calc.replace(")(", ")*(")  # Makes it possible to write (3-2)(3+2) without a * in the middle

    # Makes it possible to write 3(4+2) instead of 3*(4+2)
    for c in _allowed_nums:
        calc = calc.replace(str(c) + "(", str(c) + "*(")

    return calc

def _insert_brackets_at_double_ops(calc) -> str:

    # Handles the situation where two operators are next to each other
    # Example: 3*-4
    # Solution: 3*(-4)

    i = 0
    while i < len(calc) - 1:
        if calc[i] in _ops and calc[i + 1] in _ops:
            end_index = _find_right_boundary(calc, i + 2)

            calc = calc[:i + 1] + "(" + calc[i + 1:end_index] + ")" + calc[end_index:]
        i += 1

    return calc

def _find_right_boundary(calc: str, i: int) -> int:
    if i not in range(0, len(calc)):
        return -1

    # Returns the index after the end of the next part of the calculation:
    # Examples (S = Starting point; R = Returned index)
    # (1): 3*3.25+5
    #        S   R
    # (2): (5*2)^(3+4)+6
    #            S    R

    if calc[i] in _allowed_nums:  # (1) Without brackets
        while calc[i] in _allowed_nums:
            i += 1

    elif calc[i] == "(":  # (2) With brackets
        level = 1
        i += 1
        while level > 0:
            if calc[i] == "(":
                level += 1
            elif calc[i] == ")":
                level -= 1
            i += 1
    return i + 1

def _find_left_boundary(calc: str, i: int) -> int:
    if i not in range(0, len(calc)):
        return -1

    # Returns the index of the beginning of the previous part of the calculation:
    # Examples (S = Starting point; R = Returned index)
    # (1): 3*3.25+5
    #        R   S
    # (2): (5*2)^(3+4)+6
    #            R   S

    if calc[i] in _allowed_nums:  # (1) Without brackets
        while calc[i] in _allowed_nums:
            i -= 1

    elif calc[i] == ")":  # (2) With Brackets
        level = 1
        i -= 1
        while level > 0:
            if calc[i] == ")":
                level += 1
            elif calc[i] == "(":
                level -= 1
            i -= 1
    return i

# -3^5 -> -(3^5)
def _add_power_number_brackets(calc: str) -> str:

    # Handles the case where the exponent has to be applied to the base with a sign that should be ignored
    # Example: -2^4 is not 16 but -16
    # Solution: Inserts brackets after the sign of the base and after the exponent
    # Example: -2^4 -> -(2^4) => -2^4 = -16

    for i in range(0, len(calc)):
        if calc[i] == "^":
            start_index = _find_left_boundary(calc, i-1)
            end_index = _find_right_boundary(calc, i+1)

            first_part = calc[:start_index+1]
            base = calc[start_index+1:i]
            exponent = calc[i+1:end_index]
            last_part = calc[end_index:]

            calc = f"{first_part}({base}#{exponent}){last_part}"  # Replaces ^ with # to avoid infinite loop

    return calc.replace("#", "^")


# ==== PARSER ====

def _parse_calculation(calc: str) -> Brackets | None:

    # Parses the calculation into a Bracket object

    root, i = _next_brackets(f"({calc})", "+", 1)
    return root

def _next_brackets(calc: str, op: str, start: int) -> (Brackets | None, int | None):
    if start >= len(calc):
        return None, None
    if not is_calculation(calc):
        return None, None

    # Creates the root brackets object
    root = Brackets(op, [])

    # Temp storage for the current number
    current_op = "+"
    current_value = ""

    # Loops over the whole string
    i = start
    while i < len(calc):

        # Recursively calls itself to handle sub-brackets
        # and jumps to the returned index to skip them
        # Adds the returned brackets object to root's elements list
        if calc[i] == "(":
            bracket, new_i = _next_brackets(calc, current_op, i + 1)
            root.elements.append(bracket)
            i = new_i

        # Saves the currently stored element into root's elements list
        # and returns the latter (root) and the index caller needs to jump to
        elif calc[i] == ")":
            if current_value != "":
                root.elements.append(Number(current_op, float(current_value)))
            return root, i

        # Adds number character to the value string
        elif calc[i] in _allowed_nums:
            current_value += calc[i]

        # If current value is filled: Stores the saved number as a Number object into root's elements list
        # Resets the stored number
        elif calc[i] in _ops:
            if current_value != "":
                root.elements.append(Number(current_op, float(current_value)))

            current_op = calc[i]
            current_value = ""

        i += 1

    # Only executed when the string has reached its end
    # Returns root + the last index of the string
    return root, len(calc) - 1


# ==== CALCULATION ====

def calculate(calc: str) -> float | None:
    """
    Calculates the result of the given string.
    :param calc: The calculation
    :return: The result of the calculation or None, if there is an error in the calculation string
    """
    if not is_calculation(calc):
        return None

    parsed_calc = _parse_calculation(_format_calculation(calc))
    return parsed_calc.calculate() if (parsed_calc is not None) else None
