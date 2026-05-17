/* app.jsx — top-level App, scenario playback hook */

const { useState: useAppState, useEffect: useAppEffect, useRef: useAppRef, useCallback: useAppCallback } = React;

function useScenarioPlayback(scenario, onStepChange) {
  const [stepIdx, setStepIdx] = useAppState(0);
  const [playing, setPlaying] = useAppState(false);
  const timer = useAppRef(null);

  // reset when scenario changes
  useAppEffect(() => {
    setStepIdx(0);
    setPlaying(false);
  }, [scenario?.id]);

  // tick
  useAppEffect(() => {
    if (!playing || !scenario) return;
    timer.current = setTimeout(() => {
      setStepIdx(i => {
        if (i + 1 >= scenario.steps.length) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, 1400);
    return () => clearTimeout(timer.current);
  }, [playing, stepIdx, scenario]);

  const reset = useAppCallback(() => {
    setStepIdx(0);
    setPlaying(false);
  }, []);

  // notify
  useAppEffect(() => {
    if (scenario && onStepChange) onStepChange(scenario.steps[stepIdx]);
  }, [scenario, stepIdx]);

  return { stepIdx, playing, setPlaying, reset };
}

function App() {
  const data = window.AGENT_DATA;
  const [selected, setSelected] = useAppState(null);
  const [expanded, setExpanded] = useAppState({});
  const [scenarioId, setScenarioId] = useAppState(data.scenarios?.[0]?.id || "s1");
  const [drawerOpen, setDrawerOpen] = useAppState(false);

  const scenario = data.scenarios.find(s => s.id === scenarioId) || data.scenarios[0];
  const { stepIdx, playing, setPlaying, reset } =
    useScenarioPlayback(scenario, () => {});
  const waitingCount = data.agents.filter(a => ["waiting", "blocked", "queued"].includes(a.status)).length;
  const generatedAt = data.meta?.generatedAt || "";

  const toggleExpanded = (id) => setExpanded(e => ({ ...e, [id]: !e[id] }));

  // Active node from current scenario step
  const activeNodeId = scenario && stepIdx >= 0 && playing
    ? scenario.steps[stepIdx]?.node
    : (scenario && playing === false && stepIdx > 0 ? scenario.steps[stepIdx]?.node : null);

  // Path active when playing or stepIdx > 0
  const scenarioPath = (playing || stepIdx > 0) && scenario ? scenario.path : [];
  const dimNonScenario = playing || stepIdx > 0;

  // Inspector responsive drawer for narrow viewports
  useAppEffect(() => {
    if (selected) setDrawerOpen(true);
  }, [selected]);
  useAppEffect(() => {
    if (!drawerOpen) setSelected(null);
  }, [drawerOpen]);

  // keyboard: space = play/pause, esc = clear
  useAppEffect(() => {
    const onKey = (e) => {
      if (e.code === "Space") {
        e.preventDefault();
        setPlaying(p => !p);
      } else if (e.code === "Escape") {
        setSelected(null);
        setDrawerOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar__left">
          <div className="logo">
            <span className="logo__square"/>
            <span className="logo__text">design-studio-lead-engine</span>
          </div>
          <div className="topbar__divider"/>
          <div className="topbar__project">
            <span className="topbar__project-tag">project</span>
            <span className="topbar__project-name">Вектор Плюс-Про</span>
          </div>
          <div className="topbar__divider"/>
          <div className="topbar__chip topbar__chip--ok">
            <span className="topbar__chip-dot"/>
            <span>orchestrator {String(data.meta?.overallStatus || "online").toLowerCase()}</span>
          </div>
          <div className="topbar__chip topbar__chip--warn">
            <span className="topbar__chip-dot"/>
            <span>{waitingCount} agents need control</span>
          </div>
        </div>
        <div className="topbar__right">
          <span className="topbar__hint">live local · {data.meta?.sourceReport || "agent_dashboard.json"}</span>
          <span className="topbar__clock">{generatedAt || "generated locally"}</span>
        </div>
      </header>

      <MetricsStrip data={data}/>

      <main className="main">
        <div className="main__graph">
          <AgentSystemMap
            data={data}
            selected={selected}
            setSelected={setSelected}
            expanded={expanded}
            toggleExpanded={toggleExpanded}
            scenarioPath={scenarioPath}
            activeNodeId={activeNodeId}
            dimNonScenario={dimNonScenario}
          />
          <SafetyLegend data={data}/>
        </div>

        <aside className={`main__aside ${drawerOpen ? "is-open" : ""}`}>
          <InspectorPanel node={selected} data={data}
                          onClose={() => { setSelected(null); setDrawerOpen(false); }}/>
        </aside>
      </main>

      <footer className="footer footer--with-control">
        <div className="footer__scenario">
          <ScenarioControl
            data={data}
            scenarioId={scenarioId}
            setScenarioId={setScenarioId}
            playing={playing}
            setPlaying={setPlaying}
            stepIdx={stepIdx}
            totalSteps={scenario?.steps?.length || 0}
            onReset={reset}
          />
          <ScenarioTimeline scenario={scenario} stepIdx={stepIdx}/>
        </div>
        <AgentControlPanel data={data} selected={selected}/>
      </footer>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
