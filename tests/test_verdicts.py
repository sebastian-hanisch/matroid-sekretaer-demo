"""Verdikte (reine Funktionen in msk_evaluation.py) an festen Eingaben: jeder Zweig, jede Zahl im Text (DEMO-PLAYBOOK §4). Alles ist deterministisch (keine Löser)."""

import msk_constants as C
import msk_evaluation as ev

DEFAULT = ev.Settings()
FARBEN = ev.Settings(**C.PRESETS["Farben"])
ABSTEIGEND = ev.Settings(**C.PRESETS["Absteigende Reihenfolge"])
GUTARTIG = ev.Settings(**C.PRESETS["Gutartige Gewichte"])
PLAY = ev.Settings("plan", 8, 3, "gleich", "wald", 3, 1, "zufall")


def test_run_verdict_for_the_default_names_all_three_rules():
    kind, text = ev.verdict_run(DEFAULT, ev.run_view(DEFAULT))
    assert kind == "info" and text == (
        "Offline (alle **66** Angebote vorher bekannt, Greedy) ergibt **4 827 444** mit 11 Leitungen. Wachsende Stichprobe (f = 0,37, 24 nur angesehen): **2 710 518** (56,1 %); "
        "feste Stichprobe: **1 864 749** (38,6 %); erst kommt, erst bekommt: **1 037 873** (21,5 %). Am besten ist hier: **Wachsende Stichprobe**.")


def test_run_verdict_branches():
    kind, text = ev.verdict_run(FARBEN, ev.run_view(FARBEN))
    assert "Klassische 1/e-Regel je Farbe: **350** (63,5 %)." in text and text.endswith("Am besten ist hier: **Klassische 1/e-Regel je Farbe**.")
    kind, text = ev.verdict_run(ABSTEIGEND, ev.run_view(ABSTEIGEND))
    assert "**0** (0,0 %)" in text and "erst kommt, erst bekommt: **4 812 434** (100,0 %)" in text and text.endswith("alles Spätere wird davon aufgespannt.")
    kind, text = ev.verdict_run(GUTARTIG, ev.run_view(GUTARTIG))
    assert "Am besten ist hier: **Erst kommt, erst bekommt**." in text and "Stichprobenregeln nehmen nichts an" not in text
    v = ev.run_view(DEFAULT)
    assert ev.verdict_run(DEFAULT, {**v, "opt": 1})[0] == "error"


def test_ties_for_the_best_rule_are_named_together():
    s = ev.Settings(**C.PRESETS["Freie Wahl"])
    v = ev.run_view(s)
    kind, text = ev.verdict_run(s, {**v, "runs": {**v["runs"], "wachs": {**v["runs"]["erst"], "sample": 5}}})
    assert "Am besten ist hier: **Erst kommt, erst bekommt und Wachsende Stichprobe**." in text


def test_rule_rows_and_trace_rows():
    rows = ev.rule_rows(FARBEN, ev.run_view(FARBEN))
    assert [r["Regel"] for r in rows] == ["Offline-Optimum (alles vorher bekannt)", "Erst kommt, erst bekommt", "Feste Stichprobe", "Wachsende Stichprobe", "Klassische 1/e-Regel je Farbe"]
    assert rows[3] == {"Regel": "Wachsende Stichprobe", "Wert": 301, "Anteil am Optimum": "0,546", "angenommen": 4, "nur angesehen": "24"} and rows[1]["nur angesehen"] == "–"
    assert [r["Regel"] for r in ev.rule_rows(DEFAULT, ev.run_view(DEFAULT))][-1] == "Wachsende Stichprobe"
    v = ev.run_view(FARBEN)
    t = ev.trace_rows(v, "teil")
    assert t[0] == {"Nr.": 1, "Leitung": "A–L", "Nutzen": "9", "Entscheidung": "verworfen", "Grund": "Stichprobe: nur angesehen"} and len(t) == 66
    assert {r["Entscheidung"] for r in t} == {"angenommen", "verworfen"} and sum(1 for r in t if r["Entscheidung"] == "angenommen") == 4


