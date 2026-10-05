import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";
import {
  ArrowLeft,
  Network,
  Play,
  Square,
  Pause,
  RotateCcw,
  SkipForward,
  Maximize,
  Plus,
  Minus,
  Download,
  Github,
  Check,
} from "lucide-react";
import { useEngine, dataUrl } from "./use-engine";
import "./styles.css";

cytoscape.use(dagre);
const PRESETS = ["(a+b)*abb", "a*b*", "(ab)*", "a+E"];

function Graph({ machine, active, graphRef }) {
  const container = useRef(null);
  useEffect(() => {
    if (!machine) return;
    const elements = machine.states.map((id) => ({
      data: { id, label: id },
      classes: [
        machine.final.includes(id) ? "final" : "",
        machine.start === id ? "start" : "",
      ].join(" "),
    }));
    for (const [source, transitions] of Object.entries(machine.transitions)) {
      for (const [symbol, targets] of Object.entries(transitions)) {
        for (const target of Array.isArray(targets) ? targets : [targets]) {
          elements.push({
            data: {
              id: `${source}-${symbol || "empty"}-${target}`,
              source,
              target,
              label: symbol || "\u03b5",
            },
          });
        }
      }
    }
    const cy = cytoscape({
      container: container.current,
      elements,
      minZoom: 0.15,
      maxZoom: 4,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            width: 42,
            height: 42,
            "background-color": "#edf4f7",
            "border-width": 1.5,
            "border-color": "#9bb5c1",
            color: "#36515d",
            "font-family": "IBM Plex Mono, monospace",
            "font-size": 12,
            "text-valign": "center",
            "text-halign": "center",
          },
        },
        {
          selector: "node.final",
          style: {
            "border-width": 4,
            "border-style": "double",
            "border-color": "#b88322",
            "background-color": "#fff4d9",
          },
        },
        { selector: "node.start", style: { "border-color": "#197794" } },
        {
          selector: "node.active",
          style: {
            "background-color": "#087f83",
            color: "#fff",
            "border-color": "#05595e",
          },
        },
        {
          selector: "edge",
          style: {
            label: "data(label)",
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "line-color": "#8da7b4",
            "target-arrow-color": "#8da7b4",
            width: 1.5,
            "font-size": 12,
            color: "#425e6b",
            "text-background-color": "#fff",
            "text-background-opacity": 1,
            "text-background-padding": "3px",
            "loop-direction": "-40deg",
            "loop-sweep": "80deg",
          },
        },
      ],
      layout: {
        name: "dagre",
        rankDir: "LR",
        nodeSep: 42,
        rankSep: 70,
        padding: 35,
        animate: false,
      },
    });
    graphRef.current = cy;
    const resize = new ResizeObserver(() => {
      cy.resize();
      cy.fit(undefined, 35);
    });
    resize.observe(container.current);
    return () => {
      resize.disconnect();
      cy.destroy();
      graphRef.current = null;
    };
  }, [machine, graphRef]);
  useEffect(() => {
    const cy = graphRef.current;
    if (!cy || !machine) return;
    cy.nodes().removeClass("active");
    if (active) cy.getElementById(active).addClass("active");
  }, [active, machine, graphRef]);
  return (
    <div className="graph-shell">
      {machine ? (
        <div
          className="graph"
          ref={container}
          role="img"
          aria-label="Automaton state graph"
        />
      ) : (
        <div className="graph-empty">No automaton built yet</div>
      )}
      <div className="legend">
        <span>
          <i className="dot active" />
          Current state
        </span>
        <span>
          <i className="dot final" />
          Accepting state
        </span>
        <span>Initial state: {machine?.start || "--"}</span>
      </div>
    </div>
  );
}

