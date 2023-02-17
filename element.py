class Element:
    op: str

    def __init__(self, op: str):
        self.op = op

    def calculate(self):
        return 1.0


class Brackets(Element):
    elements = list[Element]

    def __init__(self, op: str, elements: list[Element]):
        super().__init__(op)
        self.elements = elements

    def calculate(self):
        value = 0.0

        elems = self.elements.copy()

        # Potenz
        i = 1
        while i < len(elems):
            if elems[i].op == "^":
                elem1 = elems[i - 1]
                elem2 = elems[i]

                elems[i - 1] = Number(elem2.op, pow(elem1.calculate(), elem2.calculate()))
                elems.pop(i)
            else:
                i += 1

        # Punkt
        ops = {
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y,
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
        }

        i = 1
        while i < len(elems):
            if elems[i].op in "*/":
                elem1 = elems[i - 1]
                elem2 = elems[i]

                elems[i - 1] = Number(elem1.op, ops[elem2.op](elem1.calculate(), elem2.calculate()))
                elems.pop(i)
            else:
                i += 1


        # Strich
        i = 1
        while i < len(elems):
            if elems[i].op in "+-":
                elem1 = elems[i - 1]
                elem2 = elems[i]

                elems[i - 1] = Number(elem1.op, ops[elem2.op](elem1.calculate(), elem2.calculate()))
                elems.pop(i)
            else:
                i += 1

        value = elems[0].calculate()
        if elems[0].op != "-":
            return value
        else:
            return -value


class Number(Element):
    value: float

    def __init__(self, op: str, value: float):
        super().__init__(op)
        self.value = value

    def calculate(self) -> float:
        return self.value


def print_element(element: Element):
    def print_rec(elem: Element, indent: str):
        if isinstance(elem, Brackets):
            print(indent + elem.op + "(")
            for e in elem.elements:
                print_rec(e, indent + "  ")
            print(indent + ")")
        elif isinstance(elem, Number):
            print(indent + elem.op + str(elem.value))
        elif element is None:
            print("None")

    print_rec(element, "")
