
from graphviz import Digraph

class State:
    def __init__(self, label=None, edge1=None, edge2=None):
        self.label = label
        self.edge1 = edge1
        self.edge2 = edge2

class NFA:
    def __init__(self, initial, accept):
        self.initial = initial
        self.accept = accept

def compile(postfix):
    nfa_stack = []

    for c in postfix:
        if c == '*':
            nfa1 = nfa_stack.pop()
            initial, accept = State(), State()
            initial.edge1, initial.edge2 = nfa1.initial, accept
            nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.initial, accept
            nfa_stack.append(NFA(initial, accept))
        elif c == '.':
            nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
            nfa1.accept.edge1 = nfa2.initial
            nfa_stack.append(NFA(nfa1.initial, nfa2.accept))
        elif c == '|':
            nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
            initial = State()
            initial.edge1, initial.edge2 = nfa1.initial, nfa2.initial
            accept = State()
            nfa1.accept.edge1, nfa2.accept.edge1 = accept, accept
            nfa_stack.append(NFA(initial, accept))
        elif c == '+':
            nfa1 = nfa_stack.pop()
            initial, accept = State(), State()
            initial.edge1 = nfa1.initial
            nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.initial, accept
            nfa_stack.append(NFA(initial, accept))
        elif c == '?':
            nfa1 = nfa_stack.pop()
            initial, accept = State(), State()
            initial.edge1, initial.edge2 = nfa1.initial, accept
            nfa1.accept.edge1 = accept
            nfa_stack.append(NFA(initial, accept))
        else:
            accept, initial = State(), State()
            initial.label, initial.edge1 = c, accept
            nfa_stack.append(NFA(initial, accept))

    return nfa_stack.pop()

def followes(state):
    states = set()
    states.add(state)

    if state.label is None:
        if state.edge1 is not None:
            states |= followes(state.edge1)
        if state.edge2 is not None:
            states |= followes(state.edge2)

    return states

def match(infix, string, shunting_yard):
    # Usa la función infix_to_postfix de tu instancia ShuntingYard
    success, postfix = shunting_yard.infix_to_postfix(infix)
    if not success:
        print("Error al convertir a postfix:", postfix)  # Manejo simplificado del error
        return False

    nfa = compile(postfix)  # Asume que 'compile' ya ha sido definido como se mostró anteriormente
    
    visualize_nfa(nfa.initial, nfa.accept)

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
        dot.node(get_state_id(state))

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
    dot.render('afn_visualizado', view=True)