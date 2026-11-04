"""Matroid-Sekretärproblem - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 13 der Reihe „Matroide und Submodularität“ (Bereich Kombinatorik). Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import msk_algorithm as A
import msk_constants as C
from msk_evaluation import (
    Settings,
    anteil,
    de,
    ex1_series,
    ex1_table,
    ex2_series,
    ex2_table,
    ex3_series,
    ex3_table,
    ex4_series,
    ex4_table,
    ex5_series,
    ex5_table,
    leitungen,
    play_state,
    prozent,
    rule_rows,
    run_view,
    trace_rows,
    verdict_ex1,
    verdict_ex2,
    verdict_ex3,
    verdict_ex4,
    verdict_ex5,
    verdict_play,
    verdict_run,
    zahl,
)
from msk_layout import dunkles_design, kopf_css
from msk_pdf_export import build_pdf
from msk_presets import bounds, init_session_state_defaults, load_permalink_settings, randomize_oseed, randomize_seed, sidebar_presets, sync_query_params
from msk_visualization import build_arrivals, build_f_curves, build_grouped_bars, build_map, build_rule_bars

st.set_page_config(page_title="Matroid-Sekretärproblem – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Regeln auf dem Plan rechnen …")
def _run(settings, f):
    return run_view(settings, f)


@st.cache_data(show_spinner="Experiment 1 rechnen (einige Sekunden) …")
def _ex1():
    return ex1_series()


@st.cache_data(show_spinner="Experiment 2 rechnen (einige Sekunden) …")
def _ex2():
    return ex2_series()


@st.cache_data(show_spinner="Experiment 3 rechnen …")
def _ex3():
    return ex3_series()


@st.cache_data(show_spinner="Experiment 4 rechnen (einige Sekunden) …")
def _ex4():
    return ex4_series()


@st.cache_data(show_spinner="Experiment 5 rechnen …")
def _ex5():
    return ex5_series()


def _decide(key, accept):
    st.session_state[key].append(accept)


def _reset(key):
    st.session_state[key] = []


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in msk_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📬 Matroid-Sekretärproblem – Angebote nacheinander")
st.markdown(
    """
In den Stücken davor lagen alle Leitungsangebote **vorher** auf dem Tisch. Hier kommen sie **nacheinander** in zufälliger Reihenfolge, jedes ist **sofort anzunehmen oder zu verwerfen, endgültig**, und das Angenommene muss unabhängig bleiben (höchstens k Leitungen, höchstens eine je Farbe, keine geschlossenen Ringe). Die Frage: **Wie viel vom Offline-Optimum bleibt?** Drei Regeln auf **derselben Reihenfolge**: **erst kommt, erst bekommt**; die **feste Stichprobe** (die ersten Angebote nur ansehen, danach annehmen, was nicht von schwereren Beobachteten aufgespannt wird); die **wachsende Stichprobe** (wie die feste, aber alles bisher Gesehene zählt als Beobachtung; bei Kardinalität 1 ist das die klassische 1/e-Regel).

Dies ist das **dreizehnte Stück** der Reihe „Matroide und Submodularität“ (ein gelbes Stück). Weiter unten: fünf Experimente (🔬), eine **Spielwiese „Sie sind der Planer“**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Das klassische Sekretärproblem mit **einem** Zuschlag zeigt die Online-Algorithmen-Reihe; hier geht es um mehrere Zuschläge unter einer Matroidschranke.
"""
)

with st.expander("So hängt es zusammen", expanded=True):
    st.markdown(
        """
