# DAVID SLING IATOS — Complete Architectural Comprehension Dossier

**Prepared by:** Principal Software Architect / Lead System Engineer (ingestion phase)
**Source document:** `EA 7!.txt` (5,583 lines / 658,476 bytes) — "DAVID SLING IATOS: Pure Python Architectural Blueprint"
**Repo:** `ITNATH/DAVID-SLING` @ branch `arena/f285e712-david-sling` (base `33d8baea`)
**Phase:** Comprehension & analysis only — **no implementation code written yet** (per directive)

---

## 0. Anatomy of the Source Document (provenance map)

The uploaded file is not a single spec — it is a composite of five logical sections. I verified by byte-diff that the blueprint body is repeated **three times, verbatim** (only blank-line placement differs), so the unique content is:

| Section | Lines | Content |
|---|---|---|
| §A Meta-prompt | 1–41 | The operator's directive: PHASE 1 reconnaissance, PHASE 2 web-first-then-desktop milestones, PHASE 3 features (branding "DAVID SLING", Light/Dark toggle, Omni-Trade panel, full engines), PHASE 4 zero-error self-audit loop. Mandate: **strictly Python; running web version first, then desktop.** |
| §B Blueprint ×3 | 43–5471 | "DAVID SLING IATOS" header + **Executive Architectural Directive & Anomaly Remediation Log** (4 remediations) + the **master root-to-leaf directory tree** (reproduced in full in Part 1 below). |
| §C Key-subsystem specs | 5473–5515 | §4 Detailed spec: (A) Omni-Trade Execution & Basket Panel, (B) the 52 strategies across 8 families, (C) the QSS styling system. |
| §D Invariants | 5516–5520 | §5 Zero-violation verification: L0–L9 firewall vs L11–L12, 8-stage parameter lifecycle, pure-Python cohesion. |
| §E Dependencies | 5523–5580 | Pinned `requirements.txt` for Python 3.12+ (reproduced in Part 3.8). |

### The 4 executive remediations in the blueprint (load-bearing for everything else)
1. **Purge of the mixed-language stack** — `apps/web/`, `package.json`, `tsconfig.json`, `tailwind.config.ts`, `Dockerfile.web`, `frontend-ci.yml` are *deleted*; the UI is replaced by `apps/mission_control_gui/` — pure **PySide6 (Qt 6.7+)** + **QSS** + **qasync/QtAsyncio**.
2. **First-class Omni-Trade Execution & Basket Panel** inside Mission Control Global Overview (`.../views/mission_control/components/trade_execution/`): single trades (Market/Limit/Stop, R-multiple, dynamic lots, partial close 25/50/75%, break-even lock), single-pair multi (scale-in, ladders, batch closes), cross-pair baskets (hedge matrices, aggregate PnL, panic-flatten, correlation guards).
3. **52 Strategy Vault** formalized under `src/david_sling/strategies/` — 8 families mapped to 4 peer engines with **zero engine-to-engine coupling**.
4. **15-layer unidirectional zero-circular-dependency firewall**: L0 Kernel → L1 Platform → L2 Data & Parameter → L3 Perception → L4 Scenario & Thesis → L5 Fusion Brain → L6 Validation → L7 Routing → L8 Peer Engines → L9 Precision & Signal → L10 Execution Boundary Firewall → L11 Risk & Sizing → L12 Broker & Order Execution → L13 Audit & Learning → L14 Application & GUI.

---

## PART 1 — EXHAUSTIVE, FULLY-ANNOTATED SYSTEM DIRECTORY MAP (root-to-leaf, verbatim from the blueprint)

The following is the authoritative tree exactly as specified in the document (whitespace-normalized). Every folder and file carries its prescribed purpose. This is the literal map to be created.

