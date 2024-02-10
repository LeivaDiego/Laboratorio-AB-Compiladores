
from graphviz import Digraph

class DFA:
	def __init__(self):
		self.states = []  # Lista de nombres de los estados del DFA
		self.transitions = {}  # Diccionario de transiciones; clave: estado, valor: diccionario (clave: símbolo, valor: estado destino)
		self.initial_state = None  # Estado inicial del DFA
		self.accept_states = []  # Lista de estados de aceptación
		self.alphabet = set()  # Conjunto de símbolos de entrada que el DFA puede aceptar


	def add_state(self, state, is_accept=False):
		if state not in self.states:
			self.states.append(state)
			self.transitions[state] = {}
		if is_accept:
			self.accept_states.append(state)
			

	def add_transition(self, state_from, symbol, state_to):
		if state_from in self.transitions:
			self.transitions[state_from][symbol] = state_to
			self.alphabet.add(symbol)

	def set_initial_state(self, state):
		self.initial_state = state
		

def epsilon_closure(states):
	closure = set(states)
	stack = list(states)

	while stack:
		state = stack.pop()
		if state.edge1 is not None and state.edge1 not in closure:
			closure.add(state.edge1)
			stack.append(state.edge1)
		if state.edge2 is not None and state.edge2 not in closure:
			closure.add(state.edge2)
			stack.append(state.edge2)

	return closure


def move(states, symbol):
	result = set()
	for state in states:
		if state.label == symbol:
			if state.edge1 is not None:
				result.add(state.edge1)
	return result


def dfa_from_nfa(nfa):
	initial_closure = epsilon_closure({nfa.initial})
	dfa = DFA()
	initial_state_name = 'S0'
	dfa.set_initial_state(initial_state_name)
	dfa.add_state(initial_state_name, is_accept=nfa.accept in initial_closure)

	unprocessed_states = [(initial_state_name, initial_closure)]  # Lista de estados DFA no procesados
	dfa_state_mapping = {frozenset(initial_closure): initial_state_name}  # Mapeo de conjuntos de estados NFA a nombres de estados DFA

	while unprocessed_states:
		dfa_state_name, nfa_states = unprocessed_states.pop(0)  # Usa pop(0) para procesar en orden de llegada
		for symbol in set(state.label for state in nfa_states if state.label):
			target_nfa_states = move(nfa_states, symbol)
			closure = epsilon_closure(target_nfa_states)
			closure_frozenset = frozenset(closure)

			if closure_frozenset not in dfa_state_mapping:
				new_dfa_state_name = f'S{len(dfa_state_mapping)}'
				dfa_state_mapping[closure_frozenset] = new_dfa_state_name
				dfa.add_state(new_dfa_state_name, is_accept=nfa.accept in closure)
				unprocessed_states.append((new_dfa_state_name, closure))

			dfa.add_transition(dfa_state_name, symbol, dfa_state_mapping[closure_frozenset])

	return dfa


def visualize_dfa(dfa, name):
	dot = Digraph()
	dot.attr('node', shape='circle')

	# Marcar el estado inicial con un nodo doble
	dot.node("start", shape="none", label="")
	dot.edge("start", dfa.initial_state)

	# Crear nodos para cada estado, marcando los estados de aceptación con doble círculo
	for state in dfa.states:
		if state in dfa.accept_states:
			dot.node(state, shape='circle')
		else:
			dot.node(state)

	# Agregar transiciones
	for from_state, transitions in dfa.transitions.items():
		for symbol, to_state in transitions.items():
			dot.edge(from_state, to_state, label=symbol)

	# Renderizar y visualizar el DFA
	dot.render(f'dfa_{name}', view=True, cleanup=True)


def simulate_dfa(dfa, input_string):
	# El estado actual se maneja como un conjunto para imitar la estructura del AFN, aunque siempre será de un solo elemento
	current_states = {dfa.initial_state}

	for symbol in input_string:
		next_states = set()  # Preparar el siguiente conjunto de estados (será siempre de máximo un estado en DFA)
		for current_state in current_states:
			# Verifica si existe una transición para el símbolo actual desde el estado actual
			if symbol in dfa.transitions[current_state]:
				# Mueve al siguiente estado, actualizando el conjunto de estados actuales
				next_states.add(dfa.transitions[current_state][symbol])
		
		# Actualiza los conjuntos de estados
		current_states = next_states
		
		# Si en algún punto no hay estados siguientes, la cadena no es aceptada
		if not current_states:
			return False

	# La cadena es aceptada si terminamos en un estado de aceptación
	return any(state in dfa.accept_states for state in current_states)


