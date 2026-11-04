"""Szenario: ein Leitungsnetz. Standorte auf einem Plan, mögliche Leitungen mit Nutzen (Gewicht). Knoten A ist ein Standort wie jeder andere."""

import random
from dataclasses import dataclass
from math import sqrt

import msk_constants as C

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass(frozen=True)
class Instance:
    points: tuple[tuple[float, float], ...]
    edges: tuple[tuple[int, int], ...]     # (u, v), u < v, geordnet nach (u, v); der Kantenindex ist die Position
    weights: tuple[int, ...]               # Nutzen je Leitung (positiv)

    @property
    def n(self) -> int:                    # Zahl der Standorte
        return len(self.points)

    @property
    def m(self) -> int:                    # Zahl der Leitungen (= Angebote)
        return len(self.edges)

    def name(self, v: int) -> str:
        return LETTERS[v]

    def label(self, e: int) -> str:
        u, v = self.edges[e]
        return f"{self.name(u)}–{self.name(v)}"


def complete_edges(v: int) -> list[tuple[int, int]]:
    return [(a, b) for a in range(v) for b in range(a + 1, v)]


def _find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def connected(v: int, edges) -> bool:
    parent = list(range(v))
    for a, b in edges:
        parent[_find(parent, a)] = _find(parent, b)
    return len({_find(parent, i) for i in range(v)}) == 1


def draw_weights(dist: str, m: int, rng: random.Random) -> tuple[int, ...]:
    """Nutzen je Leitung (positive ganze Zahlen) nach der gewählten Verteilung."""
    if dist == "gleich":
        w = [rng.randint(1, 100) for _ in range(m)]
    elif dist == "exp":
        w = [1 + int(rng.expovariate(1 / 25)) for _ in range(m)]
    elif dist == "pareto":
        w = [max(1, int(10 * rng.paretovariate(1.5))) for _ in range(m)]
    elif dist == "dominant":
        w = [rng.randint(1, 100) for _ in range(m)]
        w[rng.randrange(m)] = C.DOMINANT_WEIGHT
    elif dist == "geometrisch":
        w = [max(1, round(2 ** (20 * i / max(1, m - 1)))) for i in range(m)]
        rng.shuffle(w)
    elif dist == "konstant":
        w = [C.CONSTANT_WEIGHT] * m
    else:
        raise ValueError(f"Gewichtsverteilung {dist!r} unbekannt")
    return tuple(w)


def make_instance(inst: str, v: int, seed: int, wdist: str) -> Instance:
    """Deterministisch aus (inst, v, seed, wdist). plan: 8 Standorte und 14 zufällige Leitungen, zusammenhängend; gross: vollständiger Graph auf v Standorten."""
    rng = random.Random(seed)
    nodes = C.PLAN_NODES if inst == "plan" else v
    if not 2 <= nodes <= len(LETTERS):
        raise ValueError(f"{nodes} Standorte außerhalb von 2 bis {len(LETTERS)}")
    points = tuple((rng.uniform(0.05, 0.95), rng.uniform(0.05, 0.95)) for _ in range(nodes))
    allp = complete_edges(nodes)
    if inst == "plan":
        while True:
            edges = sorted(rng.sample(allp, C.PLAN_EDGES))
            if connected(nodes, edges):
                break
    else:
        edges = allp
    return Instance(points, tuple(edges), draw_weights(wdist, len(edges), random.Random(seed * 7919 + 1)))


def arrival_order(weights, kind: str, oseed: int) -> list[int]:
    """Reihenfolge der Angebote: zufällig (nach oseed), aufsteigend oder absteigend nach Nutzen (Gleichstand: kleinere Nummer zuerst)."""
    m = len(weights)
    if kind == "zufall":
        order = list(range(m))
        random.Random(oseed).shuffle(order)
        return order
    if kind == "aufsteigend":
        return sorted(range(m), key=lambda i: (weights[i], i))
    if kind == "absteigend":
        return sorted(range(m), key=lambda i: (-weights[i], i))
    raise ValueError(f"Reihenfolge {kind!r} unbekannt")
