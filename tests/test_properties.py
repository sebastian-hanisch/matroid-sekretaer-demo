"""Eigenschaftstests (Schicht „Eigenschaften“): Invarianten auf Zufallsinstanzen mit festem Seed."""

import random

import msk_algorithm as A
import msk_constants as C
import msk_evaluation as ev
from msk_scenario import arrival_order, draw_weights, make_instance

SEED = 20261126


def _cases(rng, count):
    for _ in range(count):
        inst = rng.choice(["plan", "gross"])
        dist = rng.choice(C.WEIGHTS)
        ins = make_instance(inst, rng.randint(5, 9), rng.randint(0, 999), dist)
        cons = rng.choice(C.CONSTRAINTS)
        mat = A.make_matroid(cons, ins.m, rng.randint(1, 8), ins.edges, ins.n)
        order = list(range(ins.m))
        rng.shuffle(order)
        yield ins, cons, mat, order


def test_every_output_is_independent_not_above_the_optimum_and_the_sample_is_never_taken():
    rng = random.Random(SEED)
    for ins, cons, mat, order in _cases(rng, 80):
        opt = A.offline(mat, ins.weights)[0]
        for rule in ("erst", "fest", "wachs"):
            f = rng.choice(C.F_CHOICES)
            r = A.run_rule(mat, ins.weights, order, rule, f)
            assert mat.independent(r["chosen"]) and r["value"] <= opt and r["value"] == sum(ins.weights[e] for e in r["chosen"])
            assert len(r["trace"]) == len(order) and [t[1] for t in r["trace"]] == order
            assert {t[1] for t in r["trace"] if t[3]} == set(r["chosen"])
            sample = {t[1] for t in r["trace"][: r["sample"]]}
            assert not sample & set(r["chosen"]) and (rule == "erst" or r["sample"] == A.sample_size(len(order), f))


def test_wachs_with_cardinality_one_is_the_classical_rule_and_equals_fest():
    rng = random.Random(SEED + 1)
    for _ in range(60):
        n = rng.randint(5, 40)
        w = rng.sample(range(1, 500), n)
        order = list(range(n))
        rng.shuffle(order)
        mat = A.make_matroid("card", n, 1)
        f = rng.choice(C.F_CHOICES)
        t = A.sample_size(n, f)
        wa, fe = A.run_rule(mat, w, order, "wachs", f), A.run_rule(mat, w, order, "fest", f)
        threshold = max((w[e] for e in order[:t]), default=0)
        classical = next((e for e in order[t:] if w[e] > threshold), None)
        assert wa["chosen"] == ([] if classical is None else [classical]) and fe["chosen"] == wa["chosen"]


def test_for_colors_with_capacity_one_fest_equals_wachs():
    rng = random.Random(SEED + 2)
    for _ in range(60):
        n = rng.randint(6, 30)
        mat = A.make_matroid("farbe", n, rng.randint(1, 8))
        w = [rng.randint(1, 100) for _ in range(n)]
        order = list(range(n))
        rng.shuffle(order)
        f = rng.choice(C.F_CHOICES)
        assert A.run_rule(mat, w, order, "fest", f)["chosen"] == A.run_rule(mat, w, order, "wachs", f)["chosen"]


def test_descending_order_makes_erst_optimal_and_the_sample_rules_take_nothing_under_cardinality():
    rng = random.Random(SEED + 3)
    for _ in range(40):
        ins, cons, mat, _ = next(_cases(rng, 1))
        order = arrival_order(ins.weights, "absteigend", 0)
        opt = A.offline(mat, ins.weights)[0]
        assert A.run_rule(mat, ins.weights, order, "erst")["value"] == opt, cons
    for _ in range(30):
        n, k = rng.randint(10, 60), rng.randint(1, 4)
        mat = A.make_matroid("card", n, k)
        w = draw_weights(rng.choice(C.WEIGHTS[:-1]), n, rng)
        order = arrival_order(w, "absteigend", 0)
        for f in (0.37, 0.5, 0.7):
            if A.sample_size(n, f) >= k:
                assert A.run_rule(mat, w, order, "fest", f)["value"] == 0 == A.run_rule(mat, w, order, "wachs", f)["value"]


def test_free_matroid_makes_erst_optimal_and_the_sample_costs_exactly_its_part_for_equal_weights():
    rng = random.Random(SEED + 4)
    for _ in range(30):
        n = rng.randint(6, 40)
        w = draw_weights(rng.choice(C.WEIGHTS), n, rng)
        mat = A.make_matroid("card", n, n)
        order = list(range(n))
        rng.shuffle(order)
        assert A.run_rule(mat, w, order, "erst")["value"] == sum(w)
    n, f = 60, 0.5
    mat = A.make_matroid("card", n, n)
    assert A.run_rule(mat, [10] * n, list(range(n)), "fest", f)["value"] == 10 * (n - A.sample_size(n, f))


def test_equal_weights_give_the_optimum_under_cardinality_when_enough_offers_remain():
    n, k = 100, 10
    mat = A.make_matroid("card", n, k)
    order = list(range(n))
    random.Random(SEED + 5).shuffle(order)
    opt = A.offline(mat, [10] * n)[0]
    for rule in ("erst", "fest", "wachs"):
        assert A.run_rule(mat, [10] * n, order, rule, 0.37)["value"] == opt


def test_runs_are_deterministic_and_the_series_are_reproducible():
    s = ev.Settings()
    assert ev.run_view(s, 0.37)["runs"]["wachs"]["chosen"] == A.run_rule(*(lambda b: (b["mat"], b["w"], b["order"]))(ev.build(s)), "wachs", 0.37)["chosen"]
    assert ev.ex5_series() == ev.ex5_series()


def test_wachs_beats_erst_on_skewed_weights_in_the_series_and_never_exceeds_one():
    rows = ev.ex2_series()
    by = {(r["matroid"][:4], r["dist"]): r for r in rows}
    for matroid in ("Kard", "Wald"):
        assert by[(matroid, "geometrisch")]["wachs"] > by[(matroid, "geometrisch")]["erst"] + 0.2
        assert by[(matroid, "konstant")]["erst"] == by[(matroid, "konstant")]["wachs"] == 1.0
    assert all(max(r["erst"], r["fest"], r["wachs"]) <= 1 + 1e-9 for r in rows)