1. **Offline-Optimum:** Wer alle Angebote kennt, nimmt sie nach absteigendem Nutzen und lässt weg, was die Unabhängigkeit verletzt (Greedy, Stück 1 und 5). Das ist der Maßstab.
2. **Erst kommt, erst bekommt:** Annehmen, was unabhängig bleibt. Braucht keine Beobachtung, belegt aber Plätze mit dem Ersten, was kommt.
3. **Aufgespannt:** Ein Angebot e wird von einer Menge A **aufgespannt**, wenn A + e nicht mehr Rang hat als A: bei Kardinalität, wenn A schon k Elemente hat; bei Farben, wenn A schon eine Leitung dieser Farbe hat; im Wald, wenn e einen Ring mit A schlösse. Ein Angebot, das von **schwereren** Beobachteten aufgespannt wird, wäre im Offline-Greedy nicht dabei.
4. **Feste Stichprobe:** Die ersten ⌊f · n⌋ Angebote nur ansehen; danach e annehmen, wenn die schwereren Elemente der **Stichprobe** e nicht aufspannen und e mit dem Angenommenen unabhängig bleibt.
5. **Wachsende Stichprobe:** Wie die feste, aber jedes gesehene Angebot (auch nach der Stichprobe) zählt als Beobachtung. Bei Kardinalität 1 ist das die klassische Regel: das erste Angebot nach der Stichprobe annehmen, das alle bisher gesehenen übertrifft.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Instanz**")
    inst = st.selectbox("Instanz", C.INSTANCES, key="inst_select", format_func=C.INSTANCE_NAMES.get,
                        help="Der Plan der Reihe hat 8 Standorte und 14 Leitungen; der große Plan hat alle Leitungen zwischen den Standorten (bis 16 Standorte, 120 Leitungen).")
    v = st.slider("Standorte des großen Plans", *bounds("v_slider"), key="v_slider", help="Wie viele Standorte der große Plan hat; jede Leitung zwischen zwei Standorten ist ein Angebot (Rang: Standorte − 1). Beim Plan der Reihe ohne Wirkung.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Bestimmt Standorte, Leitungen und Nutzen.")
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    wdist = st.selectbox("Nutzen der Leitungen", C.WEIGHTS, key="wdist_select", format_func=C.WEIGHT_NAMES.get,
                         help="Wie ungleich die Angebote sind. Bei gleichen Nutzen gibt es nichts Schwereres, das aufspannt; je schiefer, desto mehr hilft das Beobachten.")
    st.markdown("**Nebenbedingung**")
    cons = st.selectbox("Was darf zusammen angenommen werden?", C.CONSTRAINTS, key="cons_select", format_func=C.CONSTRAINT_NAMES.get,
                        help="Kardinalität: höchstens k Leitungen. Farben: höchstens eine Leitung je Kabelfarbe (Partitionsmatroid). Wald: keine geschlossenen Ringe (graphisches Matroid).")
    k = st.slider("Zahl k", *bounds("k_slider"), key="k_slider", help="Kardinalität: höchstens k Leitungen; Farben: Zahl der Kabelfarben (Leitung e hat die Farbe e mod k). Beim Wald ohne Wirkung.")
    st.markdown("**Reihenfolge der Ankunft**")
    okind = st.selectbox("Wie kommen die Angebote?", C.ORDERS, key="okind_select", format_func=C.ORDER_NAMES.get,
                         help="Zufällig ist die Annahme des Sekretärproblems. Absteigend und aufsteigend sind gegnerische Reihenfolgen nach Nutzen.")
    oseed = st.number_input("Seed der Reihenfolge", *bounds("oseed_input"), key="oseed_input", step=1, disabled=okind != "zufall")
    st.button("🎲 Neue Reihenfolge", width="stretch", on_click=randomize_oseed, disabled=okind != "zufall")

sync_query_params({"inst_select": inst, "v_slider": int(v), "seed_input": int(seed), "wdist_select": wdist, "cons_select": cons, "k_slider": int(k), "oseed_input": int(oseed), "okind_select": okind})

settings = Settings(inst, int(v), int(seed), wdist, cons, int(k), int(oseed), okind)
play_id = f"{inst}_{settings.v}_{settings.seed}_{wdist}_{cons}_{settings.k}_{okind}_{settings.oseed}"

# --- Ein Lauf -------------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ein Lauf: drei Regeln, eine Reihenfolge")
f = st.select_slider("Stichprobenanteil f", options=list(C.F_CHOICES), value=C.DEFAULT_F, key="f_slider",
                     help="Welcher Anteil der Angebote nur angesehen wird. 0,37 ist ungefähr 1/e; bei höheren k ist ein kleineres f oft besser (Experiment 1).")
rv = _run(settings, float(f))
ins = rv["b"]["inst"]
st.caption(f"{C.INSTANCE_NAMES[inst]}: {zahl(rv['m'])} Angebote, Rang {rv['rank']}. Zulässig: {C.CONSTRAINT_NAMES[cons]}" + (f", k = {settings.k}" if cons != "wald" else "") + f". Reihenfolge: {C.ORDER_NAMES[okind].split(' (')[0]}.")
mc = st.columns(4 if "teil" not in rv["runs"] else 5)
mc[0].metric("Offline-Optimum", zahl(rv["opt"]), help="Wert, wenn alle Angebote vorher bekannt wären (Greedy).")
mc[1].metric("Wachsende Stichprobe", zahl(rv["runs"]["wachs"]["value"]), delta=f"{prozent(rv['runs']['wachs']['value'] / rv['opt'])} % des Optimums", delta_color="off")
mc[2].metric("Feste Stichprobe", zahl(rv["runs"]["fest"]["value"]), delta=f"{prozent(rv['runs']['fest']['value'] / rv['opt'])} % des Optimums", delta_color="off")
mc[3].metric("Erst kommt, erst bekommt", zahl(rv["runs"]["erst"]["value"]), delta=f"{prozent(rv['runs']['erst']['value'] / rv['opt'])} % des Optimums", delta_color="off")
if "teil" in rv["runs"]:
    mc[4].metric("1/e-Regel je Farbe", zahl(rv["runs"]["teil"]["value"]), delta=f"{prozent(rv['runs']['teil']['value'] / rv['opt'])} % des Optimums", delta_color="off")
