"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste Fälle, Gleichstände, k = 1, leere Stichprobe, Reglergrenzen, Spielwiese."""

import random

import pytest

import msk_algorithm as A
import msk_constants as C
import msk_evaluation as ev
from msk_scenario import arrival_order, draw_weights, make_instance


def test_one_and_two_offers():
    mat = A.make_matroid("card", 1, 1)
    assert A.run_rule(mat, [7], [0], "erst")["value"] == 7
    assert A.run_rule(mat, [7], [0], "wachs", 0.5)["value"] == 7                 # ⌊0,5 · 1⌋ = 0: keine Stichprobe
    mat = A.make_matroid("card", 2, 1)
    assert A.run_rule(mat, [3, 5], [0, 1], "wachs", 0.5)["chosen"] == [1]
    assert A.run_rule(mat, [5, 3], [0, 1], "wachs", 0.5)["chosen"] == []
    assert A.run_rule(A.make_matroid("card", 0, 1), [], [], "erst")["value"] == 0


def test_empty_sample_means_every_offer_that_is_not_spanned_is_taken():
    mat = A.make_matroid("card", 5, 2)
    r = A.run_rule(mat, [1, 2, 3, 4, 5], [0, 1, 2, 3, 4], "wachs", 0.0)
    assert r["sample"] == 0 and r["chosen"] == [0, 1]
    assert [t[4] for t in r["trace"]] == ["angenommen", "angenommen", "abhaengig", "abhaengig", "abhaengig"]    # 3, 4, 5 sind schwerer als alle gesehenen, aber die Grenze ist erreicht


def test_ties_do_not_span_each_other_and_equal_weights_work():
    mat = A.make_matroid("card", 6, 2)
    r = A.run_rule(mat, [4] * 6, [0, 1, 2, 3, 4, 5], "wachs", 0.34)
    assert r["sample"] == 2 and r["chosen"] == [2, 3] and r["value"] == 8
    assert A.offline(mat, [4] * 6) == (8, [0, 1])                                  # Gleichstand: kleinere Nummer zuerst


def test_k_larger_than_the_number_of_offers_and_one_color():
    mat = A.make_matroid("card", 4, 20)
    assert A.run_rule(mat, [1, 2, 3, 4], [3, 2, 1, 0], "erst")["value"] == 10
    mat = A.make_matroid("farbe", 5, 1)
    assert set(mat.cls) == {0} and mat.rank() == 1 and A.offline(mat, [3, 9, 2, 4, 1]) == (9, [1])
    with pytest.raises(ValueError):
        A.run_teil(A.make_matroid("wald", 3, 0, [(0, 1), (1, 2), (0, 2)], 3), [1, 2, 3], [0, 1, 2])


def test_teil_with_classes_of_size_one_takes_every_class_leader():
    mat = A.make_matroid("farbe", 5, 5)                                            # fünf Einerklassen
    r = A.run_teil(mat, [3, 9, 2, 4, 1], [4, 2, 0, 3, 1])
    assert r["sample"] == 0 and r["value"] == 19 and sorted(r["chosen"]) == [0, 1, 2, 3, 4]


def test_instance_generation_is_deterministic_and_valid_at_every_size():
    for inst, v in (("plan", 6), ("gross", C.V_MIN), ("gross", C.V_MAX)):
        a, b = make_instance(inst, v, 5, "gleich"), make_instance(inst, v, 5, "gleich")
        assert a == b and len(a.weights) == a.m and all(x >= 1 for x in a.weights)
    assert make_instance("plan", 12, 3, "gleich").m == C.PLAN_EDGES and make_instance("plan", 12, 3, "gleich").n == C.PLAN_NODES
    assert make_instance("gross", C.V_MAX, 3, "gleich").m == C.V_MAX * (C.V_MAX - 1) // 2
    with pytest.raises(ValueError):
        make_instance("gross", 40, 1, "gleich")
    with pytest.raises(ValueError):
        draw_weights("unbekannt", 3, random.Random(1))
    with pytest.raises(ValueError):
        arrival_order([1, 2], "seitwaerts", 0)


def test_weight_distributions_have_their_documented_shape():
    rng = random.Random(1)
    g = draw_weights("geometrisch", 66, rng)
    assert min(g) == 1 and max(g) == 2 ** 20 and len(g) == 66
    d = draw_weights("dominant", 20, random.Random(2))
    assert d.count(C.DOMINANT_WEIGHT) == 1 and max(x for x in d if x != C.DOMINANT_WEIGHT) <= 100
    assert set(draw_weights("konstant", 7, rng)) == {C.CONSTANT_WEIGHT}
    assert all(1 <= x <= 100 for x in draw_weights("gleich", 50, rng))


def test_arrival_orders():
    w = [5, 9, 5, 1, 9]
    assert arrival_order(w, "aufsteigend", 0) == [3, 0, 2, 1, 4] and arrival_order(w, "absteigend", 0) == [1, 4, 0, 2, 3]
    a = arrival_order(w, "zufall", 3)
    assert a == arrival_order(w, "zufall", 3) and sorted(a) == [0, 1, 2, 3, 4]


def test_every_regler_corner_gives_consistent_numbers():
    for inst in C.INSTANCES:
        for cons in C.CONSTRAINTS:
            for okind in C.ORDERS:
                for wdist in (C.WEIGHTS[0], C.WEIGHTS[-1], "geometrisch"):
                    s = ev.Settings(inst, C.V_MAX if inst == "gross" else 8, 0, wdist, cons, C.K_MAX, 0, okind)
                    v = ev.run_view(s, 0.7)
                    assert all(0 <= r["value"] <= v["opt"] for r in v["runs"].values())
                    kind, text = ev.verdict_run(s, v)
                    assert kind == "info" and text.startswith("Offline (alle **")


def test_play_state_walks_through_all_offers_and_reports_the_end():
    s = ev.Settings("plan", 8, 3, "gleich", "wald", 3, 1, "zufall")
    m = ev.run_view(s)["m"]
    decisions = []
    st = ev.play_state(s, decisions)
    assert st["pos"] == 0 and not st["done"] and st["chosen"] == [] and st["can_accept"] and st["value"] == 0
    while not st["done"]:
        decisions.append(st["can_accept"])
        st = ev.play_state(s, decisions)
    assert st["pos"] == m and st["next"] is None and st["can_accept"] is False
    assert st["chosen"] == A.run_rule(st["b"]["mat"], st["b"]["w"], st["b"]["order"], "erst")["chosen"]            # immer annehmen, was geht = erst kommt, erst bekommt
    assert ev.verdict_play(s, st, ev.run_view(s))[0] in ("success", "info")