```text
DAVID_SLING_IATOS/                                                    # Master Institutional Algorithmic Trading Operating System (IATOS) Root
│
├── README.md                                                         # Master constitution, system doctrine, lifecycle, dependency laws, engine peer model, and evidence hierarchy.
├── LICENSE                                                           # Proprietary institutional software license terms, cryptographic entitlement, and governance.
├── CHANGELOG.md                                                      # Semantic version history, security updates, mathematical modifications, and architectural delta log.
├── SECURITY.md                                                       # Secure boot rules, cryptographic attestation, secret handling, and vulnerability reporting protocols.
├── CODEOWNERS                                                        # Domain ownership, review policies, and branch merge authority boundaries across all sub-frameworks.
├── CONTRIBUTING.md                                                   # Software engineering standards, testing gates, and strict zero-layer-violation rules.
├── pyproject.toml                                                    # Python package metadata, PEP 517 build configuration, dependencies, and tool settings (Ruff, Mypy, Pytest).
├── requirements.txt                                                  # Pinned production runtime dependencies: PySide6, pyqtgraph, qasync, numpy, scipy, polars, etc.
├── requirements-dev.txt                                              # Development, static analysis, profiling, property-testing, and doc generation tools.
├── .env.example                                                      # Template environment variables for local and institutional cluster deployments (zero hardcoded secrets).
├── .gitignore                                                        # Excludes secret stores, runtime state, binary logs, caches, and build artifacts.
├── .python-version                                                   # Fixed Python 3.12+ runtime environment specifier.
├── pytest.ini                                                        # Test discovery, custom tags, asyncio mode, pytest-qt desktop testing, and coverage thresholds.
├── mypy.ini                                                          # Strict static type checker configuration for core business logic, contracts, and PySide6 bindings.
├── ruff.toml                                                         # Code quality, import hygiene, and strict formatting rules.
├── Makefile                                                          # Canonical operational tasks: boot, test, lint, architecture-audit, backtest, gui, and package.
├── main.py                                                           # Single production application entry point; boots system, verifies integrity, starts engine & GUI loops.
├── run.py                                                            # Local developer launcher for live, scan, backtest, replay, gui, and diagnostic modes.
│
├── .vscode/                                                          # VS Code IDE Integration & Environment Setup
│   ├── settings.json                                                 # Interpreter paths, auto-formatting, static analyzer rules, and QSS/Python file associations.
│   ├── launch.json                                                   # Debug profiles for Boot, Mission Control GUI, API, Backtest, Replay, and Alert Dispatcher.
│   ├── tasks.json                                                    # VS Code task runner bindings for Makefile commands and validation scripts.
│   └── extensions.json                                               # Recommended extensions: Python, Mypy, Ruff, Qt for Python, Docker, YAML.
│
├── .github/                                                          # Automated Continuous Integration & Governance Workflows
│   ├── workflows/                                                    # GitHub Actions automated workflow definitions
│   │   ├── backend-ci.yml                                            # Python linting, type-checking (mypy), and pytest test suite runner.
│   │   ├── pyside6-gui-ci.yml                                        # PySide6 headless GUI unit & integration testing via pytest-qt and offscreen Xvfb.
│   │   ├── dialectical-compiler.yml                                  # Adversarial mutation and property-based invariance validation pipeline.
│   │   ├── quant-backtest-matrix.yml                                 # 31-year multi-asset automated historical simulation regression runner.
│   │   ├── performance-k6.yml                                        # Protocol-level load testing and sub-millisecond latency regression benchmarking.
│   │   ├── container-publish.yml                                     # Multi-arch Docker image builder and container registry publisher.
│   │   ├── architecture_audit.yml                                    # Validates layer isolation, imported boundaries, and zero silent-drop policy.
│   │   └── build.yml                                                 # Packaging, PyInstaller desktop artifact generation, and release verification.
│   └── ISSUE_TEMPLATE/                                               # Standardized issue templates for institutional defect reporting
│       ├── bug_report.md                                             # Form for structural, architectural, or numerical bug reports.
│       └── strategy_enhancement.md                                   # Form for proposing algorithmic or indicator enhancements.
│
├── deploy/                                                           # Production & Development Infrastructure Configurations
│   ├── docker/                                                       # Multi-stage production container blueprints
│   │   ├── Dockerfile                                                # Minimal secure production image for David Sling IATOS headless core.
│   │   ├── Dockerfile.api                                            # Optimized multi-stage build Dockerfile for FastAPI ASGI backend.
│   │   ├── Dockerfile.gui                                            # Production container for virtualized X11/Wayland/VNC institutional GUI deployment.
│   │   └── Dockerfile.dev                                            # Development container with hot-reloading, profiling, and debugging tools.
│   ├── compose/                                                      # Multi-service local and cluster container stacks
│   │   ├── docker-compose.yml                                        # Production service topology: Runtime, Mission Control API, Redis, Postgres, Ledger Node.
│   │   └── docker-compose.dev.yml                                    # Local development stack with debug endpoints and hot-reloading telemetry bus.
│   ├── kubernetes/                                                   # Cloud-native orchestration manifests
│   │   ├── namespace.yaml                                            # Isolated Kubernetes namespace definition for David Sling system.
│   │   ├── deployment.yaml                                           # Core engine pod specs with health probes and resource limits.
│   │   ├── service.yaml                                              # Cluster-internal network exposure for microservices and API gateways.
│   │   ├── ingress.yaml                                              # Ingress configuration with TLS termination for telemetry API.
│   │   ├── configmap.yaml                                            # Non-sensitive runtime parameters map.
│   │   └── secrets-sealed.yaml                                       # Bitnami SealedSecrets manifest for institutional encrypted credentials.
│   ├── packaging/                                                    # Standalone Desktop Application Bundlers
│   │   ├── pyinstaller.spec                                          # PyInstaller specification for compiling single-binary standalone PySide6 GUI desktop app.
│   │   ├── nuitka_build.py                                           # Nuitka C-extension compiler script for ultra-low latency GUI & engine binary packaging.
│   │   └── installer_manifest.json                                   # Cross-platform Windows/Linux institutional deployment manifest.
│   └── systemd/                                                      # Bare-metal host daemon specifications
│       ├── david-sling.service                                       # Systemd daemon service unit for main engine host deployments.
│       └── david-sling-bridge.service                                # Systemd daemon unit for broker execution bridge.
│
├── apps/                                                             # Deployable Operator-Facing Applications (PURE PYTHON + QSS)
│   └── mission_control_gui/                                          # Pure Python PySide6 (Qt6) Mission Control Desktop Operating Center
│       ├── __init__.py                                               # Package identity marker.
│       ├── main.py                                                   # Mission Control GUI entry point (boots PySide6 event loop & async bridge).
│       ├── config.py                                                 # GUI runtime preferences, window coordinates, theme state, refresh rate (60/120Hz).
│       │
│       ├── resources/                                                # Static Graphical Assets & QSS Stylesheets
│       │   ├── qss/                                                  # Pure Qt Style Sheets (QSS) for Professional Financial Terminals
│       │   │   ├── main.qss                                          # Root stylesheet orchestrating theme loading, global reset, and typography.
│       │   │   ├── theme_institutional_dark.qss                      # Deep charcoal/navy institutional theme (#0D1117 base, #161B22 card, #30363D border).
│       │   │   ├── theme_bloomberg_terminal.qss                      # Classic amber/black Bloomberg professional terminal color palette.
│       │   │   ├── theme_cyber_matrix.qss                            # High-contrast tactical green/cyan/magenta dark theme.
│       │   │   ├── theme_high_contrast.qss                           # Regulatory accessibility high-contrast theme.
│       │   │   └── widgets/                                          # Granular QSS Component Stylesheets
│       │   │       ├── buttons.qss                                   # Primary, secondary, danger, warning, and emergency-halt push button styles.
│       │   │       ├── inputs.qss                                    # QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, and toggle controls.
│       │   │       ├── tables.qss                                    # QTableView, QTableWidget, and QTreeWidget high-density row styling.
│       │   │       ├── cards.qss                                     # QFrame and QGroupBox container cards with header ribbons.
│       │   │       ├── tabs.qss                                      # QTabWidget and QTabBar custom tabs with glowing active pill indicator.
│       │   │       ├── status_pills.qss                              # Badges for Precision Tiers (Tier 1-4), Engine states, and Risk status.
│       │   │       ├── charts.qss                                    # PyQtGraph canvas background, grid lines, and axis label typography.
│       │   │       └── dialogs.qss                                   # Modal execution confirmations, risk alerts, and credential dialogs.
│       │   ├── icons/                                                # Vector SVG Interface Icons
│       │   │   ├── system_logo.svg                                   # David Sling Institutional emblem.
│       │   │   ├── trade_buy.svg                                     # Long entry icon.
│       │   │   ├── trade_sell.svg                                    # Short entry icon.
│       │   │   ├── trade_close.svg                                   # Position exit / close icon.
│       │   │   ├── emergency_halt.svg                                # Emergency book flatten / panic kill icon.
│       │   │   ├── engine_scalp.svg                                  # Engine A (Quant Scalping) icon.
│       │   │   ├── engine_intraday.svg                               # Engine B (Tactical Intraday) icon.
│       │   │   ├── engine_swing.svg                                  # Engine C (Swing Structural) icon.
│       │   │   ├── engine_macro.svg                                  # Engine D (Macro Institutional) icon.
│       │   │   ├── fusion_brain.svg                                  # 9-Layer Bidirectional Fusion Brain icon.
│       │   │   ├── scenario_pool.svg                                 # Universal Scenario Pool icon.
│       │   │   └── ledger_lock.svg                                   # Cryptographic ledger audit chain icon.
│       │   └── fonts/                                                # Bundled High-Legibility Monospace & Display Fonts
│       │       ├── JetBrainsMono-Regular.ttf                         # High-density numerical display font for prices, lots, and PnL.
│       │       ├── JetBrainsMono-Bold.ttf                            # Heavy numerical weights for equity and margin figures.
│       │       └── Inter-VariableFont.ttf                            # Clean typographic font for labels, logs, and dialogs.
│       │
│       ├── src/                                                      # PySide6 GUI Source Code
│       │   ├── __init__.py                                           # GUI source package boundary.
│       │   ├── app.py                                                # Custom QApplication subclass managing DPI scaling, font cache, and palette.
│       │   ├── main_window.py                                        # Master application shell: navigation bar, top status ribbon, stacked workspace.
│       │   ├── qss_manager.py                                        # Live QSS stylesheet loader, hot-reloader (in dev mode), and theme switcher.
│       │   │
│       │   ├── bridge/                                               # Backend Integration & Asynchronous IPC Bridge
│       │   │   ├── __init__.py                                       # Bridge package boundary.
│       │   │   ├── async_qt_bridge.py                                # Coordinates Python asyncio event loop with Qt6 event loop (via qasync).
│       │   │   ├── ipc_client.py                                     # High-speed IPC / UNIX domain socket / Named Pipe client to core engines.
│       │   │   ├── telemetry_receiver.py                             # High-frequency WebSocket subscriber receiving tick/PnL/health streams.
│       │   │   ├── command_dispatcher.py                             # Dispatches user trade executions and config mutations to core command bus.
│       │   │   └── event_signals.py                                  # PySide6 QObject holding all global Qt signals (telemetry, orders, alerts).
│       │   │
│       │   ├── viewmodels/                                           # MVVM Presentation Logic (Decoupled from PySide6 Widgets)
│       │   │   ├── __init__.py                                       # ViewModel package boundary.
│       │   │   ├── mission_control_vm.py                             # ViewModel driving Mission Control overview, health matrix, and scenario state.
│       │   │   ├── trade_execution_vm.py                             # ViewModel driving single-trade, single-pair, and cross-pair basket operations.
│       │   │   ├── portfolio_vm.py                                   # ViewModel driving active positions, account telemetry, and exposure metrics.
│       │   │   ├── control_panel_vm.py                               # ViewModel managing draft configuration, diffs, and authorized commits.
│       │   │   ├── fusion_graph_vm.py                                # ViewModel driving 9-layer HTF↔MTF↔LTF bidirectional convergence maps.
│       │   │   ├── scenario_pool_vm.py                               # ViewModel driving 31-scenario transitions and active state machines.
│       │   │   ├── engine_status_vm.py                               # ViewModel monitoring four peer engines (A, B, C, D) health and routing.
│       │   │   └── evidence_ledger_vm.py                             # ViewModel driving cryptographic ledger audit feeds and hash chains.
│       │   │
│       │   ├── views/                                                # Full-Screen Top-Level Workspace Views (StackedWidget pages)
│       │   │   ├── __init__.py                                       # Views package boundary.
│       │   │   │
│       │   │   ├── mission_control/                                  # GLOBAL OVERVIEW MISSION CONTROL CENTER (Executable & Viewable)
│       │   │   │   ├── __init__.py                                   # Mission Control view package boundary.
│       │   │   │   ├── global_overview_view.py                       # Top-level executable overview composed of telemetry, engines, and trade panels.
│       │   │   │   └── components/                                       # Mission Control Specialized Section Panels
│       │   │   │       ├── __init__.py                               # Components package boundary.
│       │   │   │       ├── telemetry_bar.py                          # Account balance, equity, free margin, margin level %, floating PnL ticker.
│       │   │   │       ├── system_health_matrix.py                   # Real-time grid of all 15 architecture domains and low-latency health dots.
│       │   │   │       ├── market_awareness_panel.py                 # Live price, ATR, spread, session epoch (Asia/London/NY), and regime display.
│       │   │   │       ├── scenario_pool_display.py                  # Live 31-Scenario state machine tracker with active/forming scenario badges.
│       │   │   │       ├── fusion_brain_summary.py                   # 9-Layer bidirectional convergence gauge (MN1 down to M1 score matrix).
│       │   │   │       ├── engine_status_grid.py                     # Real-time state cards for Engines A, B, C, D (Armed, Triggered, Invalidation).
│       │   │   │       ├── active_signals_feed.py                    # Live TechnicalSignalTicket queue with precision tiers (Tier 1-4).
│       │   │   │       │
│       │   │   │       └── trade_execution/                          # DEDICATED MISSION CONTROL MULTI-TRADE EXECUTION PANEL (Executable Core)
│       │   │   │           ├── __init__.py                           # Trade execution components package boundary.
│       │   │   │           ├── omni_trade_panel.py                   # Master interactive container docking single, multi, and cross-pair sections.
│       │   │   │           ├── single_trade_controller.py            # Opens/Closes single trade: Lot, Symbol, Market/Limit, TP/SL, 1-Click Close.
│       │   │   │           ├── single_pair_multi_trade_controller.py # Controls multiple trades on single pair: Scale-In, Ladder, Batch Close.
│       │   │   │           ├── cross_pair_basket_controller.py       # Cross-Pairs multiple trade execution: Basket Orders, Currency Correlation.
│       │   │   │           ├── cross_pair_pnl_matrix.py              # Real-time interactive PnL grid: Gross Profit, Loss, Net, Currency exposure.
│       │   │   │           ├── quick_action_toolbar.py               # Panic buttons: Close All Profitable, Close All Losing, Break-Even All, Halt.
│       │   │   │           └── execution_confirm_dialog.py           # Pre-flight order verification modal showing slippage, margin impact, fees.
│       │   │   │
│       │   │   ├── control_panel/                                    # HARDCORE OPERATOR CONTROL PANEL (Authorized Mutations)
│       │   │   │   ├── __init__.py                                   # Control panel view package boundary.
│       │   │   │   ├── control_panel_view.py                         # Master configuration editor with category navigation and diff preview.
│       │   │   │   └── sections/                                         # Dedicated Configuration Section Forms
│       │   │   │       ├── __init__.py                               # Sections package boundary.
│       │   │   │       ├── system_config_form.py                     # Boot parameters, logging verbosity, worker bounds, and debug mode.
│       │   │   │       ├── broker_connection_form.py                 # Broker account credentials, server address, FIX/MT5 toggle, latency test.
│       │   │   │       ├── engine_override_form.py                   # Peer engine enablement (A/B/C/D), timeframe profiles, and sensitivity.
│       │   │   │       ├── risk_governance_form.py                   # Session risk cap (1.50%), daily loss limit, drawdown circuit-breaker.
│       │   │   │       ├── position_sizing_form.py                   # Minimum lot enforcement, Kelly multiplier, risk-per-trade percentage.
│       │   │   │       ├── tp_sl_trailing_form.py                    # ATR take-profit multipliers, trailing stop triggers (+2.0R), time stops.
│       │   │   │       ├── breakeven_spike_form.py                   # Breakeven trigger (+1.5 ATR), volatility spike defense thresholds.
│       │   │   │       ├── news_blackout_form.py                     # High-impact news event filters and custom blackout window scheduler.
│       │   │   │       └── emergency_controls_form.py                # Hardware kill switch, book quarantine, and broker connection reset.
│       │   │   │
│       │   │   ├── portfolio/                                        # PORTFOLIO MANAGEMENT & EXECUTION AUDIT
│       │   │   │   ├── __init__.py                                   # Portfolio view package boundary.
│       │   │   │   ├── portfolio_view.py                             # Live positions table, closed trade history, equity/balance curve.
│       │   │   │   ├── open_positions_table.py                       # High-density real-time QTableView with in-line modify/close buttons.
│       │   │   │   ├── trade_history_table.py                        # Searchable, filterable closed trades table with execution attribution.
│       │   │   │   ├── exposure_breakdown_widget.py                  # Graphical bar chart showing net currency exposure (USD, EUR, GBP, JPY).
│       │   │   │   └── pnl_equity_chart.py                           # PyQtGraph real-time interactive equity, balance, and drawdown curves.
│       │   │   │
│       │   │   ├── evidence_ledger/                                  # CRYPTOGRAPHIC EVIDENCE LEDGER EXPLORER
│       │   │   │   ├── __init__.py                                   # Evidence ledger view package boundary.
│       │   │   │   ├── ledger_view.py                                # Append-only evidence audit stream viewer with search and filters.
│       │   │   │   ├── evidence_record_detail.py                     # Inspector for individual evidence records, parameters, and scores.
│       │   │   │   ├── hash_chain_status_widget.py                   # SHA-256 / BLAKE3 cryptographic continuity validator display.
│       │   │   │   └── lineage_tree_widget.py                        # Interactive QTreeWidget displaying decision ancestry from tick to order.
│       │   │   │
│       │   │   ├── graph_topology/                                   # MULTI-TIMEFRAME TOPOLOGY & BRAIN VISUALIZERS
│       │   │   │   ├── __init__.py                                   # Graph topology view package boundary.
│       │   │   │   ├── graph_view.py                                 # Multi-canvas visualizer for system graphs and state machines.
│       │   │   │   ├── fusion_matrix_canvas.py                       # Interactive 9-layer bidirectional HTF↔MTF↔LTF node and weight graph.
│       │   │   │   ├── scenario_state_machine_canvas.py              # Visual state diagram showing 31-scenario transitions and active path.
│       │   │   │   └── architecture_dependency_canvas.py             # Live runtime verification of zero circular imports between domains.
│       │   │   │
│       │   │   └── charts/                                           # HIGH-PERFORMANCE TRADING CHARTS (PyQtGraph)
│       │   │       ├── __init__.py                                   # Charts package boundary.
│       │   │       ├── chart_view.py                                 # Multi-timeframe tabbed chart workspace.
│       │   │       ├── candlestick_widget.py                         # 120 FPS hardware-accelerated OHLCV candlestick chart.
│       │   │       ├── orderflow_ladder_widget.py                    # Level 2 DOM depth-of-market queue and volume footprint ladder.
│       │   │       ├── liquidity_zones_overlay.py                    # Renders FVGs, Order Blocks, Liquidity Sweeps, and Breakers on chart.
│       │   │       └── indicator_dock_widget.py                      # Sub-chart docks for RSI, MACD, Volume Delta, and ATR oscillators.
│       │   │
│       │   ├── widgets/                                              # Reusable Custom PySide6 UI Primitives
│       │   │   ├── __init__.py                                       # Widgets package boundary.
│       │   │   ├── metric_card.py                                    # Formatted KPI display card with numerical delta and sparkline.
│       │   │   ├── status_badge.py                                   # Pill-shaped colored status indicator (Armed, Idle, Failed, Vetoed).
│       │   │   ├── precision_grade_pill.py                           # Tier 1 / Tier 2 / Tier 3 / Tier 4 precision quality tag.
│       │   │   ├── currency_pnl_label.py                             # Formats currency values with color-coded profit (+) / loss (-) styling.
│       │   │   ├── toggle_switch.py                                  # Smooth-animated iOS-style boolean toggle switch widget.
│       │   │   ├── numerical_slider_spinbox.py                       # Linked slider and double-spinbox for intuitive numeric inputs.
│       │   │   ├── alert_banner.py                                   # Dismissible system notification banner with auto-hide timer.
│       │   │   └── search_filter_bar.py                              # Debounced search input with column filter dropdowns for tables.
│       │   │
│       │   ├── dialogs/                                              # Modal Operator Dialogs
│       │   │   ├── __init__.py                                       # Dialogs package boundary.
│       │   │   ├── auth_login_dialog.py                              # Cryptographic Master Admin / Operator authentication gate.
│       │   │   ├── emergency_halt_dialog.py                          # Multi-confirmation emergency trading halt modal.
│       │   │   ├── config_commit_diff_dialog.py                      # Side-by-side diff viewer before applying configuration changes.
│       │   │   └── broker_reconnect_dialog.py                        # Manual broker gateway reconnection and status probe dialog.
│       │   │
│       │   └── tests/                                                # PySide6 GUI Automated Test Suites (pytest-qt)
│       │       ├── __init__.py                                       # GUI tests package boundary.
│       │       ├── conftest.py                                       # Qt test fixtures, headless display setup, mock event bus.
│       │       ├── test_main_window.py                               # Tests main window startup, view switching, and status bar.
│       │       ├── test_global_overview_view.py                      # Tests Global Overview telemetry and component synchronization.
│       │       ├── test_trade_execution_panel.py                     # Tests single, multi, and cross-pair trade execution controls.
│       │       ├── test_cross_pair_pnl_matrix.py                     # Tests real-time cross-pair PnL calculation and batch close triggers.
│       │       ├── test_control_panel_mutations.py                   # Tests configuration form validation, diffs, and commit signals.
│       │       └── test_qss_manager.py                               # Tests QSS stylesheet compilation, theme swapping, and syntax validity.
│
├── src/                                                              # Canonical Python Source Root
│   └── david_sling/                                                  # Main Canonical Package Governing All Execution Logic (David Sling OS)
│       ├── __init__.py                                               # Root package identity, version, public boundary exports.
│       ├── py.typed                                                  # Marker for strict PEP 561 typed distribution.
│       │
│       ├── core/                                                     # L0 — Constitutional Shared Kernel
│       │   ├── __init__.py                                           # Core package boundary.
│       │   ├── constitutional_laws.py                                # Immutable global laws: one scenario authority, one fusion brain, no silent drops.
│       │   ├── operating_principles.py                               # Enforces immutable governing lifecycle laws at import time.
│       │   ├── architecture_manifest.py                              # Authoritative registry of modules, domains, contracts, subsystem identities.
│       │   ├── dependency_graph.py                                   # NetworkX topological representation verifying zero circular dependencies.
│       │   ├── technical_boundaries.py                               # Structural firewall preventing technical core from touching risk/broker/sizing.
│       │   ├── evidence_hierarchy.py                                 # Strict hierarchy governing parameter scoring, evidence classes, and promotion.
│       │   ├── session_epoch_manager.py                              # 6-Phase Session Epoch Clock (Asia, London, NY, Overlaps, 10 AM Club).
│       │   ├── three_core_confluence_gatekeeper.py                   # PA (40%) + CDT (35%) + Indicators (25%) Confluence Gatekeeper.
│       │   ├── no_time_expiry_policy.py                              # Globally enforces max_hold_time = null.
│       │   ├── terminal_state_policy.py                              # UNKNOWN / CONFLICTED / NOVEL map to WAIT / NO_ROUTE / ABSTAIN.
│       │   ├── deterministic_decision_contract.py                    # Deterministic decision behavior, reproducibility, and replay contract.
│       │   ├── abstention_policy.py                                  # Explicit WAIT / NO_ROUTE / ABSTAIN behavior.
│       │   ├── exceptions.py                                         # Public exception surface re-exported from core/errors.
│       │   ├── contracts/                                            # Master System Contracts
│       │   │   ├── __init__.py                                       # Contract package boundary.
│       │   │   ├── boot_contract.py                                  # Boot stage, result, and boot attestation contracts.
│       │   │   ├── security_contract.py                              # Identity, authentication, and authorization contracts.
│       │   │   ├── license_contract.py                               # License validation, entitlement, and revocation contracts.
│       │   │   ├── configuration_contract.py                         # Effective configuration, precedence, and propagation contracts.
│       │   │   ├── parameter_contract.py                             # Parameter lifecycle, state, lineage, and contribution contracts.
│       │   │   ├── evidence_contract.py                              # Evidence record, lineage, hash chain, and audit contracts.
│       │   │   ├── market_contract.py                                # Tick, OHLCV, order book, trade flow, news, and chat contracts.
│       │   │   ├── awareness_contract.py                             # Market awareness snapshot and state contracts.
│       │   │   ├── intelligence_contract.py                          # Technical observation and evidence packet contracts.
│       │   │   ├── regime_contract.py                                # Regime classification and transition contracts.
│       │   │   ├── scenario_contract.py                              # Universal Scenario Pool state and classification contracts.
│       │   │   ├── hypothesis_contract.py                            # Thesis construction, invalidation, and revalidation contracts.
│       │   │   ├── grammar_contract.py                               # Causal formation grammar and sequence integrity contracts.
│       │   │   ├── fusion_contract.py                                # HTF ↔ MTF ↔ LTF fusion request, bundle, and decision contracts.
│       │   │   ├── validation_contract.py                            # Technical validation, contradiction, and gate contracts.
│       │   │   ├── routing_contract.py                               # Engine routing, eligibility, and NO_ROUTE contracts.
│       │   │   ├── engine_contract.py                                # Common peer-engine input/output contract.
│       │   │   ├── precision_contract.py                             # Precision grade, quality, and trigger readiness contracts.
│       │   │   ├── signal_contract.py                                # TechnicalSignalTicket and signal evidence contracts.
│       │   │   ├── execution_boundary_contract.py                    # Technical-to-downstream handoff contract.
│       │   │   ├── risk_contract.py                                  # Risk veto/approval contract without technical mutation.
│       │   │   ├── sizing_contract.py                                # Position sizing and lot normalization contract.
│       │   │   ├── portfolio_contract.py                             # Exposure, concentration, and correlation contract.
│       │   │   ├── broker_contract.py                                # Broker capability, symbol specification, and order contract.
│       │   │   ├── order_contract.py                                 # Order lifecycle and reconciliation contract.
│       │   │   ├── position_contract.py                              # Position lifecycle and thesis monitoring contract.
│       │   │   ├── multi_trade_contract.py                           # Batch single-pair and cross-pair trade execution contract.
│       │   │   ├── rescan_contract.py                                # Sub-5ms new lifecycle launcher contract after exit/failure.
│       │   │   ├── alert_contract.py                                 # Alert event, channel routing, and dispatch audit contracts.
│       │   │   ├── journal_contract.py                               # Immutable journal and attribution contracts.
│       │   │   └── monitoring_contract.py                            # Monitoring, drift proposal, and learning boundary contracts.
│       │   ├── schemas/                                              # Core Pydantic v2 Schema Definitions & Data Contracts
│       │   │   ├── __init__.py                                       # Schema package boundary.
│       │   │   ├── symbol.py                                         # Canonical instrument identity schema.
│       │   │   ├── timeframe.py                                      # Canonical timeframe identity and role schema.
│       │   │   ├── session.py                                        # Trading session, London/NY overlaps, and epoch schema.
│       │   │   ├── tick.py                                           # Tick event schema.
│       │   │   ├── candle.py                                         # OHLCV candle schema.
│       │   │   ├── orderbook.py                                      # Order-book snapshot, L2 DOM queue, and delta schema.
│       │   │   ├── trade_flow.py                                     # Executed trade flow and tape print schema.
│       │   │   ├── chat_message.py                                   # Market chat message schema.
│       │   │   ├── news_event.py                                     # News and economic event schema.
│       │   │   ├── parameter_state.py                                # VALID / INVALID / MISSING / STALE / CONFLICTED parameter schema.
│       │   │   ├── evidence_record.py                                # Immutable evidence record schema with Merkle roots.
│       │   │   ├── market_snapshot.py                                # Reconstructed market state snapshot schema.
│       │   │   ├── regime_state.py                                   # Regime classification schema.
│       │   │   ├── scenario_state.py                                 # Universal scenario classification schema (S1 to S31).
│       │   │   ├── fusion_snapshot.py                                # Bidirectional 9-layer fusion state snapshot schema.
│       │   │   ├── validation_result.py                              # Technical validation and contradiction result schema.
│       │   │   ├── hypothesis_state.py                               # Thesis state schema (ARMED, TRIGGERED, HOLD, CHANGE, FAILURE).
│       │   │   ├── grammar_state.py                                  # Formation grammar sequence state schema.
│       │   │   ├── route_decision.py                                 # Engine route or NO_ROUTE decision schema.
│       │   │   ├── engine_decision.py                                # Engine-specific qualification decision schema.
│       │   │   ├── precision_grade.py                                # Precision grade schema (Tier 1 through Tier 4).
│       │   │   ├── signal_ticket.py                                  # Canonical TechnicalSignalTicket schema.
│       │   │   ├── order_intent.py                                   # Downstream order intent schema.
│       │   │   ├── multi_trade_intent.py                             # Batch order intent and cross-pair basket instruction schema.
│       │   │   ├── cross_pair_pnl_state.py                           # Cross-pair aggregated PnL and exposure schema.
│       │   │   ├── position_state.py                                 # Active position state schema.
│       │   │   ├── alert_event.py                                    # Alert event schema.
│       │   │   └── rescan_event.py                                   # Sub-5ms rescan lifecycle event schema.
│       │   ├── utilities/                                            # Core Mathematical & Utility Functions
│       │   │   ├── __init__.py                                       # Utility package boundary.
│       │   │   ├── time_utils.py                                     # UTC timestamp, epoch, and session time utilities.
│       │   │   ├── math_utils.py                                     # Numeric math helpers for technical computation.
│       │   │   ├── decimal_utils.py                                  # Exact decimal arithmetic for price and lot safety.
│       │   │   ├── id_utils.py                                       # Deterministic UUIDv5 / ULID identity generation for records.
│       │   │   ├── hashing_utils.py                                  # SHA3/BLAKE3/SHA-256 hashing for evidence and audit chains.
│       │   │   ├── validation_utils.py                               # Shared validation helpers.
│       │   │   ├── immutable_utils.py                                # Frozen object and memory snapshot helpers.
│       │   │   ├── collection_utils.py                               # Deterministic collection helpers.
│       │   │   ├── result_utils.py                                   # Result/Ok/Error monadic functional helpers.
│       │   │   └── concurrency_utils.py                              # Safe async task, non-blocking lock, and queue helpers.
│       │   └── errors/                                               # System Error Taxonomy
│       │       ├── __init__.py                                       # Error package boundary.
│       │       ├── base.py                                           # Root David Sling error type.
│       │       ├── architecture_error.py                             # Architecture manifest and dependency violations.
│       │       ├── boundary_violation.py                             # Cross-domain firewall violations.
│       │       ├── validation_error.py                               # Schema and semantic validation failures.
│       │       ├── configuration_error.py                            # Invalid or unauthorized configuration errors.
│       │       ├── boot_error.py                                     # Boot sequence failures.
│       │       ├── security_error.py                                 # Authentication and authorization failures.
│       │       ├── license_error.py                                  # License validation failures.
│       │       ├── evidence_error.py                                 # Evidence chain or ledger failures.
│       │       ├── parameter_error.py                                # Parameter lifecycle failures.
│       │       ├── scenario_error.py                                 # Scenario classification failures.
│       │       ├── fusion_error.py                                   # Fusion coordination failures.
│       │       ├── routing_error.py                                  # Engine routing failures.
│       │       ├── engine_error.py                                   # Engine qualification failures.
│       │       ├── precision_error.py                                # Precision evaluation failures.
│       │       ├── signal_error.py                                   # Signal construction failures.
│       │       ├── execution_error.py                                # Downstream handoff failures.
│       │       ├── multi_trade_error.py                              # Batch or cross-pair execution failures.
│       │       ├── data_error.py                                     # Ingestion and integrity failures.
│       │       ├── alert_error.py                                    # Alert dispatch failures.
│       │       └── untracked_parameter_error.py                      # Raised when a parameter bypasses mandatory lifecycle.
│       │
│       ├── bootstrap/                                                # L1 — David OS Boot Domain (Loads State UI 'DAVID SLING')
│       │   ├── __init__.py                                           # Bootstrap package boundary.
│       │   ├── david_os_boot.py                                      # Supreme David OS boot orchestrator (UI shows 'DAVID SLING').
│       │   ├── boot_sequence.py                                      # Hard ordered boot stages and stage transition rules.
│       │   ├── boot_manifest.py                                      # Immutable manifest of required modules, hashes, and boot constraints.
│       │   ├── boot_state.py                                         # Immutable boot-state: BOOTING / SECURITY_CHECK / LICENSE_CHECK / READY / HALTED.
│       │   ├── secure_boot_chain.py                                  # Verifies integrity of boot components and configuration roots.
│       │   ├── preflight_checks.py                                   # Consolidated preflight supervisor.
│       │   ├── environment_validator.py                              # Python runtime, OS, architecture, memory, environment checks.
│       │   ├── dependency_validator.py                               # Validates pinned dependency versions and hashes.
│       │   ├── filesystem_validator.py                               # Required directories, permissions, writable runtime paths.
│       │   ├── clock_validator.py                                    # UTC synchronization and precision time source validation.
│       │   ├── process_lock.py                                       # Single-instance enforcement and IPC socket lock.
│       │   ├── architecture_integrity_check.py                       # Validates repository/package architecture against manifest.
│       │   ├── configuration_integrity_check.py                      # Validates config tree hashes and boot-time configuration.
│       │   ├── parameter_registry_check.py                           # Ensures every declared parameter is registered and traceable.
│       │   ├── evidence_ledger_check.py                              # Ensures evidence infrastructure is ready before intelligence starts.
│       │   ├── boot_failure.py                                       # Controlled safe halt and forensic dump.
│       │   └── boot_audit.py                                         # Immutable boot-stage audit trail.
│       │
│       ├── security/                                                 # L1 — Security / Identity / License / Authorization Domain
│       │   ├── __init__.py                                           # Security package boundary.
│       │   ├── security_engine.py                                    # Master security supervisor.
│       │   ├── identity/                                             # Authentication & Master Admin Verification
│       │   │   ├── __init__.py                                       # Identity package boundary.
│       │   │   ├── identity_provider.py                              # Issues cryptographic identities and signed claims.
│       │   │   ├── identity_registry.py                              # Registry of master admin, users, services, daemons.
│       │   │   ├── master_admin_authentication.py                    # Cryptographic Master Admin authentication gate; locked until verification.
│       │   │   ├── user_authentication.py                            # Standard operator authentication.
│       │   │   └── service_authentication.py                         # Internal service/process authentication.
│       │   ├── authorization/                                        # Role-Based Access Control (RBAC)
│       │   │   ├── __init__.py                                       # Authorization package boundary.
│       │   │   ├── role_based_access.py                              # Role and permission enforcement.
│       │   │   ├── policy_engine.py                                  # Policy-as-code authorization engine.
│       │   │   ├── admin_permissions.py                              # Master-admin privilege boundaries.
│       │   │   ├── user_permissions.py                               # Operator/analyst permission boundaries.
│       │   │   ├── service_permissions.py                            # Service-level restricted permissions.
│       │   │   ├── authorization_guard.py                            # Final operation authorization guard.
│       │   │   └── authorization_audit.py                            # Immutable authorization decision log.
│       │   ├── license/                                              # Cryptographic Institutional License Verification
│       │   │   ├── __init__.py                                       # License package boundary.
│       │   │   ├── license_engine.py                                 # Master license gate.
│       │   │   ├── license_validator.py                              # Validates signature, integrity, expiry, and entitlements.
│       │   │   ├── license_signature.py                              # Cryptographic license signature verification.
│       │   │   ├── license_expiry.py                                 # Expiry and grace policy.
│       │   │   ├── license_entitlements.py                           # Feature and capacity entitlements.
│       │   │   ├── license_feature_gate.py                           # Enables/disables licensed features.
│       │   │   ├── license_device_binding.py                         # Hardware/machine binding.
│       │   │   ├── license_session.py                                # Licensed runtime session state.
│       │   │   ├── license_revocation.py                             # Revocation handling.
│       │   │   └── license_audit.py                                  # License verification audit trail.
│       │   ├── cryptography/                                         # Hashing, Signatures, and AES-GCM Encryption
│       │   │   ├── __init__.py                                       # Cryptography package boundary.
│       │   │   ├── hash_service.py                                   # SHA3/BLAKE3/SHA-256 hashing service.
│       │   │   ├── signature_service.py                              # Ed25519/ECDSA signature service.
│       │   │   ├── encryption_service.py                             # AES-GCM envelope encryption service.
│       │   │   ├── key_manager.py                                    # Key loading, wrapping, and rotation boundary.
│       │   │   └── integrity_verifier.py                             # File/config/module integrity verification.
│       │   ├── session/                                              # Active Security Sessions
│       │   │   ├── __init__.py                                       # Session package boundary.
│       │   │   ├── security_session.py                               # Authenticated session object.
│       │   │   ├── session_token.py                                  # Signed session token.
│       │   │   ├── session_expiry.py                                 # Session timeout and renewal rules.
│       │   │   └── session_revocation.py                             # Forced logout and token invalidation.
│       │   ├── secrets/                                              # Secure Secret Scope Management
│       │   │   ├── __init__.py                                       # Secrets package boundary.
│       │   │   ├── secrets_provider.py                               # Secure secret access boundary.
│       │   │   ├── secret_scope.py                                   # Scope restriction per consumer.
│       │   │   └── secret_audit.py                                   # Secret access audit.
│       │   ├── security_monitoring/                                  # Intrusion and Anomaly Detection
│       │   │   ├── __init__.py                                       # Security monitoring package boundary.
│       │   │   ├── intrusion_detection.py                            # Detects abnormal access patterns.
│       │   │   ├── suspicious_activity.py                            # Tracks suspicious operator/service behavior.
│       │   │   ├── failed_authentication_monitor.py                  # Tracks repeated authentication failures.
│       │   │   ├── privilege_escalation_detector.py                  # Detects unauthorized privilege attempts.
│       │   │   ├── integrity_alert.py                                # Raises alerts for integrity violations.
│       │   │   └── security_event_logger.py                          # Immutable security event log.
│       │   └── security_audit.py                                     # Global security audit stream.
│       │
│       ├── configuration/                                            # L1 — Master Configuration Authority Domain
│       │   ├── __init__.py                                           # Configuration package boundary.
│       │   ├── configuration_engine.py                               # Supreme configuration coordinator.
│       │   ├── configuration_registry.py                             # Master registry of every configurable parameter.
│       │   ├── configuration_schema.py                               # Typed configuration models and section schemas.
│       │   ├── configuration_validator.py                            # Schema, range, semantic, and cross-field validation.
│       │   ├── precedence_engine.py                                  # Resolves source precedence without silent overrides.
│       │   ├── effective_configuration.py                            # Final immutable effective configuration object.
│       │   ├── configuration_snapshot.py                             # Point-in-time immutable configuration snapshot.
│       │   ├── configuration_versioning.py                           # Versioned configuration history.
│       │   ├── propagation_bus.py                                    # Publishes authorized effective configuration to governed domains.
│       │   ├── frozen_boot_constraints.py                            # Immutable constraints frozen at boot.
│       │   ├── policy_enforcer.py                                    # Enforces hard-core configuration policy across architecture.
│       │   └── configuration_audit.py                                # Records all configuration transitions.
│       │
│       ├── control_panel/                                            # Hardcore Operator Control Panel & Configuration Validation
│       │   ├── __init__.py                                           # Control Panel package boundary.
│       │   ├── panel_controller.py                                   # Receives operator commands from UI/API and imposes strict validation.
│       │   ├── input_schema.py                                       # Typed input schemas for every control-panel section.
│       │   ├── input_validator.py                                    # Validates inputs against schema and constitutional constraints.
│       │   ├── authorization_check.py                                # Ensures master admin/user has permission for requested mutation.
│       │   ├── command_handler.py                                    # Converts validated input into configuration commands.
│       │   ├── configuration_commit.py                               # Commits versioned configuration changes.
│       │   ├── hard_enforcement_router.py                            # Pushes effective controls into all governed modules dynamically.
│       │   ├── rollback.py                                           # Controlled rollback to prior valid configuration version.
│       │   ├── audit_command.py                                      # Records accepted/rejected control commands.
│       │   └── sections/                                             # Control Panel Configuration Sections
│       │       ├── __init__.py                                       # Control Panel section package boundary.
│       │       ├── david_os_status.py                                # Boot, integrity, and runtime status controls.
│       │       ├── license_auth.py                                   # License verification and session controls.
│       │       ├── system_status.py                                  # Global system health controls.
│       │       ├── broker_account.py                                 # Broker account connection and capability controls.
│       │       ├── symbols_timeframes.py                             # Symbol and timeframe matrix controls.
│       │       ├── engine_controls.py                                # Engine enable/disable and profile controls (Engines A, B, C, D).
│       │       ├── technical_mode_controls.py                        # Technical mode and strategy-family controls.
│       │       ├── indicator_controls.py                             # Indicator parameter governance controls.
│       │       ├── risk_governance.py                                # Risk policy governance controls (risk %, stop limits).
│       │       ├── capital_allocation.py                             # Capital allocation policy controls.
│       │       ├── position_sizing.py                                # Position sizing policy controls (lot sizes, min lot enforcement).
│       │       ├── order_management.py                               # Order handling policy controls.
│       │       ├── tp_sl_trailing.py                                 # TP/SL/trailing policy controls (multipliers, R-multiples).
│       │       ├── breakeven_spike_defense.py                        # Breakeven thresholds and spike defense mode controls.
│       │       ├── news_filter.py                                    # News and economic event filter controls.
│       │       ├── custom_news_windows.py                            # Custom high-impact news window controls.
│       │       ├── alert_controls.py                                 # Alert channel and routing controls.
│       │       ├── audit_export.py                                   # Audit and evidence export controls.
│       │       └── emergency_controls.py                             # Emergency halt, flatten, and quarantine controls.
│       │
│       ├── mission_control/                                          # Military Grade Mission Control Telemetry & Multi-Trade Engine
│       │   ├── __init__.py                                           # Mission Control package boundary.
│       │   ├── mission_control_server.py                             # High-speed telemetry web/IPC server feeding GUI dashboard.
│       │   ├── global_overview.py                                    # Whole-system operational overview orchestrator.
│       │   ├── architecture_map.py                                   # Live map of domains/modules/services and health state.
│       │   ├── health_matrix.py                                      # Cross-system health matrix.
│       │   ├── boot_status_board.py                                  # David OS boot stage visibility.
│       │   ├── license_status_board.py                               # License validation and entitlement visibility.
│       │   ├── security_status_board.py                              # Authentication, authorization, and session visibility.
│       │   ├── configuration_status_board.py                         # Effective configuration and propagation visibility.
│       │   ├── data_status_board.py                                  # Feed health, integrity, and reconstruction visibility.
│       │   ├── market_state_view.py                                  # Current market reconstruction state.
│       │   ├── awareness_view.py                                     # Awareness snapshot visibility.
│       │   ├── intelligence_view.py                                  # Technical intelligence evidence visibility.
│       │   ├── regime_view.py                                        # Regime classification visibility.
│       │   ├── scenario_state_view.py                                # Universal Scenario Pool visibility.
│       │   ├── fusion_state_view.py                                  # Bidirectional HTF ↔ MTF ↔ LTF fusion visibility.
│       │   ├── validation_view.py                                    # Validation and contradiction visibility.
│       │   ├── hypothesis_view.py                                    # Thesis state visibility.
│       │   ├── routing_view.py                                       # Engine routing and NO_ROUTE visibility.
│       │   ├── engine_state_view.py                                  # Four peer-engine state visibility.
│       │   ├── precision_view.py                                     # Precision grade visibility.
│       │   ├── signal_state_view.py                                  # Technical signal lifecycle visibility.
│       │   ├── execution_boundary_view.py                            # Technical-to-downstream handoff visibility.
│       │   ├── risk_view.py                                          # Risk veto/approval visibility.
│       │   ├── sizing_view.py                                        # Position sizing visibility.
│       │   ├── portfolio_view.py                                     # Portfolio exposure and margin telemetry visibility.
│       │   ├── broker_view.py                                        # Broker connectivity and capability visibility.
│       │   ├── order_view.py                                         # Order lifecycle visibility.
│       │   ├── position_view.py                                      # Position lifecycle visibility.
│       │   ├── multi_trade_operations_engine.py                      # Core engine executing single, single-pair multi, and cross-pair basket orders.
│       │   ├── cross_pair_pnl_calculator.py                          # Sub-millisecond real-time cross-pair profit/loss, swap, and spread aggregator.
│       │   ├── rescan_view.py                                        # Rescan lifecycle visibility.
│       │   ├── evidence_ledger_view.py                               # Evidence chain and ledger visibility.
│       │   ├── alert_view.py                                         # Alert dispatch and channel visibility.
│       │   ├── journal_view.py                                       # Journal and attribution visibility.
│       │   ├── learning_view.py                                      # Monitoring and drift proposal visibility.
│       │   └── ipc_telemetry_stream.py                               # Shared-memory and socket stream feeding PySide6 GUI directly.
│       │
│       ├── application/                                              # Application Façade & Use Cases
│       │   ├── __init__.py                                           # Application package boundary.
│       │   ├── service_facade.py                                     # Controlled application entry point for queries and use cases.
│       │   ├── query_gateway.py                                      # Read-model query boundary.
│       │   ├── command_gateway.py                                    # Authorized command boundary.
│       │   ├── read_models/                                          # Read models for queries
│       │   │   ├── __init__.py                                       # Read model package boundary.
│       │   │   ├── system_read_model.py                              # Boot/security/configuration/system health read model.
│       │   │   ├── market_read_model.py                              # Market reconstruction read model.
│       │   │   ├── scenario_read_model.py                            # Universal scenario read model.
│       │   │   ├── fusion_read_model.py                              # Fusion state read model.
│       │   │   ├── engine_read_model.py                              # Engine state read model.
│       │   │   ├── signal_read_model.py                              # Signal lifecycle read model.
│       │   │   ├── execution_read_model.py                           # Risk/sizing/portfolio/broker/order/position read model.
│       │   │   ├── multi_trade_read_model.py                         # Single-pair and cross-pair live trade and aggregate PnL read model.
│       │   │   └── evidence_read_model.py                            # Evidence ledger read model.
│       │   └── use_cases/                                            # System Use Cases
│       │       ├── __init__.py                                       # Use case package boundary.
│       │       ├── boot_system.py                                    # Starts David OS boot sequence.
│       │       ├── authenticate_operator.py                          # Authenticates master admin or user.
│       │       ├── query_architecture_state.py                       # Queries global architecture health.
│       │       ├── query_market_state.py                             # Queries market reconstruction and awareness.
│       │       ├── query_signal_state.py                             # Queries technical signal lifecycle.
│       │       ├── execute_single_trade.py                           # Dispatches validated single trade open/close command.
│       │       ├── execute_single_pair_multi_trade.py                # Dispatches batch orders on a single currency pair.
│       │       ├── execute_cross_pair_basket_trade.py                # Dispatches cross-pair simultaneous multi-currency basket trade.
│       │       ├── close_batch_trades.py                             # Dispatches batch close (all longs, all shorts, all in profit/loss).
│       │       ├── submit_control_panel_change.py                    # Submits authorized configuration mutation.
│       │       ├── export_audit.py                                   # Exports audit/evidence/journal records.
│       │       └── initiate_rescan.py                                # Starts a new technical lifecycle after exit/failure.
│       │
│       ├── parameter/                                                # L2 — Universal Parameter Lifecycle Domain (Zero Silent Drops)
│       │   ├── __init__.py                                           # Parameter package boundary.
│       │   ├── parameter_definition.py                               # Parameter identity, meaning, unit, domain classification.
│       │   ├── parameter_registry.py                                 # Registry of all technical/intelligence parameters.
│       │   ├── parameter_schema.py                                   # Typed parameter representation.
│       │   ├── parameter_source.py                                   # Source provenance for every parameter.
│       │   ├── parameter_context.py                                  # Symbol/timeframe/session context binding.
│       │   ├── parameter_calculation.py                              # Calculation method/period/dependency metadata.
│       │   ├── parameter_normalization.py                            # Common normalized representation.
│       │   ├── parameter_state.py                                    # VALID / INVALID / MISSING / STALE / CONFLICTED state.
│       │   ├── parameter_lifecycle_manager.py                        # INGEST → VALIDATE → DERIVE → CONTEXTUALIZE → FUSE → CONTRIBUTE → DECIDE → RECORD.
│       │   ├── parameter_lineage.py                                  # Full dependency lineage.
│       │   ├── parameter_dependency_graph.py                         # Parameter dependency graph.
│       │   ├── parameter_contribution.py                             # Contribution to technical decision.
│       │   ├── parameter_reconciliation.py                           # Cross-source/timeframe reconciliation.
│       │   ├── parameter_completeness.py                             # Detects omitted decision parameters.
│       │   ├── equal_contribution_policy.py                          # Enforces no primary/secondary parameter hierarchy.
│       │   ├── decision_impact_tracker.py                            # Tracks how each parameter impacted each decision.
│       │   ├── coverage_tracker.py                                   # Tracks parameter coverage across lifecycle stages.
│       │   ├── untracked_parameter_guard.py                          # Raises UntrackedParameterError for bypass attempts.
│       │   ├── no_silent_drop_auditor.py                             # Audits lifecycle transitions to prevent silent drops.
│       │   ├── parameter_hash.py                                     # Deterministic SHA-256 Merkle root parameter identity hashing.
│       │   └── parameter_audit.py                                    # Parameter lifecycle audit trail.
│       │
│       ├── evidence_ledger/                                          # L2 — Immutable Evidence System & Cryptographic Hash Chaining
│       │   ├── __init__.py                                           # Evidence ledger package boundary.
│       │   ├── ledger.py                                             # Append-only evidence ledger.
│       │   ├── ledger_entry.py                                       # Evidence record.
│       │   ├── evidence_identity.py                                  # Evidence IDs.
│       │   ├── evidence_lineage.py                                   # Evidence parent/child lineage.
│       │   ├── evidence_contribution.py                              # Parameter contribution records.
│       │   ├── evidence_rejection.py                                 # Rejected technical conditions.
│       │   ├── evidence_conflict.py                                  # Conflicting evidence records.
│       │   ├── evidence_missing.py                                   # Missing/unavailable evidence records.
│       │   ├── decision_evidence.py                                  # Evidence attached to final decision.
│       │   ├── parameter_accountability.py                           # Holds every parameter accountable as an evidence unit.
│       │   ├── parameter_decision_impact.py                          # Records decision impact per parameter.
│       │   ├── evidence_matrix.py                                    # Cross-domain evidence matrix.
│       │   ├── evidence_density.py                                   # Measures evidence density for precision grading.
│       │   ├── evidence_provenance_tracker.py                        # Tracks evidence origin and transformations.
│       │   ├── silent_drop_detector.py                               # Detects missing lifecycle transitions.
│       │   ├── hash_chain.py                                         # Tamper-evident evidence chain (SHA3/BLAKE3/SHA-256).
│       │   ├── ledger_validator.py                                   # Evidence continuity validation.
│       │   ├── ledger_snapshot.py                                    # Immutable evidence snapshot.
│       │   └── ledger_export.py                                      # Evidence export for audit/replay.
│       │
│       ├── data/                                                     # L2 — Market Data Domain (Ingestion, Integrity, Replay)
│       │   ├── __init__.py                                           # Data package boundary.
│       │   ├── ingestion/                                            # Ingestion routers
│       │   │   ├── __init__.py                                       # Ingestion package boundary.
│       │   │   ├── tick_ingestion.py                                 # Tick events.
│       │   │   ├── ohlcv_ingestion.py                                # OHLCV streams.
│       │   │   ├── orderbook_ingestion.py                            # Order-book L2 DOM queue and level data.
│       │   │   ├── trade_flow_ingestion.py                           # Trade-flow events and tape prints.
│       │   │   ├── volume_ingestion.py                               # Volume data.
│       │   │   ├── news_ingestion.py                                 # News/event data.
│       │   │   ├── economic_release_ingestion.py                     # Economic calendar release data.
│       │   │   ├── sentiment_ingestion.py                            # Sentiment feed inputs.
│       │   │   ├── chat_ingestion.py                                 # Market chat/social message ingestion.
│       │   │   ├── historical_ingestion.py                           # Historical datasets.
│       │   │   ├── synthetic_ingestion.py                            # Synthetic deterministic datasets.
│       │   │   └── feed_router.py                                    # Canonical feed routing.
│       │   ├── integrity/                                            # Data gap detection and validation
│       │   │   ├── __init__.py                                       # Integrity package boundary.
│       │   │   ├── schema_validator.py                               # Schema checks.
│       │   │   ├── timestamp_validator.py                            # Timestamp checks.
│       │   │   ├── sequence_validator.py                             # Event-order checks.
│       │   │   ├── duplicate_detector.py                             # Duplicate-event detection.
│       │   │   ├── gap_detector.py                                   # Missing-event detection.
│       │   │   ├── stale_feed_detector.py                            # Feed freshness checks.
│       │   │   ├── outlier_detector.py                               # Data anomaly detection.
│       │   │   ├── cross_source_reconciliation.py                    # Cross-source comparison.
│       │   │   ├── ohlcv_builder.py                                  # Canonical candle construction.
│       │   │   └── timeframe_resampler.py                            # Canonical timeframe construction.
│       │   ├── market_reconstruction/                                # Chart morphology reconstruction
│       │   │   ├── __init__.py                                       # Market reconstruction package boundary.
│       │   │   ├── market_reconstruction_engine.py                   # Continuous market reconstruction.
│       │   │   ├── historical_context.py                             # Historical technical context.
│       │   │   ├── current_state.py                                  # Current market state.
│       │   │   ├── previous_state.py                                 # Previous state.
│       │   │   ├── forming_state.py                                  # Forming state.
│       │   │   ├── state_transition.py                               # State transition detection.
│       │   │   ├── morphology_reconstruction.py                      # Multi-timeframe morphology.
│       │   │   └── reconstruction_fingerprint.py                     # Deterministic state fingerprint.
│       │   └── replay/                                               # Replay engine for backtesting
│       │       ├── __init__.py                                       # Replay package boundary.
│       │       ├── replay_engine.py                                  # Deterministic market replay engine.
│       │       ├── replay_session.py                                 # Replay session manager.
│       │       ├── deterministic_replay.py                           # Ensures replay determinism and auditability.
│       │       └── replay_audit.py                                   # Replay session audit log.
│       │
│       ├── awareness/                                                # L3 — Market Awareness Domain
│       │   ├── __init__.py                                           # Awareness package boundary.
│       │   ├── awareness_engine.py                                   # Continuous awareness supervisor.
│       │   ├── price_state.py                                        # Current price state.
│       │   ├── volatility_state.py                                   # Current volatility state.
│       │   ├── liquidity_state.py                                    # Current liquidity state.
│       │   ├── momentum_state.py                                     # Current momentum state.
│       │   ├── regime_state.py                                       # Current regime awareness.
│       │   ├── session_state.py                                      # Session structure awareness.
│       │   ├── news_state.py                                         # News event awareness.
│       │   ├── sentiment_state.py                                    # Sentiment awareness.
│       │   ├── chat_state.py                                         # Market chat burst awareness.
│       │   ├── htf_watch_state.py                                    # Persistent HTF watch state.
│       │   └── awareness_snapshot.py                                 # Immutable awareness snapshot.
│       │
│       ├── intelligence/                                             # L3 — Canonical Technical Intelligence & Perception Domain (16 Families)
│       │   ├── __init__.py                                           # Intelligence package boundary.
│       │   ├── intelligence_engine.py                                # Executes the complete technical-intelligence graph.
│       │   ├── evidence_packet_builder.py                            # Builds intelligence evidence packets for fusion.
│       │   ├── intelligence_evidence_matrix.py                       # Maps intelligence observations into evidence matrix.
│       │   ├── parameter_contribution_ledger.py                      # Records each intelligence parameter contribution.
│       │   ├── technical_conflict_detector.py                        # Detects conflicts across intelligence families.
│       │   ├── price_action/                                         # Price action detectors
│       │   │   ├── __init__.py                                       # Price action package boundary.
│       │   │   ├── impulse.py                                        # Impulse detection.
│       │   │   ├── displacement.py                                   # Displacement detection.
│       │   │   ├── rejection.py                                      # Rejection detection.
│       │   │   ├── pullback.py                                       # Pullback detection.
│       │   │   ├── breakout.py                                       # Breakout detection.
│       │   │   ├── breakout_failure.py                               # Breakout failure detection.
│       │   │   ├── compression.py                                    # Compression detection.
│       │   │   └── exhaustion.py                                     # Exhaustion detection.
│       │   ├── candles/                                              # Candle morphology analysis
│       │   │   ├── __init__.py                                       # Candle morphology package boundary.
│       │   │   ├── candle_state.py                                   # Canonical candle state.
│       │   │   ├── body_ratio.py                                     # Body ratio computation.
│       │   │   ├── upper_wick_ratio.py                               # Upper wick ratio computation.
│       │   │   ├── lower_wick_ratio.py                               # Lower wick ratio computation.
│       │   │   ├── range_ratio.py                                    # Range ratio computation.
│       │   │   ├── single_patterns.py                                # Single-candle patterns.
│       │   │   ├── dual_patterns.py                                  # Dual-candle patterns.
│       │   │   ├── multi_patterns.py                                 # Multi-candle patterns.
│       │   │   ├── sequence_patterns.py                              # Candle sequence patterns.
│       │   │   ├── displacement_cdt.py                               # 1CDT / 2CDT / 3CDT displacement confirmation engine.
│       │   │   ├── session_candle.py                                 # Session candle morphology.
│       │   │   ├── weekly_candle.py                                  # Weekly candle morphology.
│       │   │   └── monthly_candle.py                                 # Monthly candle morphology.
│       │   ├── structure/                                            # Structure analysis (BOS, CHoCH, MSS, Breaker Blocks)
│       │   │   ├── __init__.py                                       # Structure package boundary.
│       │   │   ├── swing_points.py                                   # Swing high/low detection.
│       │   │   ├── internal_structure.py                             # Internal structure detection.
│       │   │   ├── external_structure.py                             # External structure detection.
│       │   │   ├── bos.py                                            # Break of Structure.
│       │   │   ├── choch.py                                          # Change of Character.
│       │   │   ├── mss.py                                            # Market Structure Shift.
│       │   │   ├── msb.py                                            # Market Structure Break.
│       │   │   ├── cisd.py                                           # Change in State of Delivery.
│       │   │   ├── smt_divergence.py                                 # SMT divergence cross-asset validator.
│       │   │   ├── structure_sequence.py                             # Structural sequence tracking.
│       │   │   ├── trend_structure.py                                # Trend structure tracking.
│       │   │   └── structure_failure.py                              # Structural failure detection.
│       │   ├── liquidity/                                            # Liquidity pools and sweeps
│       │   │   ├── __init__.py                                       # Liquidity package boundary.
│       │   │   ├── eql.py                                            # Equal lows detection.
│       │   │   ├── eqh.py                                            # Equal highs detection.
│       │   │   ├── erl.py                                            # External range liquidity detection.
│       │   │   ├── irl.py                                            # Internal range liquidity detection.
│       │   │   ├── stop_clusters.py                                  # Stop cluster inference.
│       │   │   ├── liquidity_pools.py                                # Liquidity pool mapping.
│       │   │   ├── sweep_detector.py                                 # Liquidity sweep detection.
│       │   │   ├── stop_hunt.py                                      # Stop hunt detection.
│       │   │   ├── reclaim.py                                        # Sweep reclaim detection.
│       │   │   └── delivery_cycle.py                                 # Delivery cycle detection.
│       │   ├── orderflow/                                            # Orderflow and delta analysis
│       │   │   ├── __init__.py                                       # Orderflow package boundary.
│       │   │   ├── bid_ask_imbalance.py                              # Bid/ask imbalance detection.
│       │   │   ├── trade_imbalance.py                                # Trade imbalance detection.
│       │   │   ├── delta.py                                          # Delta computation.
│       │   │   ├── cvd.py                                            # Cumulative volume delta.
│       │   │   ├── hawkes_process.py                                 # Hawkes point process burst sniper.
│       │   │   ├── microstructure_gaps.py                            # Microstructure liquidity gap detector.
│       │   │   ├── absorption.py                                     # Absorption detection.
│       │   │   └── orderflow_shift.py                                # Orderflow shift detection.
│       │   ├── volume/                                               # Volume metrics
│       │   │   ├── __init__.py                                       # Volume package boundary.
│       │   │   ├── raw_volume.py                                     # Raw volume processing.
│       │   │   ├── relative_volume.py                                # Relative volume computation.
│       │   │   ├── volume_zscore.py                                  # Volume z-score computation.
│       │   │   ├── expansion.py                                      # Volume expansion detection.
│       │   │   └── contraction.py                                    # Volume contraction detection.
│       │   ├── volatility/                                           # Volatility metrics (ATR, realized vol, GARCH, SKEW)
│       │   │   ├── __init__.py                                       # Volatility package boundary.
│       │   │   ├── atr.py                                            # Average True Range computation.
│       │   │   ├── atr_ratio.py                                      # ATR ratio computation.
│       │   │   ├── realized_volatility.py                            # Realized volatility computation.
│       │   │   ├── volatility_zscore.py                              # Volatility z-score computation.
│       │   │   ├── volatility_percentile.py                          # Volatility percentile computation.
│       │   │   ├── skew_garch.py                                     # Cboe SKEW GARCH & Volatility Risk Premium (VRP) estimator.
│       │   │   ├── term_structure.py                                 # VIX term structure & forward volatility analyzer.
│       │   │   ├── wavelet_filter.py                                 # Wavelet multiresolution noise decomposition filter.
│       │   │   ├── compression.py                                    # Volatility compression detection.
│       │   │   ├── expansion.py                                      # Volatility expansion detection.
│       │   │   └── regime.py                                         # Volatility regime classification.
│       │   ├── momentum/                                             # Momentum metrics and divergence
│       │   │   ├── __init__.py                                       # Momentum package boundary.
│       │   │   ├── momentum_rate.py                                  # Momentum rate computation.
│       │   │   ├── impulse_strength.py                               # Impulse strength computation.
│       │   │   ├── acceleration.py                                   # Momentum acceleration detection.
│       │   │   ├── divergence.py                                     # Momentum divergence detection.
│       │   │   └── regime.py                                         # Momentum regime classification.
│       │   ├── indicators/                                           # Technical indicators (SMA, RSI, MACD, VWAP, Anchored VWAP)
│       │   │   ├── __init__.py                                       # Indicator package boundary.
│       │   │   ├── indicator_engine.py                               # One indicator engine; no duplicate indicator folders.
│       │   │   ├── moving_averages.py                                # SMA/EMA/WMA computation.
│       │   │   ├── macd.py                                           # MACD computation.
│       │   │   ├── adx.py                                            # ADX computation.
│       │   │   ├── parabolic_sar.py                                  # Parabolic SAR computation.
│       │   │   ├── ichimoku.py                                       # Ichimoku computation.
│       │   │   ├── aroon.py                                          # Aroon computation.
│       │   │   ├── rsi.py                                            # RSI computation.
│       │   │   ├── stochastic.py                                     # Stochastic computation.
│       │   │   ├── cci.py                                            # CCI computation.
│       │   │   ├── williams_r.py                                     # Williams %R computation.
│       │   │   ├── roc.py                                            # Rate of Change computation.
│       │   │   ├── bollinger_bands.py                                # Bollinger Bands computation.
│       │   │   ├── keltner_channel.py                                # Keltner Channel computation.
│       │   │   ├── vwap.py                                           # VWAP computation.
│       │   │   ├── anchored_vwap.py                                  # Anchored VWAP computation.
│       │   │   ├── obv.py                                            # On-Balance Volume computation.
│       │   │   └── volume_profile.py                                 # Volume profile computation.
│       │   ├── geometry/                                             # Range, swing, and projection geometry
│       │   │   ├── __init__.py                                       # Geometry package boundary.
│       │   │   ├── range_geometry.py                                 # Range geometry measurement.
│       │   │   ├── swing_geometry.py                                 # Swing geometry measurement.
│       │   │   ├── slope_geometry.py                                 # Slope geometry measurement.
│       │   │   ├── distance.py                                       # Price distance measurement.
│       │   │   ├── symmetry.py                                       # Symmetry measurement.
│       │   │   ├── anchor_engine.py                                  # Anchor point computation.
│       │   │   ├── projection_engine.py                              # Measured-move projections.
│       │   │   └── confluence.py                                     # Geometry confluence detection.
│       │   ├── levels/                                               # Support/resistance and session levels
│       │   │   ├── __init__.py                                       # Levels package boundary.
│       │   │   ├── pdh.py                                            # Previous day high.
│       │   │   ├── pdl.py                                            # Previous day low.
│       │   │   ├── pwh.py                                            # Previous week high.
│       │   │   ├── pwl.py                                            # Previous week low.
│       │   │   ├── session_high_low.py                               # Session high/low levels.
│       │   │   ├── opening_price.py                                  # Session opening price.
│       │   │   ├── equilibrium.py                                    # Equilibrium level computation.
│       │   │   ├── premium_discount.py                               # Premium/discount level mapping.
│       │   │   ├── swing_levels.py                                   # Swing level mapping.
│       │   │   ├── support_resistance.py                             # Support/resistance mapping.
│       │   │   ├── htf_levels.py                                     # HTF projected levels.
│       │   │   └── level_cluster_engine.py                           # Level clustering engine.
│       │   ├── zones/                                                # Order blocks, FVGs, supply & demand zones
│       │   │   ├── __init__.py                                       # Zones package boundary.
│       │   │   ├── order_block.py                                    # Order block detection.
│       │   │   ├── fair_value_gap.py                                 # Fair value gap detection.
│       │   │   ├── inversion_fvg.py                                  # Inversion fair value gap detection.
│       │   │   ├── breaker_block.py                                  # Breaker block detection.
│       │   │   ├── mitigation_block.py                               # Mitigation block detection.
│       │   │   ├── supply_zone.py                                    # Supply zone detection.
│       │   │   ├── demand_zone.py                                    # Demand zone detection.
│       │   │   ├── poi.py                                            # Point of interest detection.
│       │   │   ├── zone_quality.py                                   # Zone quality scoring.
│       │   │   ├── zone_freshness.py                                 # Zone freshness tracking.
│       │   │   ├── zone_mitigation_state.py                          # Zone mitigation state tracking.
│       │   │   └── zone_interaction.py                               # Price-zone interaction detection.
│       │   ├── fibonacci/                                            # Golden zone, OTE, retracements
│       │   │   ├── __init__.py                                       # Fibonacci package boundary.
│       │   │   ├── retracement.py                                    # Fibonacci retracement.
│       │   │   ├── extension.py                                      # Fibonacci extension.
│       │   │   ├── golden_zone.py                                    # Golden zone detection.
│       │   │   ├── ote.py                                            # Optimal Trade Entry zone.
│       │   │   ├── sniper_zone.py                                    # High-precision Fibonacci sniper zone.
│       │   │   └── fib_anchor_validation.py                          # Fibonacci anchor validation.
│       │   ├── harmonics/                                            # Harmonic pattern recognition
│       │   │   ├── __init__.py                                       # Harmonics package boundary.
│       │   │   ├── abcd.py                                           # ABCD pattern detection.
│       │   │   ├── gartley.py                                        # Gartley pattern detection.
│       │   │   ├── bat.py                                            # Bat pattern detection.
│       │   │   ├── butterfly.py                                      # Butterfly pattern detection.
│       │   │   ├── cypher.py                                         # Cypher pattern detection.
│       │   │   ├── crab.py                                           # Crab pattern detection.
│       │   │   ├── shark.py                                          # Shark pattern detection.
│       │   │   ├── prz_engine.py                                     # Potential Reversal Zone engine.
│       │   │   └── validation.py                                     # Harmonic validation.
│       │   ├── patterns/                                             # Chart, Wyckoff, and liquidity patterns
│       │   │   ├── __init__.py                                       # Pattern package boundary.
│       │   │   ├── chart/                                            # Classical chart patterns
│       │   │   │   ├── __init__.py                                   # Chart pattern package boundary.
│       │   │   │   ├── flag.py                                       # Flag pattern detection.
│       │   │   │   ├── pennant.py                                    # Pennant pattern detection.
│       │   │   │   ├── triangle.py                                   # Triangle pattern detection.
│       │   │   │   ├── rectangle.py                                  # Rectangle pattern detection.
│       │   │   │   ├── broadening.py                                 # Broadening pattern detection.
│       │   │   │   ├── cup_handle.py                                 # Cup-and-handle pattern detection.
│       │   │   │   ├── diamond.py                                    # Diamond pattern detection.
│       │   │   │   ├── quasimodo.py                                  # Quasimodo (QML) pattern detection.
│       │   │   │   ├── head_shoulders.py                             # Head-and-shoulders pattern detection.
│       │   │   │   ├── double_top.py                                 # Double top detection.
│       │   │   │   ├── double_bottom.py                              # Double bottom detection.
│       │   │   │   ├── triple_top.py                                 # Triple top detection.
│       │   │   │   └── triple_bottom.py                              # Triple bottom detection.
│       │   │   ├── wyckoff/                                          # Wyckoff schematics (Phases A–E)
│       │   │   │   ├── __init__.py                                   # Wyckoff package boundary.
│       │   │   │   ├── wyckoff_engine.py                             # Wyckoff Phases A-E accumulation/distribution scanner.
│       │   │   │   ├── accumulation.py                               # Wyckoff accumulation detection.
│       │   │   │   ├── distribution.py                               # Wyckoff distribution detection.
│       │   │   │   ├── spring.py                                     # Spring detection.
│       │   │   │   ├── upthrust.py                                   # Upthrust detection.
│       │   │   │   ├── selling_climax.py                             # Selling climax detection.
│       │   │   │   ├── automatic_rally.py                            # Automatic rally detection.
│       │   │   │   ├── sign_of_strength.py                           # Sign of strength (SOS) detection.
│       │   │   │   ├── last_point_of_support.py                      # Last point of support (LPS) detection.
│       │   │   │   ├── last_point_of_supply.py                       # Last point of supply (LPSY) detection.
│       │   │   │   ├── utad.py                                       # Upthrust After Distribution (UTAD) detection.
│       │   │   │   └── selling_climax_minor.py                       # Minor selling climax detection.
│       │   │   ├── stacey_burke/                                     # Stacey Burke 3-Day Cycle Engine
│       │   │   │   ├── __init__.py                                   # Stacey Burke cycle package boundary.
│       │   │   │   ├── three_day_cycle.py                            # 3-Day Cycle state engine (Day 1, Day 2, Day 3).
│       │   │   │   ├── first_green_day.py                            # First Green Day setup detector.
│       │   │   │   ├── first_red_day.py                              # First Red Day setup detector.
│       │   │   │   └── session_high_low_traps.py                     # Peak formation and session trap detector.
│       │   │   ├── statistical/                                      # Advanced mathematical and topological patterns
│       │   │   │   ├── __init__.py                                   # Statistical patterns package boundary.
│       │   │   │   ├── takens_phase_space.py                         # Takens Phase Space embedding manifold reconstructor.
│       │   │   │   ├── hidden_markov.py                              # Gaussian Hidden Markov Model (HMM) regime identifier.
│       │   │   │   └── topological_data_analysis.py                  # Topological Data Analysis (TDA) persistent homology scanner.
│       │   │   └── liquidity/                                        # Liquidity trap patterns
│       │   │       ├── __init__.py                                   # Liquidity pattern package boundary.
│       │   │       ├── turtle_soup.py                                # Turtle Soup Candle Range Theory (CRT) pattern detection.
│       │   │       ├── taipan_soup.py                                # Taipan Soup pattern detection.
│       │   │       ├── stop_hunt.py                                  # Stop hunt pattern detection.
│       │   │       ├── sweep_reclaim.py                              # Sweep reclaim pattern detection.
│       │   │       └── failed_breakout_reclaim.py                    # Failed breakout reclaim pattern detection.
│       │   ├── sentiment/                                            # Sentiment and narrative momentum
│       │   │   ├── __init__.py                                       # Sentiment intelligence package boundary.
│       │   │   ├── chat_sentiment.py                                 # Market chat sentiment scoring.
│       │   │   ├── news_sentiment.py                                 # News sentiment scoring.
│       │   │   ├── narrative_momentum.py                             # Narrative momentum detection.
│       │   │   └── sentiment_divergence.py                           # Sentiment-price divergence detection.
│       │   └── event_shock/                                          # News and economic event shock impact
│       │       ├── __init__.py                                       # Event shock package boundary.
│       │       ├── news_event_impact.py                              # News event impact measurement.
│       │       ├── economic_release_impact.py                        # Economic release impact measurement.
│       │       └── chat_burst_impact.py                              # Chat burst impact measurement.
│       │
│       ├── regime/                                                   # L3 — Regime Classifier Domain
│       │   ├── __init__.py                                           # Regime package boundary.
│       │   ├── regime_classifier.py                                  # Master regime classifier.
│       │   ├── trend_regime.py                                       # Trend regime detection.
│       │   ├── range_regime.py                                       # Range regime detection.
│       │   ├── compression_regime.py                                 # Compression regime detection.
│       │   ├── expansion_regime.py                                   # Expansion regime detection.
│       │   ├── transition_regime.py                                  # Transition regime detection.
│       │   ├── mean_reversion_regime.py                              # Mean-reversion regime detection.
│       │   ├── volatility_regime.py                                  # Volatility regime detection.
│       │   └── liquidity_regime.py                                   # Liquidity regime detection.
│       │
│       ├── scenario_pool/                                            # L4 — Universal Scenario Pool / King Classifier (31 Scenarios, 13 Families)
│       │   ├── __init__.py                                           # Scenario Pool package boundary.
│       │   ├── scenario_pool_engine.py                               # Single scenario classifier (Scenario is King).
│       │   ├── scenario_identity.py                                  # Scenario identity.
│       │   ├── scenario_state.py                                     # Scenario state (S1 through S31 representation).
│       │   ├── scenario_phase.py                                     # Scenario phase.
│       │   ├── previous_scenario.py                                  # Previous classification.
│       │   ├── forming_scenario.py                                   # Forming classification.
│       │   ├── scenario_transition.py                                # State transitions.
│       │   ├── scenario_evidence.py                                  # Scenario evidence.
│       │   ├── scenario_contradiction.py                             # Scenario contradictions.
│       │   ├── scenario_detector_parameters.py                       # Detector thresholds and sensitivity parameters.
│       │   ├── scenario_routing_matrix.py                            # Scenario-to-engine eligibility mapping.
│       │   ├── families/                                             # Universal scenario families (S1–S31)
│       │   │   ├── __init__.py                                       # Scenario family package boundary.
│       │   │   ├── trend_continuation.py                             # Trend continuation scenario family.
│       │   │   ├── trend_failure.py                                  # Trend failure scenario family.
│       │   │   ├── pullback.py                                       # Pullback scenario family.
│       │   │   ├── momentum.py                                       # Momentum scenario family.
│       │   │   ├── breakout.py                                       # Breakout scenario family.
│       │   │   ├── breakout_continuation.py                          # Breakout continuation scenario family.
│       │   │   ├── breakout_failure.py                               # Breakout failure scenario family.
│       │   │   ├── fakeout.py                                        # Fakeout scenario family.
│       │   │   ├── liquidity_sweep.py                                # Liquidity sweep scenario family.
│       │   │   ├── reversal.py                                       # Reversal scenario family.
│       │   │   ├── expansion.py                                      # Expansion scenario family.
│       │   │   ├── compression.py                                    # Compression scenario family.
│       │   │   ├── consolidation.py                                  # Consolidation scenario family.
│       │   │   ├── mean_reversion.py                                 # Mean reversion scenario family.
│       │   │   ├── accumulation.py                                   # Accumulation scenario family.
│       │   │   ├── distribution.py                                   # Distribution scenario family.
│       │   │   ├── markup.py                                         # Markup scenario family.
│       │   │   ├── markdown.py                                       # Markdown scenario family.
│       │   │   ├── exhaustion.py                                     # Exhaustion scenario family.
│       │   │   ├── breakout_pullback_continuation.py                 # Breakout-pullback-continuation scenario family.
│       │   │   ├── breakout_failure_reversal.py                      # Breakout-failure-reversal scenario family.
│       │   │   ├── quasimodo.py                                      # Quasimodo scenario family.
│       │   │   ├── diamond.py                                        # Diamond scenario family.
│       │   │   ├── parabolic_expansion.py                            # Parabolic expansion scenario family.
│       │   │   ├── turtle_soup.py                                    # Turtle Soup scenario family.
│       │   │   ├── taipan_soup.py                                    # Taipan Soup scenario family.
│       │   │   ├── multi_timeframe_alignment.py                      # Multi-timeframe alignment scenario family.
│       │   │   └── news_repricing.py                                 # News/economic repricing scenario family.
│       │   └── terminal/                                             # Terminal non-trading states
│       │       ├── __init__.py                                       # Terminal scenario package boundary.
│       │       ├── unknown.py                                        # UNKNOWN terminal state (forces WAIT).
│       │       ├── conflicted.py                                     # CONFLICTED terminal state (forces WAIT).
│       │       └── novel.py                                          # NOVEL terminal state (forces WAIT).
│       │
│       ├── hypothesis/                                               # L4 — Technical Thesis / Hypothesis Domain
│       │   ├── __init__.py                                           # Hypothesis package boundary.
│       │   ├── hypothesis_engine.py                                  # Builds and maintains technical thesis.
│       │   ├── bullish.py                                            # Bullish thesis construction.
│       │   ├── bearish.py                                            # Bearish thesis construction.
│       │   ├── neutral.py                                            # Neutral thesis construction.
│       │   ├── continuation.py                                       # Continuation thesis construction.
│       │   ├── reversal.py                                           # Reversal thesis construction.
│       │   ├── breakout.py                                           # Breakout thesis construction.
│       │   ├── pullback.py                                           # Pullback thesis construction.
│       │   ├── failure.py                                            # Failure thesis construction.
│       │   ├── thesis_state.py                                       # Thesis state tracking (ARMED, TRIGGERED, HOLD, CHANGE, FAILURE).
│       │   ├── thesis_invalidation.py                                # Thesis invalidation logic.
│       │   └── thesis_revalidation.py                                # Thesis revalidation logic.
│       │
│       ├── grammar/                                                  # L4 — Scenario Formation Grammar (Causal Sequences)
│       │   ├── __init__.py                                           # Grammar package boundary.
│       │   ├── grammar_engine.py                                     # Executes formation grammar.
│       │   ├── causal_sequence.py                                    # Causal sequence representation.
│       │   ├── precondition.py                                       # Precondition validation.
│       │   ├── formation_step.py                                     # Formation step validation.
│       │   ├── confirmation_step.py                                  # Confirmation step validation (1CDT, 2CDT, 3CDT, Multi-CDT).
│       │   ├── invalidation_step.py                                  # Invalidation step validation.
│       │   ├── sequence_integrity.py                                 # Sequence integrity validation.
│       │   ├── grammar_registry.py                                   # Registry of formation grammars.
│       │   └── engine_grammar_mapper.py                              # Maps grammars to eligible engines.
│       │
│       ├── fusion/                                                   # L5 — 9-Layer Central Bidirectional Fusion Brain (Monthly down to M1)
│       │   ├── __init__.py                                           # Fusion package boundary.
│       │   ├── fusion_engine.py                                      # Master HTF ↔ MTF ↔ LTF coordinator.
│       │   ├── nine_layer_fusion_brain.py                            # 9-Layer coordination plane (MN1, W1, D1, H8, H4, H1, M30, M15, M5 to M1).
│       │   ├── bidirectional_coordinator.py                          # Coordinates bidirectional flow between HTF, MTF, and LTF evidence.
│       │   ├── fusion_contract.py                                    # Defines FusionDecision, FusionRequest, EvidenceBundle.
│       │   ├── timeframe_registry.py                                 # Registers all timeframes and maintains HTF/MTF/LTF relationships.
│       │   ├── htf_state.py                                          # HTF state.
│       │   ├── mtf_state.py                                          # MTF state.
│       │   ├── ltf_state.py                                          # LTF state.
│       │   ├── fusion_snapshot.py                                    # Immutable fused state.
│       │   ├── cross_timeframe_registry.py                           # Parameter/timeframe mapping.
│       │   ├── parameter_contribution_map.py                         # Maps parameter families into fusion contribution ledger.
│       │   ├── parameter_convergence.py                              # Parameter convergence measurement.
│       │   ├── scenario_convergence.py                               # Scenario convergence measurement.
│       │   ├── evidence_convergence.py                               # Evidence convergence measurement.
│       │   ├── conflict_resolver.py                                  # Resolves cross-timeframe conflicts.
│       │   ├── trigger_alignment.py                                  # Aligns fusion state with engine trigger requirements.
│       │   ├── top_down/                                             # Top-down projections
│       │   │   ├── __init__.py                                       # Top-down package boundary.
│       │   │   ├── htf_to_mtf.py                                     # HTF → MTF context projection.
│       │   │   ├── mtf_to_ltf.py                                     # MTF → LTF context projection.
│       │   │   └── htf_to_ltf.py                                     # Direct HTF → LTF terrain/POI mapping.
│       │   ├── ground_up/                                            # Ground-up feedback
│       │   │   ├── __init__.py                                       # Ground-up package boundary.
│       │   │   ├── ltf_to_mtf.py                                     # LTF → MTF feedback.
│       │   │   ├── mtf_to_htf.py                                     # MTF → HTF pressure.
│       │   │   └── ltf_to_htf.py                                     # LTF → HTF emerging-state feedback.
│       │   ├── coordination/                                         # Coordination logic
│       │   │   ├── __init__.py                                       # Coordination package boundary.
│       │   │   ├── top_down_coordinator.py                           # Coordinates top-down constraints.
│       │   │   ├── ground_up_coordinator.py                          # Coordinates ground-up feedback.
│       │   │   ├── bidirectional_consistency.py                      # Enforces bidirectional consistency.
│       │   │   ├── timeframe_role_resolution.py                      # Resolves timeframe role conflicts.
│       │   │   ├── parameter_alignment.py                            # Aligns parameters across timeframes.
│       │   │   ├── candle_morphology_watch.py                        # Watches candle morphology across timeframes.
│       │   │   └── fusion_conflict.py                                # Records fusion conflicts.
│       │   └── convergence/                                          # Convergence calculations
│       │       ├── __init__.py                                       # Convergence package boundary.
│       │       ├── structural_convergence.py                         # Structural convergence measurement.
│       │       ├── liquidity_convergence.py                          # Liquidity convergence measurement.
│       │       ├── momentum_convergence.py                           # Momentum convergence measurement.
│       │       ├── volatility_convergence.py                         # Volatility convergence measurement.
│       │       ├── indicator_convergence.py                          # Indicator convergence measurement.
│       │       ├── level_convergence.py                              # Level convergence measurement.
│       │       └── zone_convergence.py                               # Zone convergence measurement.
│       │
│       ├── validation/                                               # L6 — Technical Validation Domain
│       │   ├── __init__.py                                           # Validation package boundary.
│       │   ├── validation_engine.py                                  # Master technical validation.
│       │   ├── parameter_validation.py                               # Full parameter validation.
│       │   ├── indicator_validation.py                               # Indicator validation.
│       │   ├── geometry_validation.py                                # Geometry validation.
│       │   ├── level_validation.py                                   # Level validation.
│       │   ├── zone_validation.py                                    # Zone validation.
│       │   ├── pattern_validation.py                                 # Formation validation.
│       │   ├── liquidity_validation.py                               # Liquidity validation.
│       │   ├── volatility_validation.py                              # Volatility validation.
│       │   ├── momentum_validation.py                                # Momentum validation.
│       │   ├── sentiment_validation.py                               # Sentiment/chat validation.
│       │   ├── event_validation.py                                   # News/economic event validation.
│       │   ├── three_core/                                           # Three-Core gate (Price Action + Candlestick + Indicators)
│       │   │   ├── __init__.py                                       # Three-core package boundary.
│       │   │   ├── price_action_validation.py                        # Price Action requirement (40% weight).
│       │   │   ├── candlestick_validation.py                         # Candle morphology/CDT requirement (35% weight).
│       │   │   ├── indicator_validation.py                           # Indicator confluence requirement (25% weight).
│       │   │   └── three_core_gate.py                                # PA + Candle + Indicator confluence gatekeeper.
│       │   └── contradiction/                                        # Contradiction detection
│       │       ├── __init__.py                                       # Contradiction package boundary.
│       │       ├── contradiction_engine.py                           # Detects contradictions across evidence.
│       │       ├── hard_conflict.py                                  # Hard conflict classification.
│       │       ├── soft_conflict.py                                  # Soft conflict classification.
│       │       └── conflict_resolution.py                            # Conflict resolution policy.
│       │
│       ├── routing/                                                  # L7 — Technical Engine Router & Setup Method Resolver
│       │   ├── __init__.py                                           # Routing package boundary.
│       │   ├── router.py                                             # Single engine-selection authority (Routes to Engines A, B, C, D or NO_ROUTE).
│       │   ├── strategy_vault_router.py                              # 50+ Strategy Vault routing tickets across Engines A, B, C, and D.
│       │   ├── routing_context.py                                    # Routing context assembly.
│       │   ├── routing_eligibility.py                                # Engine eligibility rules.
│       │   ├── engine_eligibility_matrix.py                          # Scenario/fusion/timeframe-to-engine eligibility matrix.
│       │   ├── setup_method_resolver.py                              # Determines which setup/method is eligible for the current state.
│       │   ├── routing_score.py                                      # Routing score computation.
│       │   ├── route_selection.py                                    # Final route selection.
│       │   ├── route_explanation.py                                  # Route explanation evidence.
│       │   ├── routing_conflict.py                                   # Routing conflict handling.
│       │   ├── timeframe_requirement.py                              # Timeframe requirement enforcement.
│       │   └── no_route_abstention.py                                # NO_ROUTE abstention handling.
│       │
│       ├── strategies/                                               # L7 — 50+ Master Strategy Vault Implementations (8 Strategy Families)
│       │   ├── __init__.py                                           # Strategies package boundary.
│       │   ├── base_strategy.py                                      # Base contract for all institutional strategies.
│       │   ├── strategy_registry.py                                  # Registry of all 52 active strategies with execution profiles.
│       │   │
│       │   ├── orderflow_microstructure/                             # Family 1: Orderflow & Microstructure Strategies (Engine A)
│       │   │   ├── __init__.py                                       # Package boundary.
│       │   │   ├── s01_hawkes_burst_sniper.py                        # S01: Hawkes Process orderflow burst & clustering entry.
│       │   │   ├── s02_cvd_absorption_reversal.py                    # S02: CVD divergence & limit order absorption scalp.
│       │   │   ├── s03_bid_ask_vacuum_sweep.py                       # S03: Bid-Ask depth imbalance liquidity vacuum sweep.
│       │   │   └── s04_microstructure_gap_fill.py                    # S04: Sub-millisecond microstructure liquidity gap rebalance.
│       │   │
│       │   ├── smc_ict_liquidity/                                    # Family 2: Smart Money Concepts & ICT Strategies (Engines A & B)
│       │   │   ├── __init__.py                                       # Package boundary.
│       │   │   ├── s05_turtle_soup_crt.py                            # S05: Turtle Soup Candle Range Theory sweep & reclaim.
│       │   │   ├── s06_judas_swing_london_open.py                    # S06: London Open 15-minute Judas Swing fakeout hunt.
│       │   │   ├── s07_fvg_inversion_retest.py                       # S07: Fair Value Gap inversion and mitigation retest.
│       │   │   ├── s08_cisd_order_block_tap.py                       # S08: Change in State of Delivery (CISD) Order Block tap.
│       │   │   ├── s09_breaker_block_shift.py                        # S09: Failed swing breaker block displacement & retest.
│       │   │   ├── s10_smt_divergence_cross.py                       # S10: SMT cross-asset divergence (DXY vs EURUSD / ES vs NQ).
│       │   │   └── s11_taipan_soup_wick_reversal.py                  # S11: Extreme wick liquidity raid and rapid candle reclaim.
│       │   │
│       │   ├── session_cycles/                                       # Family 3: Session Epochs & Multi-Day Cycle Strategies (Engine B)
│       │   │   ├── __init__.py                                       # Package boundary.
│       │   │   ├── s12_stacey_burke_three_day_cycle.py               # S12: Stacey Burke 3-Day Cycle Day 1/2/3 peak formation trap.
│       │   │   ├── s13_first_green_red_day_momentum.py              # S13: First Green Day / First Red Day trend explosion.
│       │   │   ├── s14_ten_am_club_reversal.py                       # S14: New York 10:00 AM Club liquidity reversal / continuation.
│       │   │   ├── s15_asian_range_raid_expansion.py                 # S15: Asian session range high/low liquidity raid & NY expansion.
│       │   │   └── s16_opening_range_breakout_orb.py                 # S16: Tactical 15-minute Opening Range Breakout (ORB-15).
│       │   │
│       │   ├── structural_swing/                                     # Family 4: Major Market Structure & Swing Strategies (Engine C)
│       │   │   ├── __init__.py                                       # Package boundary.
│       │   │   ├── s17_htf_choch_bos_pullback.py                     # S17: Major HTF CHoCH / BOS 2CDT/3CDT displacement retest.
│       │   │   ├── s18_optimal_trade_entry_ote.py                    # S18: Golden Zone / OTE 61.8%–78.6% Fibonacci retracement.
│       │   │   ├── s19_quasimodo_level_failure.py                    # S19: Classical Quasimodo (QML) structural shift & retest.
│       │   │   ├── s20_diamond_pattern_breakout.py                   # S20: Diamond top/bottom compression and measured move.
│       │   │   ├── s21_broadening_formation_expansion.py             # S21: Expanding broadening wedge swing reversal.
│       │   │   └── s22_head_shoulders_neckline_test.py               # S22: Multi-timeframe Head & Shoulders neckline retest.
│       │   │
│       │   ├── wyckoff_volume/                                       # Family 5: Wyckoff Schematics & Volume Profiling (Engines B & C)
│       │   │   ├── __init__.py                                       # Package boundary.
│       │   │   ├── s23_wyckoff_phase_c_spring.py                     # S23: Wyckoff Accumulation Phase C Spring sweep & reclaim.
│       │   │   ├── s24_wyckoff_phase_c_utad.py                       # S24: Wyckoff Distribution Phase C Upthrust After Distribution.
│       │   │   ├── s25_wyckoff_phase_d_lps.py                        # S25: Wyckoff Last Point of Support (LPS) markup entry.
│       │   │   ├── s26_wyckoff_phase_d_lpsy.py                       # S26: Wyckoff Last Point of Supply (LPSY) markdown entry.
│       │   │   ├── s27_anchored_vwap_volume_shelf.py                 # S27: Anchored VWAP institutional volume shelf defense.
│       │   │   └── s28_high_volume_node_rejection.py                 # S28: Point of Control (POC) / HVN value area rejection.
│       │   │
│       │   ├── harmonics_geometry/                                   # Family 6: Harmonic & Price Geometry Strategies (Engine C)
│       │   │   ├── __init__.py                                       # Package boundary.
│       │   │   ├── s29_harmonic_gartley_prz.py                       # S29: Harmonic Gartley 0.786 retracement PRZ reversal.
│       │   │   ├── s30_harmonic_bat_prz.py                           # S30: Harmonic Bat 0.886 deep retracement PRZ entry.
│       │   │   ├── s31_harmonic_butterfly_expansion.py               # S31: Harmonic Butterfly 1.272 extension pivot reversal.
│       │   │   ├── s32_harmonic_crab_deep_extension.py               # S32: Harmonic Crab 1.618 extreme extension reversal.
│       │   │   ├── s33_harmonic_cypher_reversal.py                   # S33: Harmonic Cypher 0.786 pattern completion sniper.
│       │   │   └── s34_measured_move_symmetry_ab_cd.py               # S34: Equal-leg AB=CD symmetry price projection confluence.
│       │   │
│       │   ├── volatility_momentum/                                  # Family 7: Volatility Regimes & Momentum Strategies (Engines A & B)
│       │   │   ├── __init__.py                                       # Package boundary.
│       │   │   ├── s35_bollinger_keltner_squeeze.py                  # S35: Volatility compression squeeze & directional expansion.
│       │   │   ├── s36_parabolic_atr_expansion.py                    # S36: Parabolic ATR ratio expansion momentum runaway.
│       │   │   ├── s37_wavelet_denoised_trend.py                     # S37: Wavelet multiresolution noise-filtered trend follow.
│       │   │   ├── s38_rsi_multi_timeframe_divergence.py             # S38: Cross-timeframe RSI momentum divergence confluence.
│       │   │   ├── s39_macd_zero_lag_impulse.py                      # S39: Zero-lag MACD histogram acceleration cross.
│       │   │   └── s40_adx_directional_exhaustion.py                 # S40: ADX peak exhaustion with counter-trend mean reversion.
│       │   │
│       │   └── macro_statistical/                                    # Family 8: Macro Institutional & Quantitative Strategies (Engine D)
│       │       ├── __init__.py                                       # Package boundary.
│       │       ├── s41_takens_phase_space_attractor.py               # S41: Takens delay embedding manifold reconstruction reversal.
│       │       ├── s42_hmm_regime_transition_trend.py                # S42: Gaussian Hidden Markov Model regime transition trend.
│       │       ├── s43_tda_persistent_homology_shift.py              # S43: Topological Data Analysis persistence barcode phase shift.
│       │       ├── s44_skew_garch_vrp_reversion.py                   # S44: Cboe SKEW GARCH Volatility Risk Premium mean reversion.
│       │       ├── s45_vix_term_structure_pivot.py                   # S45: VIX forward curve contango/backwardation macro rotation.
│       │       ├── s46_central_bank_shock_repricing.py               # S46: Central Bank surprise rate decision post-announcement drive.
│       │       ├── s47_cross_currency_synthetic_arb.py               # S47: Cross-currency triangular synthetic cointegration arb.
│       │       ├── s48_commodity_fx_cointegration.py                 # S48: Commodity-currency (AUD/NZD/CAD) cointegration swing.
│       │       ├── s49_sovereign_yield_curve_trend.py                # S49: 10Y-2Y yield curve steepening/flattening FX macro trend.
│       │       ├── s50_monthly_liquidity_pool_sweep.py               # S50: Multi-month liquidity pool sweep and macro regime retest.
│       │       ├── s51_macro_trend_following_pyramid.py              # S51: Multi-quarter macro trend-following pyramid allocation.
│       │       └── s52_edge_decay_adaptive_rotation.py               # S52: Adaptive strategy rotation based on live edge decay metrics.
│       │
│       ├── engines/                                                  # L8 — Four Peer Specialized Technical Engines (Zero Engine-to-Engine Coupling)
│       │   ├── __init__.py                                           # Engine container package boundary.
│       │   ├── engine_supervisor.py                                  # Supervises four engines.
│       │   ├── engine_registry.py                                    # Engine profile registry.
│       │   ├── engine_contract.py                                    # Common engine contract implementation helpers.
│       │   ├── engine_context.py                                     # Shared immutable technical context.
│       │   ├── engine_health.py                                      # Engine health.
│       │   ├── engine_audit.py                                       # Cross-engine audit emissions.
│       │   ├── peer_dependency_guard.py                              # Strictly prevents engine-to-engine imports.
│       │   ├── quant_scalping/                                       # ENGINE A — 15M–30M Execution Horizon (Quant Scalping)
│       │   │   ├── __init__.py                                       # Quant Scalping package boundary.
│       │   │   ├── engine.py                                         # Quant Scalping engine coordinator.
│       │   │   ├── profile.py                                        # H4/H1/M30 context, M5/M10/M15 trigger profile.
│       │   │   ├── context_adapter.py                                # Adapts common EngineContext to scalping requirements.
│       │   │   ├── decision.py                                       # Engine decision construction.
│       │   │   ├── scenario_map.py                                   # Maps universal scenarios to scalping setups.
│       │   │   ├── formation_grammar.py                              # Scalping-specific formation grammar (1CDT/2CDT rapid triggers).
│       │   │   ├── entry_requirements.py                             # Unique entry requirements for Engine A.
│       │   │   ├── limit_order_requirements.py                       # Limit-order entry requirements for Engine A.
│       │   │   ├── market_trigger_requirements.py                    # Market-trigger entry requirements for Engine A.
│       │   │   ├── target_zone_requirements.py                       # Target zone requirements for Engine A.
│       │   │   ├── exit_requirements.py                              # Exit engine trigger requirements for Engine A.
│       │   │   ├── setup_selector.py                                 # Selects eligible scalping setup.
│       │   │   ├── setup_matrix.py                                   # Scenario-to-setup matrix for Engine A.
│       │   │   ├── parameter_requirements.py                         # Required parameters for Engine A.
│       │   │   ├── liquidity_requirement.py                          # Liquidity requirement for Engine A.
│       │   │   ├── microstructure_requirement.py                     # Microstructure requirement for Engine A.
│       │   │   ├── rapid_confirmation_requirement.py                 # Rapid confirmation requirement for Engine A.
│       │   │   ├── veto_rules.py                                     # Engine-specific veto rules.
│       │   │   ├── precision_input.py                                # Precision input construction.
│       │   │   ├── precision_trigger.py                              # Precision trigger qualification.
│       │   │   └── engine_trigger.py                                 # Final scalping trigger.
│       │   ├── tactical_intraday/                                    # ENGINE B — 1H–4H Execution Horizon (Tactical Intraday)
│       │   │   ├── __init__.py                                       # Tactical Intraday package boundary.
│       │   │   ├── engine.py                                         # Tactical Intraday engine coordinator.
│       │   │   ├── profile.py                                        # H4/H1 context, M15/M30 trigger profile.
│       │   │   ├── context_adapter.py                                # Adapts common EngineContext to intraday requirements.
│       │   │   ├── decision.py                                       # Engine decision construction.
│       │   │   ├── scenario_map.py                                   # Maps universal scenarios to intraday setups.
│       │   │   ├── formation_grammar.py                              # Intraday-specific formation grammar (2CDT/3CDT confirmation).
│       │   │   ├── entry_requirements.py                             # Unique entry requirements for Engine B.
│       │   │   ├── limit_order_requirements.py                       # Limit-order entry requirements for Engine B.
│       │   │   ├── market_trigger_requirements.py                    # Market-trigger entry requirements for Engine B.
│       │   │   ├── target_zone_requirements.py                       # Target zone requirements for Engine B.
│       │   │   ├── exit_requirements.py                              # Exit engine trigger requirements for Engine B.
│       │   │   ├── setup_selector.py                                 # Selects eligible intraday setup.
│       │   │   ├── setup_matrix.py                                   # Scenario-to-setup matrix for Engine B.
│       │   │   ├── parameter_requirements.py                         # Required parameters for Engine B.
│       │   │   ├── session_structure.py                              # Session structure requirement.
│       │   │   ├── opening_range.py                                  # Opening range requirement.
│       │   │   ├── breakout_detection.py                             # Breakout requirement.
│       │   │   ├── breakout_failure.py                               # Breakout failure requirement.
│       │   │   ├── pullback_detection.py                             # Pullback requirement.
│       │   │   ├── expansion_detection.py                            # Expansion requirement.
│       │   │   ├── veto_rules.py                                     # Engine-specific veto rules.
│       │   │   ├── precision_input.py                                # Precision input construction.
│       │   │   ├── precision_trigger.py                              # Precision trigger qualification.
│       │   │   └── engine_trigger.py                                 # Final tactical-intraday trigger.
│       │   ├── swing_structural/                                     # ENGINE C — 4H–8H Execution Horizon (Swing Structural)
│       │   │   ├── __init__.py                                       # Swing Structural package boundary.
│       │   │   ├── engine.py                                         # Swing Structural engine coordinator.
│       │   │   ├── profile.py                                        # D1/H4 context, H1/H4 trigger profile.
│       │   │   ├── context_adapter.py                                # Adapts common EngineContext to swing requirements.
│       │   │   ├── decision.py                                       # Engine decision construction.
│       │   │   ├── scenario_map.py                                   # Maps universal scenarios to swing setups.
│       │   │   ├── formation_grammar.py                              # Swing-specific formation grammar (3CDT/4CDT & POI taps).
│       │   │   ├── entry_requirements.py                             # Unique entry requirements for Engine C.
│       │   │   ├── limit_order_requirements.py                       # Limit-order entry requirements for Engine C.
│       │   │   ├── market_trigger_requirements.py                    # Market-trigger entry requirements for Engine C.
│       │   │   ├── target_zone_requirements.py                       # Target zone requirements for Engine C.
│       │   │   ├── exit_requirements.py                              # Exit engine trigger requirements for Engine C.
│       │   │   ├── setup_selector.py                                 # Selects eligible swing setup.
│       │   │   ├── setup_matrix.py                                   # Scenario-to-setup matrix for Engine C.
│       │   │   ├── parameter_requirements.py                         # Required parameters for Engine C.
│       │   │   ├── major_swing_leg.py                                # Major swing leg requirement.
│       │   │   ├── structural_trend.py                               # Structural trend requirement.
│       │   │   ├── structural_reversal.py                            # Structural reversal requirement.
│       │   │   ├── structural_continuation.py                        # Structural continuation requirement.
│       │   │   ├── major_poi.py                                      # Major POI requirement.
│       │   │   ├── liquidity_requirement.py                          # Liquidity requirement for Engine C.
│       │   │   ├── zone_requirement.py                               # Zone requirement for Engine C.
│       │   │   ├── veto_rules.py                                     # Engine-specific veto rules.
│       │   │   ├── precision_input.py                                # Precision input construction.
│       │   │   ├── precision_trigger.py                              # Precision trigger qualification.
│       │   │   └── engine_trigger.py                                 # Final swing trigger.
│       │   └── macro_institutional/                                  # ENGINE D — 8H–Daily Execution Horizon (Macro Institutional)
│       │       ├── __init__.py                                       # Macro Institutional package boundary.
│       │       ├── engine.py                                         # Macro Institutional engine coordinator.
│       │       ├── profile.py                                        # W1/MN1/D1 context, H4/H8 trigger profile.
│       │       ├── context_adapter.py                                # Adapts common EngineContext to macro requirements.
│       │       ├── decision.py                                       # Engine decision construction.
│       │       ├── scenario_map.py                                   # Maps universal scenarios to macro setups.
│       │       ├── formation_grammar.py                              # Macro-specific formation grammar (Multi-CDT structural expansion).
│       │       ├── entry_requirements.py                             # Unique entry requirements for Engine D.
│       │       ├── limit_order_requirements.py                       # Limit-order entry requirements for Engine D.
│       │       ├── market_trigger_requirements.py                    # Market-trigger entry requirements for Engine D.
│       │       ├── target_zone_requirements.py                       # Target zone requirements for Engine D.
│       │       ├── exit_requirements.py                              # Exit engine trigger requirements for Engine D.
│       │       ├── setup_selector.py                                 # Selects eligible macro setup.
│       │       ├── setup_matrix.py                                   # Scenario-to-setup matrix for Engine D.
│       │       ├── parameter_requirements.py                         # Required parameters for Engine D.
│       │       ├── macro_structure.py                                # Macro structure requirement.
│       │       ├── macro_swing_network.py                            # Macro swing network requirement.
│       │       ├── macro_range.py                                    # Macro range requirement.
│       │       ├── macro_premium_discount.py                         # Macro premium/discount requirement.
│       │       ├── macro_supply_demand.py                            # Macro supply/demand requirement.
│       │       ├── macro_liquidity.py                                # Macro liquidity requirement.
│       │       ├── macro_volatility.py                               # Macro volatility requirement.
│       │       ├── macro_momentum.py                                 # Macro momentum requirement.
│       │       ├── macro_pattern.py                                  # Macro pattern requirement.
│       │       ├── macro_breakout.py                                 # Macro breakout requirement.
│       │       ├── macro_failure.py                                  # Macro failure requirement.
│       │       ├── macro_reversal.py                                 # Macro reversal requirement.
│       │       ├── macro_continuation.py                             # Macro continuation requirement.
│       │       ├── macro_news_repricing.py                           # Macro news repricing requirement.
│       │       ├── veto_rules.py                                     # Engine-specific veto rules.
│       │       ├── precision_input.py                                # Precision input construction.
│       │       ├── precision_trigger.py                              # Precision trigger qualification.
│       │       └── engine_trigger.py                                 # Final macro trigger.
│       │
│       ├── precision/                                                # L9 — Precision-Grade Domain (Evaluates WHERE & Coordinate Quality)
│       │   ├── __init__.py                                           # Precision package boundary.
│       │   ├── precision_engine.py                                   # Single precision-grade orchestrator.
│       │   ├── parameter_quality.py                                  # Parameter quality scoring.
│       │   ├── technical_quality.py                                  # Technical quality scoring.
│       │   ├── scenario_quality.py                                   # Scenario quality scoring.
│       │   ├── fusion_quality.py                                     # Fusion quality scoring.
│       │   ├── structure_quality.py                                  # Structure quality scoring.
│       │   ├── liquidity_quality.py                                  # Liquidity quality scoring.
│       │   ├── volatility_quality.py                                 # Volatility quality scoring.
│       │   ├── momentum_quality.py                                   # Momentum quality scoring.
│       │   ├── indicator_quality.py                                  # Indicator quality scoring.
│       │   ├── geometry_quality.py                                   # Geometry quality scoring.
│       │   ├── level_quality.py                                      # Level quality scoring.
│       │   ├── zone_quality.py                                       # Zone quality scoring.
│       │   ├── location_quality.py                                   # Location quality scoring.
│       │   ├── target_quality.py                                     # Target quality scoring.
│       │   ├── trigger_quality.py                                    # Trigger quality scoring.
│       │   ├── contradiction_penalty.py                              # Contradiction penalty scoring.
│       │   ├── precision_trigger_resolver.py                         # Resolves precision grade into trigger readiness.
│       │   ├── grade_mapper.py                                       # Maps scores to precision grades (Tiers 1 to 4).
│       │   └── explanation.py                                        # Precision explanation evidence.
│       │
│       ├── signal/                                                   # L9 — Final Technical Signal Domain (Produces TechnicalSignalTicket)
│       │   ├── __init__.py                                           # Signal package boundary.
│       │   ├── signal_engine.py                                      # Final signal orchestrator.
│       │   ├── technical_signal_ticket.py                            # Canonical final technical signal contract.
│       │   ├── signal_identity.py                                    # Signal identity.
│       │   ├── signal_direction.py                                   # Signal direction.
│       │   ├── signal_scenario.py                                    # Signal scenario reference.
│       │   ├── signal_setup.py                                       # Signal setup reference.
│       │   ├── entry_zone.py                                         # Entry zone definition.
│       │   ├── limit_price.py                                        # Limit price definition.
│       │   ├── market_trigger.py                                     # Market trigger definition.
│       │   ├── target_zone.py                                        # Target zone definition.
│       │   ├── invalidation_zone.py                                  # Invalidation zone definition.
│       │   ├── trigger_condition.py                                  # Trigger condition definition.
│       │   ├── trigger_state_machine.py                              # Signal trigger state machine.
│       │   ├── signal_precision_grade.py                             # Signal precision grade attachment.
│       │   ├── signal_evidence.py                                    # Signal evidence attachment.
│       │   ├── signal_abort.py                                       # Signal abort handling.
│       │   ├── signal_route_event.py                                 # Emits event when signal is generated and routed.
│       │   └── alert_event_emitter.py                                # Emits alert event for routed technical signal.
│       │
│       ├── rescan/                                                   # Sub-5ms Continuous Readiness Subsystem & Rescan Launcher
│       │   ├── __init__.py                                           # Rescan package boundary.
│       │   ├── rescan_engine.py                                      # Rescan orchestrator.
│       │   ├── rescan_orchestrator.py                                # Sub-5ms shared memory unbind, invalidation reset, and instant rescan.
│       │   ├── initial_scan.py                                       # Bot-on/pre-market scan.
│       │   ├── post_exit_rescan.py                                   # Rescan after position exit.
│       │   ├── thesis_failure_rescan.py                              # Rescan after thesis failure.
│       │   ├── fakeout_rescan.py                                     # Rescan after fakeout/trap event.
│       │   ├── spike_rescan.py                                       # Rescan after spike defense event.
│       │   ├── scenario_rescan.py                                    # Scenario transition rescan.
│       │   ├── fusion_rescan.py                                      # Fusion conflict/resolution rescan.
│       │   ├── engine_rescan.py                                      # Engine invalidation rescan.
│       │   └── rescan_evidence_snapshot.py                           # Immutable rescan evidence snapshot.
│       │
│       ├── execution_boundary/                                       # L10 — Technical-to-Operational Firewall
│       │   ├── __init__.py                                           # Execution boundary package boundary.
│       │   ├── technical_signal_adapter.py                           # Converts technical signal to downstream intent contract.
│       │   ├── execution_firewall.py                                 # Prevents technical code from directly invoking execution.
│       │   ├── downstream_contract.py                                # Explicit domain boundary contract.
│       │   └── signal_route_notifier.py                              # Notifies downstream and alert channels after routing.
│       │
│       ├── risk/                                                     # L11 — Downstream Risk Governance (Hard Veto Authority)
│       │   ├── __init__.py                                           # Risk package boundary.
│       │   ├── risk_gate.py                                          # Pre-trade risk gate.
│       │   ├── risk_governance.py                                    # Risk governance policy application.
│       │   ├── risk_boundary_quantizer.py                            # Volatility sizing, Kelly scaling, and 1.50% session risk cap.
│       │   ├── per_trade_risk.py                                     # Per-trade risk calculation.
│       │   ├── portfolio_risk.py                                     # Portfolio risk calculation.
│       │   ├── drawdown_guard.py                                     # Drawdown protection.
│       │   ├── daily_loss_cap.py                                     # Daily loss cap enforcement.
│       │   ├── exposure_engine.py                                    # Exposure calculation.
│       │   ├── circuit_breaker.py                                    # Trading circuit breaker.
│       │   ├── risk_veto.py                                          # Hard risk veto (cannot rewrite technical evidence).
│       │   └── risk_audit.py                                         # Risk decision audit.
│       │
│       ├── sizing/                                                   # L11 — Downstream Position Sizing (Broker Minimum Lot Authority)
│       │   ├── __init__.py                                           # Sizing package boundary.
│       │   ├── broker_minimum_lot.py                                 # Broker minimum lot authority.
│       │   ├── configured_lot_size.py                                # Configured lot size authority.
│       │   ├── risk_based_size.py                                    # Risk-based sizing computation.
│       │   ├── lot_normalizer.py                                     # Lot normalization.
│       │   ├── lot_step.py                                           # Lot step enforcement.
│       │   ├── lot_precision.py                                      # Lot precision enforcement.
│       │   ├── override_validator.py                                 # Override validation.
│       │   ├── effective_lot.py                                      # Effective lot resolution.
│       │   ├── position_size_engine.py                               # Position sizing engine.
│       │   └── sizing_audit.py                                       # Sizing audit.
│       │
│       ├── portfolio/                                                # L11 — Downstream Portfolio Exposure
│       │   ├── __init__.py                                           # Portfolio package boundary.
│       │   ├── exposure_engine.py                                    # Portfolio exposure engine.
│       │   ├── correlation_engine.py                                 # Correlation engine.
│       │   ├── concentration_guard.py                                # Concentration guard.
│       │   ├── net_exposure.py                                       # Net exposure computation.
│       │   └── portfolio_audit.py                                    # Portfolio audit.
│       │
│       ├── broker/                                                   # L12 — Broker Adapter Domain (MT5 / MT4 / cTrader / FIX)
│       │   ├── __init__.py                                           # Broker package boundary.
│       │   ├── broker_registry.py                                    # Broker adapter registry.
│       │   ├── capability_discovery.py                               # Broker capability discovery.
│       │   ├── symbol_specification.py                               # Symbol specification discovery.
│       │   ├── minimum_lot.py                                        # Broker minimum lot retrieval.
│       │   ├── lot_step.py                                           # Broker lot step retrieval.
│       │   ├── price_precision.py                                    # Price precision retrieval.
│       │   ├── tick_value.py                                         # Tick value retrieval.
│       │   ├── contract_size.py                                      # Contract size retrieval.
│       │   ├── order_normalizer.py                                   # Normalizes orders for broker submission.
│       │   ├── broker_reconciliation.py                              # Broker state reconciliation.
│       │   ├── broker_health.py                                      # Broker health monitoring.
│       │   └── adapters/                                             # Broker adapter implementations
│       │       ├── __init__.py                                       # Broker adapter package boundary.
│       │       ├── mt5_adapter.py                                    # MetaTrader 5 live execution adapter.
│       │       ├── mt4_adapter.py                                    # MetaTrader 4 adapter.
│       │       ├── ctrader_adapter.py                                # cTrader adapter.
│       │       ├── fix_adapter.py                                    # FIX protocol execution adapter.
│       │       ├── rest_adapter.py                                   # Generic REST broker adapter.
│       │       └── websocket_adapter.py                              # WebSocket broker adapter.
│       │
│       ├── order_management/                                         # L12 — Order Lifecycle Domain (Single & Batch Execution)
│       │   ├── __init__.py                                           # Order management package boundary.
│       │   ├── order_intent.py                                       # Order intent representation.
│       │   ├── pre_trade_gate.py                                     # Final pre-trade gate.
│       │   ├── order_constructor.py                                  # Order construction.
│       │   ├── multi_trade_batch_constructor.py                      # Multi-trade batch payload constructor for single & cross pairs.
│       │   ├── order_router.py                                       # Order routing.
│       │   ├── order_submitter.py                                    # Order submission.
│       │   ├── order_monitor.py                                      # Order monitoring.
│       │   ├── order_modify.py                                       # Order modification.
│       │   ├── order_cancel.py                                       # Order cancellation.
│       │   ├── order_reconciliation.py                               # Order reconciliation.
│       │   └── order_audit.py                                        # Order audit.
│       │
│       ├── position_management/                                      # L12 — Position Lifecycle Domain (Trade Management Lifecycle: TMS)
│       │   ├── __init__.py                                           # Position management package boundary.
│       │   ├── trade_management_lifecycle.py                         # Active lifecycle: Breakeven (+1.5 ATR), Trailing Stop (+2.0R), Time Stop.
│       │   ├── position_state.py                                     # Position state tracking.
│       │   ├── thesis_monitor.py                                     # Thesis monitoring after entry.
│       │   ├── breakeven.py                                          # Breakeven management (+1.5 ATR).
│       │   ├── trailing.py                                           # Trailing stop management (+2.0R).
│       │   ├── spike_defense.py                                      # Volatility spike defense management.
│       │   ├── tp_sl_manager.py                                      # TP/SL multiplier management.
│       │   ├── partial_profits.py                                    # Partial profit management.
│       │   ├── position_exit.py                                      # Position exit execution.
│       │   ├── batch_position_closer.py                              # Batch closer: single pair all trades / cross-pair profit & loss trades.
│       │   ├── post_close.py                                         # Post-close processing.
│       │   └── position_audit.py                                     # Position audit.
│       │
│       ├── alerts/                                                   # L13 — First-Class Alert Domain (Telegram, WhatsApp, Email, Webhook)
│       │   ├── __init__.py                                           # Alert package boundary.
│       │   ├── alert_engine.py                                       # Alert orchestration engine.
│       │   ├── alert_event.py                                        # Alert event representation.
│       │   ├── signal_alert_listener.py                              # Listens for generated/routed signal events.
│       │   ├── route_alert_listener.py                               # Listens for execution boundary routing events.
│       │   ├── channel_router.py                                     # Routes alert events to configured channels.
│       │   ├── template_renderer.py                                  # Renders alert templates per channel.
│       │   ├── rate_limiter.py                                       # Prevents alert flooding.
│       │   ├── telegram.py                                           # Telegram alert channel.
│       │   ├── email.py                                              # Email alert channel.
│       │   ├── whatsapp.py                                           # WhatsApp alert channel.
│       │   ├── websocket.py                                          # WebSocket alert channel.
│       │   ├── webhook.py                                            # Webhook alert channel.
│       │   ├── mission_control_alert.py                              # Mission Control GUI alert channel.
│       │   └── alert_audit.py                                        # Alert dispatch audit.
│       │
│       ├── journal/                                                  # L13 — First-Class Journal Domain
│       │   ├── __init__.py                                           # Journal package boundary.
│       │   ├── journal_engine.py                                     # Journal orchestration engine.
│       │   ├── signal_journal.py                                     # Signal journal.
│       │   ├── scenario_journal.py                                   # Scenario journal.
│       │   ├── fusion_journal.py                                     # Fusion journal.
│       │   ├── parameter_journal.py                                  # Parameter journal.
│       │   ├── execution_journal.py                                  # Execution journal.
│       │   ├── exit_journal.py                                       # Exit journal.
│       │   ├── rescan_journal.py                                     # Rescan journal.
│       │   ├── edge_decay_detector.py                                # Edge decay detector.
│       │   ├── outcome_attribution.py                                # Outcome attribution.
│       │   └── journal_export.py                                     # Journal export.
│       │
│       ├── monitoring_learning/                                      # L13 — Non-Mutating Monitoring / Learning Domain
│       │   ├── __init__.py                                           # Monitoring/learning package boundary.
│       │   ├── monitoring_engine.py                                  # Monitoring orchestration engine.
│       │   ├── performance_monitor.py                                # Performance monitoring.
│       │   ├── distribution_monitor.py                               # Distribution monitoring.
│       │   ├── concept_drift_detector.py                             # Concept drift detection.
│       │   ├── edge_decay_monitor.py                                 # Edge decay monitoring.
│       │   ├── walk_forward_runner.py                                # 31-year walk-forward matrix runner.
│       │   ├── out_of_sample_validator.py                            # Out-of-sample validator.
│       │   ├── drift_proposal_engine.py                              # Drift proposal engine.
│       │   ├── proposal_evidence.py                                  # Proposal evidence.
│       │   └── immutable_learning_boundary.py                        # Prevents live mutation by learning.
│       │
│       ├── api/                                                      # L14 — Low-Latency API / Access Layer (FastAPI ASGI)
│       │   ├── __init__.py                                           # API package boundary.
│       │   ├── app.py                                                # FastAPI application factory and lifespan management.
│       │   ├── dependencies.py                                       # API dependency injection boundaries.
│       │   ├── middleware.py                                         # Latency, auth, compression, correlation middleware.
│       │   ├── auth.py                                               # API authentication dependencies.
│       │   ├── serialization.py                                      # ORJSON low-latency serialization helpers.
│       │   ├── websocket.py                                          # WebSocket endpoint manager.
│       │   └── routers/                                              # API endpoint routers
│       │       ├── __init__.py                                       # API router package boundary.
│       │       ├── health.py                                         # Health endpoint.
│       │       ├── system.py                                         # System status endpoint.
│       │       ├── security.py                                       # Security/session endpoints.
│       │       ├── configuration.py                                  # Configuration read endpoints.
│       │       ├── control_panel.py                                  # Control Panel command endpoints.
│       │       ├── mission_control.py                                # Mission Control overview telemetry endpoints.
│       │       ├── trade_execution.py                                # Single, single-pair multi, and cross-pair trade execution endpoints.
│       │       ├── market.py                                         # Market data and reconstruction endpoints.
│       │       ├── awareness.py                                      # Awareness endpoints.
│       │       ├── intelligence.py                                   # Intelligence evidence endpoints.
│       │       ├── regime.py                                         # Regime endpoints.
│       │       ├── scenario.py                                       # Universal Scenario Pool endpoints.
│       │       ├── fusion.py                                         # Fusion endpoints.
│       │       ├── validation.py                                     # Validation endpoints.
│       │       ├── routing.py                                        # Routing endpoints.
│       │       ├── strategies.py                                     # Strategy Vault state and catalog endpoints.
│       │       ├── engines.py                                        # Engine state endpoints.
│       │       ├── precision.py                                      # Precision endpoints.
│       │       ├── signals.py                                        # Signal endpoints.
│       │       ├── evidence.py                                       # Evidence ledger endpoints.
│       │       ├── risk.py                                           # Risk endpoints.
│       │       ├── sizing.py                                         # Sizing endpoints.
│       │       ├── portfolio.py                                      # Portfolio endpoints.
│       │       ├── broker.py                                         # Broker endpoints.
│       │       ├── orders.py                                         # Order endpoints.
│       │       ├── positions.py                                      # Position endpoints.
│       │       ├── alerts.py                                         # Alert endpoints.
│       │       ├── journal.py                                        # Journal endpoints.
│       │       ├── monitoring.py                                     # Monitoring endpoints.
│       │       └── websocket.py                                      # WebSocket route registration.
│       │
│       ├── storage/                                                  # L1 — Persistence Infrastructure (RocksDB / Vector / SQLite)
│       │   ├── __init__.py                                           # Storage package boundary.
│       │   ├── time_series_store.py                                  # Time-series storage.
│       │   ├── parameter_store.py                                    # Parameter storage.
│       │   ├── indicator_store.py                                    # Indicator storage.
│       │   ├── scenario_store.py                                     # Scenario storage.
│       │   ├── fusion_store.py                                       # Fusion storage.
│       │   ├── signal_store.py                                       # Signal storage.
│       │   ├── order_store.py                                        # Order storage.
│       │   ├── position_store.py                                     # Position storage.
│       │   ├── audit_store.py                                        # Audit storage.
│       │   ├── evidence_ledger_store.py                              # Evidence ledger storage.
│       │   └── replay_store.py                                       # Replay storage.
│       │
│       └── services/                                                 # L1 — Shared Platform Services
│           ├── __init__.py                                           # Services package boundary.
│           ├── event_bus.py                                          # Canonical domain event bus.
│           ├── command_bus.py                                        # Canonical command bus.
│           ├── time_service.py                                       # Canonical time service.
│           ├── symbol_registry.py                                    # Symbol registry service.
│           ├── market_calendar_service.py                            # Market calendar service.
│           ├── news_calendar.py                                      # News calendar service.
│           ├── economic_release_service.py                           # Economic release service.
│           ├── sentiment_service.py                                  # Sentiment/chat analytics service.
│           ├── correlation_service.py                                # Cross-symbol correlation service.
│           ├── cache_service.py                                      # Low-latency cache service.
│           ├── telemetry_service.py                                  # Telemetry emission service.
│           ├── notification_service.py                               # Notification abstraction service.
│           └── replay_service.py                                     # Replay orchestration service.
│
├── services/                                                         # Deployable Integration Microservices
│   ├── execution-bridge/                                             # Live bi-directional broker connection service (MT5/MT4/cTrader/FIX)
│   │   ├── README.md                                                 # Service responsibility, lifecycle, credentials, deployment notes.
│   │   ├── pyproject.toml                                            # Service-specific packaging and runtime metadata.
│   │   ├── service.py                                                # Service process entry point and health lifecycle.
│   │   ├── config.py                                                 # Broker bridge configuration loader.
│   │   ├── api/                                                      # Broker Bridge API endpoints
│   │   │   ├── __init__.py                                           # Service API package boundary.
│   │   │   ├── health.py                                             # Liveness/readiness endpoints.
│   │   │   ├── account.py                                            # Account capability and telemetry endpoint.
│   │   │   ├── orders.py                                             # Order submission/status endpoint boundary.
│   │   │   └── batch_orders.py                                       # Multi-trade and cross-pair basket order execution endpoint.
│   │   ├── adapters/                                                 # Broker protocol adapters
│   │   │   ├── __init__.py                                           # Adapter package boundary.
│   │   │   ├── mt5.py                                                # MetaTrader 5 live execution adapter.
│   │   │   ├── mt4.py                                                # MetaTrader 4 execution adapter.
│   │   │   ├── ctrader.py                                            # cTrader execution adapter.
│   │   │   ├── fix.py                                                # FIX protocol execution adapter.
│   │   │   ├── rest.py                                               # Generic REST broker adapter.
│   │   │   └── websocket.py                                          # Generic WebSocket execution adapter.
│   │   ├── normalization/                                            # Broker format normalizers
│   │   │   ├── symbol_spec.py                                        # Broker symbol specification normalization.
│   │   │   ├── order_normalizer.py                                   # Order payload normalization.
│   │   │   ├── batch_order_normalizer.py                             # Batch order payload normalization.
│   │   │   └── execution_report_normalizer.py                        # Broker execution report normalization.
│   │   ├── schemas/                                                  # Broker telemetry schemas
│   │   │   ├── account.py                                            # Account state schema.
│   │   │   ├── symbol.py                                             # Symbol capability schema.
│   │   │   ├── order.py                                              # Downstream order schema.
│   │   │   ├── batch_order.py                                        # Batch order request schema.
│   │   │   └── execution_report.py                                   # Broker execution result schema.
│   │   └── tests/                                                    # Service tests
│   │       ├── test_mt5_adapter.py                                   # MT5 adapter contract tests.
│   │       ├── test_symbol_specs.py                                  # Symbol/minimum-lot capability tests.
│   │       ├── test_order_round_trip.py                              # Submit/ack/reconcile round-trip tests.
│   │       └── test_batch_execution.py                               # Cross-pair simultaneous execution tests.
│   ├── alert-gateway/                                                # Webhook and API dispatch service routing alerts to external channels
│   │   ├── README.md                                                 # Alert service contract and channel deployment notes.
│   │   ├── pyproject.toml                                            # Service packaging/runtime metadata.
│   │   ├── service.py                                                # Alert gateway process entry point.
│   │   ├── dispatcher.py                                             # Event-to-channel dispatch coordinator.
│   │   ├── deduplication.py                                          # Alert deduplication and idempotency.
│   │   ├── rate_limit.py                                             # Alert throttling.
│   │   ├── templates/                                                # Alert message templates
│   │   │   ├── signal_generated.txt.j2                               # Signal-generated alert template.
│   │   │   ├── signal_routed.txt.j2                                  # Signal-routed alert template.
│   │   │   ├── order_filled.txt.j2                                   # Execution-fill alert template.
│   │   │   ├── batch_trade_executed.txt.j2                           # Batch trade confirmation template.
│   │   │   └── risk_event.txt.j2                                     # Risk/circuit event template.
│   │   ├── channels/                                                 # Channel dispatch handlers
│   │   │   ├── telegram.py                                           # Telegram dispatch channel.
│   │   │   ├── email.py                                              # Email dispatch channel.
│   │   │   ├── whatsapp.py                                           # WhatsApp dispatch channel.
│   │   │   ├── webhook.py                                            # Generic webhook dispatch channel.
│   │   │   └── websocket.py                                          # Mission Control GUI WebSocket notification channel.
│   │   └── tests/                                                    # Alert gateway tests
│   │       ├── test_dispatcher.py                                    # Dispatch workflow tests.
│   │       ├── test_idempotency.py                                   # Duplicate-alert suppression tests.
│   │       └── test_channels.py                                      # Channel adapter contract tests.
│   └── ledger-storage-node/                                          # Dedicated RocksDB/Vector node for persisting the immutable evidence ledger
│       ├── README.md                                                 # Storage node responsibilities, retention, recovery, integrity notes.
│       ├── pyproject.toml                                            # Service packaging/runtime metadata.
│       ├── service.py                                                # Storage node process entry point.
│       ├── config.py                                                 # Storage configuration loader.
│       ├── api/                                                      # Storage node API endpoints
│       │   ├── __init__.py                                           # Storage API package boundary.
│       │   ├── health.py                                             # Storage liveness/readiness endpoint.
│       │   ├── evidence.py                                           # Evidence append/query endpoint boundary.
│       │   ├── snapshots.py                                          # Snapshot management endpoint boundary.
│       │   └── exports.py                                            # Audit export endpoint boundary.
│       ├── backends/                                                 # Persistence backends
│       │   ├── rocksdb_store.py                                      # Append-oriented RocksDB persistence adapter.
│       │   ├── sqlite_index.py                                       # Local relational index for query metadata.
│       │   ├── parquet_exporter.py                                   # Columnar audit/export writer.
│       │   └── vector_index.py                                       # Vector/semantic index for evidence retrieval.
│       ├── integrity/                                                # Storage integrity verifiers
│       │   ├── hash_chain_verifier.py                                # Evidence hash-chain verification.
│       │   ├── snapshot_verifier.py                                  # Snapshot integrity verification.
│       │   └── recovery_checker.py                                   # Recovery and continuity checks.
│       └── tests/                                                    # Storage node tests
│           ├── test_append_only.py                                   # Append-only ledger behavior tests.
│           ├── test_hash_chain.py                                    # Hash-chain continuity tests.
│           └── test_recovery.py                                      # Snapshot/recovery tests.
│
├── config/                                                           # External Versioned Configuration Tree (Single Source of Truth)
│   ├── README.md                                                     # Configuration doctrine, precedence, immutability, change control.
│   ├── module_dependencies.yaml                                      # Machine-readable approved dependency graph.
│   ├── boot_state.yaml                                               # Boot defaults and global max_hold_time = null.
│   ├── system.yaml                                                   # Platform runtime flags, lifecycle stage timeouts, worker bounds, logging, telemetry.
│   ├── environment.yaml                                              # Environment variables, staging/production endpoints, and database URIs.
│   ├── gui_preferences.yaml                                          # PySide6 GUI defaults: default theme (institutional_dark), font scale, 120Hz refresh.
│   ├── symbols.yaml                                                  # Supported instruments and symbol classes.
│   ├── timeframes.yaml                                               # Canonical timeframe definitions.
│   ├── timeframe_matrix.yaml                                         # HTF / MTF / LTF role relationships per engine and symbol class.
│   ├── sessions.yaml                                                 # Tokyo / London / New York / overlaps / synthetic epochs.
│   ├── technical_parameters.yaml                                     # Master catalogue of all technical parameters.
│   ├── parameter_registry.yaml                                       # Master registry of all parameters governing zero-silent-parameter doctrine.
│   ├── parameter_contribution_map.yaml                               # Maps technical parameters into fusion/precision contribution ledger.
│   ├── evidence_chain_sequence.yaml                                  # Synchronized chain sequence from raw data → signal.
│   ├── indicator_parameters.yaml                                     # Indicator periods, formulas, thresholds, normalization policy.
│   ├── confluence_weights.yaml                                       # Weight distribution matrix (PA 40%, Candle/CDT 35%, Indicators 25%).
│   ├── scenarios/                                                    # Scenario configuration tree (31 Scenarios, 13 Families)
│   │   ├── universal_scenario_pool.yaml                              # Universal scenario catalog (Directional, Compression, Range, Reversal).
│   │   ├── scenario_detector_parameters.yaml                         # Trend/Reversal/Breakout thresholds and sensitivity metrics.
│   │   ├── scenario_routing.yaml                                     # Scenario → engine eligibility mapping.
│   │   └── terminal_states.yaml                                      # UNKNOWN / CONFLICTED / NOVEL handling policy.
│   ├── strategies/                                                   # 50+ Master Strategy Vault Configuration
│   │   ├── strategy_vault_catalog.yaml                               # Master registry of 52 strategies with parameters and engine bindings.
│   │   ├── orderflow_microstructure.yaml                             # Config for Strategies S01 through S04.
│   │   ├── smc_ict_liquidity.yaml                                    # Config for Strategies S05 through S11.
│   │   ├── session_cycles.yaml                                       # Config for Strategies S12 through S16.
│   │   ├── structural_swing.yaml                                     # Config for Strategies S17 through S22.
│   │   ├── wyckoff_volume.yaml                                       # Config for Strategies S23 through S28.
│   │   ├── harmonics_geometry.yaml                                   # Config for Strategies S29 through S34.
│   │   ├── volatility_momentum.yaml                                  # Config for Strategies S35 through S40.
│   │   └── macro_statistical.yaml                                    # Config for Strategies S41 through S52.
│   ├── fusion/                                                       # Fusion configuration tree
│   │   ├── fusion_rules.yaml                                         # Multi-timeframe bidirectional reconciliation weights and conflict thresholds.
│   │   ├── htf_ltf_fusion.yaml                                       # HTF→LTF fusion parameters.
│   │   ├── ltf_htf_fusion.yaml                                       # LTF→HTF fusion parameters.
│   │   ├── mtf_bidirectional.yaml                                    # HTF↔MTF↔LTF bidirectional coordination rules.
│   │   ├── fusion_thresholds.yaml                                    # Fusion convergence thresholds.
│   │   └── conflict_policy.yaml                                      # Fusion conflict resolution policy.
│   ├── formation_grammars.yaml                                       # Causal formation grammars for scenario/setup validation.
│   ├── engine_profiles.yaml                                          # Four engine profiles: timeframe stacks, sensitivities, vetoes.
│   ├── engines/                                                      # Engine-specific configuration policies
│   │   ├── quant_scalping.yaml                                       # Engine A unique entry/trigger/target/exit policy.
│   │   ├── tactical_intraday.yaml                                    # Engine B unique entry/trigger/target/exit policy.
│   │   ├── swing_structural.yaml                                     # Engine C unique entry/trigger/target/exit policy.
│   │   ├── macro_institutional.yaml                                  # Engine D unique entry/trigger/target/exit policy.
│   │   └── entry_requirement_matrix.yaml                             # Cross-engine entry requirement matrix.
│   ├── precision_thresholds.yaml                                     # Precision-grade thresholds and routing margins.
│   ├── routing.yaml                                                  # Routing gates, veto lists, eligible families, NO_ROUTE policy.
│   ├── risk/                                                         # Risk policy configuration tree
│   │   ├── risk_policy.yaml                                          # Master risk policy.
│   │   ├── risk_firewall.yaml                                        # Hard stop invariants, maximum drawdown gates, and margin limits.
│   │   ├── exposure_policy.yaml                                      # Single-currency and total portfolio exposure limits.
│   │   ├── drawdown_policy.yaml                                      # Drawdown limits and automatic liquidation gates.
│   │   ├── circuit_breaker.yaml                                      # Circuit breaker triggers (volatility spike, spread widen).
│   │   └── position_limits.yaml                                      # Maximum open positions per symbol, family, and global book.
│   ├── sizing/                                                       # Sizing configuration tree
│   │   ├── lot_policy.yaml                                           # Lot sizing policy.
│   │   ├── override_policy.yaml                                      # Override policy.
│   │   └── broker_lot_rules.yaml                                     # Broker-specific lot rules.
│   ├── portfolio/                                                    # Portfolio configuration tree
│   │   ├── allocation_policy.yaml                                    # Capital allocation across Engines A, B, C, D.
│   │   ├── correlation_matrix.yaml                                   # Cross-currency correlation threshold limits.
│   │   ├── cross_pair_basket_rules.yaml                              # Execution and sizing rules for cross-pair basket operations.
│   │   └── concentration_limits.yaml                                 # Maximum capital committed per asset class.
│   ├── broker/                                                       # Broker configuration tree
│   │   ├── accounts.yaml                                             # Broker account definitions, servers, protocols.
│   │   ├── symbol_specs/                                             # Symbol specification overrides
│   │   │   ├── forex_majors.yaml                                     # EURUSD, GBPUSD, USDJPY specifications.
│   │   │   ├── forex_crosses.yaml                                    # EURGBP, EURJPY, GBPJPY specifications.
│   │   │   ├── metals.yaml                                           # XAUUSD, XAGUSD specifications.
│   │   │   └── indices.yaml                                          # US30, NAS100, SPX500 specifications.
│   │   └── order_types.yaml                                          # Broker supported order types and fill policies.
│   ├── alerts/                                                       # Alert configuration tree
│   │   ├── alert_channels.yaml                                       # Enabled channels (Telegram, WhatsApp, Webhook, Mission Control).
│   │   ├── notification_levels.yaml                                  # Alert priority levels (INFO, WARNING, CRITICAL, EMERGENCY).
│   │   └── alert_throttling.yaml                                     # Channel rate-limit and deduplication rules.
│   └── journal/                                                      # Journal configuration tree
│       ├── journal_retention.yaml                                    # Retention policies for trade and evidence logs.
│       └── attribution_rules.yaml                                    # Rules for attributing PnL to technical parameters and scenarios.
│
├── tests/                                                            # Master Institutional Test Framework
│   ├── __init__.py                                                   # Tests package boundary.
│   ├── conftest.py                                                   # Root test fixtures, event loop setup, mock market data.
│   ├── unit/                                                         # Unit test suites isolated by domain
│   │   ├── core/                                                     # Core kernel unit tests
│   │   │   ├── test_constitutional_laws.py                           # Tests immutable constitutional laws.
│   │   │   ├── test_three_core_gatekeeper.py                         # Tests PA + Candle + Indicator gatekeeper weights.
│   │   │   ├── test_dependency_graph.py                              # Tests zero circular dependencies via NetworkX.
│   │   │   └── test_session_epoch.py                                 # Tests 6-phase session epoch manager.
│   │   ├── parameters/                                               # Parameter domain tests
│   │   │   ├── test_parameter_lifecycle.py                           # Tests INGEST → DECIDE lifecycle transitions.
│   │   │   ├── test_no_silent_drop.py                                # Validates that untracked parameters raise errors.
│   │   │   └── test_parameter_hashing.py                             # Tests Merkle root parameter identity hash generation.
│   │   ├── intelligence/                                             # Technical intelligence unit tests
│   │   │   ├── test_orderflow_delta.py                               # Tests CVD, cumulative delta, absorption detectors.
│   │   │   ├── test_hawkes_process.py                                # Tests Hawkes point-process orderflow clustering.
│   │   │   ├── test_smt_divergence.py                                # Tests SMT divergence cross-asset logic.
│   │   │   ├── test_stacey_burke_cycles.py                           # Tests 3-day cycle and peak formation traps.
│   │   │   └── test_harmonic_patterns.py                             # Tests Gartley, Bat, Butterfly, Cypher PRZ calculations.
│   │   ├── scenario_pool/                                            # Scenario Pool unit tests
│   │   │   ├── test_scenario_classifier.py                           # Tests S1-S31 classification accuracy.
│   │   │   ├── test_scenario_transitions.py                          # Tests valid state machine transitions.
│   │   │   └── test_terminal_states.py                               # Tests UNKNOWN/CONFLICTED/NOVEL map to WAIT.
│   │   ├── fusion/                                                   # Fusion Brain unit tests
│   │   │   ├── test_nine_layer_brain.py                              # Tests 9-layer convergence (MN1 to M1).
│   │   │   ├── test_bidirectional_flow.py                            # Tests top-down context and ground-up feedback.
│   │   │   └── test_fusion_conflict_resolution.py                    # Tests cross-timeframe conflict arbitration.
│   │   ├── strategies/                                               # 52 Strategies unit tests
│   │   │   ├── test_orderflow_strategies.py                          # Tests Strategies S01-S04.
│   │   │   ├── test_smc_ict_strategies.py                            # Tests Strategies S05-S11.
│   │   │   ├── test_session_cycle_strategies.py                      # Tests Strategies S12-S16.
│   │   │   ├── test_structural_swing_strategies.py                   # Tests Strategies S17-S22.
│   │   │   ├── test_wyckoff_volume_strategies.py                     # Tests Strategies S23-S28.
│   │   │   ├── test_harmonics_strategies.py                          # Tests Strategies S29-S34.
│   │   │   ├── test_volatility_momentum_strategies.py                # Tests Strategies S35-S40.
│   │   │   └── test_macro_statistical_strategies.py                  # Tests Strategies S41-S52.
│   │   ├── engines/                                                  # Peer engines unit tests
│   │   │   ├── test_quant_scalping_engine.py                         # Tests Engine A trigger rules and limits.
│   │   │   ├── test_tactical_intraday_engine.py                      # Tests Engine B trigger rules and limits.
│   │   │   ├── test_swing_structural_engine.py                       # Tests Engine C trigger rules and limits.
│   │   │   ├── test_macro_institutional_engine.py                    # Tests Engine D trigger rules and limits.
│   │   │   └── test_peer_dependency_guard.py                         # Verifies zero engine-to-engine coupling.
│   │   ├── risk_sizing/                                              # Risk and sizing unit tests
│   │   │   ├── test_risk_firewall.py                                 # Tests pre-trade risk vetoes.
│   │   │   ├── test_broker_minimum_lot.py                            # Tests broker minimum lot enforcement.
│   │   │   └── test_kelly_boundary_quantizer.py                      # Tests Kelly fraction and volatility scaling.
│   │   └── mission_control/                                          # Mission Control & Multi-Trade unit tests
│   │       ├── test_single_trade_execution.py                        # Tests single trade open/close mechanics.
│   │       ├── test_single_pair_multi_trade.py                       # Tests single pair tranche batch execution.
│   │       ├── test_cross_pair_basket_execution.py                   # Tests cross-pair multi-currency execution.
│   │       └── test_cross_pair_pnl_calculation.py                    # Tests real-time cross-pair profit/loss aggregation.
│   ├── integration/                                                  # End-to-end integration workflows
│   │   ├── test_tick_to_signal_pipeline.py                           # Full pipeline: Ingestion → Fusion → Engine → Ticket.
│   │   ├── test_signal_to_broker_execution.py                        # Downstream pipeline: Ticket → Firewall → Broker → Fill.
│   │   ├── test_rescan_sub_5ms_cycle.py                              # Validates <5ms unbind, reset, and rescan cycle.
│   │   ├── test_pyside6_ipc_stream.py                                # Integration test between core engines and PySide6 GUI.
│   │   └── test_cross_pair_hedge_lifecycle.py                        # End-to-end test of cross-pair hedge basket execution & flatten.
│   ├── property_based/                                               # Hypothesis property-based testing
│   │   ├── test_price_invariants.py                                  # Mathematical invariances across decimal prices and lots.
│   │   ├── test_hash_chain_integrity.py                              # Cryptographic continuity of evidence ledger under mutation.
│   │   └── test_decision_determinism.py                              # Verifies identical inputs produce identical decisions.
│   └── performance/                                                  # Sub-millisecond latency regression benchmarks
│       ├── test_fusion_calculation_latency.py                        # Benchmarks 9-layer fusion computation (<500μs).
│       ├── test_trade_panel_dispatch_latency.py                      # Benchmarks PySide6 GUI trade dispatch latency (<1ms).
│       └── test_rescan_benchmark.py                                  # Enforces rescan lifecycle execution < 5 milliseconds.
│
├── scripts/                                                          # Operational, Audit & Diagnostic Tooling
│   ├── architecture_audit.py                                         # Verifies 100% adherence to zero-layer-violation doctrine.
│   ├── circular_dependency_check.py                                  # AST-based static import scanner ensuring 0 circular references.
│   ├── parameter_completeness_audit.py                               # Confirms every registered parameter is tracked in the ledger.
│   ├── compile_qss.py                                                # Pre-compiles and validates all QSS stylesheets for syntax errors.
│   ├── generate_synthetic_data.py                                    # Generates deterministic tick/OHLCV data for backtesting.
│   ├── run_matrix_backtest.py                                        # Runs 31-year multi-asset walk-forward backtest matrix.
│   ├── export_evidence_ledger.py                                     # Exports cryptographic evidence chain to Parquet/JSONL.
│   └── launch_mission_control.py                                     # Diagnostic launcher for PySide6 GUI with performance profiler.
│
├── data/                                                             # Local File-System Data Directories
│   ├── ticks/                                                        # Local tick cache and high-frequency tape prints.
│   ├── ohlcv/                                                        # Standardized Parquet multi-timeframe candles.
│   ├── orderbook/                                                    # Level 2 DOM snapshots and queue delta logs.
│   ├── news/                                                         # Economic calendar releases and historical shock timestamps.
│   └── synthetic/                                                    # Deterministic synthetic test market feeds.
│
└── storage/                                                          # Local Runtime Storage & Persistence Files
    ├── rocksdb/                                                      # High-speed RocksDB append-only evidence store.
    ├── sqlite/                                                       # Local SQLite relational query index.
    ├── vector/                                                       # Vector indices for semantic similarity matching.
    ├── audit/                                                        # Immutable audit logs and security attestation records.
    └── snapshots/                                                    # Point-in-time state backups and disaster-recovery dumps.
```

