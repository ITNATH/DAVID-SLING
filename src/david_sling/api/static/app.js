/* ==========================================================================
   DAVID SLING IATOS — Global Overview & Execution Command Center.
   Vanilla JS + canvas + WebSocket. Backend is strictly pure Python (FastAPI);
   this file is the operator UI only. All market data is SIMULATED.
   ========================================================================== */
"use strict";

const state = {
  symbols: ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "V75", "V25", "STEP"],
  selected: "EURUSD",
  equity: [],
  theme: localStorage.getItem("ds-theme") || "dark",
  lastPrice: null,
  fusion: {}, awareness: {},
  ticksPrev: 0, ticksRate: 0,
  rescans: 0, vetoes: 0,
  logLevel: "ALL",
  lastSignals: [],
};

/* ---------------- theme toggle (Light / Dark) ---------------- */
function applyTheme(t) {
  state.theme = t;
  document.documentElement.setAttribute("data-theme", t);
  localStorage.setItem("ds-theme", t);
  document.getElementById("theme-toggle").textContent = t === "dark" ? "🌙 Dark" : "☀️ Light";
}
document.getElementById("theme-toggle").addEventListener("click", () =>
  applyTheme(state.theme === "dark" ? "light" : "dark"));
applyTheme(state.theme);

/* ---------------- helpers ---------------- */
const $ = (id) => document.getElementById(id);
const fmt = (n, d = 2) => (n === null || n === undefined || Number.isNaN(n)) ? "—" : Number(n).toFixed(d);
const cls = (n) => (n >= 0 ? "pos" : "neg");
const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(path, opt);
  return r.json();
}
function toast(msg, kind = "") {
  const host = $("toasts");
  const el = document.createElement("div");
  el.className = "toast " + kind;
  el.textContent = msg;
  host.appendChild(el);
  setTimeout(() => { el.classList.add("out"); setTimeout(() => el.remove(), 300); }, 4200);
}

/* ---------------- symbols from the live API ---------------- */
async function fillSymbols() {
  try {
    const m = await api("/api/market");
    const inner = m && m.market !== undefined ? m.market : m;
    const syms = Array.isArray(inner) ? inner : Object.keys(inner);
    if (syms.length) state.symbols = syms;
  } catch (e) { /* keep defaults */ }
  for (const id of ["symbol-select", "t-symbol", "m-symbol"]) {
    const sel = $(id);
    sel.innerHTML = state.symbols.map(s => `<option ${s === state.selected ? "selected" : ""}>${s}</option>`).join("");
  }
  $("basket-symbols").innerHTML = state.symbols.map(s =>
    `<label style="flex-direction:row;align-items:center;gap:4px"><input type="checkbox" class="bsym" value="${s}" ${s === "EURUSD" || s === "USDJPY" ? "checked" : ""}> ${s}</label>`).join("");
}
$("symbol-select").addEventListener("change", e => { state.selected = e.target.value; $("depth-symbol").textContent = e.target.value; });

/* trade-panel tabs */
document.querySelectorAll("#card-trade .tab").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll("#card-trade .tab").forEach(x => x.classList.remove("active"));
  b.classList.add("active");
  document.querySelectorAll("#card-trade .tabpane").forEach(p => p.classList.add("hidden"));
  $("tab-" + b.dataset.tab).classList.remove("hidden");
}));

/* bottom console tabs */
document.querySelectorAll("[data-ctab]").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll("[data-ctab]").forEach(x => x.classList.remove("active"));
  b.classList.add("active");
  document.querySelectorAll(".ctabpane").forEach(p => p.classList.add("hidden"));
  $("ctab-" + b.dataset.ctab).classList.remove("hidden");
  if (b.dataset.ctab === "depth") Console.drawDepth();
}));

/* log level filters */
document.querySelectorAll("#log-filters [data-lv]").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll("#log-filters [data-lv]").forEach(x => x.classList.remove("active"));
  b.classList.add("active");
  state.logLevel = b.dataset.lv;
  renderLogs(state.lastAlerts || []);
}));

/* R-multiple live calculator */
function updateR() {
  const entry = parseFloat($("t-price").value) || null;
  const sl = parseFloat($("t-sl").value), tp = parseFloat($("t-tp").value);
  if (sl && tp && state.lastPrice) {
    const e = entry || state.lastPrice;
    const r = Math.abs(tp - e) / Math.abs(e - sl);
    $("r-multiple").textContent = `R ≈ ${r.toFixed(2)} (SL dist ${Math.abs(e - sl).toFixed(5)})`;
  }
}
["t-price", "t-sl", "t-tp"].forEach(id => $(id).addEventListener("input", updateR));

/* ---------------- press & hold 2s safeguard (destructive actions) ---------------- */
function holdToConfirm(el, ms, fn) {
  let t0 = null, raf = null;
  const tick = () => {
    const p = Math.min(1, (performance.now() - t0) / ms);
    el.style.setProperty("--hold", (p * 100).toFixed(1));
    if (p >= 1) { el.classList.add("armed"); cleanup(); fn(); return; }
    raf = requestAnimationFrame(tick);
  };
  const cleanup = () => { if (raf) cancelAnimationFrame(raf); raf = null; t0 = null;
    el.style.setProperty("--hold", 0); el.classList.remove("armed"); };
  el.addEventListener("pointerdown", (e) => { e.preventDefault(); t0 = performance.now(); raf = requestAnimationFrame(tick); });
  el.addEventListener("pointerup", cleanup);
  el.addEventListener("pointerleave", cleanup);
  el.addEventListener("pointercancel", cleanup);
}

