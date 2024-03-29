from dfa import DFA

# Clase DirectDFA para construir un DFA directamente a partir de un �rbol sint�ctico de una expresi�n regular.
class DirectDFA:
	def __init__(self, root):
		self.root = root
		self.dfa = DFA()
		self.positions = {}  # Mapea nodos a sus posiciones
		self.followpos = {}  # Mapea posiciones a sus followpos
		self.state_counter = 0
		self.alphabet = set()  # Conjunto de s�mbolos del alfabeto

	# M�todo principal para construir el DFA.
	def build(self):
		self.initialize_positions(self.root)
		self.calculate_followpos(self.root)
		self.construct_dfa()
		
	 # Determina si un conjunto de estados incluye el estado de aceptaci�n.
	def is_accept_state(self, state_set):
		# Asume que el estado de aceptaci�n incluye la posici�n del s�mbolo '#'
		# Primero, encuentra la posici�n del s�mbolo '#' en el �rbol sint�ctico
		# Esto asume que ya has asignado posiciones a cada nodo en el �rbol
		accept_pos = self.positions[next(node for node in self.positions if node.value == '#')]
		# Luego, verifica si el conjunto de estados (state_set) incluye esa posici�n
		return accept_pos in state_set

	# Asigna posiciones a los nodos del �rbol y prepara los conjuntos followpos.
	def initialize_positions(self, node, pos=[1]):
		if node.value not in '*|.':
			# Nodo hoja (operando)
			self.positions[node] = pos[0]
			self.followpos[pos[0]] = set()
			self.alphabet.add(node.value)
			pos[0] += 1
		else:
			# Nodo interno (operador)
			for child in node.children:
				self.initialize_positions(child, pos)

	 # Calcula los conjuntos followpos para cada nodo.
	def calculate_followpos(self, node):
		if node.value == '.':
			# Concatenaci�n: lastpos(n1) -> firstpos(n2)
			lastpos_n1 = self.get_lastpos(node.children[0])
			firstpos_n2 = self.get_firstpos(node.children[1])
			for pos in lastpos_n1:
				self.followpos[pos].update(firstpos_n2)
		elif node.value == '*':
			# Cierre de Kleene: lastpos(n) -> firstpos(n)
			lastpos_n = self.get_lastpos(node)
			firstpos_n = self.get_firstpos(node)
			for pos in lastpos_n:
				self.followpos[pos].update(firstpos_n)
		for child in node.children:
			self.calculate_followpos(child)

	# Obtiene los conjuntos firstpos y lastpos para un nodo.
	def get_firstpos(self, node):
		if node.value in '*|.':
			if node.value == '*':
				return self.get_firstpos(node.children[0])
			elif node.value == '|':
				return self.get_firstpos(node.children[0]).union(self.get_firstpos(node.children[1]))
			elif node.value == '.':
				if self.is_nullable(node.children[0]):
					return self.get_firstpos(node.children[0]).union(self.get_firstpos(node.children[1]))
				else:
					return self.get_firstpos(node.children[0])
		else:
			return {self.positions[node]}

	def get_lastpos(self, node):
		if node.value in '*|.':
			if node.value == '*':
				return self.get_lastpos(node.children[0])
			elif node.value == '|':
				return self.get_lastpos(node.children[0]).union(self.get_lastpos(node.children[1]))
			elif node.value == '.':
				if self.is_nullable(node.children[1]):
					return self.get_lastpos(node.children[0]).union(self.get_lastpos(node.children[1]))
				else:
					return self.get_lastpos(node.children[1])
		else:
			return {self.positions[node]}

	# Verifica si un nodo puede derivar la cadena vac�a.
	def is_nullable(self, node):
		if node.value == '*':
			return True
		elif node.value == '|':
			return self.is_nullable(node.children[0]) or self.is_nullable(node.children[1])
		elif node.value == '.':
			return self.is_nullable(node.children[0]) and self.is_nullable(node.children[1])
		else:
			return False

	# Construye el DFA utilizando los conjuntos firstpos, lastpos y followpos.
	def construct_dfa(self):
		state_names = {}  # Mapea frozensets a nombres de estados
		state_name_counter = [0]  # Usamos una lista para poder modificarlo dentro de get_state_name

		def get_state_name(state_set):
			# Devuelve un nombre de estado existente o genera uno nuevo
			if state_set not in state_names:
				# Accedemos al contador usando state_name_counter[0]
				state_names[state_set] = f'S{state_name_counter[0]}'
				state_name_counter[0] += 1
			return state_names[state_set]

		initial_state = frozenset(self.get_firstpos(self.root))
		self.dfa.add_state(get_state_name(initial_state), is_accept=self.is_accept_state(initial_state))
		self.dfa.set_initial_state(get_state_name(initial_state))
		unmarked_states = [initial_state]
		marked_states = set()

		while unmarked_states:
			S = unmarked_states.pop()
			marked_states.add(S)
			for a in self.alphabet:
				move = set()
				for pos in S:
					# Asegurarse de que se refiere al valor correcto y no al nodo directamente
					if pos in self.positions.values() and a == list(self.positions.keys())[list(self.positions.values()).index(pos)].value:
						move.update(self.followpos[pos])
				U = frozenset(move)
				if U not in marked_states and U not in unmarked_states:
					self.dfa.add_state(get_state_name(U), is_accept=self.is_accept_state(U))
					unmarked_states.append(U)
				if U:
					self.dfa.add_transition(get_state_name(S), a, get_state_name(U))



	def is_accept_state(self, state_set):
		# Asume que el estado de aceptaci�n es el �ltimo nodo hoja a�adido
		accept_pos = max(self.positions.values())
		return accept_pos in state_set