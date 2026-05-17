/* graph.jsx — SVG-based node graph. Hand-positioned, pan/zoom, edge pulse. */

const { useState, useEffect, useRef, useMemo, useCallback } = React;

// ------------ helpers --------------------------------------------------------

function edgePath(a, b) {
  // bezier between two rects' nearest edges
  const ax = a.x + a.w / 2, ay = a.y + a.h / 2;
  const bx = b.x + b.w / 2, by = b.y + b.h / 2;
  const dx = bx - ax, dy = by - ay;
  const horiz = Math.abs(dx) > Math.abs(dy);

  let p1, p2;
  if (horiz) {
    p1 = { x: dx > 0 ? a.x + a.w : a.x, y: ay };
    p2 = { x: dx > 0 ? b.x : b.x + b.w, y: by };
  } else {
    p1 = { x: ax, y: dy > 0 ? a.y + a.h : a.y };
    p2 = { x: bx, y: dy > 0 ? b.y : b.y + b.h };
  }
  const c1 = horiz
    ? { x: p1.x + (p2.x - p1.x) * 0.5, y: p1.y }
    : { x: p1.x, y: p1.y + (p2.y - p1.y) * 0.5 };
  const c2 = horiz
    ? { x: p1.x + (p2.x - p1.x) * 0.5, y: p2.y }
    : { x: p2.x, y: p1.y + (p2.y - p1.y) * 0.5 };

  return {
    d: `M ${p1.x} ${p1.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${p2.x} ${p2.y}`,
    p1, p2,
  };
}

const edgeStyle = (type) => {
  switch (type) {
    case "handoff":   return { stroke: "#4DE3FF", dash: null,    width: 1.4, opacity: 0.85 };
    case "feedback":  return { stroke: "#F6C85F", dash: "5 4",   width: 1.2, opacity: 0.8 };
    case "hierarchy": return { stroke: "#8E9AAA", dash: null,    width: 0.8, opacity: 0.32 };
    case "artifact":  return { stroke: "#66F2A6", dash: null,    width: 1.2, opacity: 0.75 };
    case "safety":    return { stroke: "#FF5C7A", dash: "2 4",   width: 1,   opacity: 0.7 };
    default:          return { stroke: "#8E9AAA", dash: null,    width: 1,   opacity: 0.5 };
  }
};

function statusColor(status) {
  switch (status) {
    case "active":  return "#66F2A6";
    case "queued":  return "#4DE3FF";
    case "waiting": return "#F6C85F";
    case "done":    return "#66F2A6";
    case "blocked": return "#FF5C7A";
    default:        return "#8E9AAA";
  }
}

function statusLabel(status, override) {
  if (override) return override;
  return ({
    active:"В работе", queued:"В очереди", waiting:"Ждёт", done:"Готово",
    blocked:"Блок", idle:"Пауза",
  })[status] || "Пауза";
}

// ------------ node renderers -------------------------------------------------

function OrchestratorNode({ n, onClick, selected, dim, active }) {
  const cx = n.x + n.w/2, cy = n.y + n.h/2;
  return (
    <g
      className={`node node--orch ${dim ? "is-dim" : ""} ${selected ? "is-selected" : ""} ${active ? "is-active" : ""}`}
      onClick={onClick}
      style={{ cursor: "pointer" }}
    >
      <rect x={n.x-6} y={n.y-6} width={n.w+12} height={n.h+12} rx={18}
            className="node__halo" fill="none" stroke="#4DE3FF" strokeOpacity="0.18" strokeWidth="1"/>
      <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={14}
            fill="url(#orch-fill)" stroke="rgba(77,227,255,0.45)" strokeWidth="1.2"/>
      {/* pulse core */}
      <circle cx={n.x + 32} cy={n.y + 32} r="9"  fill="#4DE3FF" opacity="0.85">
        <animate attributeName="r" values="9;12;9" dur="2.4s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.9;0.4;0.9" dur="2.4s" repeatCount="indefinite"/>
      </circle>
      <circle cx={n.x + 32} cy={n.y + 32} r="3.5" fill="#F4F7FA"/>
      {/* label */}
      <text x={n.x + 56} y={n.y + 30} className="node__title node__title--big" fill="#F4F7FA">
        {n.label}
      </text>
      <text x={n.x + 56} y={n.y + 50} className="node__sub" fill="#8E9AAA">
        {n.sublabel}
      </text>
      {/* status badge */}
      <g transform={`translate(${n.x + 16}, ${n.y + n.h - 36})`}>
        <rect width="180" height="22" rx="6" fill="rgba(77,227,255,0.08)" stroke="rgba(77,227,255,0.3)"/>
        <circle cx="12" cy="11" r="3.5" fill="#4DE3FF"/>
        <text x="24" y="15" className="node__status" fill="#4DE3FF">{n.statusLabel || "Routing task"}</text>
      </g>
      <text x={n.x + n.w - 16} y={n.y + n.h - 18} textAnchor="end" className="node__hint" fill="#8E9AAA">
        клик · детали
      </text>
    </g>
  );
}

