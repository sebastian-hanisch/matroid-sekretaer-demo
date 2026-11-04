"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import msk_algorithm as A  # noqa: E402


@pytest.fixture
def card1():
    """Vier Leitungen mit Nutzen 10, 8, 5, 2, höchstens eine (Kardinalität 1)."""
    return A.make_matroid("card", 4, 1), [10, 8, 5, 2]


@pytest.fixture
def card2():
    """Dieselben Nutzen, höchstens zwei. Optimum 18."""
    return A.make_matroid("card", 4, 2), [10, 8, 5, 2]


@pytest.fixture
def wald():
    """Dreieck mit ab = 9, bc = 6, ac = 4 und Pendelkante cd = 1 (Knoten a bis d = 0 bis 3). Optimum Greedy: ab, bc, cd = 16."""
    return A.make_matroid("wald", 4, 0, [(0, 1), (1, 2), (0, 2), (2, 3)], 4), [9, 6, 4, 1]


@pytest.fixture
def farben():
    """Sechs Leitungen in zwei Farben ({0, 1, 2} und {3, 4, 5} über cls), Nutzen 5, 9, 3 und 2, 8, 4. Optimum 9 + 8 = 17."""
    return A.Matroid("part", 6, cls=(0, 0, 0, 1, 1, 1), cap=1), [5, 9, 3, 2, 8, 4]