---

## PART 2 — MACRO-SYSTEM ARCHITECTURE (THE FOREST)

### 2.1 Global topology

`DAVID_SLING_IATOS/` is a **single pure-Python 3.12+ monorepo** with four deployable surfaces:

1. **Core package** `src/david_sling/` — the entire trading OS, organized as a 15-layer DAG (L0–L14). This is where 100% of business/technical logic lives.
2. **Desktop app** `apps/mission_control_gui/` — PySide6 Mission Control GUI (MVVM), the L14 presentation surface, talking to the core over IPC/WebSocket/shared-memory telemetry.
3. **Integration microservices** `services/` — three independently deployable processes: `execution-bridge` (broker connectivity), `alert-gateway` (external channel dispatch), `ledger-storage-node` (RocksDB/vector persistence of the evidence ledger).
4. **L14 access layer** `src/david_sling/api/` — FastAPI ASGI app (the "web version first" milestone: REST routers + real-time telemetry WebSockets + ORJSON serialization), plus infrastructure under `deploy/` (Docker ×4, compose ×2, K8s ×6, PyInstaller/Nuitka packaging, systemd ×2).

Entry points: `main.py` (production boot: integrity verify → engine loop → GUI loop) and `run.py` (dev launcher: live / scan / backtest / replay / gui / diagnostic modes). Governance files at root (`pyproject.toml`, `requirements*.txt`, `pytest.ini`, `mypy.ini`, `ruff.toml`, `Makefile`, `.env.example`, `.python-version`), IDE config `.vscode/`, CI `.github/workflows/` (7 pipelines incl. `architecture_audit.yml`, `dialectical-compiler.yml`, `quant-backtest-matrix.yml` running the **31-year multi-asset** regression, `performance-k6.yml`).

