from regex_parser.validation import is_balanced_regex

def main():
    # Ejemplo de una regex
    regex = "(a|b)*a(a|b)"
    if is_balanced_regex(regex):
        print(f"The regular expression '{regex}' is balanced.")
    else:
        print(f"The regular expression '{regex}' is not balanced.")

if __name__ == "__main__":
    main()
