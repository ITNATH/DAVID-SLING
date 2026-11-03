/* DAVID SLING IATOS - Mission Control operator interface (vanilla JS + WebSocket). */
"use strict";

const state = { symbols: ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"], selected: "EURUSD",
                 equity: [], theme: localStorage.getItem("ds-theme") || "dark" };

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
const fmt = (n, d = 2) => (n === null || n === undefined) ? "—" : Number(n).toFixed(d);
const cls = (n) => (n >= 0 ? "pos" : "neg");
async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(path, opt);
  return r.json();
}

/* ---------------- static form population ---------------- */
function fillSymbols() {
  for (const id of ["symbol-select", "t-symbol", "m-symbol"]) {
    const sel = $(id);
    sel.innerHTML = state.symbols.map(s => `<option ${s === state.selected ? "selected" : ""}>${s}</option>`).join("");
  }
  $("basket-symbols").innerHTML = state.symbols.map(s =>
    `<label style="flex-direction:row;align-items:center;gap:4px"><input type="checkbox" class="bsym" value="${s}" ${s === "EURUSD" || s === "USDJPY" ? "checked" : ""}> ${s}</label>`).join("");
}
$("symbol-select").addEventListener("change", e => { state.selected = e.target.value; });

/* tabs */
document.querySelectorAll(".tab").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  b.classList.add("active");
  document.querySelectorAll(".tabpane").forEach(p => p.classList.add("hidden"));
  $("tab-" + b.dataset.tab).classList.remove("hidden");
}));

/* R-multiple live calculator */
function updateR() {
  const entry = parseFloat($("t-price").value) || null;
  const sl = parseFloat($("t-sl").value), tp = parseFloat($("t-tp").value);
  if (sl && tp && state.lastPrice) {
    const e = entry || state.lastPrice;
    const r = Math.abs(tp - e) / Math.abs(e - sl);
    $("r-multiple").textContent = `R-multiple ≈ ${r.toFixed(2)}R (SL dist ${Math.abs(e - sl).toFixed(5)})`;
  }
}
["t-price", "t-sl", "t-tp"].forEach(id => $(id).addEventListener("input", updateR));

/* trade actions */
$("btn-open").addEventListener("click", async () => {
  const res = await api("/api/trade/single", {
    symbol: $("t-symbol").value, side: $("t-side").value, order_type: $("t-type").value,
    volume: parseFloat($("t-vol").value), price: parseFloat($("t-price").value) || null,
    sl: parseFloat($("t-sl").value) || null, tp: parseFloat($("t-tp").value) || null,
    risk_pct: parseFloat($("t-risk").value) || null });
  $("trade-result").textContent = JSON.stringify(res);
});
$("btn-multi").addEventListener("click", async () => {
  const res = await api("/api/trade/single-pair-multi", {
    symbol: $("m-symbol").value, side: $("m-side").value,
    tranches: parseInt($("m-tranches").value), lots: parseFloat($("m-lots").value),
    sl: parseFloat($("m-sl").value) || null, tp: parseFloat($("m-tp").value) || null });
  $("trade-result").textContent = JSON.stringify(res);
});
$("btn-basket").addEventListener("click", async () => {
  const symbols = [...document.querySelectorAll(".bsym:checked")].map(c => c.value);
  const res = await api("/api/trade/cross-pair-basket", {
    symbols, side: $("b-side").value, lots: parseFloat($("b-lots").value),
    sl_atr_mult: parseFloat($("b-sl").value), tp_rr: parseFloat($("b-rr").value) });
  $("trade-result").textContent = JSON.stringify(res);
});
document.querySelectorAll("[data-batch]").forEach(b => b.addEventListener("click", async () => {
  const payload = JSON.parse(b.dataset.batch);
  payload.symbol = state.selected;
  const res = await api("/api/trade/batch-close", payload);
  $("trade-result").textContent = JSON.stringify(res);
}));
$("btn-be-all").addEventListener("click", () => api("/api/trade/breakeven-all").then(r => $("trade-result").textContent = JSON.stringify(r)));
$("btn-panic").addEventListener("click", () => api("/api/trade/panic-flatten", {}).then(r => $("trade-result").textContent = "🚨 " + JSON.stringify(r)));
$("btn-halt").addEventListener("click", () => {
  const reason = prompt("Emergency halt reason:", "operator emergency halt");
  if (reason === null) return;
  if (!confirm("EMERGENCY HALT: veto ALL new entries until resumed?")) return;
  api("/api/trade/halt", { reason }).then(r => $("trade-result").textContent = "⛔ " + JSON.stringify(r));
});
$("btn-resume").addEventListener("click", () => api("/api/trade/resume", {}).then(r => $("trade-result").textContent = "▶ " + JSON.stringify(r)));