/* trade actions */
function showTradeResult(res, prefix = "") {
  $("trade-result").textContent = prefix + JSON.stringify(res);
  const ok = res && (res.ok || res.closed || res.halted !== undefined || res.engine);
  toast(prefix + (res.message || res.status || JSON.stringify(res).slice(0, 140)), ok === false ? "crit" : "ok");
}
$("btn-open").addEventListener("click", async () => {
  const res = await api("/api/trade/single", {
    symbol: $("t-symbol").value, side: $("t-side").value, order_type: $("t-type").value,
    volume: parseFloat($("t-vol").value), price: parseFloat($("t-price").value) || null,
    sl: parseFloat($("t-sl").value) || null, tp: parseFloat($("t-tp").value) || null,
    risk_pct: parseFloat($("t-risk").value) || null });
  showTradeResult(res);
});
$("btn-multi").addEventListener("click", async () => {
  const res = await api("/api/trade/single-pair-multi", {
    symbol: $("m-symbol").value, side: $("m-side").value,
    tranches: parseInt($("m-tranches").value), lots: parseFloat($("m-lots").value),
    sl: parseFloat($("m-sl").value) || null, tp: parseFloat($("m-tp").value) || null });
  showTradeResult(res);
});
$("btn-basket").addEventListener("click", async () => {
  const symbols = [...document.querySelectorAll(".bsym:checked")].map(c => c.value);
  const res = await api("/api/trade/cross-pair-basket", {
    symbols, side: $("b-side").value, lots: parseFloat($("b-lots").value),
    sl_atr_mult: parseFloat($("b-sl").value), tp_rr: parseFloat($("b-rr").value) });
  showTradeResult(res);
});
document.querySelectorAll("[data-batch]").forEach(b => {
  const fire = async () => {
    const payload = JSON.parse(b.dataset.batch);
    payload.symbol = state.selected;
    showTradeResult(await api("/api/trade/batch-close", payload));
  };
  if (b.classList.contains("hold")) holdToConfirm(b, parseInt(b.dataset.hold || "2000"), fire);
  else b.addEventListener("click", fire);
});
$("btn-be-all").addEventListener("click", () => api("/api/trade/breakeven-all").then(r => showTradeResult(r)));
holdToConfirm($("btn-panic"), 2000, () => api("/api/trade/panic-flatten", {}).then(r => showTradeResult(r, "🚨 ")));
holdToConfirm($("btn-halt"), 2000, () => {
  const reason = prompt("Emergency halt reason:", "operator emergency halt");
  if (reason === null) return;
  api("/api/trade/halt", { reason }).then(r => showTradeResult(r, "⛔ "));
});
$("btn-resume").addEventListener("click", () => api("/api/trade/resume", {}).then(r => showTradeResult(r, "▶ ")));
/* same operations available from the basket module via data-action (no duplicate ids) */
document.querySelectorAll("[data-action]").forEach(b => {
  const fire = async () => {
    const act = b.dataset.action;
    if (act === "be-all") showTradeResult(await api("/api/trade/breakeven-all"));
    else if (act === "panic") showTradeResult(await api("/api/trade/panic-flatten", {}), "🚨 ");
    else if (act === "halt") {
      const reason = prompt("Emergency halt reason:", "operator emergency halt");
      if (reason === null) return;
      showTradeResult(await api("/api/trade/halt", { reason }), "⛔ ");
    } else if (act === "resume") showTradeResult(await api("/api/trade/resume", {}), "▶ ");
  };
  if (b.classList.contains("hold")) holdToConfirm(b, parseInt(b.dataset.hold || "2000"), fire);
  else b.addEventListener("click", fire);
});

/* ---------------- PROTECTIONS — live status indicators (News Filter / Breakeven /
   Spike Defence / Thesis Failure) + halt flag + broker link, polled read-only API ---------------- */
async function loadProtections() {
  try {
    const d = await api("/api/protection_status");
    const n = d.news_filter || {};
    const newsEl = $("prot-news");
    newsEl.textContent = n.active ? `ACTIVE · ${Math.ceil(n.seconds_left ?? 0)}s left` : "INACTIVE";
    newsEl.className = "v " + (n.active ? "neg" : "dim");
    const be = d.breakeven || {};
    const beEl = $("prot-be");
    beEl.textContent = `trigger +${be.trigger_atr_mult ?? 1.5} ATR · armed ${be.positions_armed ?? 0}`;
    beEl.className = "v " + ((be.positions_armed ?? 0) > 0 ? "pos" : "dim");
    const sp = d.spike_defence || {};
    const armed = Object.values(sp.per_symbol || {}).filter(x => x.armed).length;
    const spEl = $("prot-spike");
    spEl.textContent = `ATR ×${sp.atr_spike_mult ?? 3} · spread ×${sp.spread_widen_mult ?? 4} · ${armed} armed`;
    spEl.className = "v " + (armed ? "neg" : "dim");
    const th = d.thesis_failure || {};
    const thEl = $("prot-thesis");
    thEl.textContent = `invalidations ${th.invalidations_total ?? 0}` + (th.last && th.last.symbol ? ` · last ${th.last.symbol}` : "");
    thEl.className = "v " + ((th.invalidations_total ?? 0) > 0 ? "neg" : "dim");
    const br = d.broker || {};
    const live = br.type === "Mt5Adapter" && br.connected;
    $("foot-broker").textContent = live ? "MT5 LIVE" : (br.type === "Mt5Adapter" ? "MT5 DOWN" : "SIM");
    $("foot-broker").style.color = live ? "var(--ok)" : br.type === "Mt5Adapter" ? "var(--danger)" : "var(--warn)";
    document.body.classList.toggle("halted", !!d.halted);
  } catch (e) { /* next poll retries */ }
}

