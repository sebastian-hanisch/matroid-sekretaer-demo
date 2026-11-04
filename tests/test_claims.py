"""Jede Zahl der README („Befunde“) wird hier mit den Funktionen der App nachgerechnet (DEMO-PLAYBOOK §4)."""

from fractions import Fraction
from pathlib import Path

import msk_algorithm as A
import msk_constants as C
import msk_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")


def _cell(v, rule):
    value = v["runs"][rule]["value"]
    return f"{ev.zahl(value)} ({ev.anteil(value / v['opt'])})"


EXAMPLES = {   # Preset -> (Zeile der README ohne die Zahlen; welche Regeln stehen in der Tabelle)
    "Standardfall (Voreinstellung)": "Standardfall (12 Standorte, verdoppelnd, Wald)",
    "Gutartige Gewichte": "Gutartige Gewichte (Plan, gleichverteilt, Wald)",
    "Absteigende Reihenfolge": "Absteigende Reihenfolge (Kardinalität 10)",
    "Farben": "Farben (6 Farben, gleichverteilt)",
    "Freie Wahl": "Freie Wahl (Plan, Kardinalität 14)",
}


def test_the_example_table():
    for preset, name in EXAMPLES.items():
        s = ev.Settings(**C.PRESETS[preset])
        v = ev.run_view(s, C.DEFAULT_F)
        teil = _cell(v, "teil") if "teil" in v["runs"] else "–"
        row = f"| {name} | {v['m']} | {v['rank']} | {ev.zahl(v['opt'])} | {_cell(v, 'erst')} | {_cell(v, 'fest')} | {_cell(v, 'wachs')} | {teil} |"
        assert row in README, row


def test_experiment_1():
    rows = ev.ex1_series()
    assert [r["k"] for r in rows] == [1, 3, 10, 20]
    assert [r["best_wachs"] for r in rows] == [0.1, 0.2, 0.3, 0.3]
    assert [round(r["wachs"][r["best_wachs"]], 3) for r in rows] == [0.905, 0.917, 0.896, 0.867]
    assert [round(r["erst"], 3) for r in rows] == [0.51, 0.51, 0.527, 0.563]
    assert (round(min(r["wachs"][0.7] for r in rows), 3), round(max(r["wachs"][0.7] for r in rows), 3)) == (0.353, 0.399)
    assert rows[0]["fest"] == rows[0]["wachs"]                                                     # bei Kardinalität 1 gleich
    for text in ("**0,10 / 0,20 / 0,30 / 0,30** mit Anteil **0,905 / 0,917 / 0,896 / 0,867**", "**0,510 / 0,510 / 0,527 / 0,563**", "mit f = 0,7 nur **0,353 bis 0,399**"):
        assert text in README, text


def test_experiment_2():
    by = {(r["matroid"][:4], r["dist"]): r for r in ev.ex2_series()}
    assert [round(by[("Kard", "gleich")][k], 3) for k in ("erst", "wachs")] == [0.543, 0.851] and [round(by[("Wald", "gleich")][k], 3) for k in ("erst", "wachs")] == [0.565, 0.762]
    assert [round(by[("Kard", "geometrisch")][k], 3) for k in ("erst", "wachs")] == [0.125, 0.63] and [round(by[("Wald", "geometrisch")][k], 3) for k in ("erst", "wachs")] == [0.187, 0.54]
    assert all(by[(m, "konstant")][k] == 1.0 for m in ("Kard", "Wald") for k in ("erst", "fest", "wachs"))
    for text in ("Kardinalität erst **0,543**, wachsend **0,851**; Wald erst **0,565**, wachsend **0,762**", "Kardinalität erst **0,125**, wachsend **0,630**; Wald erst **0,187**, wachsend **0,540**", "Alle Nutzen gleich: **1,000** bei allen Regeln"):
        assert text in README, text


def test_experiment_3():
    by = {(r["matroid"][:4], r["okind"]): r for r in ev.ex3_series()}
    assert [round(by[("Kard", "zufall")]["wachs"], 3), round(by[("Wald", "zufall")]["wachs"], 3)] == [0.852, 0.757]
    assert all((by[(m, "absteigend")]["fest"], by[(m, "absteigend")]["wachs"], by[(m, "absteigend")]["erst"]) == (0.0, 0.0, 1.0) for m in ("Kard", "Wald"))
    assert [round(by[("Kard", "aufsteigend")]["erst"], 3), round(by[("Wald", "aufsteigend")]["erst"], 3)] == [0.063, 0.119]
    for text in ("wachsend **0,852** und **0,757**", "beide Stichprobenregeln **0,000**, erst kommt, erst bekommt **1,000**", "erst kommt, erst bekommt **0,063** und **0,119**"):
        assert text in README, text


