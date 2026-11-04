"""AppTest: Hauptansicht, Experimente 1 bis 5, Spielwiese, Permalink und PDF (DEMO-PLAYBOOK §3, §5)."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import msk_constants as C
import msk_evaluation as ev
from msk_pdf_export import build_pdf

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))
PLAY = "gross_12_8_geometrisch_wald_3_zufall_7"


def _app(params=None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (params or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [m.value for m in list(at.success) + list(at.info) + list(at.warning) + list(at.error)]


def _click_preset(at, name):
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]


def test_default_shows_the_metrics_and_the_verdicts():
    at = _app()
    assert [m.value for m in at.metric][:4] == ["4 827 444", "2 710 518", "1 864 749", "1 037 873"]
    texts = _texts(at)
    assert any(t.startswith("Offline (alle **66** Angebote vorher bekannt, Greedy) ergibt **4 827 444**") for t in texts)
    assert any(t.startswith("Angebot 1 von 66: Leitung **A–L**") for t in texts)


def test_main_verdict_matches_each_preset():
    expected = {
        "Standardfall (Voreinstellung)": "Wachsende Stichprobe (f = 0,37, 24 nur angesehen): **2 710 518** (56,1 %)",
        "Gutartige Gewichte": "erst kommt, erst bekommt: **340** (84,0 %). Am besten ist hier: **Erst kommt, erst bekommt**.",
        "Absteigende Reihenfolge": "Die Stichprobenregeln nehmen nichts an",
        "Farben": "Klassische 1/e-Regel je Farbe: **350** (63,5 %)",
        "Freie Wahl": "erst kommt, erst bekommt: **578** (100,0 %)",
    }
    at = _app()
    for name, needle in expected.items():
        _click_preset(at, name)
        assert any(needle in t for t in _texts(at)), name


def test_stichprobe_slider_rule_radio_and_optimum_toggle():
    at = _app()
    at.select_slider(key="f_slider").set_value(0.5).run()
    assert not at.exception and any("Wachsende Stichprobe (f = 0,50, 33 nur angesehen)" in t for t in _texts(at))
    for rule in ("erst", "fest", "wachs"):
        at.radio(key="trace_rule").set_value(rule).run()
        assert not at.exception, rule
    at.toggle(key="show_opt").set_value(True).run()
    assert not at.exception


def test_farben_offers_the_classical_rule_in_the_radio():
    at = _app()
    _click_preset(at, "Farben")
    assert list(at.radio(key="trace_rule").options) == ["Erst kommt, erst bekommt", "Feste Stichprobe", "Wachsende Stichprobe", "Klassische 1/e-Regel je Farbe"]
    at.radio(key="trace_rule").set_value("teil").run()
    assert not at.exception and len(at.metric) == 5


def test_on_demand_series_appear_and_stay():
    at = _app()
    assert not any("Das beste f der wachsenden Stichprobe" in t or "beste f der wachsenden" in t for t in _texts(at))
    at.button(key="ex1_run").click().run()
    assert not at.exception and any(t.startswith("Bei k = 1 / 3 / 10 / 20 liegt das beste f der wachsenden Stichprobe") for t in _texts(at))
    at.button(key="ex2_run").click().run()
    assert not at.exception and any(t.startswith("Bei gleichverteilten Nutzen: Kardinalität erst") for t in _texts(at))
    at.button(key="ex3_run").click().run()
    assert not at.exception and any("**Absteigend** (wertvolle zuerst) nehmen beide Stichprobenregeln **nichts** an" in t for t in _texts(at))
    at.button(key="ex4_run").click().run()
    assert not at.exception and any(t.startswith("Bei verdoppelnden Nutzen und Rang 4 / 7 / 11 / 15") for t in _texts(at))
    at.button(key="ex5_run").click().run()
    assert not at.exception and any(t.startswith("Beim **freien Matroid**") for t in _texts(at))
    _click_preset(at, "Farben")
    assert any(t.startswith("Beim **freien Matroid**") for t in _texts(at))                      # die Ergebnisse bleiben nach anderen Änderungen


def test_playground_accept_reject_reset_and_the_end():
    at = _app()
    at.button(key="play_accept").click().run()
    assert not at.exception and any(t.startswith("Angebot 2 von 66") and "Bisher angenommen: 1 Leitung" in t for t in _texts(at))
    at.button(key="play_reject").click().run()
    assert not at.exception and any(t.startswith("Angebot 3 von 66") for t in _texts(at))
    assert len(at.session_state[f"play_dec_{PLAY}"]) == 2
    at.button(key="play_reset").click().run()
    assert not at.exception and at.session_state[f"play_dec_{PLAY}"] == [] and any(t.startswith("Angebot 1 von 66") for t in _texts(at))


def test_playground_runs_to_the_end_with_a_comparison():
    at = _app()
    _click_preset(at, "Freie Wahl")
    for _ in range(14):
        at.button(key="play_accept").click().run()
        assert not at.exception
    assert any(t.startswith("Fertig: Sie haben **578** (100,0 % des Offline-Optimums **578**)") for t in _texts(at))
    assert at.button(key="play_accept").disabled and at.button(key="play_reject").disabled


def test_every_instance_constraint_order_and_size_runs_without_exception_and_has_a_verdict():
    at = _app()
    for inst in C.INSTANCES:
        for cons in C.CONSTRAINTS:
            for okind in C.ORDERS:
                at.sidebar.selectbox(key="inst_select").set_value(inst).run()
                at.sidebar.selectbox(key="cons_select").set_value(cons).run()
                at.sidebar.selectbox(key="okind_select").set_value(okind).run()
                assert not at.exception, (inst, cons, okind, [str(e) for e in at.exception])
                assert any(t.startswith("Offline (alle **") for t in _texts(at)), (inst, cons, okind)
    for v in (C.V_MIN, C.V_MAX):
        at.sidebar.selectbox(key="inst_select").set_value("gross").run()
        at.sidebar.slider(key="v_slider").set_value(v).run()
        assert not at.exception, v


def test_every_weight_distribution_runs():
    at = _app()
    for w in C.WEIGHTS:
        at.sidebar.selectbox(key="wdist_select").set_value(w).run()
        assert not at.exception, w
        assert any(t.startswith("Offline (alle **") for t in _texts(at)), w


def test_permalink_loads_valid_values_and_ignores_invalid_choices():
    at = _app(dict(inst="plan", v="9", seed="3", wdist="pareto", cons="farbe", k="4", oseed="5", okind="aufsteigend"))
    sb = at.sidebar
    assert sb.selectbox(key="inst_select").value == "plan" and sb.slider(key="v_slider").value == 9 and sb.number_input(key="seed_input").value == 3
    assert sb.selectbox(key="wdist_select").value == "pareto" and sb.selectbox(key="cons_select").value == "farbe" and sb.slider(key="k_slider").value == 4
    assert sb.number_input(key="oseed_input").value == 5 and sb.selectbox(key="okind_select").value == "aufsteigend"
    bad = _app(dict(inst="nichts", v="99", seed="-4", wdist="nichts", cons="nichts", k="99", oseed="-1", okind="nichts"))
    b = bad.sidebar
    assert b.selectbox(key="inst_select").value == "gross" and b.slider(key="v_slider").value == C.V_MAX and b.number_input(key="seed_input").value == 0
    assert b.selectbox(key="wdist_select").value == "geometrisch" and b.selectbox(key="cons_select").value == "wald" and b.slider(key="k_slider").value == C.K_MAX
    assert b.number_input(key="oseed_input").value == 0 and b.selectbox(key="okind_select").value == "zufall"


def test_address_line_mirrors_the_settings():
    at = _app(dict(cons="farbe"))
    assert str(at.query_params["cons"]) in ("farbe", "['farbe']")


def test_pdf_button_makes_a_download():
    at = _app()
    at.button(key="pdf_make").click().run()
    assert not at.exception and "pdf_made" in at.session_state and at.session_state["pdf_made"][2][:4] == b"%PDF"


def test_pdf_builds_for_every_instance_and_constraint():
    for inst in C.INSTANCES:
        for cons in C.CONSTRAINTS:
            assert build_pdf(ev.Settings(inst, 8, 2, "gleich", cons, 3, 1, "zufall"), 0.37)[:4] == b"%PDF", (inst, cons)
