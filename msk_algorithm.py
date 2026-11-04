"""Kern: Matroid-Orakel, Offline-Greedy und die Online-Regeln des Sekretärproblems.

Angebote (Elemente) kommen in einer Reihenfolge, jedes ist sofort anzunehmen oder zu verwerfen, endgültig; das Angenommene muss unabhängig bleiben.
Regeln (alle kennen das Matroid, nicht die Gewichte künftiger Angebote):
  erst   erst kommt, erst bekommt: annehmen, was unabhängig bleibt;
  fest   die ersten ⌊f·n⌋ Angebote nur ansehen; danach e annehmen, wenn e nicht von schwereren Elementen der STICHPROBE aufgespannt wird und unabhängig bleibt;
  wachs  wie fest, aber als Beobachtung zählen alle bisher gesehenen Angebote (Stichprobe und spätere); bei Kardinalität 1 ist das die klassische 1/e-Regel;
  teil   (nur Farben, Kapazität 1) die klassische 1/e-Regel je Farbklasse mit der Zahl der Elemente der Klasse.
Die Namen „feste“ und „wachsende Stichprobe“ sind Bezeichnungen dieser Demo, keine zitierten Algorithmen."""

from __future__ import annotations

import itertools
from bisect import bisect_left, insort
from dataclasses import dataclass
from fractions import Fraction
from math import e as EULER


def sample_size(n: int, f: float) -> int:
    """So viele Angebote werden nur angesehen: ⌊f · n⌋ (mit kleiner Toleranz gegen Rundungsfehler wie 0,57 · 100 = 56,999…)."""
    return int(f * n + 1e-9)


def _find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


@dataclass(frozen=True)
class Matroid:
    """kind: 'card' (höchstens k), 'part' (Klasse cls[e], Kapazität cap), 'wald' (edges[e] = (u, v) auf nodes Knoten)."""

    kind: str
    n: int                                  # Zahl der Elemente (Angebote)
    k: int = 0
    cls: tuple = ()
    cap: int = 1
    edges: tuple = ()
    nodes: int = 0

    # --- Orakel (einfache Fassung, auch Gegenprobe für die schnelle Fassung der Läufe) -----------------------------------------------------------

    def independent(self, s) -> bool:
        s = list(s)
        if self.kind == "card":
            return len(s) <= self.k
        if self.kind == "part":
            counts: dict = {}
            for e in s:
                counts[self.cls[e]] = counts.get(self.cls[e], 0) + 1
            return all(c <= self.cap for c in counts.values())
        parent = list(range(self.nodes))
        for e in s:
            a, b = _find(parent, self.edges[e][0]), _find(parent, self.edges[e][1])
            if a == b:
                return False
            parent[a] = b
        return True

    def can_add(self, chosen, e) -> bool:
        return self.independent(list(chosen) + [e])

    def spanned(self, heavier, e) -> bool:
        """Liegt e im Aufspann der Menge heavier? (Der Rang von heavier + e ist nicht größer als der von heavier.)"""
        heavier = list(heavier)
        if self.kind == "card":
            return len(heavier) >= self.k
        if self.kind == "part":
            return sum(1 for x in heavier if self.cls[x] == self.cls[e]) >= self.cap
        parent = list(range(self.nodes))
        for x in heavier:
            parent[_find(parent, self.edges[x][0])] = _find(parent, self.edges[x][1])
        return _find(parent, self.edges[e][0]) == _find(parent, self.edges[e][1])

    def rank(self) -> int:
        """Rang des Matroids (Größe jeder Basis)."""
        if self.kind == "card":
            return min(self.k, self.n)
        if self.kind == "part":
            counts: dict = {}
            for c in self.cls:
                counts[c] = counts.get(c, 0) + 1
            return sum(min(self.cap, c) for c in counts.values())
        parent = list(range(self.nodes))
        r = 0
        for u, v in self.edges:
            a, b = _find(parent, u), _find(parent, v)
            if a != b:
                parent[a] = b
                r += 1
        return r