rule_show = st.radio("Regel für Karte und Ankunftstabelle", list(rv["runs"]), index=2, key="trace_rule", format_func=C.RULE_NAMES.get, horizontal=True,
                     help="Welche Regel die Karte (angenommene Leitungen) und die Tabelle der Ankunft zeigen.")
show_opt = st.toggle("Offline-Optimum einblenden", value=False, key="show_opt", help="Legt das Offline-Optimum orange unter die Karte.")
col_a, col_b = st.columns([3, 2])
with col_a:
    st.plotly_chart(build_map(ins, rv["runs"][rule_show]["chosen"], rv["opt_chosen"] if show_opt else (), label_weights=ins.m <= 20), width="stretch", key="map_run")
    st.caption("Dünn grau: mögliche Leitungen (bei dem kleinen Plan mit Nutzen beschriftet); dick blaugrün: angenommen; orange unterlegt: Offline-Optimum.")
with col_b:
    st.markdown("**Die Regeln**")
    st.dataframe(rule_rows(settings, rv), hide_index=True, width="stretch")
st.markdown("**Ankunft: was die gewählte Regel getan hat**")
st.plotly_chart(build_arrivals(rv["runs"][rule_show]["trace"]), width="stretch", key="arrival_chart")
st.dataframe(trace_rows(rv, rule_show), hide_index=True, width="stretch", height=260)

