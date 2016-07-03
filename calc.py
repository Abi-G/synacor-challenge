from itertools import permutations


def calc(a, b, c, d, e):
    if a + b * c**2 + d**3 - e == 399:
        return True
    else:
        return False


def main():
    for vals in permutations((2, 9, 3, 5, 7)):
        if calc(*vals):
            print("ANSWER: ", vals)


if __name__ == "__main__":
    main()