function AgentNode({ n, onClick, expanded, onToggle, selected, dim, active }) {
  const accent = n.accent;
  return (
    <g
      className={`node node--agent ${dim ? "is-dim" : ""} ${selected ? "is-selected" : ""} ${active ? "is-active" : ""}`}
      style={{ cursor: "pointer" }}
    >
      <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={12}
            fill="rgba(16,21,29,0.92)" stroke="rgba(255,255,255,0.10)" strokeWidth="1"
            onClick={onClick}/>
      {/* accent rail */}
      <rect x={n.x} y={n.y} width="3" height={n.h} rx="2" fill={accent} opacity="0.85"/>
      {/* header row */}
      <text x={n.x + 16} y={n.y + 24} className="node__title" fill="#F4F7FA" onClick={onClick}>
        {n.label}
      </text>
      <text x={n.x + 16} y={n.y + 42} className="node__sub" fill="#8E9AAA" onClick={onClick}>
        {n.department}
      </text>

      {/* status pill */}
      <g transform={`translate(${n.x + n.w - 96}, ${n.y + 14})`} onClick={onClick}>
        <rect width="80" height="20" rx="6" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.10)"/>
        <circle cx="11" cy="10" r="3.5" fill={statusColor(n.status)}/>
        <text x="22" y="14" className="node__status" fill={statusColor(n.status)}>
          {statusLabel(n.status, n.statusLabel)}
        </text>
      </g>

      {/* readiness bars */}
      <g transform={`translate(${n.x + 16}, ${n.y + 58})`} onClick={onClick}>
        <text x="0" y="0" className="node__metric-label" fill="#8E9AAA">readiness</text>
        <text x={n.w - 32} y="0" textAnchor="end" className="node__metric-val" fill="#F4F7FA">{n.readiness}%</text>
        <rect x="0" y="6" width={n.w - 32} height="3" rx="2" fill="rgba(255,255,255,0.06)"/>
        <rect x="0" y="6" width={(n.w - 32) * (n.readiness/100)} height="3" rx="2" fill={accent} opacity="0.9"/>

        <text x="0" y="24" className="node__metric-label" fill="#8E9AAA">KR readiness</text>
        <text x={n.w - 32} y="24" textAnchor="end" className="node__metric-val" fill="#F4F7FA">{n.krReadiness}%</text>
        <rect x="0" y="30" width={n.w - 32} height="3" rx="2" fill="rgba(255,255,255,0.06)"/>
        <rect x="0" y="30" width={(n.w - 32) * (n.krReadiness/100)} height="3" rx="2" fill={accent} opacity="0.55"/>
      </g>

      {/* stats 2x2 */}
      <g transform={`translate(${n.x + 16}, ${n.y + 112})`} onClick={onClick}>
        {n.stats.slice(0, 4).map((s, i) => {
          const col = i % 2, row = Math.floor(i / 2);
          const cx = col * ((n.w - 32) / 2), cy = row * 26;
          return (
            <g key={i} transform={`translate(${cx}, ${cy})`}>
              <text x="0" y="0" className="node__stat-k" fill="#8E9AAA">{s.k}</text>
              <text x="0" y="14" className="node__stat-v" fill="#F4F7FA">{s.v}</text>
            </g>
          );
        })}
      </g>

      {/* expand chip */}
      <g transform={`translate(${n.x + n.w - 96}, ${n.y + n.h - 26})`} onClick={(e)=>{e.stopPropagation(); onToggle();}}>
        <rect width="80" height="18" rx="5" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.12)"/>
        <text x="40" y="13" textAnchor="middle" className="node__hint" fill="#8E9AAA">
          {expanded ? "− свернуть" : "+ развернуть"}
        </text>
      </g>
    </g>
  );
}