def build_minimized_dfa(dfa, partition_map, partitions):
    """
    Construye el DFA minimizado a partir de las particiones finales.
    """
    minimized_dfa = DFA()
    state_name_map = {}  # Mapea índices de partición a nombres de nuevos estados
    
    # Crear nuevos estados en el DFA minimizado
    for partition_index, partition in enumerate(partitions):
        state_name = f"S{partition_index}"  # Nombre del nuevo estado
        state_name_map[partition_index] = state_name
        minimized_dfa.add_state(state_name, is_accept=any(state in dfa.accept_states for state in partition))
    
    # Establecer el estado inicial
    for state in dfa.states:
        if state == dfa.initial_state:
            minimized_dfa.set_initial_state(state_name_map[partition_map[state]])
            break
    
    # Definir las transiciones del DFA minimizado
    for partition_index, partition in enumerate(partitions):
        representative_state = partition[0]  # Tomar un estado representativo de la partición
        for symbol in dfa.alphabet:
            if representative_state in dfa.transitions and symbol in dfa.transitions[representative_state]:
                target_state = dfa.transitions[representative_state][symbol]
                minimized_dfa.add_transition(
                    state_name_map[partition_index], 
                    symbol, 
                    state_name_map[partition_map[target_state]]
                )
                
    return minimized_dfa

def refine_partitions(dfa, partition_map, partitions):
    changed = True
    while changed:
        changed = False
        new_partitions = []
        new_partition_map = {}
        
        for partition in partitions:
            # Un diccionario para agrupar estados por las particiones de destino de sus transiciones
            transition_groups = {}
            
            for state in partition:
                # Clave para agrupar: una tupla de las particiones de destino para cada símbolo del alfabeto
                # Maneja transiciones no definidas asignando un valor especial (por ejemplo, -1)
                group_key = tuple(partition_map.get(dfa.transitions[state].get(symbol), -1) for symbol in sorted(dfa.alphabet))
                
                if group_key not in transition_groups:
                    transition_groups[group_key] = []
                transition_groups[group_key].append(state)
            
            if len(transition_groups) > 1:
                changed = True
            
            for group in transition_groups.values():
                new_partitions.append(group)
                for state in group:
                    new_partition_map[state] = len(new_partitions) - 1
        
        partitions = new_partitions
        partition_map = new_partition_map
    
    return partition_map, partitions


def initial_partition(dfa):
    """
    Crea particiones iniciales del DFA basadas en estados de aceptación y no aceptación.
    Retorna un diccionario que mapea cada estado a su partición correspondiente y
    una lista de particiones para mantener un registro de los grupos actuales.
    """
    partition_map = {}  # Mapea cada estado a su partición (0 o 1)
    partitions = [[], []]  # [0] para no aceptadores, [1] para aceptadores
    
    for state in dfa.states:
        if state in dfa.accept_states:
            partition_map[state] = 1  # Estado de aceptación
            partitions[1].append(state)
        else:
            partition_map[state] = 0  # Estado no aceptador
            partitions[0].append(state)
    
    return partition_map, partitions

def remove_unreachable_states(dfa):
    """
    Elimina los estados inalcanzables de un DFA dado.
    """
    reachable_states = set()
    stack = [dfa.initial_state]  # Comienza con el estado inicial
    while stack:
        state = stack.pop()
        if state not in reachable_states:
            reachable_states.add(state)
            # Asume que `dfa.transitions` es un diccionario donde las claves son los estados
            # y los valores son diccionarios de transiciones (clave: símbolo, valor: estado destino).
            if state in dfa.transitions:
                for symbol in dfa.transitions[state]:
                    next_state = dfa.transitions[state][symbol]
                    if next_state not in reachable_states:
                        stack.append(next_state)

    # Actualiza el DFA para mantener solo los estados alcanzables y sus transiciones
    dfa.states = [state for state in dfa.states if state in reachable_states]
    dfa.transitions = {state: transitions for state, transitions in dfa.transitions.items() if state in reachable_states}
    dfa.accept_states = [state for state in dfa.accept_states if state in reachable_states]


def minimize_dfa(dfa):
    """
    Función que encapsula los pasos de minimización de un DFA.
    """
    # Paso 1: Eliminar estados inalcanzables
    remove_unreachable_states(dfa)
    
    # Paso 2: Crear particiones iniciales
    partition_map, partitions = initial_partition(dfa)
    
    # Paso 3: Refinar particiones
    partition_map, partitions = refine_partitions(dfa, partition_map, partitions)
    
    # Paso 4: Construir el DFA minimizado
    minimized_dfa = build_minimized_dfa(dfa, partition_map, partitions)
    
    return minimized_dfa