def make_matroid(cons: str, n: int, k: int, edges=(), nodes: int = 0) -> Matroid:
    if cons == "card":
        return Matroid("card", n, k=k)
    if cons == "farbe":
        return Matroid("part", n, cls=tuple(e % k for e in range(n)), cap=1)
    if cons == "wald":
        return Matroid("wald", n, edges=tuple(edges), nodes=nodes)
    raise ValueError(f"Nebenbedingung {cons!r} unbekannt")


def offline(mat: Matroid, w) -> tuple[int, list[int]]:
    """Offline-Optimum: Greedy nach absteigendem Nutzen (Gleichstand: kleinere Nummer), Rado–Edmonds. Alle Nutzen sind positiv."""
    chosen: list[int] = []
    for e in sorted(range(mat.n), key=lambda i: (-w[i], i)):
        if mat.can_add(chosen, e):
            chosen.append(e)
    return sum(w[e] for e in chosen), chosen


# --- Schnelle Fassung der Läufe: Zustand für „aufgespannt?“ und „unabhängig?“ -----------------------------------------------------------------------


class _Observed:
    """Gesehene Elemente mit Nutzen; fragt: liegt e im Aufspann der gesehenen Elemente, die schwerer sind als e?"""

    def __init__(self, mat: Matroid, w):
        self.mat, self.w = mat, w
        self.negs: list | dict = {} if mat.kind == "part" else []
        self.items: list[int] = []

    def add(self, e: int) -> None:
        self.items.append(e)
        if self.mat.kind == "card":
            insort(self.negs, -self.w[e])
        elif self.mat.kind == "part":
            insort(self.negs.setdefault(self.mat.cls[e], []), -self.w[e])

    def spans(self, e: int) -> bool:
        mat, w = self.mat, self.w
        if mat.kind == "card":
            return bisect_left(self.negs, -w[e]) >= mat.k
        if mat.kind == "part":
            return bisect_left(self.negs.get(mat.cls[e], []), -w[e]) >= mat.cap
        parent = list(range(mat.nodes))
        for x in self.items:
            if w[x] > w[e]:
                parent[_find(parent, mat.edges[x][0])] = _find(parent, mat.edges[x][1])
        return _find(parent, mat.edges[e][0]) == _find(parent, mat.edges[e][1])


class _Chosen:
    """Das bisher Angenommene mit schneller Unabhängigkeitsprüfung."""

    def __init__(self, mat: Matroid):
        self.mat = mat
        self.items: list[int] = []
        self.counts: dict = {}
        self.parent = list(range(mat.nodes)) if mat.kind == "wald" else []

    def can_add(self, e: int) -> bool:
        mat = self.mat
        if mat.kind == "card":
            return len(self.items) < mat.k
        if mat.kind == "part":
            return self.counts.get(mat.cls[e], 0) < mat.cap
        return _find(self.parent, mat.edges[e][0]) != _find(self.parent, mat.edges[e][1])

    def add(self, e: int) -> None:
        mat = self.mat
        self.items.append(e)
        if mat.kind == "part":
            self.counts[mat.cls[e]] = self.counts.get(mat.cls[e], 0) + 1
        elif mat.kind == "wald":
            self.parent[_find(self.parent, mat.edges[e][0])] = _find(self.parent, mat.edges[e][1])


REASONS = {
    "stichprobe": "Stichprobe: nur angesehen",
    "aufgespannt": "von schwereren Beobachteten aufgespannt",
    "abhaengig": "abhängig vom Angenommenen",
    "angenommen": "angenommen",
}