// expanded modules drawer below an agent
function AgentModulesDrawer({ n }) {
  const items = n.modules || [];
  const colW = 132, gap = 8;
  const cols = Math.min(items.length, 2);
  const rows = Math.ceil(items.length / 2);
  const w = cols * colW + (cols - 1) * gap + 16;
  const h = rows * 28 + 20;
  return (
    <g transform={`translate(${n.x + n.w + 16}, ${n.y})`}>
      <rect width={w} height={h} rx={10} fill="rgba(16,21,29,0.85)" stroke="rgba(255,255,255,0.10)"/>
      <text x="10" y="14" className="node__sub" fill="#8E9AAA">модули · скиллы</text>
      {items.map((m, i) => {
        const col = i % 2, row = Math.floor(i / 2);
        return (
          <g key={m} transform={`translate(${8 + col * (colW + gap)}, ${22 + row * 28})`}>
            <rect width={colW} height="22" rx="5" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.08)"/>
            <circle cx="9" cy="11" r="2.5" fill={n.accent} opacity="0.85"/>
            <text x="18" y="15" className="node__module" fill="#F4F7FA">{m}</text>
          </g>
        );
      })}
    </g>
  );
}

function ServiceNode({ n, onClick, dim, selected, active }) {
  return (
    <g
      className={`node node--service ${dim ? "is-dim" : ""} ${selected ? "is-selected" : ""} ${active ? "is-active" : ""}`}
      style={{ cursor: "pointer" }}
      onClick={onClick}
    >
      <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={10}
            fill="rgba(8,11,16,0.92)" stroke="rgba(255,255,255,0.10)"
            strokeDasharray={n.status === "blocked" ? "3 4" : "0"}/>
      <text x={n.x + 14} y={n.y + 22} className="node__title-sm" fill="#F4F7FA">{n.label}</text>
      <g transform={`translate(${n.x + 14}, ${n.y + 36})`}>
        <circle cx="0" cy="0" r="3" fill={statusColor(n.status)}/>
        <text x="10" y="4" className="node__status" fill={statusColor(n.status)}>
          {n.statusLabel || statusLabel(n.status)}
        </text>
      </g>
      <text x={n.x + n.w - 14} y={n.y + n.h - 12} textAnchor="end" className="node__hint" fill="#5C6678">
        сервисный модуль
      </text>
    </g>
  );
}

function ArtifactNode({ n, onClick, dim, selected, active }) {
  return (
    <g
      className={`node node--artifact ${dim ? "is-dim" : ""} ${selected ? "is-selected" : ""} ${active ? "is-active" : ""}`}
      style={{ cursor: "pointer" }}
      onClick={onClick}
    >
      <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={8}
            fill="rgba(16,21,29,0.7)" stroke={n.accent} strokeOpacity="0.35"/>
      <rect x={n.x + 8} y={n.y + 8} width="14" height={n.h - 16} rx="3"
            fill={n.accent} fillOpacity="0.18" stroke={n.accent} strokeOpacity="0.55"/>
      <text x={n.x + 30} y={n.y + n.h/2 + 4} className="node__artifact" fill="#F4F7FA">
        {n.label}
      </text>
    </g>
  );
}

function SourceNode({ n, onClick, dim, selected, active, expanded, onToggle }) {
  return (
    <g
      className={`node node--source ${dim ? "is-dim" : ""} ${selected ? "is-selected" : ""} ${active ? "is-active" : ""}`}
      style={{ cursor: "pointer" }}
    >
      <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={10}
            fill="rgba(8,11,16,0.85)" stroke="rgba(255,255,255,0.08)"
            onClick={onClick}/>
      <rect x={n.x} y={n.y} width="2" height={n.h} fill={n.accent} opacity="0.7"/>
      <text x={n.x + 14} y={n.y + 22} className="node__title-sm" fill="#F4F7FA" onClick={onClick}>{n.label}</text>
      <text x={n.x + 14} y={n.y + 38} className="node__sub" fill="#8E9AAA" onClick={onClick}>{n.list.length} {n.list.length === 1 ? "строка" : (n.list.length < 5 ? "пункта" : "пунктов")}</text>
      <g onClick={onClick}>
        {n.list.slice(0, expanded ? n.list.length : 4).map((item, i) => (
          <g key={item} transform={`translate(${n.x + 14}, ${n.y + 56 + i * 16})`}>
            <circle cx="2" cy="-3" r="1.5" fill={n.accent} opacity="0.55"/>
            <text x="10" y="0" className="node__list" fill="#C7D0DD">{item}</text>
          </g>
        ))}
        {!expanded && n.list.length > 4 && (
          <text x={n.x + 24} y={n.y + 56 + 4 * 16} className="node__list" fill="#5C6678">
            +{n.list.length - 4} ещё…
          </text>
        )}
      </g>
    </g>
  );
}

// ------------ pulses ---------------------------------------------------------

