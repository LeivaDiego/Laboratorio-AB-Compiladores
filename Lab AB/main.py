from regex_parser import ShuntingYard
from syntax_tree import SyntaxTree

def main():
    # Crear una instancia de la clase ShuntingYard
    sy = ShuntingYard()
    tm = SyntaxTree()
    
    # Solicitar al usuario que ingrese la expresión regular infix
    infix_regex = input("Ingresa la expresión regular infix: ")
    
    # Convertir la expresion regular infix a postfix
    postfix_regex = sy.infix_to_postfix(infix_regex)
    # Imprimir el resultado
    print(f"Expresión Regular Infix: {infix_regex}")
    print(f"Expresión Regular Postfix: {postfix_regex}")
    
    # Construccion y visualizacion del arbol sintactico
    root = tm.build_tree(postfix_regex)
    tree_dot = tm.visualize_tree(root)
    tree_dot.render(f'arbol_sintactico', view=True, cleanup=True)

if __name__ == "__main__":
    main()