def run_rule(mat: Matroid, w, order, rule: str, f: float = 0.37) -> dict:
    """Ein Lauf einer Regel (erst, fest, wachs). Rückgabe: value, chosen (in der Reihenfolge der Annahme), trace [(Position, Element, Nutzen, angenommen?, Grund)], sample (Zahl der nur angesehenen)."""
    n = len(order)
    t = sample_size(n, f) if rule != "erst" else 0
    chosen, observed, trace = _Chosen(mat), _Observed(mat, w), []
    ref = _Observed(mat, w)                                  # nur für „fest“: die Stichprobe
    for pos, e in enumerate(order):
        if pos < t:
            ok, why = False, "stichprobe"
        else:
            spanned = False if rule == "erst" else (ref.spans(e) if rule == "fest" else observed.spans(e))
            if spanned:
                ok, why = False, "aufgespannt"
            elif not chosen.can_add(e):
                ok, why = False, "abhaengig"
            else:
                ok, why = True, "angenommen"
                chosen.add(e)
        trace.append((pos, e, w[e], ok, why))
        observed.add(e)
        if rule == "fest" and pos < t:
            ref.add(e)
    return {"value": sum(w[e] for e in chosen.items), "chosen": list(chosen.items), "trace": trace, "sample": t}


def run_teil(mat: Matroid, w, order) -> dict:
    """Klassische 1/e-Regel je Farbklasse (nur Partition mit Kapazität 1): in jeder Klasse die ersten ⌊Größe / e⌋ Angebote ansehen, dann das erste annehmen, das alle bisher gesehenen der Klasse übertrifft."""
    if mat.kind != "part" or mat.cap != 1:
        raise ValueError("teil gibt es nur für Farben (Partition, Kapazität 1)")
    size: dict = {}
    for c in mat.cls:
        size[c] = size.get(c, 0) + 1
    seen_cnt: dict = {}
    best: dict = {}
    done: set = set()
    chosen, trace, sample = [], [], 0
    for pos, e in enumerate(order):
        c = mat.cls[e]
        seen_cnt[c] = seen_cnt.get(c, 0) + 1
        t = int(size[c] / EULER + 1e-9)
        if seen_cnt[c] <= t:
            ok, why = False, "stichprobe"
            sample += 1
        elif c in done:
            ok, why = False, "abhaengig"
        elif w[e] > best.get(c, -1):
            ok, why = True, "angenommen"
            chosen.append(e)
            done.add(c)
        else:
            ok, why = False, "aufgespannt"
        trace.append((pos, e, w[e], ok, why))
        best[c] = max(best.get(c, -1), w[e])
    return {"value": sum(w[e] for e in chosen), "chosen": chosen, "trace": trace, "sample": sample}


def run_any(mat: Matroid, w, order, rule: str, f: float = 0.37) -> dict:
    return run_teil(mat, w, order) if rule == "teil" else run_rule(mat, w, order, rule, f)


# --- Exakte Erwartung über alle Reihenfolgen (kleine Fälle; Orakel für die Tests und das Handbeispiel) ---------------------------------------------


def expectation(mat: Matroid, w, rule: str, f: float = 0.37) -> dict:
    """Aufzählung aller n! Reihenfolgen (n ≤ 8): Erwartung als Bruch, schlechteste und beste Reihenfolge, Zahl der Reihenfolgen mit Offline-Wert."""
    n = mat.n
    if n > 8:
        raise ValueError("Aufzählung nur bis 8 Elemente")
    opt, _ = offline(mat, w)
    vals = [run_any(mat, w, list(o), rule, f)["value"] for o in itertools.permutations(range(n))]
    total = len(vals)
    return {"expected": Fraction(sum(vals), total), "worst": min(vals), "best": max(vals), "optimal_orders": sum(1 for v in vals if v == opt), "orders": total, "opt": opt}


def classical_success(n: int, t: int) -> Fraction:
    """Klassische Sekretärregel mit Stichprobe t (t ≥ 1): Wahrscheinlichkeit, das beste von n Angeboten zu wählen: (t/n) · Σ_{j=t+1}^{n} 1/(j − 1)."""
    if t < 1 or t >= n:
        return Fraction(1, n) if t == 0 else Fraction(0)
    return Fraction(t, n) * sum(Fraction(1, j - 1) for j in range(t + 1, n + 1))