function EdgePulse({ pathRef, color, duration = 1800 }) {
  const [pos, setPos] = useState(null);
  useEffect(() => {
    if (!pathRef.current) return;
    let raf, start;
    const path = pathRef.current;
    const total = path.getTotalLength();
    const step = (t) => {
      if (!start) start = t;
      const elapsed = (t - start) % duration;
      const k = elapsed / duration;
      const pt = path.getPointAtLength(k * total);
      setPos({ x: pt.x, y: pt.y });
      raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [duration]);
  if (!pos) return null;
  return (
    <g pointerEvents="none">
      <circle cx={pos.x} cy={pos.y} r="6" fill={color} opacity="0.18"/>
      <circle cx={pos.x} cy={pos.y} r="3" fill={color}/>
    </g>
  );
}

// ------------ graph ---------------------------------------------------------

function AgentSystemMap({
  data, selected, setSelected, expanded, toggleExpanded,
  scenarioPath, activeNodeId, dimNonScenario,
}) {
  const allNodes = useMemo(() => {
    return [
      data.orchestrator,
      ...data.agents,
      ...data.services,
      ...data.sources,
      ...data.artifacts,
    ];
  }, [data]);
  const byId = useMemo(() => {
    const m = {};
    allNodes.forEach(n => m[n.id] = n);
    return m;
  }, [allNodes]);

  // viewport pan/zoom
  const VIEW = { w: 2440, h: 1500 };
  const [tx, setTx] = useState(0), [ty, setTy] = useState(0), [scale, setScale] = useState(1);
  const containerRef = useRef(null);
  const drag = useRef(null);

  const fitView = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const s = Math.min(rect.width / VIEW.w, rect.height / VIEW.h);
    setScale(s);
    setTx((rect.width - VIEW.w * s) / 2);
    setTy((rect.height - VIEW.h * s) / 2);
  }, []);
  useEffect(() => {
    fitView();
    window.addEventListener("resize", fitView);
    return () => window.removeEventListener("resize", fitView);
  }, [fitView]);

  const onWheel = (e) => {
    const rect = containerRef.current.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const next = Math.max(0.2, Math.min(2.4, scale * (e.deltaY < 0 ? 1.08 : 1/1.08)));
    setTx(mx - (mx - tx) * (next / scale));
    setTy(my - (my - ty) * (next / scale));
    setScale(next);
  };
  const onDown = (e) => {
    if (e.button !== 0) return;
    drag.current = { x: e.clientX - tx, y: e.clientY - ty };
  };
  const onMove = (e) => {
    if (!drag.current) return;
    setTx(e.clientX - drag.current.x);
    setTy(e.clientY - drag.current.y);
  };
  const onUp = () => { drag.current = null; };

  // scenario active set
  const scenarioSet = useMemo(() => new Set(scenarioPath || []), [scenarioPath]);
  const isDim = (id) => {
    if (dimNonScenario && scenarioSet.size > 0) return !scenarioSet.has(id);
    if (selected && selected.type === "agent") {
      // focus mode: dim everything except orchestrator and the selected agent
      return id !== selected.id && id !== "orchestrator" && byId[id]?.type !== "module";
    }
    return false;
  };

  // edges
  const edgeRefs = useRef({});

  return (
    <div className="graph" ref={containerRef}
         onWheel={onWheel} onMouseDown={onDown} onMouseMove={onMove}
         onMouseUp={onUp} onMouseLeave={onUp}>
      <div className="graph__overlay-tl">
        <button className="iconbtn" onClick={() => setScale(s => Math.min(2.4, s * 1.15))}>+</button>
        <button className="iconbtn" onClick={() => setScale(s => Math.max(0.2, s / 1.15))}>−</button>
        <button className="iconbtn iconbtn--text" onClick={fitView}>центр</button>
      </div>
      <svg className="graph__svg" width="100%" height="100%">
        <defs>
          <linearGradient id="orch-fill" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(77,227,255,0.16)"/>
            <stop offset="50%" stopColor="rgba(16,21,29,0.85)"/>
            <stop offset="100%" stopColor="rgba(102,242,166,0.10)"/>
          </linearGradient>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.025)" strokeWidth="1"/>
          </pattern>
          <pattern id="grid-major" width="200" height="200" patternUnits="userSpaceOnUse">
            <path d="M 200 0 L 0 0 0 200" fill="none" stroke="rgba(77,227,255,0.045)" strokeWidth="1"/>
          </pattern>
          <radialGradient id="bg-glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(77,227,255,0.06)"/>
            <stop offset="100%" stopColor="rgba(0,0,0,0)"/>
          </radialGradient>
          <filter id="soft-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>

        <g transform={`translate(${tx}, ${ty}) scale(${scale})`}>
          {/* background */}
          <rect x="0" y="0" width={VIEW.w} height={VIEW.h} fill="url(#grid)"/>
          <rect x="0" y="0" width={VIEW.w} height={VIEW.h} fill="url(#grid-major)"/>
          <ellipse cx={data.orchestrator.x + data.orchestrator.w/2}
                   cy={data.orchestrator.y + data.orchestrator.h/2}
                   rx="900" ry="700" fill="url(#bg-glow)"/>

          {/* coordinate ticks */}
          <g opacity="0.18">
            {Array.from({length: 12}).map((_, i) => (
              <text key={i} x={i * 200 + 6} y={14} className="grid-tick" fill="#3a4452">
                {String(i * 200).padStart(4, "0")}
              </text>
            ))}
          </g>

          {/* edges */}
          <g className="edges">
            {data.edges.map(e => {
              const a = byId[e.source], b = byId[e.target];
              if (!a || !b) return null;
              const { d } = edgePath(a, b);
              const st = edgeStyle(e.type);
              const inPath = scenarioSet.has(e.source) && scenarioSet.has(e.target);
              const dim = dimNonScenario && scenarioSet.size > 0 && !inPath;
              const refKey = e.id;
              return (
                <g key={e.id} className={`edge ${dim ? "is-dim" : ""}`}>
                  <path
                    d={d}
                    ref={(el) => { if (el) edgeRefs.current[refKey] = el; }}
                    fill="none" stroke={st.stroke} strokeWidth={st.width}
                    strokeDasharray={st.dash || undefined}
                    opacity={dim ? 0.06 : st.opacity}
                  />
                  {e.label && !dim && (
                    <EdgeLabel d={d} label={e.label} color={st.stroke}/>
                  )}
                  {(e.animated || inPath) && !dim && edgeRefs.current[refKey] && (
                    <EdgePulse pathRef={{ current: edgeRefs.current[refKey] }}
                               color={inPath ? "#66F2A6" : st.stroke}
                               duration={inPath ? 1400 : 2000}/>
                  )}
                </g>
              );
            })}
          </g>

          {/* sources */}
          {data.sources.map(n => (
            <SourceNode key={n.id} n={n}
              onClick={() => setSelected(n)}
              dim={isDim(n.id)}
              selected={selected?.id === n.id}
              active={activeNodeId === n.id}
              expanded={expanded[n.id]}
              onToggle={() => toggleExpanded(n.id)}/>
          ))}

          {/* service modules */}
          {data.services.map(n => (
            <ServiceNode key={n.id} n={n}
              onClick={() => setSelected(n)}
              dim={isDim(n.id)}
              selected={selected?.id === n.id}
              active={activeNodeId === n.id}/>
          ))}

          {/* artifacts */}
          {data.artifacts.map(n => (
            <ArtifactNode key={n.id} n={n}
              onClick={() => setSelected(n)}
              dim={isDim(n.id)}
              selected={selected?.id === n.id}
              active={activeNodeId === n.id}/>
          ))}

          {/* agents */}
          {data.agents.map(n => (
            <React.Fragment key={n.id}>
              <AgentNode n={n}
                onClick={() => setSelected(n)}
                onToggle={() => toggleExpanded(n.id)}
                expanded={expanded[n.id]}
                dim={isDim(n.id)}
                selected={selected?.id === n.id}
                active={activeNodeId === n.id}/>
              {expanded[n.id] && <AgentModulesDrawer n={n}/>}
            </React.Fragment>
          ))}

          {/* orchestrator on top */}
          <OrchestratorNode n={data.orchestrator}
            onClick={() => setSelected(data.orchestrator)}
            selected={selected?.id === data.orchestrator.id}
            dim={isDim(data.orchestrator.id)}
            active={activeNodeId === data.orchestrator.id}/>
        </g>
      </svg>
    </div>
  );
}

function EdgeLabel({ d, label, color }) {
  // place label near 45% along path
  const ref = useRef(null);
  const [pt, setPt] = useState(null);
  useEffect(() => {
    if (!ref.current) return;
    const total = ref.current.getTotalLength();
    setPt(ref.current.getPointAtLength(total * 0.45));
  }, [d]);
  return (
    <>
      <path d={d} ref={ref} fill="none" stroke="none"/>
      {pt && (
        <g transform={`translate(${pt.x}, ${pt.y})`}>
          <rect x="-3" y="-9" width={label.length * 6 + 8} height="14" rx="3"
                fill="rgba(5,7,10,0.85)" stroke="rgba(255,255,255,0.05)"/>
          <text x="1" y="1" className="edge__label" fill={color} opacity="0.85">{label}</text>
        </g>
      )}
    </>
  );
}

window.AgentSystemMap = AgentSystemMap;
