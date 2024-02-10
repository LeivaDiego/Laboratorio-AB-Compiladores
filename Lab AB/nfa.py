
from graphviz import Digraph

# Define la clase State para representar un estado en el NFA.
# Cada estado puede tener etiquetas (para los estados iniciales y de aceptación) y hasta dos aristas de transición.
class State:
	def __init__(self, label=None, edge1=None, edge2=None):
		self.label = label  # La etiqueta del estado (usualmente se usa para estados de aceptación o específicos).
		self.edge1 = edge1  # Primera arista de transición desde este estado.
		self.edge2 = edge2  # Segunda arista de transición (para NFA, donde un estado puede tener múltiples transiciones posibles).

# Define la clase NFA, que representa un autómata finito no determinista.
# Un NFA se define por un estado inicial y un estado de aceptación.
class NFA:
	def __init__(self, initial, accept):
		self.initial = initial  # El estado inicial del NFA.
		self.accept = accept  # El estado de aceptación del NFA.

# La función Thompson realiza la construcción de Thompson para convertir una expresión regular en un NFA.
def Thompson(postfix):
	nfa_stack = []  # Una pila para almacenar los NFA intermedios durante la construcción.

	for c in postfix:  # Itera sobre cada caracter en la expresión regular en forma posfija.
		if c == '*':  # Operador de Kleene: Crea un NFA que acepta 0 o más repeticiones de la expresión anterior.
			nfa1 = nfa_stack.pop()
			initial, accept = State(), State()
			initial.edge1, initial.edge2 = nfa1.initial, accept
			nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.initial, accept
			nfa_stack.append(NFA(initial, accept))
		elif c == '.':  # Concatenación: Une dos NFAs de la pila.
			nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
			nfa1.accept.edge1 = nfa2.initial
			nfa_stack.append(NFA(nfa1.initial, nfa2.accept))
		elif c == '|':  # Alternancia: Crea un NFA que acepta cualquiera de las dos expresiones anteriores.
			nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
			initial = State()
			initial.edge1, initial.edge2 = nfa1.initial, nfa2.initial
			accept = State()
			nfa1.accept.edge1, nfa2.accept.edge1 = accept, accept
			nfa_stack.append(NFA(initial, accept))
		elif c == '+':  # Una o más repeticiones: Similar a '*', pero al menos una repetición es necesaria.
			nfa1 = nfa_stack.pop()
			initial, accept = State(), State()
			initial.edge1 = nfa1.initial
			nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.initial, accept
			nfa_stack.append(NFA(initial, accept))
		elif c == '?':  # Opcional: La expresión anterior puede estar presente 0 o 1 vez.
			nfa1 = nfa_stack.pop()
			initial, accept = State(), State()
			initial.edge1, initial.edge2 = nfa1.initial, accept
			nfa1.accept.edge1 = accept
			nfa_stack.append(NFA(initial, accept))
		else:  # Un caracter específico: Crea un NFA básico que acepta ese caracter.
			accept, initial = State(), State()
			initial.label, initial.edge1 = c, accept
			nfa_stack.append(NFA(initial, accept))

	return nfa_stack.pop()  # Retorna el NFA resultante.

# La función followes obtiene el conjunto de todos los estados alcanzables desde un estado dado, incluido él mismo.
def followes(state):
	states = set()  # Inicializa un conjunto vacío para almacenar los estados.
	states.add(state)  # Agrega el estado actual al conjunto.

	# Si el estado no tiene etiqueta (no es un estado de aceptación), verifica sus transiciones.
	if state.label is None:
		if state.edge1 is not None:
			states |= followes(state.edge1)  # Agrega los estados alcanzables a través de la primera arista.
		if state.edge2 is not None:
			states |= followes(state.edge2)  # Agrega los estados alcanzables a través de la segunda arista.

	return states  # Retorna el conjunto de estados alcanzables.



def match(infix, string, shunting_yard, nfa):
	# Simulador del AFN

	success, postfix = shunting_yard.infix_to_postfix(infix)
	if not success:
		print("Error al convertir a postfix:", postfix)  # Manejo simplificado del error
		return False

	# El conjunto de estados actual y el siguiente conjunto de estados
	current_states = set()
	next_states = set()

	# Agrega el estado inicial al conjunto de estados actual
	current_states |= followes(nfa.initial)

	# Recorre cada carácter de la cadena
	for s in string:
		# Recorre el conjunto actual de estados
		for c in current_states:
			# Comprueba si el estado tiene la etiqueta 's'
			if c.label == s:
				# Agrega a next_states todos los estados alcanzables desde c.edge1
				next_states |= followes(c.edge1)
		# Prepara current_states y next_states para la siguiente ronda
		current_states, next_states = next_states, set()

	# Comprueba si el estado de aceptación está en el conjunto de estados actual
	return nfa.accept in current_states


def visualize_nfa(initial, accept):
	dot = Digraph()
	dot.attr('node', shape='circle')

	visited = set()  # Para mantener un registro de los estados visitados
	state_ids = {}  # Para asignar y recordar IDs a los estados

	def get_state_id(state):
		if state not in state_ids:
			state_ids[state] = str(len(state_ids))
		return state_ids[state]

	# Nodo inicial invisible para señalar el estado inicial del NFA
	dot.node('start', shape="none", label="")  # Nodo 'start' sin forma ni etiqueta
	dot.edge('start', get_state_id(initial), label="")  # Arista desde 'start' hacia el estado inicial

	# Función recursiva para visitar los estados y crear nodos y aristas
	def visit(state):
		if state in visited:
			return
		visited.add(state)

		# Usa 'doublecircle' para estados de aceptación, de lo contrario 'circle'
		if state == accept:
			dot.attr('node', shape='doublecircle')
		else:
			dot.attr('node', shape='circle')

		# Crea un nodo para el estado actual
		dot.node(get_state_id(state), get_state_id(state))

		# Si el estado tiene una transición a otro estado (edge1)
		if state.edge1:
			label = state.label if state.label else 'ε'
			dot.edge(get_state_id(state), get_state_id(state.edge1), label=label)
			visit(state.edge1)
		
		# Si el estado tiene una segunda transición a otro estado (edge2)
		if state.edge2:
			dot.edge(get_state_id(state), get_state_id(state.edge2), label='ε')
			visit(state.edge2)
	
		# Restablece el estilo de nodo a 'circle' por si se cambió a 'doublecircle'
		dot.attr('node', shape='circle')

	visit(initial)  # Comienza el recorrido desde el estado inicial

	# Renderiza y muestra el gráfico
	dot.render('afn_visualizado', view=True, cleanup=True)