def test_experiment_verdicts_on_handmade_rows():
    fests = {f: 0.5 for f in C.F_CHOICES}
    rows1 = [{"k": 1, "erst": 0.49, "fest": dict(fests), "wachs": {**fests, 0.1: 0.93, 0.7: 0.35}, "best_fest": 0.1, "best_wachs": 0.1},
             {"k": 10, "erst": 0.53, "fest": dict(fests), "wachs": {**fests, 0.3: 0.89, 0.7: 0.40}, "best_fest": 0.3, "best_wachs": 0.3}]
    kind, text = ev.verdict_ex1(rows1)
    assert kind == "info" and text.startswith("Bei k = 1 / 10 liegt das beste f der wachsenden Stichprobe bei **0,10 / 0,30** mit Anteil **0,930 / 0,890** am Offline-Optimum; erst kommt, erst bekommt erreicht **0,490 / 0,530**.") and "**0,350 bis 0,400**" in text
    assert ev.verdict_ex1([{**rows1[0], "wachs": {**fests, 0.1: 1.2}}])[0] == "error"
    assert ev.ex1_table(rows1)[1] == {"k": 1, "Regel": "Wachsende Stichprobe", "f = 0,10": "0,930", "f = 0,20": "0,500", "f = 0,30": "0,500", "f = 0,37": "0,500", "f = 0,50": "0,500", "f = 0,70": "0,350", "erst kommt": "0,490"}

    def row(matroid, dist, erst, fest, wachs):
        return {"matroid": matroid, "dist": dist, "erst": erst, "fest": fest, "wachs": wachs, "wachs_min": wachs - 0.1, "erst_min": erst - 0.1}
    rows2 = [row(m, d, e, f_, w) for m in ("Kardinalität 10 (100 Angebote)", "Wald (vollständiger Graph, 12 Standorte)") for d, e, f_, w in (("gleich", 0.5, 0.8, 0.85), ("geometrisch", 0.1, 0.5, 0.6), ("konstant", 1.0, 1.0, 1.0))]
    kind, text = ev.verdict_ex2(rows2)
    assert kind == "info" and "Bei gleichverteilten Nutzen: Kardinalität erst **0,500**, wachsend **0,850**; Wald erst **0,500**, wachsend **0,850**." in text and "Sind alle Nutzen gleich, ist alles optimal (**1,000**)" in text
    assert ev.verdict_ex2([row("Kardinalität", "gleich", 1.1, 0.2, 0.2)] + rows2)[0] == "error"
    assert ev.ex2_table(rows2)[1]["Nutzen"] == "verdoppelnd (1 bis 1 048 576)" and ev.ex2_table(rows2)[1]["Minimum (wachsend)"] == "0,500"