### 2.2 Macro-components and boundary interfaces

| Macro-component | Location | Boundary interface (what crosses in/out) |
|---|---|---|
| L0 Kernel | `core/` | Constitutional laws, contracts, Pydantic schemas, utilities, error taxonomy. Nothing imports upward; everything imports *from* here. |
| L1 Platform | `bootstrap/ security/ configuration/ control_panel/ mission_control/ application/ storage/ services/` | Boot attestation, RBAC/license/crypto, effective config + propagation bus, operator command validation, read models/use cases, persistence, canonical event/command buses. |
| L2 Data & Parameter | `parameter/ evidence_ledger/ data/` | Raw feeds → validated canonical events; the 8-stage parameter lifecycle; append-only hash-chained evidence ledger. |
| L3 Perception | `awareness/ intelligence/ regime/` | Awareness snapshot; 16 intelligence families → evidence packets; regime classification. |
| L4 Scenario & Thesis | `scenario_pool/ hypothesis/ grammar/` | 31-scenario classifier ("Scenario is King"), thesis state machine, causal formation grammars (CDT confirmations). |
| L5 Fusion Brain | `fusion/` | 9-layer bidirectional HTF↔MTF↔LTF coordination → immutable FusionSnapshot. |
| L6 Validation | `validation/` | Three-Core gate (PA 40% + Candle/CDT 35% + Indicators 25%) + contradiction engine. |
| L7 Routing & Strategies | `routing/ strategies/` | Single routing authority → Engine A/B/C/D or NO_ROUTE; 52-strategy vault in 8 families. |
| L8 Peer Engines | `engines/` | Four zero-coupling engines, each with profile/context/decision/scenario-map/grammar/requirements/vetoes/precision/trigger. |
| L9 Precision & Signal | `precision/ signal/ rescan/` | Tier 1–4 grading → canonical `TechnicalSignalTicket`; sub-5 ms rescan subsystem. |
| L10 Execution Boundary | `execution_boundary/` | The **only** door from technical (L0–L9) to operational (L11–L12): converts signal → order intent. |
| L11 Risk & Sizing & Portfolio | `risk/ sizing/ portfolio/` | Hard veto authority, broker min-lot authority, exposure/correlation/concentration guards. |
| L12 Broker & Orders | `broker/ order_management/ position_management/` | Adapters (MT5/MT4/cTrader/FIX/REST/WebSocket), order lifecycle, position TMS lifecycle. |
| L13 Audit & Learning | `alerts/ journal/ monitoring_learning/` | Alert channels, immutable journal, non-mutating monitoring (walk-forward, drift proposals). |
| L14 Application & GUI | `api/ application/` + `apps/mission_control_gui/` | FastAPI routers/WebSockets; PySide6 MVVM GUI with QSS themes. |

