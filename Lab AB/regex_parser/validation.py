
def is_balanced_regex(expression):
    # Validacion basica para comprobar que los parentesis estan balanceados
    stack = []
    for char in expression:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack:
                return False
            stack.pop()
    # Return True si el stack esta vacio (balanceado), de lo contrario falso
    return not stack
