from regex_parser import ShuntingYard
from syntax_tree import SyntaxTree
from nfa import match, Thompson, visualize_nfa
from dfa import dfa_from_nfa, visualize_dfa, simulate_dfa

def main():
	# Crear una instancia de la clase ShuntingYard 
	sy = ShuntingYard()
	st = SyntaxTree()
	
	# Solicitar al usuario que ingrese la expresión regular infix
	infix_regex = input("Ingresa la expresión regular infix: ")
	
	# Convertir la expresion regular infix a postfix
	success, postfix_regex = sy.infix_to_postfix(infix_regex)
	
	if success:
		# Imprimir el resultado
		print(f"Expresión Regular Infix: {infix_regex}")
		print(f"Expresión Regular Postfix: {postfix_regex}")
	
		# Construccion y visualizacion del arbol sintactico
		root = st.build_tree(postfix_regex)
		tree_dot = st.visualize_tree(root)
		tree_dot.render(f'arbol_sintactico', view=True, cleanup=True)
		
		# Construccion y visualizacion del afn
		nfa = Thompson(postfix_regex)
		visualize_nfa(nfa.initial, nfa.accept)
		
		# Solicitar al usuario que ingrese la cadena a comprobar
		test_string = input("Ingresa la cadena a comprobar: ")
		
		# Comprobar si la cadena coincide con la expresión regular con AFN
		matched = match(infix_regex, test_string, sy, nfa)
		
		if matched:
			print("La cadena coincide con la expresión regular.")
		else:
			print("La cadena NO coincide con la expresión regular.")

		# Construccion y visualizacion de AFD a partir del AFN
		dfa = dfa_from_nfa(nfa)
		visualize_dfa(dfa)
		
		# Solicitar al usuario que ingrese la cadena a comprobar
		test_string = input("Ingresa la cadena a comprobar: ")
		
		# Comprobar si la cadena coincide con la expresión regular con AFN
		matched = simulate_dfa(dfa,test_string)
		
		if matched:
			print("La cadena coincide con la expresión regular.")
		else:
			print("La cadena NO coincide con la expresión regular.")
		
	else:
		print(f"Expresión Regular no válida: {postfix_regex}")

if __name__ == "__main__":
	main()
