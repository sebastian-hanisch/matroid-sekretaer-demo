"""Orakel (ORACLE-PLAYBOOK §5): unabhängig geschriebene, einfache Gegenproben für Matroid-Orakel, Offline-Greedy und die Regeln."""

import itertools
import random
from fractions import Fraction

import pytest

import msk_algorithm as A
from msk_scenario import make_instance

SEED = 20261125


def _rank_brute(mat, s):
    """Rang einer Menge: größte unabhängige Teilmenge durch Aufzählung."""
    s = list(s)
    for size in range(len(s), -1, -1):
        for sub in itertools.combinations(s, size):
            if mat.independent(sub):
                return size
    return 0


def _random_matroid(rng, kind=None):
    kind = kind or rng.choice(["card", "farbe", "wald"])
    if kind == "card":
        n = rng.randint(3, 8)
        return A.make_matroid("card", n, rng.randint(1, 4))
    if kind == "farbe":
        n = rng.randint(3, 8)
        return A.make_matroid("farbe", n, rng.randint(1, 4))
    nodes = rng.randint(3, 5)
    edges = [(a, b) for a in range(nodes) for b in range(a + 1, nodes)]
    rng.shuffle(edges)
    return _wald(rng, nodes, edges)


def _wald(rng, nodes, edges):
    chosen = edges[: rng.randint(3, len(edges))]
    return A.make_matroid("wald", len(chosen), 0, chosen, nodes)


def _naive_run(mat, w, order, rule, f):
    """Einfache Neufassung der Regeln mit den Orakeln der Matroid-Klasse (Listen statt Zählerstrukturen)."""
    t = A.sample_size(len(order), f) if rule != "erst" else 0
    chosen, seen = [], []
    for pos, e in enumerate(order):
        if pos >= t:
            base = order[:t] if rule == "fest" else seen
            heavier = [x for x in base if w[x] > w[e]]
            if (rule == "erst" or not mat.spanned(heavier, e)) and mat.can_add(chosen, e):
                chosen.append(e)
        seen.append(e)
    return chosen


def test_spanned_equals_the_rank_definition_on_random_matroids():
    rng = random.Random(SEED)
    for _ in range(120):
        mat = _random_matroid(rng)
        items = list(range(mat.n))
        a = rng.sample(items, rng.randint(0, min(6, mat.n - 1)))
        e = rng.choice([x for x in items if x not in a])
        assert mat.spanned(a, e) == (_rank_brute(mat, a + [e]) == _rank_brute(mat, a)), (mat.kind, a, e)


def test_rank_equals_the_size_of_the_largest_independent_set():
    rng = random.Random(SEED + 1)
    for _ in range(60):
        mat = _random_matroid(rng)
        assert mat.rank() == _rank_brute(mat, range(mat.n))


def test_offline_greedy_equals_the_best_independent_set_by_enumeration():
    rng = random.Random(SEED + 2)
    for _ in range(80):
        mat = _random_matroid(rng)
        w = [rng.randint(1, 20) for _ in range(mat.n)]
        best = max(sum(w[e] for e in sub) for r in range(mat.n + 1) for sub in itertools.combinations(range(mat.n), r) if mat.independent(sub))
        assert A.offline(mat, w)[0] == best


def test_fast_rules_equal_the_naive_rules_on_random_runs():
    rng = random.Random(SEED + 3)
    for _ in range(300):
        mat = _random_matroid(rng)
        w = [rng.randint(1, 15) for _ in range(mat.n)]
        order = list(range(mat.n))
        rng.shuffle(order)
        f = rng.choice([0.1, 0.25, 0.37, 0.5, 0.7])
        for rule in ("erst", "fest", "wachs"):
            assert A.run_rule(mat, w, order, rule, f)["chosen"] == _naive_run(mat, w, order, rule, f), (mat.kind, rule)


def test_fast_rules_equal_the_naive_rules_on_the_app_instances():
    for inst, v, seed, dist, cons, k in (("gross", 8, 3, "gleich", "wald", 0), ("gross", 8, 3, "geometrisch", "card", 5), ("plan", 8, 4, "pareto", "farbe", 4), ("gross", 10, 5, "dominant", "wald", 0)):
        ins = make_instance(inst, v, seed, dist)
        mat = A.make_matroid(cons, ins.m, k, ins.edges, ins.n)
        order = list(range(ins.m))
        random.Random(seed).shuffle(order)
        for rule in ("erst", "fest", "wachs"):
            assert A.run_rule(mat, ins.weights, order, rule, 0.37)["chosen"] == _naive_run(mat, ins.weights, order, rule, 0.37), (inst, cons, rule)


@pytest.mark.parametrize("n", [3, 4, 5, 6, 7])
def test_classical_success_probability_equals_the_enumeration(n):
    mat, w = A.make_matroid("card", n, 1), [10 * (i + 1) + i for i in range(n)]      # verschiedene Nutzen
    for t in range(1, n):
        f = t / n
        ex = A.expectation(mat, w, "wachs", f)
        assert Fraction(ex["optimal_orders"], ex["orders"]) == A.classical_success(n, A.sample_size(n, f)), (n, t)


def test_expectation_of_erst_equals_the_mean_over_all_orders_computed_independently():
    rng = random.Random(SEED + 4)
    for _ in range(10):
        mat = _random_matroid(rng, "wald")
        if mat.n > 7:
            continue
        w = [rng.randint(1, 9) for _ in range(mat.n)]
        total = Fraction(0)
        count = 0
        for o in itertools.permutations(range(mat.n)):
            ch = []
            for e in o:
                if mat.can_add(ch, e):
                    ch.append(e)
            total += sum(w[e] for e in ch)
            count += 1
        assert A.expectation(mat, w, "erst")["expected"] == total / count
