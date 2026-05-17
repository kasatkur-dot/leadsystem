/* panels.jsx — Inspector, ScenarioControl, ScenarioTimeline, SafetyLegend */

const { useState: usePanelState, useEffect: usePanelEffect, useRef: usePanelRef } = React;

// ----- Inspector ------------------------------------------------------------

function InspectorPanel({ node, onClose, data }) {
  if (!node) return (
    <div className="inspector inspector--empty">
      <div className="inspector__placeholder">
        <div className="inspector__placeholder-icon">◌</div>
        <div className="inspector__placeholder-title">Inspector</div>
        <div className="inspector__placeholder-sub">
          Кликни любой узел, чтобы увидеть Role, OKR, KR, защитные метрики и инструменты.
        </div>
        <div className="inspector__keys">
          <span><kbd>scroll</kbd> zoom</span>
          <span><kbd>drag</kbd> pan</span>
          <span><kbd>space</kbd> play scenario</span>
        </div>
      </div>
    </div>
  );

  const isAgent = node.type === "agent";
  const isOrch = node.type === "orchestrator";
  const isArtifact = node.type === "artifact";
  const isSource = node.type === "source";
  const isModule = node.type === "module";
  const accent = node.accent || "#4DE3FF";

  // for artifact: find producer and consumer
  let producers = [], consumers = [];
  if (isArtifact) {
    data.edges.forEach(e => {
      if (e.target === node.id) producers.push(e.source);
      if (e.source === node.id) consumers.push(e.target);
    });
    const nodeById = {};
    [data.orchestrator, ...data.agents, ...data.services, ...data.sources, ...data.artifacts]
      .forEach(n => nodeById[n.id] = n);
    producers = producers.map(id => nodeById[id]).filter(Boolean);
    consumers = consumers.map(id => nodeById[id]).filter(Boolean);
  }

  return (
    <div className="inspector">
      <div className="inspector__head" style={{ borderColor: `${accent}33` }}>
        <div className="inspector__crumbs">
          <span className="inspector__crumb">{
            isAgent ? "agent" :
            isOrch ? "orchestrator" :
            isArtifact ? "artifact" :
            isSource ? "source" :
            isModule ? "module" : "node"
          }</span>
          {node.department && <><span className="inspector__sep">/</span>
            <span className="inspector__crumb">{node.department}</span></>}
        </div>
        <div className="inspector__title-row">
          <h2 className="inspector__title">{node.label}</h2>
          <button className="inspector__close" onClick={onClose}>×</button>
        </div>
        {node.sublabel && <div className="inspector__sublabel">{node.sublabel}</div>}
        {node.description && <p className="inspector__desc">{node.description}</p>}

        {(isAgent || isOrch) && (
          <div className="inspector__pills">
            <span className="pill" style={{ borderColor: `${statusToCSS(node.status)}55`, color: statusToCSS(node.status) }}>
              <i className="pill__dot" style={{ background: statusToCSS(node.status) }}/>
              {node.statusLabel || labelFor(node.status)}
            </span>
            {typeof node.readiness === "number" && (
              <span className="pill pill--muted">readiness · {node.readiness}%</span>
            )}
            {typeof node.krReadiness === "number" && (
              <span className="pill pill--muted">KR · {node.krReadiness}%</span>
            )}
          </div>
        )}
      </div>

      <div className="inspector__body">
        {isAgent && (
          <>
            {node.okr && (
              <Section title="OKR" accent={accent}>
                <p className="inspector__okr">{node.okr}</p>
              </Section>
            )}
            {node.krMetrics && (
              <Section title="KR metrics" accent={accent}>
                <div className="krgrid">
                  {node.krMetrics.map(m => {
                    const ratio = m.direction === "at_most"
                      ? (m.target === 0 ? (m.current === 0 ? 1 : 0) : 1 - Math.min(1, m.current / Math.max(1, m.target * 4)))
                      : Math.min(1, m.current / Math.max(1, m.target));
                    return (
                      <div key={m.label} className="kr">
                        <div className="kr__row">
                          <span className="kr__label">{m.label}</span>
                          <span className="kr__val">{m.current} / {m.target} <span className="kr__unit">{m.unit}</span></span>
                        </div>
                        <div className="kr__bar"><span style={{ width: `${ratio * 100}%`, background: accent }}/></div>
                      </div>
                    );
                  })}
                </div>
              </Section>
            )}
            {node.guardMetrics && (
              <Section title="Guard metrics" accent="#FF5C7A">
                <ul className="bullets bullets--guard">
                  {node.guardMetrics.map((g, i) => <li key={i}>{g}</li>)}
                </ul>
              </Section>
            )}
            <Section title="Inputs · Outputs" accent={accent}>
              <div className="twocol">
                <div>
                  <div className="twocol__label">inputs</div>
                  <ul className="bullets">{node.inputs.map((x,i)=> <li key={i}>{x}</li>)}</ul>
                </div>
                <div>
                  <div className="twocol__label">outputs</div>
                  <ul className="bullets">{node.outputs.map((x,i)=> <li key={i}>{x}</li>)}</ul>
                </div>
              </div>
            </Section>
            {node.sources && (
              <Section title={`Sources · ${node.sources.length}`} accent={accent}>
                <div className="chips">{node.sources.map(s => <span key={s} className="chip">{s}</span>)}</div>
              </Section>
            )}
            {node.skills && (
              <Section title="Skills" accent={accent}>
                <div className="chips">{node.skills.map(s => <span key={s} className="chip chip--ghost">{s}</span>)}</div>
              </Section>
            )}
            {node.modules && (
              <Section title="Modules" accent={accent}>
                <div className="chips">{node.modules.map(m => <span key={m} className="chip chip--solid">{m}</span>)}</div>
              </Section>
            )}
            {node.responsibilities && (
              <Section title="Responsibilities" accent={accent}>
                <ul className="bullets">{node.responsibilities.map((x,i)=> <li key={i}>{x}</li>)}</ul>
              </Section>
            )}
            {node.tools && (
              <Section title="Tools / API" accent={accent}>
                <div className="chips">{node.tools.map(t => <span key={t} className="chip chip--mono">{t}</span>)}</div>
              </Section>
            )}
            {node.nextAction && (
              <Section title="Next action" accent={accent}>
                <p className="inspector__next">{node.nextAction}</p>
              </Section>
            )}
            {node.exampleTask && (
              <Section title="Example task" accent="#8E9AAA">
                <p className="inspector__example">«{node.exampleTask}»</p>
              </Section>
            )}
          </>
        )}

        {isOrch && (
          <>
            <Section title="Responsibilities" accent={accent}>
              <ul className="bullets">{node.responsibilities.map((x,i)=> <li key={i}>{x}</li>)}</ul>
            </Section>
            <Section title="Inputs · Outputs" accent={accent}>
              <div className="twocol">
                <div><div className="twocol__label">inputs</div>
                  <ul className="bullets">{node.inputs.map((x,i)=> <li key={i}>{x}</li>)}</ul></div>
                <div><div className="twocol__label">outputs</div>
                  <ul className="bullets">{node.outputs.map((x,i)=> <li key={i}>{x}</li>)}</ul></div>
              </div>
            </Section>
            <Section title="State machine" accent={accent}>
              <div className="chips">{node.statusStates.map(s => <span key={s} className="chip chip--ghost">{s}</span>)}</div>
            </Section>
            <Section title="Files" accent={accent}>
              <div className="chips">{node.tools.map(t => <span key={t} className="chip chip--mono">{t}</span>)}</div>
            </Section>
          </>
        )}

        {isArtifact && (
          <>
            <Section title="Тип" accent={accent}>
              <p className="inspector__desc">Артефакт системы — конкретный deliverable, передаваемый между агентами через Redis или CRM.</p>
            </Section>
            {producers.length > 0 && (
              <Section title="Кто создаёт" accent={accent}>
                <div className="chips">{producers.map(p => <span key={p.id} className="chip">{p.label}</span>)}</div>
              </Section>
            )}
            {consumers.length > 0 && (
              <Section title="Кто принимает" accent={accent}>
                <div className="chips">{consumers.map(c => <span key={c.id} className="chip">{c.label}</span>)}</div>
              </Section>
            )}
          </>
        )}

        {isSource && (
          <>
            <Section title="Каналы" accent={accent}>
              <ul className="bullets">{node.list.map((s,i) => <li key={i}>{s}</li>)}</ul>
            </Section>
            <Section title="Назначение" accent={accent}>
              <p className="inspector__desc">Эти каналы агент 1 Scout раскладывает по агентам сбора, контента и аналитики. UTM-логика — на Agent 5.</p>
            </Section>
          </>
        )}

        {isModule && (
          <>
            <Section title="Responsibilities" accent={accent}>
              <ul className="bullets">{node.responsibilities.map((x,i)=> <li key={i}>{x}</li>)}</ul>
            </Section>
            <Section title="Inputs · Outputs" accent={accent}>
              <div className="twocol">
                <div><div className="twocol__label">inputs</div>
                  <ul className="bullets">{node.inputs.map((x,i)=> <li key={i}>{x}</li>)}</ul></div>
                <div><div className="twocol__label">outputs</div>
                  <ul className="bullets">{node.outputs.map((x,i)=> <li key={i}>{x}</li>)}</ul></div>
              </div>
            </Section>
            {node.tools && (
              <Section title="Files / API" accent={accent}>
                <div className="chips">{node.tools.map(t => <span key={t} className="chip chip--mono">{t}</span>)}</div>
              </Section>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function Section({ title, accent, children }) {
  return (
    <section className="isect">
      <div className="isect__head">
        <span className="isect__bullet" style={{ background: accent }}/>
        <span className="isect__title">{title}</span>
      </div>
      <div className="isect__body">{children}</div>
    </section>
  );
}

function statusToCSS(s) {
  return ({ active:"#66F2A6", queued:"#4DE3FF", waiting:"#F6C85F", done:"#66F2A6",
            blocked:"#FF5C7A", idle:"#8E9AAA" })[s] || "#8E9AAA";
}
function labelFor(s) {
  return ({ active:"Active", queued:"Queued", waiting:"Waiting", done:"Done",
            blocked:"Blocked", idle:"Idle" })[s] || "Idle";
}

// ----- Scenario control + timeline -----------------------------------------

function ScenarioControl({ data, scenarioId, setScenarioId, playing, setPlaying, stepIdx, totalSteps, onReset }) {
  return (
    <div className="scenario">
      <div className="scenario__left">
        <div className="scenario__tag">scenarios</div>
        <div className="scenario__list">
          {data.scenarios.map(s => (
            <button
              key={s.id}
              className={`scenario__btn ${scenarioId === s.id ? "is-active" : ""}`}
              onClick={() => { setScenarioId(s.id); onReset(); }}
            >
              <span className="scenario__btn-id">{s.id.toUpperCase()}</span>
              <span className="scenario__btn-label">{s.label}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="scenario__right">
        <div className="scenario__counter">
          step <span>{Math.min(stepIdx + 1, totalSteps)}</span> / {totalSteps}
        </div>
        <button className="scenario__play" onClick={() => setPlaying(p => !p)}>
          {playing
            ? <><svg width="10" height="12" viewBox="0 0 10 12"><rect x="0" y="0" width="3" height="12" fill="currentColor"/><rect x="7" y="0" width="3" height="12" fill="currentColor"/></svg> Pause</>
            : <><svg width="10" height="12" viewBox="0 0 10 12"><polygon points="0,0 10,6 0,12" fill="currentColor"/></svg> Play</>}
        </button>
        <button className="scenario__reset" onClick={onReset}>⟲</button>
      </div>
    </div>
  );
}

function ScenarioTimeline({ scenario, stepIdx }) {
  if (!scenario) return null;
  return (
    <div className="timeline">
      <div className="timeline__head">
        <span className="timeline__id">{scenario.id.toUpperCase()}</span>
        <span className="timeline__label">{scenario.label}</span>
        <span className="timeline__summary">{scenario.summary}</span>
      </div>
      <div className="timeline__track">
        {scenario.steps.map((s, i) => {
          const state = i < stepIdx ? "done" : i === stepIdx ? "active" : "queued";
          return (
            <div key={i} className={`tstep tstep--${state}`}>
              <div className="tstep__dot">
                {state === "done" ? "✓" : i + 1}
              </div>
              <div className="tstep__label">{s.t}</div>
              {s.artifact && <div className="tstep__artifact">→ {s.artifact.replace("art-","")}</div>}
              {i < scenario.steps.length - 1 && <div className="tstep__rail"/>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ----- Safety / legend ------------------------------------------------------

function SafetyLegend({ data }) {
  const [open, setOpen] = usePanelState(false);
  return (
    <div className={`safety ${open ? "" : "is-closed"}`}>
      <button className="safety__head" onClick={() => setOpen(o => !o)}>
        <span className="safety__dot"/>
        <span className="safety__title">safety locks</span>
        <span className="safety__count">{data.safety.length}</span>
        <span className="safety__chev">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <div className="safety__body">
          {data.safety.map(s => (
            <div key={s.id} className="lock">
              <div className="lock__bar"/>
              <div className="lock__text">
                <div className="lock__name">{s.label}</div>
                <div className="lock__reason">{s.reason}</div>
              </div>
            </div>
          ))}
          <div className="legend">
            <div className="legend__row"><span className="leg leg--cyan"/> handoff</div>
            <div className="legend__row"><span className="leg leg--amber dashed"/> review · approval</div>
            <div className="legend__row"><span className="leg leg--green"/> artifact</div>
            <div className="legend__row"><span className="leg leg--grey"/> hierarchy</div>
            <div className="legend__row"><span className="leg leg--red dashed"/> safety lock</div>
          </div>
        </div>
      )}
    </div>
  );
}

// ----- System metrics strip -------------------------------------------------

function MetricsStrip({ data }) {
  const total = data.agents.length;
  const avgReadiness = Math.round(data.agents.reduce((a, n) => a + n.readiness, 0) / total);
  const avgKR = Math.round(data.agents.reduce((a, n) => a + n.krReadiness, 0) / total);
  const blocked = data.agents.filter(a => a.status === "blocked").length;
  const totalNodes =
    1 + data.agents.length + data.services.length + data.sources.length + data.artifacts.length;
  const channelsTotal = data.summary?.channelsTotal || 0;
  const wave1 = data.summary?.wave1Channels || 0;
  const subroles = data.summary?.subrolesCount || 0;

  return (
    <div className="metricstrip">
      <Metric k="agents"          v={`${total}`}            sub="продуктовых"/>
      <Metric k="subroles"        v={`${subroles}`}         sub="внутри 6 агентов"/>
      <Metric k="readiness"       v={`${avgReadiness}%`}    sub="средняя по агентам"/>
      <Metric k="KR readiness"    v={`${avgKR}%`}           sub="по 6 контрактам"/>
      <Metric k="channels"        v={`${channelsTotal}`}    sub={`${wave1} первой волны`}/>
      <Metric k="artifacts"       v={`${data.artifacts.length}`} sub="deliverables"/>
      <Metric k="safety locks"    v={`${data.safety.length}`} sub="активных правил"/>
      <Metric k="nodes"           v={`${totalNodes}`}       sub="в графе"/>
    </div>
  );
}
function Metric({ k, v, sub, warn }) {
  return (
    <div className={`metric ${warn ? "metric--warn" : ""}`}>
      <div className="metric__k">{k}</div>
      <div className="metric__v">{v}</div>
      <div className="metric__sub">{sub}</div>
    </div>
  );
}

// ----- Agent control chat / voice ------------------------------------------

function AgentControlPanel({ data, selected }) {
  const routes = data.agentControl?.routes || [];
  const liveEnabled = Boolean(data.agentControl?.live_llm_enabled);
  const agents = [
    { id: "orchestrator", label: "AI Orchestrator" },
    ...data.agents.map(agent => ({ id: agent.dashboardAgentId, label: agent.label })),
  ];
  const [mode, setMode] = usePanelState("manage");
  const [targetAgentId, setTargetAgentId] = usePanelState(selected?.dashboardAgentId || "orchestrator");
  const [message, setMessage] = usePanelState("");
  const [status, setStatus] = usePanelState("idle");
  const [recording, setRecording] = usePanelState(false);
  const [log, setLog] = usePanelState([
    {
      role: "system",
      text: window.location.protocol === "file:"
        ? "Чат открыт как файл. Для работы команд открой http://127.0.0.1:8788/ через backend."
        : liveEnabled
          ? "Локальный пульт готов. Текстовый LLM включён; Redis, Bitrix24, Telegram, scheduler и publisher не вызываются."
          : "Локальный пульт готов. Сейчас команды идут в preview: внешние сервисы не вызываются.",
    },
  ]);
  const mediaRef = usePanelRef(null);
  const chunksRef = usePanelRef([]);

  usePanelEffect(() => {
    if (selected?.dashboardAgentId) setTargetAgentId(selected.dashboardAgentId);
  }, [selected?.dashboardAgentId]);

  const currentRoute = routeForMode(routes, mode);

  async function sendMessage(event) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || status === "sending") return;
    setMessage("");
    setStatus("sending");
    setLog(items => [...items, { role: "user", text: trimmed }]);
    try {
      const endpoint = endpointForMode(mode);
      const payload = mode === "image"
        ? { prompt: trimmed, targetAgentId }
        : mode === "knowledge"
          ? { query: trimmed, targetAgentId }
          : { message: trimmed, mode, targetAgentId };
      const response = await fetch(apiUrl(endpoint), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await parseControlJson(response);
      setLog(items => [...items, responseToLogItem(data, mode)]);
      setStatus("idle");
    } catch (error) {
      setLog(items => [...items, { role: "error", text: `Ошибка локального control API: ${error.message}` }]);
      setStatus("idle");
    }
  }

  async function toggleRecording() {
    if (recording) {
      mediaRef.current?.stop();
      setRecording(false);
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setLog(items => [...items, { role: "error", text: "Браузер не дал доступ к записи голоса или MediaRecorder недоступен." }]);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        setStatus("sending");
        try {
          const response = await fetch(apiUrl("/api/agent-control/voice"), {
            method: "POST",
            headers: { "Content-Type": blob.type },
            body: blob,
          });
          const payload = await parseControlJson(response);
          setLog(items => [...items, responseToLogItem(payload, "voice")]);
        } catch (error) {
          setLog(items => [...items, { role: "error", text: `Ошибка voice endpoint: ${error.message}` }]);
        } finally {
          setStatus("idle");
        }
      };
      mediaRef.current = recorder;
      recorder.start();
      setRecording(true);
      setLog(items => [...items, { role: "system", text: "Запись началась. Нажми ещё раз, чтобы остановить." }]);
    } catch (error) {
      setLog(items => [...items, { role: "error", text: `Не удалось начать запись: ${error.message}` }]);
    }
  }

  return (
    <section className="agent-control">
      <div className="agent-control__head">
        <div>
          <div className="agent-control__eyebrow">agent control</div>
          <h3 className="agent-control__title">Chat / voice command center</h3>
        </div>
        <span className={`agent-control__mode ${liveEnabled ? "is-live" : ""}`}>
          {liveEnabled ? "live llm" : "dry-run"}
        </span>
      </div>

      <div className="agent-control__routes">
        {["agent_control", "default_free", "development", "marketing", "transcription", "image", "embedding"].map(key => {
          const route = routes.find(item => item.key === key);
          return route ? <span key={key} className="route-chip">{route.label}</span> : null;
        })}
      </div>

      <div className="agent-control__log" aria-live="polite">
        {log.map((item, index) => (
          <div key={index} className={`agent-msg agent-msg--${item.role}`}>
            <span className="agent-msg__role">{item.role}</span>
            <span className="agent-msg__text">{item.text}</span>
            {item.meta && <span className="agent-msg__meta">{item.meta}</span>}
          </div>
        ))}
      </div>

      <form className="agent-control__form" onSubmit={sendMessage}>
        <div className="agent-control__selectors">
          <select value={mode} onChange={event => setMode(event.target.value)}>
            <option value="manage">{modeOptionLabel(routes, "manage", "Управление агентами")}</option>
            <option value="default">{modeOptionLabel(routes, "default", "Обычная задача")}</option>
            <option value="develop">{modeOptionLabel(routes, "develop", "Разработка")}</option>
            <option value="marketing">{modeOptionLabel(routes, "marketing", "Маркетинг")}</option>
            <option value="knowledge">Поиск в базе знаний · embeddings</option>
            <option value="image">Картинка в чат · Kling/Nano Banana</option>
          </select>
          <select value={targetAgentId} onChange={event => setTargetAgentId(event.target.value)}>
            {agents.map(agent => <option key={agent.id} value={agent.id}>{agent.label}</option>)}
          </select>
        </div>
        <div className="agent-control__inputrow">
          <textarea
            value={message}
            onChange={event => setMessage(event.target.value)}
            onKeyDown={event => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            placeholder="Напиши команду агенту или запрос для базы знаний..."
            rows="2"
          />
          <button className="agent-control__voice" type="button" onClick={toggleRecording}>
            {recording ? "Stop" : "Voice"}
          </button>
          <button className="agent-control__send" type="submit" disabled={!message.trim() || status === "sending"}>
            {status === "sending" ? "..." : "Send"}
          </button>
        </div>
        <div className="agent-control__route-note">
          route: {currentRoute?.label || "unknown"} · model: {currentRoute?.model || "not configured"}
        </div>
        <div className="agent-control__help">
          Enter отправляет · Shift+Enter перенос строки · текущий режим: {data.agentControl?.runtime_mode || "unknown"}
        </div>
      </form>
    </section>
  );
}

function endpointForMode(mode) {
  if (mode === "image") return "/api/agent-control/image";
  if (mode === "knowledge") return "/api/agent-control/knowledge-search";
  return "/api/agent-control/chat";
}

function controlApiBase() {
  const configured = window.AGENT_CONTROL_API_BASE || window.AGENT_DATA?.agentControl?.api_base_url;
  if (configured) return String(configured).replace(/\/$/, "");
  if (window.location.protocol === "file:") return "http://127.0.0.1:8788";
  const host = window.location.hostname;
  const isLocal = host === "127.0.0.1" || host === "localhost";
  if (isLocal && window.location.port && window.location.port !== "8788") {
    return "http://127.0.0.1:8788";
  }
  return "";
}

function apiUrl(path) {
  return `${controlApiBase()}${path}`;
}

async function parseControlJson(response) {
  const contentType = response.headers.get("content-type") || "";
  const text = await response.text();
  if (!contentType.includes("application/json")) {
    const hint = text.trim().startsWith("<!DOCTYPE") || text.trim().startsWith("<html")
      ? "Открыта не backend-страница агентской системы. Открой http://127.0.0.1:8788/ или запусти backend на порту 8788."
      : "Control API вернул не JSON.";
    throw new Error(`${hint} HTTP ${response.status}.`);
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Control API вернул повреждённый JSON: ${error.message}`);
  }
}

function routeForMode(routes, mode) {
  const key = ({
    manage: "agent_control",
    agent_control: "agent_control",
    default: "default_free",
    develop: "development",
    marketing: "marketing",
    knowledge: "knowledge",
    image: "image",
  })[mode] || "default_free";
  return routes.find(route => route.key === key);
}

function modeOptionLabel(routes, mode, label) {
  const route = routeForMode(routes, mode);
  return route ? `${label} · ${route.label}` : label;
}

function responseToLogItem(payload, mode) {
  if (mode === "image") {
    return {
      role: "assistant",
      text: `${payload.status}: картинка не генерировалась, маршрут подготовлен.`,
      meta: payload.route ? `${payload.route.label} · ${payload.route.model}` : "",
    };
  }
  if (mode === "knowledge") {
    return {
      role: "assistant",
      text: `${payload.status}: поиск по базе знаний пока preview, совпадения не запрашивались.`,
      meta: payload.embedding_route ? `${payload.embedding_route.label} · ${payload.embedding_route.model}` : "",
    };
  }
  if (mode === "voice") {
    return {
      role: "assistant",
      text: `${payload.status}: аудио получено локально, расшифровка Whisper пока не запускалась.`,
      meta: payload.route ? `${payload.route.label} · ${payload.received_audio?.bytes || 0} bytes` : "",
    };
  }
  return {
    role: "assistant",
    text: payload.assistant_message || payload.status || "Ответ получен.",
    meta: payload.selected_route ? `${payload.selected_route.label} · ${payload.llm_status}` : "",
  };
}

window.InspectorPanel = InspectorPanel;
window.ScenarioControl = ScenarioControl;
window.ScenarioTimeline = ScenarioTimeline;
window.SafetyLegend = SafetyLegend;
window.MetricsStrip = MetricsStrip;
window.AgentControlPanel = AgentControlPanel;