if st.button("📄 PDF des aktuellen Beispiels erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, float(f), build_pdf(settings, float(f)))
made = st.session_state.get("pdf_made")
if made and made[0] == settings and made[1] == float(f):
    st.download_button("⬇️ PDF herunterladen", data=made[2], file_name="matroid-sekretaer.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viel vom Offline-Optimum bleibt, wenn die Angebote nacheinander kommen?")
kind_v, text_v = verdict_run(settings, rv)
getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Wie lange zusehen?")
st.caption(f"Kardinalität k mit {C.EX1_N} gleichverteilten Angeboten, {C.EX1_INSTANCES} Instanzen × {C.EX1_ORDERS} zufällige Reihenfolgen je Zelle (Median über die Instanzen). Gestrichelt: erst kommt, erst bekommt.")
if st.button("📊 Stichprobenanteil gegen k messen", key="ex1_run"):
    st.session_state["ex1_done"] = True
if st.session_state.get("ex1_done"):
    r1 = _ex1()
    st.plotly_chart(build_f_curves(r1), width="stretch", key="ex1_chart")
    st.dataframe(ex1_table(r1), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex1(r1)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 2: Wie ungleich sind die Angebote?")
st.caption(f"Kardinalität 10 mit {C.EX2_CARD_N} Angeboten und Wald auf dem vollständigen Graphen mit {C.EX2_WALD_V} Standorten; sechs Verteilungen der Nutzen; {C.EX2_INSTANCES} Instanzen × {C.EX2_ORDERS} Reihenfolgen (Median).")
if st.button("📊 Verteilungen der Nutzen messen", key="ex2_run"):
    st.session_state["ex2_done"] = True
if st.session_state.get("ex2_done"):
    r2 = _ex2()
    card = [r for r in r2 if r["matroid"].startswith("Kard")]
    st.plotly_chart(build_grouped_bars([C.WEIGHT_NAMES[r["dist"]].split(" (")[0] for r in card], [("erst kommt", [r["erst"] for r in card], C.COLOR_ERST), ("feste Stichprobe", [r["fest"] for r in card], C.COLOR_FEST), ("wachsende Stichprobe", [r["wachs"] for r in card], C.COLOR_WACHS)],
                                       "Nutzen der Angebote (Kardinalität 10)", "Anteil am Offline-Optimum"), width="stretch", key="ex2_chart")
    st.dataframe(ex2_table(r2), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex2(r2)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 3: Die Reihenfolge ist die Annahme")
st.caption("Gleichverteilte Nutzen; zufällige Reihenfolge gegen aufsteigende und absteigende nach Nutzen (eine Reihenfolge je Instanz, Median).")
if st.button("📊 Reihenfolgen vergleichen", key="ex3_run"):
    st.session_state["ex3_done"] = True
if st.session_state.get("ex3_done"):
    r3 = _ex3()
    cats = [f"{r['matroid'].split(' (')[0]}, {C.ORDER_NAMES[r['okind']].split(' (')[0]}" for r in r3]
    st.plotly_chart(build_grouped_bars(cats, [("erst kommt", [r["erst"] for r in r3], C.COLOR_ERST), ("feste Stichprobe", [r["fest"] for r in r3], C.COLOR_FEST), ("wachsende Stichprobe", [r["wachs"] for r in r3], C.COLOR_WACHS)], "Nebenbedingung und Reihenfolge", "Anteil am Offline-Optimum"),
                    width="stretch", key="ex3_chart")
    st.dataframe(ex3_table(r3), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex3(r3)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 4: Fällt der Anteil mit dem Rang?")
st.caption("Wald auf dem vollständigen Graphen mit 5, 8, 12 und 16 Standorten (Rang 4, 7, 11, 15); gleichverteilte gegen verdoppelnde Nutzen; Median über Instanzen und Reihenfolgen.")
if st.button("📊 Anteil gegen Rang messen", key="ex4_run"):
    st.session_state["ex4_done"] = True
if st.session_state.get("ex4_done"):
    r4 = _ex4()
    st.dataframe(ex4_table(r4), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex4(r4)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 5: Was die Stichprobe kostet, und die Spezialregel")
st.caption(f"{C.EX5_N} gleichverteilte Angebote; das freie Matroid (alles darf mit), viele kleine Farbklassen und 6 Farben mit der klassischen 1/e-Regel je Farbe; {C.EX5_INSTANCES} Instanzen × {C.EX5_ORDERS} Reihenfolgen (Median).")
if st.button("📊 Kosten der Stichprobe messen", key="ex5_run"):
    st.session_state["ex5_done"] = True
if st.session_state.get("ex5_done"):
    r5 = _ex5()
    st.dataframe(ex5_table(r5), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex5(r5)
    getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------------

st.subheader("🛠️ Spielwiese: Sie sind der Planer")
st.caption("Die Angebote der obigen Instanz und Reihenfolge werden einzeln aufgedeckt. Sie entscheiden sofort und endgültig; die App zeigt, was die wachsende Stichprobe an derselben Stelle getan hat, und am Ende den Vergleich.")
play_key = f"play_dec_{play_id}"
if play_key not in st.session_state:
    st.session_state[play_key] = []
pstate = play_state(settings, st.session_state[play_key])
pc1, pc2, pc3 = st.columns(3)
pc1.button("✅ Annehmen", key="play_accept", width="stretch", disabled=pstate["done"] or not pstate["can_accept"], on_click=_decide, args=(play_key, True))
pc2.button("❌ Verwerfen", key="play_reject", width="stretch", disabled=pstate["done"], on_click=_decide, args=(play_key, False))
pc3.button("↩️ Von vorn", key="play_reset", width="stretch", on_click=_reset, args=(play_key,))
kind_v, text_v = verdict_play(settings, pstate, rv)
getattr(st, kind_v)(text_v)
if st.session_state[play_key]:
    wtrace = rv["runs"]["wachs"]["trace"]
    st.dataframe([{"Nr.": i + 1, "Leitung": ins.label(rv["b"]["order"][i]), "Nutzen": zahl(rv["b"]["w"][rv["b"]["order"][i]]), "Ihre Entscheidung": "angenommen" if d else "verworfen",
                   "Wachsende Stichprobe": "angenommen" if wtrace[i][3] else "verworfen"} for i, d in enumerate(st.session_state[play_key])], hide_index=True, width="stretch", height=240)
st.plotly_chart(build_map(ins, pstate["chosen"], rv["opt_chosen"] if pstate["done"] else (), label_weights=ins.m <= 20), width="stretch", key="map_play")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist (wer setzt an) |
|---|---|
| **Zufällige Reihenfolge** | Kommen die wertvollsten Angebote zuerst, nehmen beide Stichprobenregeln nichts an; kommen sie zuletzt, bleibt von „erst kommt, erst bekommt“ fast nichts. Das Sekretärmodell setzt die Zufallsreihenfolge voraus. **(Stück 13, Experiment 3)** |
| **Alle Angebote sind unterscheidbar nach Nutzen** | Bei gleichen Nutzen gibt es nichts Schwereres, das aufspannt: Die Regeln nehmen an, was unabhängig bleibt. Die Demo setzt Gleichstände so (kein Satz). **(Stück 13)** |
| **Das Matroid ist bekannt, die Nutzen kommender Angebote nicht** | Das ist das Sekretärmodell. Kennt man die Verteilungen der Nutzen (Prophet-Modell), sind andere Regeln möglich. **(nicht in dieser Reihe)** |
| **Die Regeln sind Bezeichnungen dieser Demo** | „Feste“ und „wachsende Stichprobe“ sind hier benannt, keine zitierten Algorithmen; ob sie mit Verfahren der Literatur übereinstimmen, ist nicht geprüft. **(nicht geprüft)** |
| **Nur Kardinalität, Farben und Wald gemessen** | Laminare und Transversal-Matroide fehlen; für sie und für allgemeine Matroide sind in der Literatur nur schwächere oder keine konstanten Faktoren bekannt. Die Vermutung „konstanter Faktor für alle Matroide“ ist offen; diese kleinen Fälle beweisen dazu nichts. **(Literatur, nicht gemessen)** |
| **Nutzen aus Verteilungen, nicht von einem Gegner** | Die Zahlen gelten für die gezogenen Instanzen und Seeds, nicht für den schlechtesten Fall. **(nicht allgemein)** |
| **Streaming ist ein anderes Modell** | Dort darf die Reihenfolge beliebig sein, dafür ist der Speicher knapp (Stück 12). Hier ist die Reihenfolge zufällig und die Entscheidung sofort und endgültig, der Speicher egal. **(Stück 12)** |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein Matroid $M = (E, \mathcal I)$ mit Rangfunktion $r$, Nutzen $w : E \to \mathbb{R}_{>0}$ und eine Reihenfolge $e_1, \dots, e_n$ der Elemente (zufällig, gleichverteilt unter allen $n!$ Reihenfolgen). Das Verfahren sieht $e_t$ zur Zeit $t$ mit $w(e_t)$ und entscheidet sofort und endgültig; die angenommene Menge $I_t$ muss in $\mathcal I$ liegen.

**Offline-Optimum.** $\mathrm{OPT} = \max \{ w(I) : I \in \mathcal I \}$; Greedy nach absteigendem Nutzen erreicht es (Rado–Edmonds). Gemessen wird der **Anteil** $\mathbb{E}[w(\mathrm{ALG})] / \mathrm{OPT}$.

**Aufspannen.** $e \in \operatorname{span}(A) \iff r(A + e) = r(A)$. Bei Kardinalität $k$: $\lvert A \rvert \ge k$; bei Farben (Kapazität 1): $A$ enthält schon ein Element der Farbe von $e$; im Wald: die Endpunkte von $e$ sind in $A$ verbunden.

**Regeln.** Mit $O_t = \{e_1, \dots, e_{t-1}\}$ und $S = \{e_1, \dots, e_s\}$, $s = \lfloor f n \rfloor$:

- erst: nimm $e_t$, wenn $I_{t-1} + e_t \in \mathcal I$;
- fest: für $t > s$ nimm $e_t$, wenn $e_t \notin \operatorname{span}(\{x \in S : w(x) > w(e_t)\})$ und $I_{t-1} + e_t \in \mathcal I$;
- wachsend: für $t > s$ wie fest, aber mit $\{x \in O_t : w(x) > w(e_t)\}$ statt $S$.

**Klassischer Sonderfall.** Bei Kardinalität 1 und $s \ge 1$ nimmt die wachsende Regel das erste $e_t$ mit $t > s$, das alle bisherigen übertrifft; die Wahrscheinlichkeit, das **beste** Angebot zu wählen, ist $\frac{s}{n} \sum_{j=s+1}^{n} \frac{1}{j-1}$ (für $n \to \infty$ und $s \approx n/e$ gegen $1/e$).

**Literatur.** Das Matroid-Sekretärproblem: Die Vermutung „konstanter Faktor für alle Matroide“ ist offen; konstante Faktoren sind für Partitions-, uniforme, graphische und laminare Matroide bekannt, allgemein etwa $1/\log\log r$ mit dem Rang $r$; das Problem ist äquivalent zu Contention Resolution für allgemeine Verteilungen ([arXiv 2103.04205](https://arxiv.org/pdf/2103.04205), [arXiv 2111.04114](https://arxiv.org/pdf/2111.04114)). Quelle: Websuche, Auszüge, nicht gegen die Primärtexte geprüft; konkrete Faktoren und Autoren sind hier nicht genannt.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
