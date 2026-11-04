"""PDF-Export des aktuellen Beispiels (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import msk_constants as C
from msk_evaluation import Settings, rule_rows, run_view, trace_rows, verdict_run

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "×": "x", "≈": "~", "½": "1/2"}


def _s(text) -> str:
    out = str(text).replace("**", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings, f: float = C.DEFAULT_F) -> bytes:
    v = run_view(s, f)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Matroid-Sekretärproblem"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    place = "Plan der Reihe (8 Standorte, 14 Leitungen)" if s.inst == "plan" else f"Vollständiger Graph mit {s.v} Standorten"
    pdf.multi_cell(0, 5, _s(f"{place}, Seed {s.seed}. Nutzen: {C.WEIGHT_NAMES[s.wdist]}. Zulässig: {C.CONSTRAINT_NAMES[s.cons]}" + (f", k = {s.k}" if s.cons != "wald" else "") + f". Reihenfolge: {C.ORDER_NAMES[s.okind]} (Seed {s.oseed}). Stichprobenanteil f = {f}."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, _s("Die Regeln"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for row in rule_rows(s, v):
        pdf.multi_cell(0, 5, _s(" | ".join(f"{k}: {val}" for k, val in row.items())), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_run(s, v)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, _s("Ankunft (wachsende Stichprobe, erste 25 Angebote)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    for row in trace_rows(v, "wachs")[:25]:
        pdf.multi_cell(0, 4, _s(" | ".join(str(x) for x in row.values())), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: matroid-sekretaer-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
