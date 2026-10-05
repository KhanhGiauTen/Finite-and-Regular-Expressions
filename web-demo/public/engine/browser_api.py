"""Bounded JSON adapter around the unchanged coursework algorithms."""
import json
from automata import RegexToNFAConverter, nfa_to_dfa


def validate_regex(expression):
    if not isinstance(expression, str) or not 1 <= len(expression) <= 32:
        raise ValueError("Regex must contain 1 to 32 characters.")
    alphabet = {c for c in expression if c in "abcdefghijklmnopqrstuvwxyz0123456789."}
    if len(alphabet) > 4 or expression.count("*") > 4:
        raise ValueError("Use at most four alphabet symbols and four stars.")
    depth, operand = 0, False
    for char in expression:
        if char in "abcdefghijklmnopqrstuvwxyz0123456789.E":
            operand = True
        elif char == "(":
            depth += 1
            operand = False
        elif char == ")":
            if depth == 0 or not operand:
                raise ValueError("Unbalanced or empty parentheses.")
            depth -= 1
            operand = True
        elif char == "+":
            if not operand:
                raise ValueError("Union requires a left operand.")
            operand = False
        elif char == "*":
            if not operand:
                raise ValueError("Star requires an operand.")
        else:
            raise ValueError("Supported literals: a-z, 0-9, dot; operators: +, *, parentheses; E is empty.")
    if depth or not operand:
        raise ValueError("Incomplete expression or unbalanced parentheses.")


def run_public(payload):
    params = json.loads(payload)
    if not isinstance(params, dict) or set(params) != {"regex", "text"}:
        raise ValueError("Expected regex and text only.")
    expression, text = params["regex"], params["text"]
    validate_regex(expression)
    if not isinstance(text, str) or len(text) > 128:
        raise ValueError("Test string must contain at most 128 characters.")
    nfa = RegexToNFAConverter().regex_to_nfa(expression)
    dfa = nfa_to_dfa(nfa)
    state = dfa["start"]
    trace = [{"index": 0, "symbol": "", "state": state}]
    for index, char in enumerate(text, 1):
        state = dfa["transitions"].get(state, {}).get(char) if state else None
        trace.append({"index": index, "symbol": char, "state": state})
    accepted = state in dfa["final"]
    for machine in (nfa, dfa):
        machine["final"] = sorted(machine["final"])
        states = {machine["start"], *machine["final"], *machine["transitions"]}
        for transitions in machine["transitions"].values():
            for target in transitions.values():
                states.update(target if isinstance(target, list) else [target])
        machine["states"] = sorted(states, key=lambda item: int(item[1:]))
    dfa["alphabet"] = nfa["alphabet"]
    if len(dfa["states"]) > 256:
        raise ValueError("DFA exceeds the 256-state browser display limit.")
    return json.dumps({"regex": expression, "text": text, "nfa": nfa, "dfa": dfa,
                       "trace": trace, "accepted": accepted}, allow_nan=False)