def test_order_rank_and_cost_verdicts():
    rows3 = [{"matroid": m, "okind": o, "erst": e, "fest": fe, "wachs": wa} for m in ("Kardinalität 10 (100 Angebote)", "Wald (12 Standorte)")
             for o, e, fe, wa in (("zufall", 0.55, 0.79, 0.85), ("aufsteigend", 0.06, 0.59, 0.43), ("absteigend", 1.0, 0.0, 0.0))]
    kind, text = ev.verdict_ex3(rows3)
    assert kind == "info" and "**Absteigend** (wertvolle zuerst) nehmen beide Stichprobenregeln **nichts** an (**0,000**), erst kommt, erst bekommt ist dort optimal (**1,000**)." in text and "fällt erst kommt, erst bekommt auf **0,060** und **0,060**" in text
    assert ev.verdict_ex3(rows3[:2] + [dict(rows3[2], wachs=0.2)] + rows3[3:])[0] == "error"
    assert ev.ex3_table(rows3)[2]["Reihenfolge"] == "absteigend"

    rows4 = [{"dist": d, "v": v, "rank": v - 1, "erst": e, "fest": 0.4, "wachs": w, "wachs_min": 0.3} for d, items in (("gleich", ((5, 0.68, 0.73), (8, 0.6, 0.72))), ("geometrisch", ((5, 0.37, 0.52), (8, 0.27, 0.5)))) for v, e, w in items]
    kind, text = ev.verdict_ex4(rows4)
    assert kind == "info" and "Bei verdoppelnden Nutzen und Rang 4 / 7 liegt die wachsende Stichprobe bei **0,520 / 0,500**, erst kommt, erst bekommt bei **0,370 / 0,270**." in text and "ist offen" in text
    assert ev.verdict_ex4([dict(rows4[0], erst=1.5)] + rows4[1:])[0] == "error" and ev.ex4_table(rows4)[0]["Rang"] == 4

    rows5 = [{"case": c, "erst": e, "fest": f_, "wachs": w, "teil": t} for c, e, f_, w, t in (("Freies Matroid (alles darf mit)", 1.0, 0.5, 0.63, None), ("a", 0.7, 0.4, 0.5, None), ("b", 0.7, 0.4, 0.5, 0.7), ("6 Farben zu je 10 Angeboten", 0.55, 0.47, 0.58, 0.65))]
    kind, text = ev.verdict_ex5(rows5)
    assert kind == "info" and "f = 0,5 liefert **0,500**, f = 0,37 wachsend **0,630**" in text and "**klassische Regel je Farbe** (**0,650**) die allgemeine Matroid-Regel (**0,580**)" in text
    assert ev.verdict_ex5([dict(rows5[0], erst=2.0)] + rows5[1:])[0] == "error" and ev.ex5_table(rows5)[0]["klassische 1/e-Regel je Farbe"] == "–"


def test_play_verdict_branches():
    v = ev.run_view(PLAY)
    kind, text = ev.verdict_play(PLAY, ev.play_state(PLAY, []), v)
    assert kind == "info" and text == "Angebot 1 von 14: Leitung **E–G** mit Nutzen **56**. Bisher angenommen: 0 Leitungen (Wert **0**)."
    kind, text = ev.verdict_play(PLAY, ev.play_state(PLAY, [True, False, True]), v)
    assert text == "Angebot 4 von 14: Leitung **E–F** mit Nutzen **54**. Bisher angenommen: 2 Leitungen (Wert **64**)."
    decisions = []
    while not ev.play_state(PLAY, decisions)["done"]:
        decisions.append(ev.play_state(PLAY, decisions)["can_accept"])
    kind, text = ev.verdict_play(PLAY, ev.play_state(PLAY, decisions), v)
    assert kind == "info" and text == "Fertig: Sie haben **318** (80,5 % des Offline-Optimums **395**). Die wachsende Stichprobe (f = 0,37) hätte **324** erreicht, erst kommt, erst bekommt **318**."
    st = ev.play_state(PLAY, decisions)
    assert ev.verdict_play(PLAY, {**st, "value": 330}, v)[0] == "success" and ev.verdict_play(PLAY, {**st, "value": 999}, v)[0] == "error"


def test_play_hint_when_an_offer_closes_a_ring():
    decisions = []
    st = ev.play_state(PLAY, decisions)
    while not st["done"] and st["can_accept"]:
        decisions.append(True)
        st = ev.play_state(PLAY, decisions)
    assert not st["done"] and not st["can_accept"]
    text = ev.verdict_play(PLAY, st, ev.run_view(PLAY))[1]
    assert text.endswith("Sie können es nur verwerfen: Mit dem Angenommenen entstünde ein Ring (oder die Grenze wäre erreicht).")


def test_formatting_helpers():
    assert (ev.de(0.5, 3), ev.num(3.0), ev.num(2.5), ev.prozent(0.5612), ev.zahl(4827444), ev.anteil(0.5), ev.leitungen(1), ev.leitungen(4)) == ("0,500", "3", "2,5", "56,1", "4 827 444", "0,500", "1 Leitung", "4 Leitungen")