function App() {
  const [regex, setRegex] = useState("(a+b)*abb");
  const [text, setText] = useState("aabb");
  const [mode, setMode] = useState("dfa");
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const graph = useRef(null);
  const engine = useEngine();
  const result = engine.result;
  const stale = result && (result.regex !== regex || result.text !== text);
  const machine = result?.[mode];
  const last = result ? result.trace.length - 1 : 0;
  useEffect(() => {
    setStep(0);
    setPlaying(false);
  }, [result]);
  useEffect(() => {
    if (!playing || step >= last) {
      if (playing) setPlaying(false);
      return;
    }
    const timer = setTimeout(() => setStep((value) => value + 1), 650);
    return () => clearTimeout(timer);
  }, [playing, step, last]);
  const active = mode === "dfa" ? result?.trace[step]?.state : machine?.start;
  const run = (event) => {
    event.preventDefault();
    setPlaying(false);
    engine.run({ regex, text });
  };
  return (
    <>
      <header>
        <strong>
          <Network />
          Automata Studio
        </strong>
        <nav>
          <a href="https://khanh-portfolio-ochre.vercel.app/projects/automata-studio">
            <ArrowLeft /> Portfolio
          </a>
          <a
            href="https://github.com/KhanhGiauTen/Finite-and-Regular-Expressions"
            target="_blank"
            rel="noreferrer"
          >
            <Github /> Source
          </a>
        </nav>
      </header>
      <main>
        <div className="heading">
          <div>
            <div className="eyebrow">Algorithms / Formal languages</div>
            <h1>From expression to state.</h1>
          </div>
          <span className="badge">
            <Check />
            On-device Python
          </span>
        </div>
        <div className="workspace">
          <aside className="controls">
            <h2>Expression</h2>
            <form onSubmit={run}>
              <label>
                Regular expression
                <input
                  className="mono"
                  value={regex}
                  maxLength={32}
                  onChange={(event) => setRegex(event.target.value)}
                  required
                  spellCheck="false"
                  autoCapitalize="off"
                  autoComplete="off"
                />
              </label>
              <div className="presets">
                {PRESETS.map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => {
                      setRegex(preset);
                      setPlaying(false);
                    }}
                  >
                    {preset}
                  </button>
                ))}
              </div>
              <label>
                Test string
                <input
                  className="mono"
                  value={text}
                  maxLength={128}
                  onChange={(event) => {
                    setText(event.target.value);
                    setPlaying(false);
                  }}
                  spellCheck="false"
                  autoCapitalize="off"
                  autoComplete="off"
                  placeholder="Empty string"
                />
              </label>
              <div className="actions">
                <button className="primary" disabled={engine.busy}>
                  <Play />
                  Build & test
                </button>
                {engine.busy && (
                  <button type="button" onClick={engine.stop}>
                    <Square />
                    Stop
                  </button>
                )}
              </div>
            </form>
            <p className="status" role="status">
              {engine.status}
            </p>
            {engine.error && (
              <p className="error" role="alert">
                {engine.error}
              </p>
            )}
            <div className="disclosure muted">
              Educational subset: concatenation, union (+), Kleene star (*),
              parentheses and empty E. Not JavaScript or PCRE syntax.
            </div>
            <p className="muted">
              Original team coursework engine. Inputs stay on your device; no
              account, remote execution or saved submissions.
            </p>
          </aside>
          <section className="result-area" aria-label="Automaton results">
            {stale && (
              <div className="stale">
                Inputs changed. Results below belong to the last completed run.
              </div>
            )}
            <div className="toolbar">
              <div className="tabs" role="tablist" aria-label="Automaton type">
                {["dfa", "nfa"].map((type) => (
                  <button
                    key={type}
                    role="tab"
                    aria-selected={mode === type}
                    onClick={() => setMode(type)}
                  >
                    {type.toUpperCase()}
                  </button>
                ))}
              </div>
              <div className="toolbar-actions">
                <button
                  className="icon"
                  title="Zoom out"
                  aria-label="Zoom out"
                  disabled={!machine}
                  onClick={() =>
                    graph.current?.zoom(graph.current.zoom() / 1.2)
                  }
                >
                  <Minus />
                </button>
                <button
                  className="icon"
                  title="Zoom in"
                  aria-label="Zoom in"
                  disabled={!machine}
                  onClick={() =>
                    graph.current?.zoom(graph.current.zoom() * 1.2)
                  }
                >
                  <Plus />
                </button>
                <button
                  className="icon"
                  title="Fit graph"
                  aria-label="Fit graph"
                  disabled={!machine}
                  onClick={() => graph.current?.fit(undefined, 35)}
                >
                  <Maximize />
                </button>
              </div>
            </div>
            <Graph machine={machine} active={active} graphRef={graph} />
            <div className="metrics">
              <div className="metric">
                <span>NFA states</span>
                <strong>{result?.nfa.states.length ?? "--"}</strong>
              </div>
              <div className="metric">
                <span>DFA states</span>
                <strong>{result?.dfa.states.length ?? "--"}</strong>
              </div>
              <div className="metric">
                <span>Alphabet</span>
                <strong>{result?.dfa.alphabet.join(" ") || "--"}</strong>
              </div>
              <div className="metric">
                <span>Python execution</span>
                <strong>
                  {result ? engine.milliseconds.toFixed(1) : "--"}
                  <small>ms</small>
                </strong>
              </div>
            </div>
            <div className="trace-section">
              <div className="toolbar">
                <h2>Recognition trace</h2>
                <div className="toolbar-actions">
                  <button
                    className="icon"
                    title="Reset trace"
                    aria-label="Reset trace"
                    disabled={!result}
                    onClick={() => {
                      setStep(0);
                      setPlaying(false);
                    }}
                  >
                    <RotateCcw />
                  </button>
                  <button
                    className="icon"
                    title={playing ? "Pause trace" : "Play trace"}
                    aria-label={playing ? "Pause trace" : "Play trace"}
                    disabled={!result || last === 0 || stale}
                    onClick={() => {
                      if (!playing && step === last) setStep(0);
                      setMode("dfa");
                      setPlaying((value) => !value);
                    }}
                  >
                    {playing ? <Pause /> : <Play />}
                  </button>
                  <button
                    className="icon"
                    title="Next symbol"
                    aria-label="Next symbol"
                    disabled={!result || step >= last || stale}
                    onClick={() => {
                      setMode("dfa");
                      setPlaying(false);
                      setStep((value) => value + 1);
                    }}
                  >
                    <SkipForward />
                  </button>
                </div>
              </div>
              <div className="trace-symbols">
                {result?.trace.map((item, index) => (
                  <button
                    key={index}
                    className={index === step ? "current" : ""}
                    aria-pressed={index === step}
                    aria-label={`Step ${index}: ${item.symbol || "start"}`}
                    title={item.state || "No transition"}
                    onClick={() => {
                      setMode("dfa");
                      setStep(index);
                      setPlaying(false);
                    }}
                  >
                    {item.symbol || "\u03b5"}
                  </button>
                ))}
              </div>
              <p className="muted">
                {result
                  ? `Step ${step} / ${last} · State ${result.trace[step]?.state || "no transition"}`
                  : "No completed run"}
              </p>
              {result && (
                <p className={`verdict ${!result.accepted ? "rejected" : ""}`}>
                  Completed result: {result.accepted ? "Accepted" : "Rejected"}{" "}
                  {result.text ? `\u201c${result.text}\u201d` : "empty string"}
                </p>
              )}
            </div>
            {machine && (
              <>
                <div className="section-title">
                  <h2>Transition table</h2>
                  <a
                    className="export"
                    download="automata-result.json"
                    href={dataUrl(result)}
                  >
                    <Download />
                    JSON
                  </a>
                </div>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>State</th>
                        {[
                          ...(mode === "nfa" ? [""] : []),
                          ...machine.alphabet,
                        ].map((symbol) => (
                          <th key={symbol}>{symbol || "\u03b5"}</th>
                        ))}
                        <th>Accepting</th>
                      </tr>
                    </thead>
                    <tbody>
                      {machine.states.map((state) => (
                        <tr key={state}>
                          <td>{state}</td>
                          {[
                            ...(mode === "nfa" ? [""] : []),
                            ...machine.alphabet,
                          ].map((symbol) => (
                            <td key={symbol}>
                              {[]
                                .concat(
                                  machine.transitions[state]?.[symbol] || [],
                                )
                                .join(", ") || "--"}
                            </td>
                          ))}
                          <td>
                            {machine.final.includes(state) ? "Yes" : "No"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </section>
        </div>
        <footer>
          <span>Nguyen Quoc Khanh / Team coursework</span>
          <span>Thompson construction + subset construction</span>
        </footer>
      </main>
    </>
  );
}
createRoot(document.getElementById("root")).render(<App />);
