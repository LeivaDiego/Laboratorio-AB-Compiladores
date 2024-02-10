from dfa import DFA

class DirectDFA:
	def __init__(self, root):
		self.root = root
		self.dfa = DFA()
		self.positions = {}  # Mapea nodos a sus posiciones
		self.followpos = {}  # Mapea posiciones a sus followpos
		self.state_counter = 0
		self.alphabet = set()  # Conjunto de símbolos del alfabeto

	def build(self):
		self.initialize_positions(self.root)
		self.calculate_followpos(self.root)
		self.construct_dfa()
		
	def is_accept_state(self, state_set):
		# Asume que el estado de aceptación incluye la posición del símbolo '#'
		# Primero, encuentra la posición del símbolo '#' en el árbol sintáctico
		# Esto asume que ya has asignado posiciones a cada nodo en el árbol
		accept_pos = self.positions[next(node for node in self.positions if node.value == '#')]
		# Luego, verifica si el conjunto de estados (state_set) incluye esa posición
		return accept_pos in state_set

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

	def calculate_followpos(self, node):
		if node.value == '.':
			# Concatenación: lastpos(n1) -> firstpos(n2)
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

	def is_nullable(self, node):
		if node.value == '*':
			return True
		elif node.value == '|':
			return self.is_nullable(node.children[0]) or self.is_nullable(node.children[1])
		elif node.value == '.':
			return self.is_nullable(node.children[0]) and self.is_nullable(node.children[1])
		else:
			return False

	def construct_dfa(self):
		initial_state = frozenset(self.get_firstpos(self.root))
		self.dfa.add_state(str(initial_state), is_accept=self.is_accept_state(initial_state))
		self.dfa.set_initial_state(str(initial_state))
		unmarked_states = [initial_state]
		marked_states = set()
		while unmarked_states:
			S = unmarked_states.pop()
			marked_states.add(S)
			for a in self.alphabet:
				move = set()
				for pos in S:
					if pos in self.positions.values() and a == list(self.positions.keys())[list(self.positions.values()).index(pos)].value:
						move.update(self.followpos[pos])
				U = frozenset(move)
				if U and U not in marked_states and U not in unmarked_states:
					self.dfa.add_state(str(U), is_accept=self.is_accept_state(U))
					unmarked_states.append(U)
				if U:
					self.dfa.add_transition(str(S), a, str(U))

	def is_accept_state(self, state_set):
		# Asume que el estado de aceptación es el último nodo hoja añadido
		accept_pos = max(self.positions.values())
		return accept_pos in state_set