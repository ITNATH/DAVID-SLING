"""L14 application/desktop/qss - Qt Style Sheets block for the DAVID SLING desktop shell.

Mirrors the web command center's strict 11-color XDR palette:
c0 bg . c1 surface . c2 card . c3 text . c4 dim . c5 cyan(ok/buy)
c6 amber(warn) . c7 crimson(threat/sell) . c8 white . c9 hairline . c10 well
Dark is the default (XDR midnight); `stylesheet("light")` returns the mirrored
light theme. Pure QSS embedded in Python - zero external CSS.
"""
from __future__ import annotations

DARK = {
    "c0": "#000000", "c1": "#0A0A0C", "c2": "#12141B", "c3": "#E8EAF0", "c4": "#7A8090",
    "c5": "#00F0FF", "c6": "#FFB800", "c7": "#FF2D55", "c8": "#FFFFFF", "c9": "#1E222B", "c10": "#2A2F3A",
}
LIGHT = {
    "c0": "#FFFFFF", "c1": "#F4F6F8", "c2": "#FFFFFF", "c3": "#101828", "c4": "#667085",
    "c5": "#0E7490", "c6": "#B45309", "c7": "#E11D48", "c8": "#101828", "c9": "#E4E7EC", "c10": "#EEF1F4",
}


