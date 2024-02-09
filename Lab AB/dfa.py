
from graphviz import Digraph

class DFA:
    def __init__(self):
        self.states = []  # Lista de nombres de los estados del DFA
        self.transitions = {}  # Diccionario de transiciones; clave: estado, valor: diccionario (clave: símbolo, valor: estado destino)
        self.initial_state = None  # Estado inicial del DFA
        self.accept_states = []  # Lista de estados de aceptación

    def add_state(self, state, is_accept=False):
        if state not in self.states:
            self.states.append(state)
            self.transitions[state] = {}
        if is_accept:
            self.accept_states.append(state)

    def add_transition(self, state_from, symbol, state_to):
        if state_from in self.transitions:
            self.transitions[state_from][symbol] = state_to

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


def visualize_dfa(dfa):
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
    dot.render('dfa', view=True, cleanup=True)


def simulate_dfa(dfa, input_string):
    current_state = dfa.initial_state  # Comenzamos en el estado inicial del DFA

    for symbol in input_string:
        # Verificar si existe una transición para el símbolo actual desde el estado actual
        if symbol in dfa.transitions[current_state]:
            current_state = dfa.transitions[current_state][symbol]  # Mover al siguiente estado
        else:
            return False  # Si no hay transición para el símbolo, la cadena no es aceptada

    # La cadena es aceptada si terminamos en un estado de aceptación después de procesar todos los símbolos
    return current_state in dfa.accept_states

