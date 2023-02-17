import calculator



if __name__ == "__main__":

    while True:
        print("> ", end="")
        calc = input()

        if calc == "exit":
            break

        try:
            res = calculator.calculate(calc)

            if res is None:
                print("=> Error")
            else:
                print(f"=> {res}")
        except OverflowError:
            print("=> Result too large")