### 2.3 Macro data-flow pipelines

- **P1 Ingestion→Persistence:** feeds (`data/ingestion/`: tick, OHLCV, orderbook L2, trade flow, volume, news, economic releases, sentiment, chat, historical, synthetic) → `feed_router` → integrity validators (schema/timestamp/sequence/duplicate/gap/stale/outlier/cross-source) → canonical `ohlcv_builder` + `timeframe_resampler` → `market_reconstruction` (current/previous/forming state, morphology, deterministic fingerprint) → storage (RocksDB time-series, SQLite index, Parquet export) + `replay/` deterministic backtest engine.
- **P2 Parameter lifecycle (zero-silent-drop):** INGEST → VALIDATE → DERIVE → CONTEXTUALIZE → FUSE → CONTRIBUTE → DECIDE → RECORD. Any parameter bypassing registration raises `UntrackedParameterError` and **halts execution**.
- **P3 Decision pipeline (tick→signal):** awareness → intelligence evidence matrix → regime → scenario pool (S1–S31 or terminal UNKNOWN/CONFLICTED/NOVEL) → hypothesis (ARMED/TRIGGERED/HOLD/CHANGE/FAILURE) → grammar sequence integrity → 9-layer fusion → validation + 3-core gate → routing → peer engine trigger → precision grade → `TechnicalSignalTicket` (+ alert emission + route event).
- **P4 Execution pipeline (signal→broker):** L10 firewall → risk gate (hard veto, no technical mutation) → sizing (broker min-lot/step/precision authority, Kelly/risk-based) → portfolio exposure/correlation check → broker adapter normalization → order lifecycle (construct/submit/monitor/modify/cancel/reconcile) → position TMS (breakeven +1.5 ATR, trailing +2.0R, spike defense, partials 25/50/75%, batch close, panic flatten) → post-close → **sub-5 ms rescan** relaunches P3.
- **P5 Telemetry pipeline (core→operator):** `services/event_bus` + `command_bus` → `mission_control` telemetry server → WebSocket/IPC/shared-memory stream (`ipc_telemetry_stream.py`) → FastAPI WebSocket (`api/websocket.py`) → GUI `bridge/telemetry_receiver.py` → Qt signals → viewmodels → views (60/120 Hz refresh).
- **P6 Audit pipeline:** every stage appends to the hash-chained `evidence_ledger` (SHA3/BLAKE3/SHA-256, Merkle roots) + journals + alert audit + `ledger-storage-node` service; exportable to Parquet/JSONL.