def stylesheet(theme: str = "dark") -> str:
    """Return the full QSS stylesheet for the given theme (dark | light)."""
    c = DARK if theme != "light" else LIGHT
    mono = "JetBrains Mono, Menlo, Consolas, monospace"
    sans = "-apple-system, 'SF Pro Display', 'Segoe UI', Inter, sans-serif"
    return f"""
* {{ font-family: {sans}; font-size: 12.5px; color: {c['c3']}; }}
QMainWindow, QDialog {{ background: {c['c0']}; }}
QWidget#topbar {{ background: {c['c1']}; border-bottom: 1px solid {c['c9']}; }}
QWidget#kpiStrip {{ background: {c['c2']}; border: 1px solid {c['c9']}; border-radius: 12px; }}
QFrame.card, QGroupBox.card {{ background: {c['c2']}; border: 1px solid {c['c9']}; border-radius: 12px; }}
QGroupBox.card {{ margin-top: 14px; }}
QGroupBox.card::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; color: {c['c4']};
  font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.6px; }}
QLabel.dim {{ color: {c['c4']}; }}
QLabel.mono, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QListWidget, QPlainTextEdit {{
  font-family: {mono}; }}
QLabel.brandName {{ font-family: {mono}; font-weight: 800; font-size: 16px; letter-spacing: 3px; }}
QLabel.brandSub {{ color: {c['c4']}; font-size: 10px; }}
QLabel.logo {{ color: {c['c5']}; font-size: 20px; }}
QLabel.kpiK {{ color: {c['c4']}; font-size: 9px; text-transform: uppercase; }}
QLabel.kpiV {{ font-family: {mono}; font-size: 17px; font-weight: 700; }}
QLabel.pos {{ color: {c['c5']}; }} QLabel.neg {{ color: {c['c7']}; }}
QLabel.bigBadge {{ font-family: {mono}; font-size: 18px; font-weight: 800; }}
QLabel.pill {{ background: {c['c2']}; border: 1px solid {c['c9']}; border-radius: 10px;
  padding: 3px 10px; font-family: {mono}; font-size: 10px; color: {c['c4']}; }}
QLabel.pillOk {{ color: {c['c5']}; border-color: {c['c5']}; }}
QLabel.pillWarn {{ color: {c['c6']}; border-color: {c['c6']}; }}
QLabel.pillCrit {{ color: {c['c7']}; border-color: {c['c7']}; }}
QLabel.prov {{ color: {c['c6']}; border: 1px solid {c['c6']}; border-radius: 4px; padding: 0 5px;
  font-family: {mono}; font-size: 8.5px; }}
QLabel.hcell {{ background: {c['c1']}; border: 1px solid {c['c9']}; border-radius: 6px;
  padding: 3px 7px; font-family: {mono}; font-size: 10px; }}
QPushButton {{ background: {c['c2']}; color: {c['c3']}; border: 1px solid {c['c9']};
  border-radius: 8px; padding: 7px 13px; }}
QPushButton:hover {{ border-color: {c['c5']}; }}
QPushButton:pressed {{ background: {c['c10']}; }}
QPushButton:focus {{ outline: 2px solid {c['c5']}; }}
QPushButton.btnBuy {{ background: {c['c5']}; color: {c['c0']}; font-weight: 700; border: none; }}
QPushButton.btnSell {{ background: {c['c7']}; color: {c['c8']}; font-weight: 700; border: none; }}
QPushButton.btnWarn {{ background: {c['c6']}; color: {c['c0']}; font-weight: 700; border: none; }}
QPushButton.btnDanger {{ background: {c['c7']}; color: {c['c8']}; font-weight: 800; border: none; }}
QPushButton.btnOk {{ background: {c['c5']}; color: {c['c0']}; font-weight: 700; border: none; }}
QPushButton.hold {{ }}
QPushButton:disabled {{ color: {c['c4']}; border-color: {c['c9']}; }}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{ background: {c['c10']}; border: 1px solid {c['c9']};
  border-radius: 6px; padding: 5px 8px; font-size: 12px; selection-background-color: {c['c5']}; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {c['c5']}; }}
QComboBox QAbstractItemView {{ background: {c['c2']}; border: 1px solid {c['c9']}; }}
QTabWidget::pane {{ border: 1px solid {c['c9']}; border-radius: 8px; background: {c['c2']}; }}
QTabBar::tab {{ background: {c['c1']}; color: {c['c4']}; border: 1px solid {c['c9']};
  border-radius: 6px; padding: 5px 11px; margin-right: 4px; font-family: {mono}; font-size: 10.5px; }}
QTabBar::tab:selected {{ color: {c['c3']}; border-color: {c['c5']}; font-weight: 700; }}
QTableWidget {{ background: {c['c1']}; border: 1px solid {c['c9']}; border-radius: 8px;
  gridline-color: {c['c9']}; font-size: 10.5px; }}
QTableWidget::item {{ padding: 3px 7px; }}
QHeaderView::section {{ background: {c['c2']}; color: {c['c4']}; border: none;
  border-bottom: 1px solid {c['c9']}; padding: 4px 7px; font-size: 9px; font-weight: 600; }}
QListWidget {{ background: {c['c1']}; border: 1px solid {c['c9']}; border-radius: 8px; font-size: 10.5px; }}
QListWidget::item {{ padding: 3px 6px; border-bottom: 1px solid {c['c9']}; }}
QListWidget::item.lv-WARNING {{ color: {c['c6']}; border-left: 2px solid {c['c6']}; }}
QListWidget::item.lv-CRITICAL, QListWidget::item.lv-ERROR {{ color: {c['c7']}; border-left: 2px solid {c['c7']}; }}
QListWidget::item.lv-INFO {{ border-left: 2px solid {c['c5']}; }}
QProgressBar {{ background: {c['c10']}; border: 1px solid {c['c9']}; border-radius: 4px; height: 8px; }}
QProgressBar::chunk {{ background: {c['c5']}; border-radius: 4px; }}
QCheckBox {{ spacing: 6px; }}
QCheckBox::indicator {{ width: 40px; height: 22px; border-radius: 11px; background: {c['c7']}; }}
QCheckBox::indicator:checked {{ background: {c['c5']}; }}
QCheckBox::indicator::handle {{ }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: {c['c10']}; border-radius: 4px; min-height: 20px; }}
QStatusBar {{ background: {c['c1']}; border-top: 1px solid {c['c9']}; color: {c['c4']};
  font-family: {mono}; font-size: 10.5px; }}
QSplitter::handle {{ background: {c['c0']}; }}
QToolTip {{ background: {c['c2']}; color: {c['c3']}; border: 1px solid {c['c9']}; font-family: {mono}; }}
QWidget#globe, QWidget#equity, QWidget#depth {{ background: {c['c1']}; border: 1px solid {c['c9']};
  border-radius: 8px; }}
"""