/* ---------------- rendering ---------------- */
function renderTelemetry(a) {
  const items = [
    ["Balance", a.balance, 2], ["Equity", a.equity, 2], ["Floating PnL", a.floating_pnl, 2],
    ["Margin", a.margin, 2], ["Free Margin", a.free_margin, 2], ["Margin Level %", a.margin_level_pct, 1],
  ];
  $("telemetry").innerHTML = items.map(([k, v, d]) =>
    `<div class="metric"><div class="k">${k}</div><div class="v ${k === "Floating PnL" ? cls(v) : ""}">${fmt(v, d)}</div></div>`).join("");
}
function renderHealth(h) {
  $("health").innerHTML = h.map(x =>
    `<div class="hcell"><span class="dot ${x.healthy ? "" : "bad"}"></span>${x.domain} <span class="dim">${x.layer}</span></div>`).join("");
}
function renderAwareness(aw, symbol) {
  const a = aw[symbol];
  if (!a) { $("awareness").innerHTML = "<div class='dim'>no data yet</div>"; return; }
  $("awareness").innerHTML = [
    ["Price", fmt(a.price, 5)], ["ATR(M1)", fmt(a.atr_m1, 6)], ["ATR% H1", fmt(a.atr_pct_h1, 1)],
    ["Spread (pts)", fmt(a.spread_points, 1)], ["Session", a.session_epoch], ["Phase", a.session_phase],
    ["Regime", `${a.regime} (${fmt(a.regime_confidence * 100, 0)}%)`],
  ].map(([k, v]) => `<div class="k">${k}</div><div>${v}</div>`).join("");
}
function renderScenario(sc, symbol) {
  const s = sc[symbol];
  const el = $("scenario");
  if (!s) { el.textContent = "—"; return; }
  el.textContent = `${s.scenario} · ${s.family}`;
  el.style.color = s.scenario.startsWith("S") ? "var(--accent)" : "var(--warn)";
}
function renderFusion(fu, symbol) {
  const f = fu[symbol];
  if (!f) return;
  const el = $("fusion-dir");
  el.textContent = `${f.direction.toUpperCase()} · conv ${fmt(f.convergence * 100, 0)}% · conflicts ${f.conflicts}`;
  el.style.color = f.direction === "long" ? "var(--ok)" : f.direction === "short" ? "var(--sell)" : "var(--dim)";
  $("fusion-layers").innerHTML = Object.entries(f.layers).map(([tf, v]) => {
    const h = Math.abs(v) * 80;
    return `<div class="bar ${v < 0 ? "neg" : ""}" style="height:${Math.max(h, 2)}px" title="${tf}: ${v}"><span>${tf}</span></div>`;
  }).join("");
}
function renderEngines(en) {
  $("engines").innerHTML = Object.entries(en).map(([id, e]) =>
    `<div class="ecard"><div class="nm">Engine ${id} — ${e.name}</div>
     <div class="st">${e.horizon} · ctx ${e.context_tfs.join("/")} · trig ${e.trigger_tfs.join("/")}</div>
     <div class="st" style="color:${e.state === "TRIGGERED" ? "var(--ok)" : e.enabled ? "var(--accent)" : "var(--sell)"}">${e.state}${e.enabled ? "" : " (disabled)"}</div></div>`).join("");
}
function renderEngineControls(en, version) {
  const host = $("engine-controls");
  if (!host) return;
  host.innerHTML = Object.entries(en).map(([id, e]) => `
    <div class="eng-row ${e.enabled ? "on" : "off"}">
      <div class="eng-id">${id}</div>
      <div class="eng-meta"><b>${e.name}</b> · ${e.horizon}<br>
        <span class="dim">ctx ${e.context_tfs.join("/")} · trig ${e.trigger_tfs.join("/")} · state ${e.state}</span></div>
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
  if (r.engine) loadEngineControls();
}
async function loadEngineControls() {
  try { const d = await api("/api/control/engines"); renderEngineControls(d.engines, d.config_version); } catch (e) {}
}
function renderSignals(sigs) {
  $("signals").innerHTML = sigs.slice(-12).reverse().map(s =>
    `<div><span class="tier tier${s.precision.tier}">T${s.precision.tier}</span>
     <b>${s.symbol}</b> ${s.direction} <span class="side-${s.direction === "long" ? "buy" : "sell"}">${s.direction.toUpperCase()}</span>
     · ${s.strategy_id} · Engine ${s.engine} · ${s.scenario} · ${s.status} · R${fmt(s.risk_reward, 1)}</div>`).join("") || "<div class='dim'>no signals routed yet</div>";
}
function renderPositions(pos, pnl) {
  const tb = $("positions").querySelector("tbody");
  tb.innerHTML = pos.map(p => `<tr>
    <td>${p.position_id.slice(0, 12)}</td><td>${p.symbol}</td>
    <td class="side-${p.side === "BUY" ? "buy" : "sell"}">${p.side}</td>
    <td>${p.volume}</td><td>${fmt(p.entry_price, 5)}</td><td>${fmt(p.stop_loss, 5)}</td><td>${fmt(p.take_profit, 5)}</td>
    <td class="${cls(p.realized_pnl)}">${fmt(p.realized_pnl)}</td><td>${p.breakeven_done ? "✓" : ""}</td>
    <td><button class="btn" onclick="closePos('${p.position_id}',0.5)">50%</button></td>
    <td><button class="btn btn-sell" onclick="closePos('${p.position_id}',null)">✕</button></td></tr>`).join("")
    || '<tr><td colspan="11" class="dim">flat</td></tr>';
  const pm = $("pnl-matrix").querySelector("tbody");
  pm.innerHTML = pnl.map(r => `<tr><td>${r.symbol}</td><td class="pos">${fmt(r.gross_profit)}</td>
    <td class="neg">${fmt(r.gross_loss)}</td><td class="${cls(r.net)}">${fmt(r.net)}</td>
    <td>${fmt(r.swap)}</td><td>${fmt(r.margin)}</td><td>${r.open_positions}</td></tr>`).join("")
    || '<tr><td colspan="7" class="dim">no exposure</td></tr>';
}
window.closePos = async (id, pct) => { $("trade-result").textContent = JSON.stringify(await api("/api/trade/close", { position_id: id, pct })); };
function renderAlerts(al) {
  $("alerts").innerHTML = al.slice(-10).reverse().map(a =>
    `<div>[${a.level}] ${a.message}</div>`).join("") || "<div class='dim'>—</div>";
}
function renderLedger(l) {
  $("ledger").innerHTML = [
    ["Entries", l.entries], ["Chain", l.chain_ok ? "✓ VERIFIED (SHA3-256)" : "✗ BROKEN"], ["Head", (l.head || "—")],
  ].map(([k, v]) => `<div class="k">${k}</div><div>${v}</div>`).join("");
}
function renderEquity(a) {
  state.equity.push(a.equity); if (state.equity.length > 120) state.equity.shift();
  const c = $("equity"), ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  const vals = state.equity, min = Math.min(...vals), max = Math.max(...vals), span = (max - min) || 1;
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent");
  ctx.beginPath();
  vals.forEach((v, i) => { const x = (i / 119) * c.width, y = c.height - ((v - min) / span) * (c.height - 10) - 5;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
  ctx.stroke();
}

/* ---------------- websocket ---------------- */
function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws/telemetry`);
  ws.onopen = () => { $("conn").textContent = "● LIVE"; $("conn").className = "pill pill-ok"; };
  ws.onclose = () => { $("conn").textContent = "○ reconnecting…"; $("conn").className = "pill pill-bad"; setTimeout(connect, 1500); };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.topic === "overview") {
      state.lastPrice = msg.market ? undefined : state.lastPrice;
      const aw = msg.awareness[state.selected];
      if (aw) state.lastPrice = aw.price;
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
    } else if (msg.topic === "alert") {
      // alerts refresh on next overview tick
    }
  };
}
fillSymbols();
api("/api/health").then(h => { if (h.status === "ok") $("conn").textContent = "boot OK"; });
loadEngineControls();
connect();
