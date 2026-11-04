"""Kern an Handrechnungen (DEMO-PLAYBOOK §1b): Offline-Greedy, die drei Regeln, die klassische Regel je Farbe und die exakte Erwartung über alle Reihenfolgen."""

from fractions import Fraction

import pytest

import msk_algorithm as A


def test_offline_greedy_by_hand(card1, card2, wald, farben):
    assert A.offline(*card1) == (10, [0])
    assert A.offline(*card2) == (18, [0, 1])
    assert A.offline(*wald) == (16, [0, 1, 3])
    assert A.offline(*farben) == (17, [1, 4])


def test_sample_size_rounds_down_with_tolerance():
    assert (A.sample_size(14, 0.37), A.sample_size(10, 0.3), A.sample_size(100, 0.57), A.sample_size(4, 0.25), A.sample_size(60, 0.5), A.sample_size(5, 0.1)) == (5, 3, 57, 1, 30, 0)


def test_matroid_oracles_by_hand(wald):
    mat, _ = wald
    assert mat.independent([0, 1, 3]) and not mat.independent([0, 1, 2])       # ab, bc, ac schließen das Dreieck
    assert mat.spanned([0, 1], 2) and not mat.spanned([0], 2) and not mat.spanned([0, 1, 2], 3)
    assert mat.rank() == 3 and mat.can_add([0], 1) and not mat.can_add([0, 1], 2)
    card = A.make_matroid("card", 5, 2)
    assert card.independent([0, 1]) and not card.independent([0, 1, 2]) and card.spanned([3, 4], 0) and not card.spanned([3], 0) and card.rank() == 2
    farbe = A.make_matroid("farbe", 6, 3)
    assert farbe.cls == (0, 1, 2, 0, 1, 2) and farbe.independent([0, 1, 2]) and not farbe.independent([0, 3]) and farbe.rank() == 3


def test_expectations_over_all_orders_for_cardinality_one(card1):
    assert A.expectation(*card1, "erst")["expected"] == Fraction(25, 4)
    fe = A.expectation(*card1, "fest", 0.25)
    assert (fe["expected"], fe["optimal_orders"], fe["orders"], fe["worst"]) == (Fraction(20, 3), 11, 24, 0)
    assert A.expectation(*card1, "wachs", 0.25)["expected"] == Fraction(20, 3)
    fe = A.expectation(*card1, "fest", 0.5)
    assert (fe["expected"], fe["optimal_orders"]) == (Fraction(29, 6), 10)
    assert A.expectation(*card1, "erst")["worst"] == 2 and A.expectation(*card1, "erst")["optimal_orders"] == 6


def test_expectations_for_two_and_for_the_forest(card2, wald):
    assert A.expectation(*card2, "erst")["expected"] == Fraction(25, 2)
    assert A.expectation(*card2, "fest", 0.5)["expected"] == Fraction(32, 3)
    assert A.expectation(*card2, "wachs", 0.5)["expected"] == Fraction(59, 6)
    assert A.expectation(*wald, "erst")["expected"] == Fraction(41, 3)
    assert A.expectation(*wald, "fest", 0.5)["expected"] == Fraction(28, 3)
    assert A.expectation(*wald, "wachs", 0.5)["expected"] == Fraction(26, 3)
    assert A.expectation(*wald, "wachs", 0.25)["expected"] == Fraction(149, 12)


def test_classical_success_formula():
    assert (A.classical_success(4, 1), A.classical_success(4, 2), A.classical_success(4, 0), A.classical_success(4, 4)) == (Fraction(11, 24), Fraction(5, 12), Fraction(1, 4), Fraction(0))
    assert float(A.classical_success(1000, 368)) == pytest.approx(0.36788, abs=5e-4)               # Grenzwert 1/e


def test_forest_trace_by_hand(wald):
    r = A.run_rule(*wald, [3, 2, 0, 1], "wachs", 0.25)
    assert r["value"] == 13 and r["chosen"] == [2, 0] and r["sample"] == 1
    assert [(t[1], t[3], t[4]) for t in r["trace"]] == [(3, False, "stichprobe"), (2, True, "angenommen"), (0, True, "angenommen"), (1, False, "abhaengig")]
    f = A.run_rule(*wald, [3, 2, 0, 1], "fest", 0.25)
    assert f["value"] == 13
    e = A.run_rule(*wald, [3, 2, 0, 1], "erst")
    assert (e["value"], e["chosen"]) == (14, [3, 2, 0])                # cd, ac, ab bilden einen Baum (Rang 3); bc würde das Dreieck schließen
    assert e["trace"][3][4] == "abhaengig"


def test_classical_rule_per_color_by_hand(farben):
    mat, w = farben
    r = A.run_teil(mat, w, [0, 3, 1, 4, 2, 5])                          # je Farbe ⌊3 / e⌋ = 1 Angebot Stichprobe
    assert (r["value"], r["chosen"], r["sample"]) == (17, [1, 4], 2)
    assert [t[4] for t in r["trace"]] == ["stichprobe", "stichprobe", "angenommen", "angenommen", "abhaengig", "abhaengig"]
    bad = A.run_teil(mat, w, [1, 0, 2, 4, 3, 5])                        # die 9 und die 8 liegen in der Stichprobe: nichts kommt hinein
    assert (bad["value"], bad["chosen"]) == (0, [])
    assert [t[4] for t in bad["trace"]] == ["stichprobe", "aufgespannt", "aufgespannt", "stichprobe", "aufgespannt", "aufgespannt"]
    with pytest.raises(ValueError):
        A.run_teil(A.make_matroid("card", 4, 2), [1, 2, 3, 4], [0, 1, 2, 3])


def test_run_any_dispatches(card1):
    mat, w = card1
    assert A.run_any(mat, w, [0, 1, 2, 3], "erst")["value"] == 10
    assert A.run_any(mat, w, [3, 2, 1, 0], "wachs", 0.25)["value"] == A.run_rule(mat, w, [3, 2, 1, 0], "wachs", 0.25)["value"]


def test_enumeration_is_limited_to_eight_elements():
    with pytest.raises(ValueError):
        A.expectation(A.make_matroid("card", 9, 2), list(range(1, 10)), "erst")


def test_make_matroid_rejects_unknown_kind():
    with pytest.raises(ValueError):
        A.make_matroid("kreis", 3, 1)
