
def check_number(n):
    """Return a message describing whether n is positive, negative, or zero."""
    if n > 0:
        return "The number is positive."
    elif n < 0:
        return "The number is negative."
    else:
        return "The number is zero."


def main():
    try:
        s = input("Enter a number: ")
        # Accept integers or floats
        if "." in s:
            num = float(s)
        else:
            num = int(s)
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    print(check_number(num))


if __name__ == "__main__":
    main()
