# Browser Demo

Public production URL: https://automata-khanh-demo.vercel.app

## Scope

The original `automata/regex_to_nfa.py` and `automata/nfa_to_dfa.py` are unchanged.
`browser_api.py` validates JSON, converts the expression and traces recognition
using the resulting DFA. React and Cytoscape/Dagre replace Tkinter/Graphviz only
for the public interface. This is a team educational tool, not sole-authorship
or production-regex-engine work.

The supported browser subset is a-z, digits, literal dot, concatenation, union
`+`, Kleene star `*`, parentheses and `E` for the empty word. Leading literal
plus and the desktop converter's alternate Unicode epsilon are not offered.
Inputs are limited to 32 expression characters, four alphabet symbols, four
stars, 128 test characters and 256 displayed DFA states. Invalid syntax is
rejected before the original converter's permissive parsing can ignore it.
Subset construction can still grow exponentially; execution is in a worker with
a 60-second deadline and Stop/retry controls.

NFA/DFA selection, zoom/fit, recognition step/play/reset and the transition table
are live. Trace states belong to the DFA; the NFA view highlights its initial
state, not a falsely inferred single NFA recognition state. No minimization or
new language features are claimed. Graph layout has no motion transitions.

## Privacy And Deployment

Inputs execute on the visitor's device. No API, persistence, telemetry or remote
code evaluation is added. Only required static runtime/source files are served.
The JSON export is a native local data URL. As with earlier demos, the embedded
browser's download-event capture does not validate local data URL transfers;
the export payload itself can be inspected and parsed.

Vercel Git project: `automata-khanh-demo`, repository root setting `web-demo`,
Node 24.x. No paid server, domain or API key is required. `public/runtime` is
generated from pinned Pyodide 314.0.7 at build time; source copies and SHA256
manifest in `public/engine` are tracked for reproducible standalone builds.
The original source takes precedence on whole-repository builds.

## Verification

```powershell
python -m unittest test_browser_api.py
cd web-demo
npm ci
npm test
npm run build
npm run dev -- --port 3004
```

Five native tests include exhaustive short-string comparison with Python's
regex engine for the translated subset, syntax/bounds, epsilon and dead states.
Four fixtures additionally compare native Python with the actual Pyodide runtime
and verify packaged source hashes. No original generated diagram is overwritten.

Primary implementation references: [Pyodide workers](https://pyodide.org/en/stable/usage/webworker.html),
[Cytoscape](https://js.cytoscape.org/), [Dagre extension](https://github.com/cytoscape/cytoscape.js-dagre).
