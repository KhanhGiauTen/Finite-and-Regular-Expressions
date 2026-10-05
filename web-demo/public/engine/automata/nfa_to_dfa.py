def nfa_to_dfa(nfa):
    def get_epsilon_closure(states, transitions):
        stack = list(states)
        closure = set(states)
        while stack:
            s = stack.pop()
            if s in transitions and '' in transitions[s]:
                for next_s in transitions[s]['']:
                    if next_s not in closure:
                        closure.add(next_s)
                        stack.append(next_s)
        return frozenset(sorted(list(closure))) # Frozenset để làm key dict

    start_closure = get_epsilon_closure([nfa['start']], nfa['transitions'])
    
    dfa_states = {start_closure: "q0"} # Map {Set_NFA: Name_DFA}
    dfa_trans = {}
    queue = [start_closure]
    processed_count = 0
    
    while queue:
        current_set = queue.pop(0)
        current_name = dfa_states[current_set]
        
        for char in nfa['alphabet']:
            next_set_raw = set()
            for s in current_set:
                if s in nfa['transitions'] and char in nfa['transitions'][s]:
                    for target in nfa['transitions'][s][char]:
                        next_set_raw.add(target)
            
            if not next_set_raw: continue # Không có đường đi
            
            next_closure = get_epsilon_closure(next_set_raw, nfa['transitions'])
            
            if next_closure not in dfa_states:
                processed_count += 1
                new_name = f"q{processed_count}"
                dfa_states[next_closure] = new_name
                queue.append(next_closure)
            
            if current_name not in dfa_trans: dfa_trans[current_name] = {}
            dfa_trans[current_name][char] = dfa_states[next_closure]

    # Xác định Final States
    dfa_finals = set()
    for state_set, name in dfa_states.items():
        if not state_set.isdisjoint(nfa['final']):
            dfa_finals.add(name)

    return {
        'transitions': dfa_trans,
        'start': "q0",
        'final': dfa_finals
    }