---

## PART 3 — MICRO / SUB-MICRO UNIT LOGIC (THE LEAVES)

### 3.1 L0 Kernel (`core/`)
- **Constitutional laws** (`constitutional_laws.py`, `operating_principles.py`): one scenario authority, one fusion brain, no silent drops, enforced at import time.
- **Architecture manifest + dependency graph**: `architecture_manifest.py` is the authoritative module registry; `dependency_graph.py` is a NetworkX topological model asserting **zero circular dependencies**; `technical_boundaries.py` structurally prevents technical core from importing risk/broker/sizing.
- **Policies**: `session_epoch_manager.py` = 6-phase session clock (Asia/London/NY/overlaps/"10 AM Club"); `three_core_confluence_gatekeeper.py` = PA 40% + CDT 35% + Indicators 25%; `no_time_expiry_policy.py` = `max_hold_time = null` globally; `terminal_state_policy.py` = UNKNOWN/CONFLICTED/NOVEL → WAIT/NO_ROUTE/ABSTAIN; `deterministic_decision_contract.py` = replay determinism; `abstention_policy.py`.
- **28 contract modules** (`core/contracts/`) and **26 Pydantic v2 schemas** (`core/schemas/`): symbol, timeframe, session, tick, candle, orderbook, trade_flow, chat_message, news_event, parameter_state (VALID/INVALID/MISSING/STALE/CONFLICTED), evidence_record (Merkle roots), market_snapshot, regime_state, scenario_state (S1–S31), fusion_snapshot, validation_result, hypothesis_state, grammar_state, route_decision, engine_decision, precision_grade (Tier 1–4), signal_ticket, order_intent, multi_trade_intent, cross_pair_pnl_state, position_state, alert_event, rescan_event.
- **Utilities**: time, math, **exact decimal arithmetic** (`decimal_utils.py` — price/lot safety), deterministic UUIDv5/ULID, SHA3/BLAKE3/SHA-256 hashing, validation, immutable/frozen snapshots, deterministic collections, Result/Ok/Error monads, concurrency helpers.
- **19-class error taxonomy** (`core/errors/`): base, architecture, boundary_violation, validation, configuration, boot, security, license, evidence, parameter, scenario, fusion, routing, engine, precision, signal, execution, multi_trade, data, alert, + `untracked_parameter_error` (the zero-silent-drop tripwire).