def test_experiment_4():
    rows = ev.ex4_series()
    g = [r for r in rows if r["dist"] == "geometrisch"]
    q = [r for r in rows if r["dist"] == "gleich"]
    assert [r["rank"] for r in g] == [4, 7, 11, 15]
    assert [round(r["wachs"], 3) for r in g] == [0.544, 0.5, 0.527, 0.554] and [round(r["erst"], 3) for r in g] == [0.394, 0.27, 0.198, 0.165]
    assert [round(r["wachs"], 3) for r in q] == [0.704, 0.713, 0.748, 0.78] and [round(r["erst"], 3) for r in q] == [0.642, 0.597, 0.562, 0.555]
    for text in ("wachsend **0,544 / 0,500 / 0,527 / 0,554**, erst **0,394 / 0,270 / 0,198 / 0,165**", "wachsend **0,704 / 0,713 / 0,748 / 0,780**, erst **0,642 / 0,597 / 0,562 / 0,555**"):
        assert text in README, text


def test_experiment_5():
    rows = {r["case"]: r for r in ev.ex5_series()}
    free, ones, twos, six = (rows[k] for k in ("Freies Matroid (alles darf mit)", "60 Einerklassen (jede Farbe einmal)", "30 Farben zu je 2 Angeboten", "6 Farben zu je 10 Angeboten"))
    assert (free["erst"], round(free["fest"], 3), round(free["wachs"], 3)) == (1.0, 0.503, 0.634)
    assert (ones["erst"], round(ones["fest"], 3), round(ones["wachs"], 3)) == (1.0, 0.502, 0.633)
    assert [round(twos[k], 3) for k in ("erst", "fest", "wachs", "teil")] == [0.749, 0.447, 0.538, 0.749]
    assert [round(six[k], 3) for k in ("erst", "fest", "wachs", "teil")] == [0.541, 0.495, 0.594, 0.645]
    for text in ("Freies Matroid: erst **1,000**, fest 0,5 **0,503**, wachsend **0,634**", "60 Einerklassen: 1,000 / 0,502 / 0,633", "erst 0,749, fest 0,447, wachsend 0,538, **klassisch je Farbe 0,749**",
                 "erst 0,541, fest 0,495, wachsend **0,594**, **klassisch je Farbe 0,645**"):
        assert text in README, text


def test_the_hand_example_for_cardinality_one():
    mat, w = A.make_matroid("card", 4, 1), [10, 8, 5, 2]
    assert A.expectation(mat, w, "fest", 0.25)["expected"] == Fraction(20, 3) and A.expectation(mat, w, "fest", 0.25)["optimal_orders"] == 11
    assert A.expectation(mat, w, "fest", 0.5)["expected"] == Fraction(29, 6) and A.expectation(mat, w, "fest", 0.5)["optimal_orders"] == 10
    e = A.expectation(mat, w, "erst")
    assert (e["expected"], e["worst"]) == (Fraction(25, 4), 2)
    assert A.classical_success(4, 1) == Fraction(11, 24) and A.classical_success(4, 2) == Fraction(10, 24)
    for text in ("Stichprobe 1: Erwartung **20/3**, bestes Angebot in **11/24** der Reihenfolgen", "Stichprobe 2: Erwartung **29/6**, bestes in **10/24**", "erst kommt, erst bekommt **25/4** (schlechteste Reihenfolge 2)"):
        assert text in README, text


def test_the_hand_example_for_the_forest():
    mat, w = A.make_matroid("wald", 4, 0, [(0, 1), (1, 2), (0, 2), (2, 3)], 4), [9, 6, 4, 1]
    assert A.offline(mat, w)[0] == 16
    r = A.run_rule(mat, w, [3, 2, 0, 1], "wachs", 0.25)
    assert r["value"] == 13 and r["trace"][3][4] == "abhaengig"
    assert A.expectation(mat, w, "erst")["expected"] == Fraction(41, 3) and A.expectation(mat, w, "wachs", 0.25)["expected"] == Fraction(149, 12)
    for text in ("**13** von 16", "erst **41/3**, wachsend mit Stichprobe 1 **149/12**", "bc hängt ab (Dreieck)"):
        assert text in README, text


def test_constants_in_the_readme():
    assert (C.PLAN_NODES, C.PLAN_EDGES, C.V_MIN, C.V_MAX, C.DOMINANT_WEIGHT, C.CONSTANT_WEIGHT) == (8, 14, 6, 16, 5000, 10)
    assert (C.EX1_INSTANCES, C.EX1_ORDERS, C.EX2_INSTANCES, C.EX2_ORDERS, C.EX5_N) == (30, 40, 20, 30, 60)
    for text in ("30 Instanzen × 40 Reihenfolgen", "20 Instanzen × 30 Reihenfolgen", "8 Standorte, 14 zufällige Leitungen", "bis 120 Angebote", "ein dominantes Angebot (5 000)", "alle gleich (10)"):
        assert text in README, text
    assert ev.build(ev.Settings("gross", 16, 1, "gleich", "wald", 3, 1, "zufall"))["inst"].m == 120
    ws = ev.build(ev.Settings("gross", 12, 1, "geometrisch", "wald", 3, 1, "zufall"))["w"]
    assert (min(ws), max(ws)) == (1, 2 ** 20)
