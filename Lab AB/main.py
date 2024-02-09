from regex_parser import ShuntingYard

def main():
    # Crear una instancia de la clase ShuntingYard
    sy = ShuntingYard()
    
    # Regex de ejemplo
    infix_regex = 'a|b'
    
    # Convertir la expresion regular infix a postfix
    postfix_regex = sy.infix_to_postfix(infix_regex)
    
    # Imprimir el resultado
    print(f"Expresión Regular Infix: {infix_regex}")
    print(f"Expresión Regular Postfix: {postfix_regex}")

if __name__ == "__main__":
    main()