### 3.2 L1 Platform
- **Boot** (`bootstrap/`): supreme orchestrator `david_os_boot.py` (UI shows "DAVID SLING"); ordered stages with `boot_state` BOOTING→SECURITY_CHECK→LICENSE_CHECK→READY/HALTED; secure boot chain, preflight (environment/dependency-hash/filesystem/UTC-clock), **single-instance process lock**, architecture & configuration & parameter-registry & evidence-ledger integrity checks, controlled `boot_failure` forensic halt, immutable `boot_audit`.
- **Security** (`security/`): identity provider/registry (master admin, users, services), cryptographic master-admin gate, RBAC + policy-as-code + authorization guard + immutable audit, **cryptographic license engine** (signature Ed25519/ECDSA, expiry/grace, entitlements, feature gate, device binding, session, revocation, audit), AES-GCM envelope encryption + key manager, session tokens/expiry/revocation, scoped secrets provider, intrusion/suspicious-activity/failed-auth/privilege-escalation/integrity monitoring.
- **Configuration** (`configuration/`): registry of *every* parameter, typed schemas, validator, **precedence engine with no silent overrides**, immutable effective configuration + snapshots + versioning, propagation bus, boot-frozen constraints, policy enforcer, audit. Externalized in `config/*.yaml` (the single source of truth).
- **Control panel** (`control_panel/` + GUI forms): validated operator mutations → command → versioned commit → hard-enforcement router → rollback; 17 sections (system/license/broker/symbols/engines/technical/indicators/risk/capital/sizing/orders/TP-SL-trailing/breakeven-spike/news/custom-news/alerts/audit-export/emergency).
- **Mission Control core** (`mission_control/`): telemetry server, 30+ status boards (one per domain), `multi_trade_operations_engine.py` + `cross_pair_pnl_calculator.py` (sub-millisecond aggregate PnL/swap/spread), `ipc_telemetry_stream.py`.
- **Application façade** (`application/`): query/command gateways, 9 read models, 11 use cases (boot, authenticate, queries…, `execute_single_trade`, `execute_single_pair_multi_trade`, `execute_cross_pair_basket_trade`, `close_batch_trades`, control-panel submit, audit export, rescan).

### 3.3 L2 Data, Parameter, Evidence
- **Ingestion** 11 routers + canonical feed router; **integrity** 10 validators + candle builder + resampler; **reconstruction** 7 modules with deterministic fingerprint; **replay** deterministic engine/session/audit.
- **Parameter domain**: definition/registry/schema/source/context/calculation/normalization/state, lifecycle manager (8 stages), lineage, dependency graph, contribution, reconciliation, completeness, **equal-contribution policy** (no primary/secondary parameter), decision-impact tracker, coverage tracker, untracked-parameter guard, no-silent-drop auditor, SHA-256 Merkle parameter hashing, audit.
- **Evidence ledger**: append-only ledger, entries, identity, lineage, contribution/rejection/conflict/missing/decision records, parameter accountability & decision impact, evidence matrix, **evidence density** (feeds precision grading), provenance tracker, silent-drop detector, hash chain, validator, snapshot, export.

### 3.4 L3 Perception — Awareness, Intelligence (16 families), Regime
- **Awareness** 11 state modules → immutable snapshot.
- **Intelligence** 16 families: price_action (impulse, displacement, rejection, pullback, breakout, breakout_failure, compression, exhaustion); candles (body/wick/range ratios, single/dual/multi/sequence patterns, **1CDT/2CDT/3CDT displacement confirmation**, session/weekly/monthly candles); structure (swing points, internal/external, **BOS, CHoCH, MSS, MSB, CISD, SMT divergence**, sequences, trend, failure); liquidity (EQL/EQH/ERL/IRL, stop clusters, pools, sweep, stop hunt, reclaim, delivery cycle); orderflow (bid-ask & trade imbalance, delta, **CVD**, **Hawkes process burst sniper**, microstructure gaps, absorption, shift); volume (raw, relative, z-score, expansion, contraction); volatility (ATR, ATR ratio, realized vol, z-score, percentile, **SKEW-GARCH VRP**, **VIX term structure**, **wavelet filter**, compression/expansion, regime); momentum (rate, impulse strength, acceleration, divergence, regime); indicators (single `indicator_engine` — no duplicate folders — SMA/EMA/WMA, MACD, ADX, PSAR, Ichimoku, Aroon, RSI, Stochastic, CCI, Williams %R, ROC, Bollinger, Keltner, VWAP, **anchored VWAP**, OBV, volume profile); geometry (range/swing/slope, distance, symmetry, anchors, measured-move projections, confluence); levels (PDH/PDL/PWH/PWL, session H/L, opening price, equilibrium, premium/discount, swing levels, S/R, HTF levels, cluster engine); zones (order block, FVG, inversion FVG, breaker, mitigation, supply/demand, POI, quality/freshness/mitigation state, interaction); fibonacci (retracement, extension, golden zone, **OTE**, sniper zone, anchor validation); harmonics (ABCD, Gartley, Bat, Butterfly, Cypher, Crab, Shark, PRZ engine, validation); patterns (13 classical chart patterns; **Wyckoff Phases A–E** incl. spring/UTAD/SOS/LPS/LPSY/UTAD/selling climax; **Stacey Burke 3-day cycle** incl. first green/red day & session H/L traps; statistical: **Takens phase-space embedding, Gaussian HMM, TDA persistent homology**; liquidity traps: turtle soup/CRT, taipan soup, stop hunt, sweep reclaim, failed breakout reclaim); sentiment (chat, news, narrative momentum, divergence); event shock (news/economic/chat-burst impact).
- **Regime** 8 classifiers: trend, range, compression, expansion, transition, mean-reversion, volatility, liquidity.