/* ---------------- rendering: overview ---------------- */
function renderTelemetry(a) {
  const items = [
    ["Balance", a.balance, 2], ["Equity", a.equity, 2], ["Floating PnL", a.floating_pnl, 2],
    ["Margin", a.margin, 2], ["Free Margin", a.free_margin, 2], ["Margin Level %", a.margin_level_pct, 1],
  ];
  $("telemetry").innerHTML = items.map(([k, v, d]) =>
    `<div class="metric"><div class="k">${k}</div><div class="v ${k === "Floating PnL" ? cls(v) : ""}">${k === "Floating PnL" ? (v >= 0 ? "▲ " : "▼ ") : ""}${fmt(v, d)}</div></div>`).join("");
  const ml = a.margin_level_pct;
  const fill = $("margin-meter");
  fill.style.width = Math.max(0, Math.min(100, ml > 1000 ? 100 : ml || 0)) + "%";
  fill.style.background = ml >= 300 ? "var(--ok)" : ml >= 150 ? "var(--warn)" : "var(--danger)";
  const lbl = $("margin-label");
  lbl.textContent = fmt(ml, 1) + "% " + (ml >= 300 ? "SAFE" : ml >= 150 ? "CAUTION" : "CRITICAL");
  lbl.style.color = ml >= 300 ? "var(--ok)" : ml >= 150 ? "var(--warn)" : "var(--danger)";
}
function renderHealth(h) {
  $("health-count").textContent = h.length;
  $("health").innerHTML = h.map(x =>
    `<div class="hcell ${x.healthy ? "" : "bad"}"><span class="dot"></span>${esc(x.domain)} <span class="dim">${esc(x.layer)}</span><span class="st">${x.healthy ? "OK" : "DOWN"}</span></div>`).join("");
}
function renderAwareness(aw, symbol) {
  const a = aw[symbol];
  if (!a) { $("awareness").innerHTML = "<div class='dim'>no data yet</div>"; return; }
  $("awareness").innerHTML = [
    ["Price", fmt(a.price, 5)], ["ATR(M1)", fmt(a.atr_m1, 6)], ["ATR% H1", fmt(a.atr_pct_h1, 1)],
    ["Spread (pts)", fmt(a.spread_points, 1)], ["Session", a.session_epoch], ["Phase", a.session_phase],
    ["Regime", `${a.regime} (${fmt((a.regime_confidence ?? 0) * 100, 0)}%)`],
  ].map(([k, v]) => `<div class="k">${k}</div><div>${v}</div>`).join("");
}
function renderScenario(sc, symbol) {
  const s = sc[symbol];
  const el = $("scenario");
  if (!s) { el.textContent = "—"; return; }
  el.textContent = `${s.scenario} · ${s.family}`;
  el.style.color = s.scenario.startsWith("S") ? "var(--accent)" : "var(--warn)";
  $("hypothesis").innerHTML = [
    ["Confidence", fmt((s.confidence ?? 0) * 100, 0) + "%"],
    ["Forming", s.forming ? "yes (bar open)" : "no (closed)"],
    ["Class", s.scenario.startsWith("S") ? "structural" : "flow"],
  ].map(([k, v]) => `<div class="k">${k}</div><div>${v}</div>`).join("");
}
function renderFusion(fu, symbol) {
  const f = fu[symbol];
  if (!f) return;
  state.fusion[symbol] = f;
  const el = $("fusion-dir");
  el.textContent = `${f.direction.toUpperCase()} · conv ${fmt(f.convergence * 100, 0)}% · conflicts ${f.conflicts}`;
  el.style.color = f.direction === "long" ? "var(--ok)" : f.direction === "short" ? "var(--sell)" : "var(--dim)";
  $("fusion-layers").innerHTML = Object.entries(f.layers).map(([tf, v]) => {
    const h = Math.abs(v) * 66;
    return `<div class="bar ${v < 0 ? "neg" : ""}" style="height:${Math.max(h, 2)}px" title="${tf}: ${v}"><span>${tf}</span></div>`;
  }).join("");
}
function renderEngines(en) {
  $("engines").innerHTML = Object.entries(en).map(([id, e]) => {
    const col = e.state === "TRIGGERED" ? "var(--ok)" : e.enabled ? "var(--accent)" : "var(--sell)";
    const st = e.state === "TRIGGERED" ? "TRIGGERED" : e.enabled ? e.state : e.state + " · OFF";
    return `<div class="ecard"><div class="nm">Engine ${id} — ${esc(e.name)}</div>
     <div class="st dim">${e.horizon} · ctx ${e.context_tfs.join("/")} · trig ${e.trigger_tfs.join("/")}</div>
     <div class="st" style="color:${col}">${st}</div></div>`;
  }).join("");
}
function renderEngineControls(en, version) {
  const host = $("engine-controls");
  if (!host) return;
  host.innerHTML = Object.entries(en).map(([id, e]) => `
    <div class="eng-row ${e.enabled ? "on" : "off"}">
      <div class="eng-id">${id}</div>
      <div class="eng-meta"><b>${esc(e.name)}</b> · ${e.horizon}<br>
        <span class="dim">ctx ${e.context_tfs.join("/")} · trig ${e.trigger_tfs.join("/")} · ${e.state}${e.enabled ? "" : " · OFF"}</span></div>
      <label class="switch" title="Enable / disable Engine ${id}">
        <input type="checkbox" data-engine="${id}" ${e.enabled ? "checked" : ""}>
        <span class="slider"></span>
      </label>
    </div>`).join("");
  if (version) $("control-result").textContent = `config v${version} · mutations recorded in evidence ledger`;
  host.querySelectorAll("input[data-engine]").forEach(inp =>
    inp.addEventListener("change", () => toggleEngine(inp.dataset.engine, inp.checked)));
}
async function toggleEngine(id, enabled) {
  const r = await api(`/api/control/engines/${id}`, { enabled, actor: "operator" });
  $("control-result").textContent = `engine ${id} ${enabled ? "ENABLED" : "DISABLED"} · config v${r.config_version} · ledgered`;
  toast(`Engine ${id} ${enabled ? "ENABLED" : "DISABLED"} · config v${r.config_version}`, "ok");
  if (r.engine) loadEngineControls();
}
async function loadEngineControls() {
  try { const d = await api("/api/control/engines"); renderEngineControls(d.engines, d.config_version); } catch (e) {}
}
function renderSignals(sigs) {
  state.lastSignals = sigs;
  $("signals").innerHTML = sigs.slice(-14).reverse().map(s =>
    `<div><span class="tier tier${s.precision.tier}">T${s.precision.tier}</span>
     <b>${esc(s.symbol)}</b> <span class="side-${s.direction === "long" ? "buy" : "sell"}">${s.direction.toUpperCase()}</span>
     · ${esc(s.strategy_id)} · Eng ${s.engine} · ${esc(s.scenario)} · ${esc(s.status)} · R${fmt(s.risk_reward, 1)}</div>`).join("") || "<div class='dim'>no signals routed yet</div>";
}
function renderPositions(pos, pnl) {
  const tb = $("positions").querySelector("tbody");
  tb.innerHTML = pos.map(p => `<tr>
    <td>${esc(p.position_id.slice(0, 12))}</td><td>${esc(p.symbol)}</td>
    <td class="side-${p.side === "BUY" ? "buy" : "sell"}">${p.side}</td>
    <td>${p.volume}</td><td>${fmt(p.entry_price, 5)}</td><td>${fmt(p.stop_loss, 5)}</td><td>${fmt(p.take_profit, 5)}</td>
    <td class="${cls(p.realized_pnl)}">${fmt(p.realized_pnl)}</td><td>${p.breakeven_done ? "✓" : ""}</td>
    <td><button class="btn" onclick="closePos('${p.position_id}',0.5)">50%</button></td>
    <td><button class="btn btn-sell" onclick="closePos('${p.position_id}',null)">✕</button></td></tr>`).join("")
    || '<tr><td colspan="11" class="dim">flat — no open positions</td></tr>';
  const pm = $("pnl-matrix").querySelector("tbody");
  pm.innerHTML = pnl.map(r => `<tr><td>${esc(r.symbol)}</td><td class="pos">${fmt(r.gross_profit)}</td>
    <td class="neg">${fmt(r.gross_loss)}</td><td class="${cls(r.net)}">${fmt(r.net)}</td>
    <td>${fmt(r.swap)}</td><td>${fmt(r.margin)}</td><td>${r.open_positions}</td></tr>`).join("")
    || '<tr><td colspan="7" class="dim">no exposure</td></tr>';
}
window.closePos = async (id, pct) => { showTradeResult(await api("/api/trade/close", { position_id: id, pct })); };
function renderAlerts(al) {
  state.lastAlerts = al;
  renderLogs(al);
}
function renderLogs(al) {
  const lv = state.logLevel;
  const rows = al.slice(-60).reverse().filter(a => lv === "ALL" || a.level === lv);
  $("logs-body").innerHTML = rows.map(a =>
    `<div class="lv-${a.level}"><span class="ts">${esc((a.ts || "").slice(11, 19))}</span>[${a.level}] ${esc(a.message)}</div>`).join("")
    || "<div class='dim'>no log entries at this level</div>";
}
function renderLedger(l) {
  $("ledger").innerHTML = `Entries ${l.entries} · Chain ${l.chain_ok ? "✓ VERIFIED (SHA3-256)" : "✗ BROKEN"} · Head ${(l.head || "—").slice(0, 12)}…`;
  $("ledger").className = "ledger-chip mono " + (l.chain_ok ? "ok" : "bad");
}
function renderEquity(a) {
  state.equity.push(a.equity); if (state.equity.length > 120) state.equity.shift();
  const c = $("equity"), ctx = c.getContext("2d");
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = c.clientWidth * dpr, h = c.clientHeight * dpr;
  if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
  ctx.clearRect(0, 0, w, h);
  const vals = state.equity, min = Math.min(...vals), max = Math.max(...vals), span = (max - min) || 1;
  const accent = cssVar("--accent");
  ctx.strokeStyle = accent; ctx.lineWidth = 1.6 * dpr; ctx.beginPath();
  vals.forEach((v, i) => {
    const x = (i / 119) * w, y = h - ((v - min) / span) * (h - 12 * dpr) - 6 * dpr;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.stroke();
  ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
  ctx.fillStyle = accent + "22"; ctx.fill();
}

/* ---------------- MONITORING panel (learning engine, read-only API) ---------------- */
async function loadMonitoring() {
  try {
    const d = await api("/api/monitoring");
    const st = d.stats || {};
    const disp = st.dispatch || {};
    $("mon-dispatch").textContent = `${fmt(disp.avg_ms, 2)}ms`;
    $("mon-drift").textContent = (d.proposals || []).length;
    const strat = st.strategies || {};
    const tb = $("mon-strategies").querySelector("tbody");
    const rows = Object.entries(strat).sort((a, b) => (b[1].pnl || 0) - (a[1].pnl || 0)).slice(0, 8);
    tb.innerHTML = rows.map(([sid, s]) =>
      `<tr><td>${esc(sid)}</td><td>${s.trades}</td><td>${fmt((s.win_rate ?? 0) * 100, 1)}</td>
       <td class="${cls(s.pnl)}">${fmt(s.pnl, 0)}</td></tr>`).join("")
      || '<tr><td colspan="4" class="dim">no strategy outcomes yet</td></tr>';
    $("mon-proposals").innerHTML = (d.proposals || []).slice(-4).reverse().map(p =>
      `<div>⚠ drift proposal: ${esc(p.strategy || p.type)} (${esc(p.type)})</div>`).join("")
      || "<div class='dim'>no drift proposals — learning loop stable</div>";
  } catch (e) { /* next poll retries */ }
}

/* ---------------- TRADE JOURNAL panel (journal.* evidence, read-only API) ---------------- */
async function loadJournal() {
  try {
    const d = await api("/api/evidence?limit=250");
    const ev = (d.evidence || []).filter(e =>
      e.kind.startsWith("journal.") || e.kind === "position.closed" || e.kind === "risk.veto");
    state.vetoes += 0;
    const vetoCount = (d.evidence || []).filter(e => e.kind === "risk.veto").length;
    $("mon-vetoes").textContent = vetoCount;
    const tb = $("journal-body");
    tb.innerHTML = ev.slice(-40).reverse().map(e => {
      const p = e.payload || {};
      const sym = p.symbol || (p.intent && p.intent.symbol) || (p.trade && p.trade.symbol) || "—";
      const side = p.side || (p.intent && p.intent.side) || (p.trade && p.trade.side) || "";
      let detail = "", pnl = "";
      if (e.kind === "journal.exit" || e.kind === "position.closed") {
        const t = p.trade || p;
        detail = `exit ${t.reason || ""} · vol ${t.volume ?? ""}`;
        pnl = t.pnl !== undefined ? fmt(t.pnl, 2) : "";
      } else if (e.kind === "journal.execution") {
        const i = p.intent || {};
        detail = `${i.order_type || ""} @ ${i.price ?? "mkt"} · SL ${i.stop_loss ?? "—"} · TP ${i.take_profit ?? "—"}`;
      } else if (e.kind === "journal.signal") {
        const s = p.ticket || p;
        detail = `${s.strategy_id || ""} · ${s.scenario || ""} · R${s.risk_reward ?? "—"} · conf ${fmt((s.confidence ?? 0) * 100, 0)}%`;
      } else if (e.kind === "risk.veto") {
        detail = esc(p.reason || JSON.stringify(p).slice(0, 60));
      }
      const kcls = e.kind === "risk.veto" ? "kindchip risk" : "kindchip journal";
      return `<tr><td class="dim">${esc((e.ts || "").slice(11, 19))}</td>
        <td><span class="${kcls}">${esc(e.kind.replace("journal.", "J:"))}</span></td>
        <td>${esc(sym)}</td><td>${esc(side)}</td><td>${detail}</td>
        <td class="${pnl !== "" ? cls(Number(pnl)) : ""}">${pnl}</td>
        <td class="dim">${esc((e.evidence_id || "").slice(0, 10))}</td></tr>`;
    }).join("") || '<tr><td colspan="7" class="dim">journal empty — no trades journaled yet</td></tr>';
  } catch (e) { /* next poll retries */ }
}

/* ==========================================================================
   CENTER CANVAS — 3D liquidity globe (orthographic, canvas 2D),
   wheel zoom transitions: GLOBE -> 2D HEATMAP -> ORDER-ROUTING CORRIDORS
   ========================================================================== */
const Globe = (() => {
  const canvas = () => $("globe-canvas");
  let mode = "globe", rotY = 0.6, rotX = -0.35, zoom = 1, auto = 0.0022;
  let dragging = false, lastX = 0, lastY = 0;
  const N = 170, nodes = [];
  for (let i = 0; i < N; i++) {
    const y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), th = i * 2.399963;
    nodes.push([r * Math.cos(th), y, r * Math.sin(th)]);
  }
  const arcs = [];
  for (let i = 0; i < 26; i++) arcs.push([Math.floor(Math.random() * N), Math.floor(Math.random() * N), Math.random()]);
  const cv = canvas();
  cv.addEventListener("pointerdown", (e) => { dragging = true; lastX = e.clientX; lastY = e.clientY; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    rotY += (e.clientX - lastX) * 0.008; rotX += (e.clientY - lastY) * 0.008;
    rotX = Math.max(-1.4, Math.min(1.4, rotX));
    lastX = e.clientX; lastY = e.clientY;
  });
  cv.addEventListener("pointerup", () => { dragging = false; });
  cv.addEventListener("wheel", (e) => {
    e.preventDefault();
    zoom = Math.max(0.6, Math.min(3.2, zoom * (e.deltaY < 0 ? 1.12 : 0.89)));
    setMode(zoom > 2.4 ? "routes" : zoom > 1.5 ? "heatmap" : "globe");
  }, { passive: false });
  document.querySelectorAll(".mode-switch .tab").forEach(b => b.addEventListener("click", () => setMode(b.dataset.mode)));
  function setMode(m) {
    mode = m; zoom = m === "globe" ? 1 : m === "heatmap" ? 1.9 : 2.8;
    document.querySelectorAll(".mode-switch .tab").forEach(x => x.classList.toggle("active", x.dataset.mode === m));
    $("globe-hint").textContent = m === "globe" ? "drag = rotate · wheel = zoom · SIMULATED FEED"
      : m === "heatmap" ? "2D tactical heatmap · cell = fusion conviction · wheel out = globe"
      : "order-routing corridors · packets = routed signals · wheel out = heatmap";
  }
  function project(p, R, cx, cy) {
    const [x, y, z] = p;
    const cy1 = Math.cos(rotY), sy1 = Math.sin(rotY), cx1 = Math.cos(rotX), sx1 = Math.sin(rotX);
    const X = x * cy1 + z * sy1, Z = -x * sy1 + z * cy1, Y = y;
    const Y2 = Y * cx1 - Z * sx1, Z2 = Y * sx1 + Z * cx1;
    return [cx + X * R, cy - Y2 * R, Z2];
  }
  function drawGlobe(ctx, w, h, t) {
    const R = Math.min(w, h) * 0.36 * zoom, cx = w / 2, cy = h / 2;
    const accent = cssVar("--accent"), dim = cssVar("--c4");
    ctx.strokeStyle = dim + "55"; ctx.lineWidth = 1;
    for (let lat = -60; lat <= 60; lat += 30) {
      ctx.beginPath();
      for (let lon = 0; lon <= 360; lon += 6) {
        const p = [Math.cos(lat * Math.PI / 180) * Math.cos(lon * Math.PI / 180),
                   Math.sin(lat * Math.PI / 180),
                   Math.cos(lat * Math.PI / 180) * Math.sin(lon * Math.PI / 180)];
        const [X, Y] = project(p, R, cx, cy);
        lon === 0 ? ctx.moveTo(X, Y) : ctx.lineTo(X, Y);
      }
      ctx.stroke();
    }
    for (let lon = 0; lon < 180; lon += 30) {
      ctx.beginPath();
      for (let lat = -90; lat <= 90; lat += 6) {
        const p = [Math.cos(lat * Math.PI / 180) * Math.cos(lon * Math.PI / 180),
                   Math.sin(lat * Math.PI / 180),
                   Math.cos(lat * Math.PI / 180) * Math.sin(lon * Math.PI / 180)];
        const [X, Y] = project(p, R, cx, cy);
        lat === -90 ? ctx.moveTo(X, Y) : ctx.lineTo(X, Y);
      }
      ctx.stroke();
    }
    for (const [a, b, ph] of arcs) {
      const A = nodes[a], B = nodes[b];
      ctx.strokeStyle = accent + "66"; ctx.lineWidth = 1; ctx.beginPath();
      for (let s = 0; s <= 20; s++) {
        const u = s / 20, pu = 1 - u;
        const mid = [(pu*pu*A[0] + 2*pu*u*((A[0]+B[0])/2) + u*u*B[0]) * 1.25,
                     (pu*pu*A[1] + 2*pu*u*((A[1]+B[1])/2) + u*u*B[1]) * 1.25,
                     (pu*pu*A[2] + 2*pu*u*((A[2]+B[2])/2) + u*u*B[2]) * 1.25];
        const [X, Y] = project(mid, R, cx, cy);
        s === 0 ? ctx.moveTo(X, Y) : ctx.lineTo(X, Y);
      }
      ctx.stroke();
      const u = (t * 0.4 + ph) % 1, pu = 1 - u;
      const pk = [(pu*pu*A[0] + 2*pu*u*((A[0]+B[0])/2) + u*u*B[0]) * 1.25,
                  (pu*pu*A[1] + 2*pu*u*((A[1]+B[1])/2) + u*u*B[1]) * 1.25,
                  (pu*pu*A[2] + 2*pu*u*((A[2]+B[2])/2) + u*u*B[2]) * 1.25];
      const [X, Y, Z] = project(pk, R, cx, cy);
      if (Z > 0) { ctx.fillStyle = accent; ctx.beginPath(); ctx.arc(X, Y, 2.2, 0, 7); ctx.fill(); }
    }
    for (let i = 0; i < N; i++) {
      const [X, Y, Z] = project(nodes[i], R, cx, cy);
      if (Z <= 0) continue;
      const pulse = 0.5 + 0.5 * Math.sin(t * 2 + i);
      ctx.fillStyle = accent; ctx.globalAlpha = 0.25 + 0.55 * pulse * (Z * 0.5 + 0.5);
      ctx.beginPath(); ctx.arc(X, Y, 1 + pulse * 1.6, 0, 7); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
  function drawHeatmap(ctx, w, h) {
    const syms = state.symbols;
    const cols = Math.max(2, Math.ceil(Math.sqrt(syms.length * (w / h))));
    const rows = Math.ceil(syms.length / cols);
    const cw = w / cols, ch = h / rows;
    syms.forEach((s, i) => {
      const f = state.fusion[s];
      const conv = f ? Math.min(1, Math.abs(f.convergence)) : 0.3;
      const long = f ? f.direction === "long" : true;
      const x = (i % cols) * cw, y = Math.floor(i / cols) * ch;
      const base = long ? cssVar("--ok") : cssVar("--sell");
      ctx.fillStyle = base; ctx.globalAlpha = 0.08 + 0.75 * conv;
      ctx.fillRect(x + 2, y + 2, cw - 4, ch - 4);
      ctx.globalAlpha = 1;
      ctx.strokeStyle = cssVar("--border"); ctx.strokeRect(x + 2, y + 2, cw - 4, ch - 4);
      ctx.fillStyle = cssVar("--c3"); ctx.font = `${Math.min(13, cw * 0.16)}px "JetBrains Mono", monospace`;
      ctx.fillText(s, x + 8, y + 17);
      ctx.fillStyle = base; ctx.font = `${Math.min(10, cw * 0.12)}px "JetBrains Mono", monospace`;
      ctx.fillText(`${long ? "LONG ▲" : "SHORT ▼"} ${(conv * 100).toFixed(0)}%`, x + 8, y + 17 + Math.min(12, cw * 0.14));
    });
  }
  function drawRoutes(ctx, w, h, t) {
    const venues = ["LD4", "NY4", "TY3", "SG1", "FR2"];
    const pts = venues.map((v, i) => {
      const ang = (i / venues.length) * Math.PI * 2 - Math.PI / 2;
      return [w / 2 + Math.cos(ang) * Math.min(w, h) * 0.36, h / 2 + Math.sin(ang) * Math.min(w, h) * 0.36, v];
    });
    const accent = cssVar("--accent"), warn = cssVar("--warn");
    ctx.strokeStyle = cssVar("--c4") + "66"; ctx.lineWidth = 1;
    pts.forEach((p, i) => pts.forEach((q, j) => {
      if (j <= i) return;
      ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); ctx.stroke();
    }));
    (state.lastSignals || []).slice(-10).forEach((s, k) => {
      const a = pts[k % pts.length], b = pts[(k * 2 + 1) % pts.length];
      const ph = (t * 0.25 + k * 0.13) % 1;
      ctx.fillStyle = s.direction === "long" ? accent : warn;
      ctx.beginPath(); ctx.arc(a[0] + (b[0] - a[0]) * ph, a[1] + (b[1] - a[1]) * ph, 3, 0, 7); ctx.fill();
    });
    pts.forEach(([x, y, v]) => {
      ctx.fillStyle = cssVar("--c2"); ctx.strokeStyle = accent; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(x, y, 16, 0, 7); ctx.fill(); ctx.stroke();
      ctx.fillStyle = cssVar("--c3"); ctx.font = "10px " + cssVar("--mono");
      ctx.textAlign = "center"; ctx.fillText(v, x, y + 3); ctx.textAlign = "left";
    });
    ctx.fillStyle = cssVar("--c4"); ctx.font = "10px " + cssVar("--mono");
    ctx.fillText("routing corridors · packets = live routed signals · SIMULATED", 10, h - 10);
  }
  function frame(t) {
    const cv = canvas();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = cv.clientWidth * dpr, h = cv.clientHeight * dpr;
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    const ctx = cv.getContext("2d");
    ctx.clearRect(0, 0, w, h);
    if (!dragging && mode === "globe") rotY += auto;
    if (mode === "globe") drawGlobe(ctx, w, h, t);
    else if (mode === "heatmap") drawHeatmap(ctx, w, h);
    else drawRoutes(ctx, w, h, t);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  return { setMode };
})();

/* ==========================================================================
   INFRA console — latency, venues (SIMULATED, labelled), depth (SIMULATED)
   ========================================================================== */
const Console = (() => {
  const regions = ["LD4", "NY4", "TY3", "SG1", "FR2", "CH1"].map(r => ({ r, ms: 20 + Math.random() * 30 }));
  const venues = ["SIM-PRIME", "SIM-LP-1", "SIM-LP-2", "SIM-XCHG"];
  function tickLatency() {
    $("latency").innerHTML = regions.map(x => {
      x.ms = Math.max(8, Math.min(220, x.ms + (Math.random() - 0.5) * 14));
      const st = x.ms < 60 ? "" : x.ms < 130 ? "warn" : "crit";
      const lbl = x.ms < 60 ? "OK" : x.ms < 130 ? "SLOW" : "DEGRADED";
      return `<div class="lat ${st}"><span class="dot"></span>${x.r}<span class="ms">${x.ms.toFixed(0)}ms ${lbl}</span></div>`;
    }).join("");
  }
  function tickVenues() {
    const rate = state.ticksRate;
    const st = rate > 0 ? "" : "crit";
    const lbl = rate > 0 ? "CONNECTED" : "STALLED";
    $("venues").innerHTML = venues.map((v, i) =>
      `<div class="lat ${st}"><span class="dot"></span>${v}<span class="ms">${(rate * (1 + i * 0.13)).toFixed(0)} t/s ${lbl}</span></div>`).join("");
  }
  setInterval(() => { tickLatency(); tickVenues(); }, 1000);
  tickLatency(); tickVenues();
  let lastDraw = 0;
  function drawDepth() {
    const cv = $("depth");
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = cv.clientWidth * dpr, h = cv.clientHeight * dpr;
    if (!w || cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    if (!w) return;
    const ctx = cv.getContext("2d");
    ctx.clearRect(0, 0, w, h);
    const mid = state.lastPrice || 1.0;
    const aw = state.awareness[state.selected];
    const step = aw ? Math.max(aw.atr_m1 || 0, 1e-9) * 0.25 : mid * 0.0002;
    const n = 18;
    for (let i = 0; i < n; i++) {
      const size = (1 - i / n) * (h * 0.42) * (0.6 + Math.random() * 0.4);
      ctx.fillStyle = cssVar("--ok"); ctx.globalAlpha = 0.55;
      ctx.fillRect(w / 2 - 6 - i * w * 0.024, h - 10 - size, i * w * 0.024 + 6, size);
      ctx.fillStyle = cssVar("--sell");
      ctx.fillRect(w / 2 + i * w * 0.024, h - 10 - size * 0.9, i * w * 0.024 + 6, size * 0.9);
    }
    ctx.globalAlpha = 1;
    ctx.fillStyle = cssVar("--c3"); ctx.font = `${10 * dpr}px "JetBrains Mono", monospace`;
    ctx.fillText(`mid ${fmt(mid, 5)} · step ${fmt(step, 6)} · ${state.selected} · SIMULATED DEPTH`, 8, 14 * dpr);
    lastDraw = performance.now();
  }
  setInterval(() => { if (performance.now() - lastDraw > 1500) drawDepth(); }, 700);
  return { drawDepth };
})();

/* ---------------- clock ---------------- */
setInterval(() => {
  const t = $("foot-ts").textContent;
  $("clock").textContent = t ? t.slice(11, 19) : new Date().toISOString().slice(11, 19);
}, 1000);

/* ---------------- websocket ---------------- */
function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws/telemetry`);
  ws.onopen = () => { const c = $("conn"); c.innerHTML = '<span class="dot"></span>● LIVE'; c.className = "pill st-ok"; };
  ws.onclose = () => { const c = $("conn"); c.innerHTML = '<span class="dot"></span>○ reconnecting…'; c.className = "pill st-crit"; setTimeout(connect, 1500); };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.topic === "overview") {
      const aw = msg.awareness[state.selected];
      if (aw) { state.lastPrice = aw.price; }
      Object.assign(state.awareness, msg.awareness);
      state.fusion = msg.fusion;
      if (typeof msg.feed_ticks === "number") {
        state.ticksRate = state.ticksPrev ? (msg.feed_ticks - state.ticksPrev) / 0.5 : 0;
        state.ticksPrev = msg.feed_ticks;
      }
      state.rescans = (msg.rescans || []).length;
      $("mon-rescans").textContent = state.rescans;
      renderTelemetry(msg.account);
      renderHealth(msg.health);
      renderAwareness(msg.awareness, state.selected);
      renderScenario(msg.scenarios, state.selected);
      renderFusion(msg.fusion, state.selected);
      renderEngines(msg.engines);
      renderEngineControls(msg.engines);
      renderSignals(msg.signals);
      renderPositions(msg.positions, msg.pnl_matrix);
      renderAlerts(msg.alerts);
      renderLedger(msg.ledger);
      renderEquity(msg.account);
      $("session").textContent = `${msg.session_phase} · ${msg.session_epoch}`;
      $("foot-ts").textContent = msg.ts;
      updateR();
      Console.drawDepth();
    } else if (msg.topic === "alert") {
      renderAlerts([msg, ...(state.lastAlerts || [])].slice(0, 200));
      if (msg.level === "WARNING" || msg.level === "CRITICAL") toast(msg.message, msg.level === "CRITICAL" ? "crit" : "warn");
    }
  };
}
fillSymbols();
api("/api/health").then(h => {
  const b = $("boot");
  if (h.status === "ok") { b.innerHTML = '<span class="dot"></span>boot OK'; b.className = "pill st-ok"; }
  else { b.innerHTML = '<span class="dot"></span>boot FAIL'; b.className = "pill st-crit"; }
  if (h.broker) {
    const live = h.broker.type === "Mt5Adapter" && h.broker.connected;
    const fb = $("foot-broker");
    if (fb) { fb.textContent = live ? "MT5 LIVE" : (h.broker.type === "Mt5Adapter" ? "MT5 DOWN" : "SIM");
      fb.style.color = live ? "var(--ok)" : h.broker.type === "Mt5Adapter" ? "var(--danger)" : "var(--warn)"; }
  }
});
loadEngineControls();
loadMonitoring();
loadJournal();
loadProtections();
setInterval(loadMonitoring, 2500);
setInterval(loadJournal, 3000);
setInterval(loadProtections, 2500);
connect();
