# Define la clase Shunting Yard para la conversion de una expresion regular infix a postfix

class ShuntingYard:
	
	# Inicializa la lista de operadores validos 
	def __init__(self):
		self.binary_operators = ['|','.']
		self.unary_operators = ['?', '+', '*']
		self.all_operators = self.binary_operators + self.unary_operators
		self.special_characters = ['(', ')', '.']

	# Retorna la precedencia del operador dado, 0 si no se encuentra
	def get_precedence(self, c):
		precedence = {
			'(': 1,
			'|': 2,
			'.': 3,
			'?': 4,
			'*': 4,
			'+': 4,
		}
		return precedence.get(c, 0)

	# Valida que la expresion este balanceada 
	def validate_parentheses(self, regex):
		stack = []
		for char in regex:
			if char == '(':
				stack.append(char)
			elif char == ')':
				if not stack or stack[-1] != '(':
					return False
				stack.pop()
		return not stack

	# Valida que la sintaxis de la expresion este correcta
	def validate_operators(self, regex):
		for i, char in enumerate(regex):
			# Validación para operadores unarios
			if char in self.unary_operators:
				if i == 0 or (regex[i - 1] in self.all_operators + ['(']):
					raise ValueError(f"Operador unario '{char}' no tiene operando a la izquierda en la posición {i}.")

			# Validación para operadores binarios
			if char in self.binary_operators:
				if i == 0 or i == len(regex) - 1:
					raise ValueError(f"Operador binario '{char}' no tiene operandos en la posición {i}.")

				# Verificar si a la izquierda del operador binario hay un operador unario o un paréntesis abierto sin un operando adecuado antes
				left_invalid = i - 1 == 0 and regex[i - 1] in ['('] or \
							   (i - 2 >= 0 and regex[i - 1] in self.unary_operators and (regex[i - 2] in self.all_operators + ['(']))
				right_invalid = i + 1 == len(regex) - 1 and regex[i + 1] in [')'] or \
								(i + 2 < len(regex) and regex[i + 1] in self.unary_operators and (regex[i + 2] in self.all_operators + [')']))

				if left_invalid or right_invalid:
					raise ValueError(f"Operador binario '{char}' usado incorrectamente en la posición {i}.")


	# Valida la expresion
	def validate_expression(self, regex):
		if not self.validate_parentheses(regex):
			raise ValueError("La expresión regular tiene paréntesis no balanceados.")
		self.validate_operators(regex)

	# Convierte el operador '+' a su forma explicita, es decir, 'a+' pasa a ser 'aa*'
	def plus_operator_conversion(self, regex):

		i = 0
		transformed_exp = ""

		# Bucle que recorre la expresion regular
		while i < len(regex):

			# Si encuentra un '+' verifica el caracter anterior
			if regex[i] == '+':
				# si es un parentesis, busca el parentesis correspondiente y reemplaza por '*'
				if regex[i-1] == ')':
					for j in range(i-1, -1, -1):
						if regex[j] == '(':
							transformed_exp += regex[j:i] + "*"
						  
				else:
					transformed_exp += regex[i-1] + '*'
			else:
				transformed_exp += regex[i]
			i += 1
		return transformed_exp


	# Convierte la extension de expresion '?' a su forma explicita, es decir, 'a?' a 'a|ε'
	def interrogation_operator_conversion(self, regex):
		
		stack = []
		openParentesis = []
		i = 0

		# Bucle que recorre la expresion regular
		while i < len(regex):
			# Si encuentra '?', verifica el caracter anterior
			if regex[i] == '?':
				# si es un parentesis, busca el parentesis correspondiente 
				if regex[i-1] == ')':
					for j in range(i-1, -1, -1):
						if regex[j] == ')':
							stack.append(regex[j])
						elif regex[j] == '(':
							stack.pop()
							if not stack:
								openParentesis.append(j + 1)
								break
				else:
					openParentesis.append(i - 1)
			i += 1

		transformed_exp = ""
		i = 0

		while i < len(regex):
			if i in openParentesis:
				count = openParentesis.count(i)
				transformed_exp += '(' * count + regex[i]

			elif regex[i] == '?':
				transformed_exp += '|ε)' #  reemplaza por '|ε'

			else:
				transformed_exp += regex[i]

			i += 1

		return transformed_exp


	# Maneja la concatenacion implicita, transformandola en explicita usando .
	def concatenation_conversion(self, expression):
	   
		new_expression = []

		# Bucle que recorre la expresion
		for i in range(len(expression) - 1):
			new_expression.append(expression[i])

			# si encuentra caracteres consecutivos que no sean operadores, agrega '.' entre caracteres
			if (expression[i] not in ['|', '(', '.'] and 
				expression[i+1] not in ['|', ')', '*', '+', '?']
				):
				new_expression.append('.')

		new_expression.append(expression[-1])

		return ''.join(new_expression)

	# Hace uso de las conversiones para transformar la expresion a su forma explicita 
	# antes de hacer shunting yard
	def format_regex(self, regex):
		regex = self.plus_operator_conversion(regex)
		regex = self.interrogation_operator_conversion(regex)
		regex = self.concatenation_conversion(regex)
		return regex

	# Convierte la expresion infix a formato postfix utilizando el algoritmo de Shunting Yard
	def infix_to_postfix(self, regex):
		try:
			self.validate_expression(regex)
		except ValueError as e:
			return False, str(e)
		
		postfix = []
		stack = []
		formatted_regex = self.format_regex(regex)

		for c in formatted_regex:
			if c == '(':
				stack.append(c)
			elif c == ')':
				while stack and stack[-1] != '(':
					postfix.append(stack.pop())
				stack.pop()
			elif c in self.all_operators:
				while stack and self.get_precedence(stack[-1]) >= self.get_precedence(c):
					postfix.append(stack.pop())
				stack.append(c)
			else:
				postfix.append(c)

		while stack:
			postfix.append(stack.pop())

		return True, ''.join(postfix)