### 3.5 L4 Scenario Pool (the "King"), Hypothesis, Grammar
- **31 scenarios S1–S31** organized as **28 concrete family classifiers** + **3 terminal states** (`terminal/unknown.py`, `conflicted.py`, `novel.py` → force WAIT/NO_ROUTE/ABSTAIN). Families: trend_continuation, trend_failure, pullback, momentum, breakout, breakout_continuation, breakout_failure, fakeout, liquidity_sweep, reversal, expansion, compression, consolidation, mean_reversion, accumulation, distribution, markup, markdown, exhaustion, breakout_pullback_continuation, breakout_failure_reversal, quasimodo, diamond, parabolic_expansion, turtle_soup, taipan_soup, multi_timeframe_alignment, news_repricing. Each with identity/state/phase/previous/forming/transition/evidence/contradiction/detector-parameters; `scenario_routing_matrix.py` maps scenarios→engine eligibility. (Blueprint header says "13 Families" while listing 28 family files — see §6 observations.)
- **Hypothesis**: bullish/bearish/neutral/continuation/reversal/breakout/pullback/failure theses; state ARMED/TRIGGERED/HOLD/CHANGE/FAILURE; invalidation + revalidation.
- **Grammar**: causal sequences with precondition/formation/confirmation (1CDT/2CDT/3CDT/Multi-CDT)/invalidation steps, sequence integrity, grammar registry, engine-grammar mapper.

### 3.6 L5 — 9-Layer Bidirectional Fusion Brain
`fusion_engine` + `nine_layer_fusion_brain` coordinating **MN1, W1, D1, H8, H4, H1, M30, M15, M5→M1**; timeframe registry with HTF/MTF/LTF roles; immutable fusion snapshot; cross-TF parameter registry/contribution map; convergence measured across structure/liquidity/momentum/volatility/indicator/level/zone; **top-down** (HTF→MTF, MTF→LTF, HTF→LTF terrain/POI) and **ground-up** (LTF→MTF, MTF→HTF, LTF→HTF) coordinators with bidirectional consistency, role-conflict resolution, parameter alignment, candle-morphology watch, conflict recording; trigger alignment with engine requirements. Latency budget: fusion computation **< 500 µs**.

### 3.7 L6 Validation, L7 Routing & the 52-Strategy Vault
- **Validation**: per-domain validators (parameter, indicator, geometry, level, zone, pattern, liquidity, volatility, momentum, sentiment, event) + **three-core gate** (PA 40% / Candle+CDT 35% / Indicators 25%) + contradiction engine (hard/soft conflicts + resolution policy).
- **Routing**: single authority `router.py` → A/B/C/D or NO_ROUTE; strategy-vault router; eligibility matrix; setup-method resolver; scoring; route explanation evidence; NO_ROUTE abstention.
- **Strategies S01–S52, 8 families** (each a class implementing `base_strategy.py`, registered in `strategy_registry.py`):
  - **Family 1 Orderflow & Microstructure (Engine A):** S01 Hawkes burst sniper, S02 CVD absorption reversal, S03 bid-ask vacuum sweep, S04 microstructure gap fill.
  - **Family 2 SMC & ICT Liquidity (A & B):** S05 Turtle Soup/CRT, S06 London-open 15M Judas swing, S07 FVG inversion retest, S08 CISD order-block tap, S09 breaker-block shift, S10 SMT cross-asset divergence (DXY vs EURUSD, ES vs NQ), S11 Taipan wick raid.
  - **Family 3 Session Epochs & Cycles (B):** S12 Stacey Burke 3-day cycle, S13 First Green/Red Day, S14 NY 10 AM Club, S15 Asian range raid→NY expansion, S16 ORB-15.
  - **Family 4 Structural Swing (C):** S17 HTF CHoCH/BOS 2CDT/3CDT retest, S18 Golden Zone/OTE 61.8–78.6%, S19 Quasimodo/QML, S20 Diamond, S21 Broadening wedge, S22 Head & Shoulders neckline.
  - **Family 5 Wyckoff & Volume (B & C):** S23 Phase-C spring, S24 UTAD, S25 LPS markup, S26 LPSY markdown, S27 anchored-VWAP volume shelf, S28 POC/HVN rejection.
  - **Family 6 Harmonics & Geometry (C):** S29 Gartley 0.786 PRZ, S30 Bat 0.886, S31 Butterfly 1.272, S32 Crab 1.618, S33 Cypher 0.786, S34 AB=CD measured move.
  - **Family 7 Volatility & Momentum (A & B):** S35 Bollinger–Keltner squeeze, S36 parabolic ATR expansion, S37 wavelet-denoised trend, S38 multi-TF RSI divergence, S39 zero-lag MACD impulse, S40 ADX exhaustion reversion.
  - **Family 8 Macro Institutional & Quant (D):** S41 Takens attractor, S42 HMM regime transition, S43 TDA persistent homology, S44 SKEW-GARCH VRP reversion, S45 VIX term-structure pivot, S46 central-bank shock repricing, S47 triangular synthetic arb, S48 commodity-FX cointegration (AUD/NZD/CAD), S49 10Y-2Y curve FX trend, S50 multi-month liquidity pool sweep, S51 macro trend pyramid, S52 edge-decay adaptive rotation.

### 3.8 L8 — Four Peer Engines (zero engine-to-engine coupling, enforced by `peer_dependency_guard.py`)

| Engine | Horizon | Context TFs | Trigger TFs | Grammar | Strategy families |
|---|---|---|---|---|---|
| **A — Quant Scalping** | 15M–30M | H4/H1/M30 | M5/M10/M15 | 1CDT/2CDT rapid | 1, 2 (partial), 7 (partial) |
| **B — Tactical Intraday** | 1H–4H | H4/H1 | M15/M30 | 2CDT/3CDT | 2, 3, 5 (partial), 7 (partial) |
| **C — Swing Structural** | 4H–8H | D1/H4 | H1/H4 | 3CDT/4CDT & POI taps | 4, 5 (partial), 6 |
| **D — Macro Institutional** | 8H–Daily | W1/MN1/D1 | H4/H8 | Multi-CDT structural expansion | 8 |

Each engine package is identical in shape: `engine.py` coordinator, `profile.py`, `context_adapter.py`, `decision.py`, `scenario_map.py`, `formation_grammar.py`, entry/limit/market-trigger/target/exit `*_requirements.py`, `setup_selector.py` + `setup_matrix.py`, `parameter_requirements.py`, domain requirement modules (liquidity/microstructure/rapid-confirmation for A; session/opening-range/breakout/pullback/expansion for B; swing/structure/POI/zone for C; 14 macro_* modules for D), `veto_rules.py`, `precision_input.py` + `precision_trigger.py`, `engine_trigger.py`. Supervisor/registry/health/audit at container level.

### 3.9 L9 Precision & Signal + Rescan
- **Precision**: 16 quality scorers (parameter, technical, scenario, fusion, structure, liquidity, volatility, momentum, indicator, geometry, level, zone, location, target, trigger + contradiction penalty) → grade mapper → **Tier 1–4** + explanation evidence → trigger readiness.
- **Signal**: canonical `TechnicalSignalTicket` with identity, direction, scenario/setup refs, entry zone, limit price, market trigger, target zone, invalidation zone, trigger condition + **trigger state machine**, precision grade, evidence, abort handling, route event + alert emission.
- **Rescan** (sub-5 ms budget, shared-memory unbind → invalidation reset → instant rescan): initial scan, post-exit, thesis-failure, fakeout, spike, scenario, fusion, engine rescans + immutable rescan evidence snapshot.

### 3.10 L10–L12 Execution side (the operational half)
- **L10 Execution Boundary Firewall**: technical signal → downstream intent adapter; technical code *cannot* invoke execution directly; route notifier emits to downstream + alert channels.
- **L11 Risk**: pre-trade gate, governance, **risk boundary quantizer (volatility sizing, Kelly scaling, 1.50% session risk cap)**, per-trade & portfolio risk, drawdown guard, **daily loss cap**, exposure engine, **circuit breaker** (volatility spike, spread widen), **hard veto that can never rewrite technical evidence**, audit. Sizing: **broker minimum lot is the authority**, configured lot, risk-based size, lot normalizer/step/precision, override validator, effective lot, audit. Portfolio: exposure, correlation engine, concentration guard, net exposure, audit.
- **L12 Broker/Order/Position**: capability discovery, symbol spec (min lot, lot step, price precision, tick value, contract size), order normalizer, reconciliation, health; adapters MT5/MT4/cTrader/FIX/REST/WebSocket (mirrored in `services/execution-bridge`). Order lifecycle: intent → pre-trade gate → constructor → **multi-trade batch constructor (single-pair & cross-pair)** → router → submitter → monitor/modify/cancel/reconciliation/audit. Position **TMS lifecycle**: breakeven **+1.5 ATR**, trailing **+2.0R**, spike defense, TP/SL multipliers, partial profits, exit, **batch closer** (pair-all / cross-pair profit-loss), post-close, audit. Time stop exists as a *control*, but `max_hold_time = null` is the global policy (no time expiry).
- **Multi-trade operations**: `multi_trade_operations_engine` (single, single-pair multi, cross-pair basket) + `cross_pair_pnl_calculator` (sub-ms gross profit/loss, net, swap, spread, margin per pair + aggregate) — mirrored in the GUI Omni-Trade panel and `services/execution-bridge/api/batch_orders.py`.

### 3.11 L13 Audit & Learning
- **Alerts**: engine + listeners for signal/route events, channel router (Telegram, Email, WhatsApp, WebSocket, Webhook, Mission Control), template renderer, rate limiter, audit; mirrored by `services/alert-gateway` (dedup/idempotency, Jinja2 templates, 5 channels).
- **Journal**: signal/scenario/fusion/parameter/execution/exit/rescan journals, edge-decay detector, outcome attribution, export.
- **Monitoring/learning (non-mutating)**: performance, distribution, concept-drift, edge-decay monitors, **31-year walk-forward runner**, out-of-sample validator, drift proposal engine + evidence, **immutable learning boundary** (learning can propose, never mutate live).

### 3.12 L14 Application & GUI
- **API** (`src/david_sling/api/`): FastAPI factory/lifespan, DI, middleware (latency/auth/compression/correlation), auth deps, **ORJSON** serialization, WebSocket manager; **30 routers** (health, system, security, configuration, control_panel, mission_control, trade_execution, market, awareness, intelligence, regime, scenario, fusion, validation, routing, strategies, engines, precision, signals, evidence, risk, sizing, portfolio, broker, orders, positions, alerts, journal, monitoring, websocket).
- **GUI** (`apps/mission_control_gui/`): `app.py` (QApplication, DPI, fonts), `main_window.py` (nav + status ribbon + stacked workspace), `qss_manager.py` (live theme swap + dev hot-reload); **bridge** (qasync asyncio↔Qt, IPC client, WebSocket telemetry receiver, command dispatcher, global Qt signals); **8 viewmodels** (MVVM, Qt-free); **5 views** — mission_control (global overview + telemetry bar, health matrix, market awareness, scenario pool display, fusion brain summary, engine status grid, signals feed, **trade_execution/ omni panel**: omni_trade_panel, single_trade_controller, single_pair_multi_trade_controller, cross_pair_basket_controller, cross_pair_pnl_matrix, quick_action_toolbar [close profitable/losing, break-even all, halt], execution_confirm_dialog [slippage/margin/fees pre-flight]), control_panel (8 forms), portfolio (positions/history/exposure/equity chart), evidence_ledger (stream, record inspector, hash-chain validator, lineage tree), graph_topology (fusion matrix canvas, scenario state machine, architecture dependency canvas), charts (candlestick 120 FPS, orderflow DOM ladder, liquidity-zone overlay, indicator docks); **9 widgets** (metric card, status badge, precision pill, currency PnL label, **toggle switch**, slider-spinbox, alert banner, search bar); **4 dialogs** (auth, emergency halt, config diff, broker reconnect); pytest-qt test suite.
- **QSS theming**: `main.qss` + themes `institutional_dark` (#0D1117/#161B22/#30363D), `bloomberg_terminal`, `cyber_matrix`, `high_contrast`, + widget partials (buttons/inputs/tables/cards/tabs/status_pills/charts/dialogs); SVG icon set (logo + trade/engine/fusion/scenario/ledger icons); JetBrains Mono + Inter fonts.

---

## PART 4 — CROSS-LAYER DEPENDENCIES & INTEGRATION

### 4.1 The layer law (how sub-micro gates bubble up)
- Dependency direction is strictly **downward-only**: layer Li may import Lj only for j<i. Enforced four ways: NetworkX `dependency_graph.py` (import-time), `technical_boundaries.py` + `execution_firewall.py` + `peer_dependency_guard.py` (structural), `scripts/architecture_audit.py` + `circular_dependency_check.py` (AST CI scan), `architecture_dependency_canvas.py` (runtime GUI proof) + `architecture_audit.yml` CI.
- **Bubble-up chain example (tick→UI):** an untracked parameter raises `UntrackedParameterError` at L2 → halts the lifecycle → health matrix dot turns red (L1 mission_control) → WebSocket telemetry → GUI `event_signals` → alert banner + status pill; a risk hard-veto at L11 surfaces as VETOED badge + CRITICAL alert (L13) + API response on `trade_execution` router + journal entry; terminal scenario states force WAIT → NO_ROUTE → empty `active_signals_feed`; broker disconnect → `broker_health` red → telemetry bar + `broker_reconnect_dialog`.
- **The L10 firewall is the only sync handoff** from technical to operational layers; everything else crosses via the canonical **event bus** (async pub/sub) and **command bus** (authorized commands).

### 4.2 Sync vs async, transport, serialization
- **Async core**: asyncio throughout; qasync/QtAsyncio merges asyncio into the Qt loop in the GUI; GUI→core commands via `command_dispatcher` → command bus → use cases.
- **Transports**: in-process buses (event/command), WebSockets (API telemetry + alert channel + broker WS adapter), IPC UNIX domain sockets / named pipes (GUI↔core `ipc_client`), **shared memory** (sub-5 ms rescan + `ipc_telemetry_stream`), HTTP (FastAPI/REST adapters, aiohttp/httpx), broker protocols (MT5/MT4/cTrader/FIX/WebSocket/REST) isolated in `execution-bridge` service.
- **Serialization**: ORJSON (API), msgpack (low-latency binary), Pydantic v2 validation at every boundary, Parquet/JSONL for ledger export, YAML for config, PyArrow for columnar data, RocksDB/Redis/Postgres/SQLite in storage & compose topology.

---

## PART 5 — CODE-READY ANNOTATIONS

### 5.1 Numeric / policy constants extracted from the document
| Constant | Value | Where enforced |
|---|---|---|
| Three-core confluence weights | PA **40%** / Candle-CDT **35%** / Indicators **25%** | `core/three_core_confluence_gatekeeper.py`, `validation/three_core/`, `config/confluence_weights.yaml` |
| Session risk cap | **1.50%** | `risk/risk_boundary_quantizer.py`, control panel risk form, `config/risk/` |
| Breakeven trigger | **+1.5 ATR** | `position_management/breakeven.py`, GUI single-trade "break-even lock" |
| Trailing stop trigger | **+2.0R** | `position_management/trailing.py`, tp_sl_trailing form |
| Partial close ladder | **25% / 50% / 75%** | GUI single-trade controller, `partial_profits.py` |
| Global hold-time policy | `max_hold_time = null` (no time expiry) | `core/no_time_expiry_policy.py`, `config/boot_state.yaml` |
| OTE / Golden zone | **61.8%–78.6%** | fibonacci `ote.py`/`golden_zone.py`, strategy S18 |
| Harmonic ratios | Gartley **0.786**, Bat **0.886**, Butterfly **1.272**, Crab **1.618**, Cypher **0.786** | `harmonics/*`, S29–S33 |
| Precision grades | **Tier 1–4** | `precision/grade_mapper.py`, schema `precision_grade.py`, GUI pill |
| Scenario pool | **S1–S31** (28 families + 3 terminal: UNKNOWN/CONFLICTED/NOVEL) | `scenario_pool/`, schema `scenario_state.py` |
| Strategy vault | **52 strategies / 8 families** | `strategies/`, `config/strategies/` |
| Peer engines | **4** (A scalp 15M–30M, B intraday 1H–4H, C swing 4H–8H, D macro 8H–D) | `engines/`, `config/engines/` |
| Session epochs | **6 phases** (Asia/London/NY/overlaps/10 AM Club) | `core/session_epoch_manager.py`, `config/sessions.yaml` |
| Fusion brain | "9-layer" MN1→M1 (enumerates MN1,W1,D1,H8,H4,H1,M30,M15,M5,M1) | `fusion/nine_layer_fusion_brain.py` |
| Latency budgets | fusion **< 500 µs**; rescan **< 5 ms**; GUI trade dispatch **< 1 ms**; charts **120 FPS**; refresh **60/120 Hz** | `tests/performance/`, `apps/.../config.py` |
| Backtest | **31-year** multi-asset walk-forward matrix | `scripts/run_matrix_backtest.py`, CI `quant-backtest-matrix.yml`, `monitoring_learning/walk_forward_runner.py` |
| Runtime | **Python 3.12+**, PySide6 ≥ 6.7.2, Pydantic v2, ORJSON | `.python-version`, `pyproject.toml` |

### 5.2 Input/Output schema surface (to be generated 1:1)
28 contract modules + 26 Pydantic schemas (listed in §3.1) define every I/O: inbound feeds (tick/candle/orderbook/trade_flow/chat/news), lifecycle states, decision artifacts (route_decision, engine_decision, signal_ticket, order_intent, multi_trade_intent, cross_pair_pnl_state, position_state, alert_event, rescan_event). Validation constraints: schema + timestamp + sequence + duplicate + gap + stale + outlier checks at ingestion; cross-field and range validation at configuration; exact-decimal arithmetic for price/lot.

### 5.3 Complexity & latency targets
- Fusion: < 500 µs (performance test `test_fusion_calculation_latency.py`).
- Rescan cycle (unbind/reset/rescan): < 5 ms (`test_rescan_benchmark.py`).
- GUI trade dispatch: < 1 ms (`test_trade_panel_dispatch_latency.py`).
- Cross-pair PnL aggregation: sub-millisecond (`cross_pair_pnl_calculator.py`).
- Charts: 120 FPS hardware-accelerated pyqtgraph; GUI refresh 60/120 Hz.
- Determinism: identical inputs → identical decisions (property test `test_decision_determinism.py`); hash-chain continuity under mutation (`test_hash_chain_integrity.py`); decimal price/lot invariants (`test_price_invariants.py`).

### 5.4 Error-handling protocols & edge cases
- 19-class taxonomy (§3.1); boundary violations, boot failures (controlled halt + forensic dump), license revocation, risk veto (hard, non-mutating), terminal states → WAIT/NO_ROUTE/ABSTAIN, untracked parameter → halt, data gaps/duplicates/stale/outliers, broker reconciliation mismatches, alert flooding (rate limiter + dedup), emergency halt (multi-confirmation dialog + book quarantine + panic flatten), single-instance lock, clock skew (UTC validator).

### 5.5 Pinned runtime dependencies (verbatim from §E of the document)
```
PySide6>=6.7.2, pyqtgraph>=0.13.7, qasync>=0.27.1, superqt>=0.6.7
numpy>=2.0.0, scipy>=1.14.0, pandas>=2.2.2, polars>=1.5.0, numba>=0.60.0, networkx>=3.3
scikit-learn>=1.5.1, statsmodels>=0.14.2, arch>=7.0.0, PyWavelets>=1.6.0, hmmlearn>=0.3.2, giotto-tda>=0.6.0
aiohttp>=3.10.0, websockets>=12.0, httpx>=0.27.0, fastapi>=0.112.0, uvicorn[standard]>=0.30.5
pydantic>=2.8.2, pydantic-settings>=2.4.0, orjson>=3.10.7, msgpack>=1.0.8, pyarrow>=17.0.0
cryptography>=43.0.0, blake3>=0.4.1
rocksdict>=0.3.28, aiosqlite>=0.20.0, redis>=5.0.8
MetaTrader5>=5.0.45 (win32 only), quickfix>=1.15.1
pyyaml>=6.0.2, rich>=13.7.1, loguru>=0.7.2, psutil>=6.0.0
```

---

## PART 6 — SPEC AMBIGUITIES & DECISIONS TO LOCK BEFORE CODING (architect's notes)

1. **"Web version first" vs the pure-Python purge.** The meta-prompt (Milestone A) demands a running web app with a "responsive web frontend" before the desktop app, but the remediation log deletes the entire TS/Next.js web stack. Resolution to implement: **Milestone A = the L14 FastAPI ASGI backend + WebSocket telemetry + trade-execution routers fully running** (serving a minimal static operator page if needed), **Milestone B = the PySide6 Mission Control desktop app**. No TS/Node code will be reintroduced.
2. **"9-layer fusion" vs 10 enumerated timeframes.** The brain is called 9-layer but lists MN1, W1, D1, H8, H4, H1, M30, M15, M5, M1 (10 TFs). I will implement the 9 coordination layers over that TF stack and pin the exact layer↔TF binding in `fusion/fusion_contract.py` + `config/fusion/`.
3. **Light/Dark toggle vs dark-only theme list.** The meta-prompt mandates a Light Mode ↔ Dark Mode toggle; the QSS spec ships four dark-variant themes. I will add an institutional **light** theme (`theme_institutional_light.qss`) alongside `theme_institutional_dark.qss` and drive both from `qss_manager.py` + the `toggle_switch` widget.
4. **"31 scenarios, 13 families" vs 28 family files.** The tree lists 28 concrete scenario-family classes + 3 terminal states (= 31 states S1–S31); "13 families" matches the config-level grouping in `config/scenarios/universal_scenario_pool.yaml` (Directional/Compression/Range/Reversal groups). Implementation: 31 scenario states backed by 28 detectors + 3 terminal handlers.
5. **`asyncio>=3.4.3` in requirements** is a stdlib placeholder — will be dropped from the pinned file (stdlib needs no pin); MetaTrader5 stays win32-only, with the FIX/REST/WebSocket adapters as the cross-platform execution path.
6. **Repo root naming**: the blueprint root is `DAVID_SLING_IATOS/`; this checkout is `DAVID-SLING`. I will map the tree 1:1 onto the repo root (`src/david_sling/`, `apps/mission_control_gui/`, `services/`, `config/`, `deploy/`, `tests/`, `scripts/`, `data/`, `storage/`, root governance files) without renaming the repository.

---

## PART 7 — STANDING BY

Comprehension phase complete. I have internalized: the 15-layer unidirectional architecture and its enforcement machinery; the 8-stage zero-silent-drop parameter lifecycle; the 31-scenario pool with terminal abstention states; the 9-layer bidirectional fusion brain; the 3-core 40/35/25 confluence gate; the 52-strategy / 8-family vault mapped onto 4 zero-coupling peer engines; the L10 execution firewall into L11 risk/sizing/portfolio (1.50% session cap, broker min-lot authority, +1.5 ATR breakeven, +2.0R trailing, 25/50/75% partials) and L12 broker/order/position TMS; the L13 evidence ledger (hash-chained), alerts, journal, and non-mutating learning; the L14 FastAPI + WebSocket web layer and the PySide6/QSS Mission Control GUI with the Omni-Trade Execution panel and Light/Dark toggle; plus all latency budgets, the pinned dependency set, and the six spec decisions above.

**No implementation code has been written.** Ready to receive incremental code-generation commands — recommended build order: (1) root governance + `core/` kernel (laws, manifest, contracts, schemas, errors, utilities), (2) `parameter/` + `evidence_ledger/` + `data/`, (3) perception L3, (4) L4–L6, (5) L7–L9, (6) L10–L12, (7) L13 + L14 API (Milestone A web), (8) `apps/mission_control_gui/` (Milestone B desktop), (9) `services/`, `config/`, `deploy/`, tests, scripts — with `architecture_audit.py` + pytest/mypy/ruff gates after each layer.
