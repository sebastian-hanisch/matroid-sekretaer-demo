"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

V_MIN, V_MAX, DEFAULT_V = 6, 16, 12          # Standorte der großen Instanz (vollständiger Graph: v (v − 1) / 2 mögliche Leitungen, Rang v − 1)
PLAN_NODES, PLAN_EDGES = 8, 14               # der Plan der Reihe
SEED_MAX, DEFAULT_SEED = 999999, 8
K_MIN, K_MAX, DEFAULT_K = 1, 20, 3           # Kardinalität: höchstens k Leitungen; Farben: k Kabelfarben
INSTANCES = ("plan", "gross")
INSTANCE_NAMES = {"plan": "Plan der Reihe (8 Standorte, 14 Leitungen)", "gross": "Großer Plan (vollständiger Graph, bis 16 Standorte)"}
CONSTRAINTS = ("card", "farbe", "wald")
CONSTRAINT_NAMES = {"card": "Kardinalität: höchstens k Leitungen", "farbe": "Farben: höchstens eine Leitung je Kabelfarbe (k Farben)", "wald": "Wald: keine geschlossenen Ringe"}
WEIGHTS = ("gleich", "exp", "pareto", "dominant", "geometrisch", "konstant")
WEIGHT_NAMES = {"gleich": "gleichverteilt (1 bis 100)", "exp": "exponentiell (Mittel 25)", "pareto": "schwerer Rand (Pareto)", "dominant": "ein dominantes Angebot (5 000)", "geometrisch": "verdoppelnd (1 bis 1 048 576)", "konstant": "alle gleich (10)"}
ORDERS = ("zufall", "aufsteigend", "absteigend")
ORDER_NAMES = {"zufall": "zufällig (nach Seed der Reihenfolge)", "aufsteigend": "aufsteigend (wertvolle zuletzt)", "absteigend": "absteigend (wertvolle zuerst)"}
RULES = ("erst", "fest", "wachs", "teil")
RULE_NAMES = {"erst": "Erst kommt, erst bekommt", "fest": "Feste Stichprobe", "wachs": "Wachsende Stichprobe", "teil": "Klassische 1/e-Regel je Farbe"}
F_CHOICES = (0.1, 0.2, 0.3, 0.37, 0.5, 0.7)
DEFAULT_F = 0.37                              # ≈ 1/e: bei Kardinalität 1 ist die wachsende Stichprobe damit die klassische Sekretärregel
DOMINANT_WEIGHT = 5000
CONSTANT_WEIGHT = 10

# Messreihen (alle deterministisch über feste Seeds; Reihenfolge und Gewichte werden daraus gezogen)
SERIES_SEED = 20261123
EX1_N, EX1_KS, EX1_INSTANCES, EX1_ORDERS = 100, (1, 3, 10, 20), 30, 40        # Experiment 1: Kardinalität, Stichprobenanteil
EX2_CARD_N, EX2_CARD_K, EX2_WALD_V, EX2_INSTANCES, EX2_ORDERS = 100, 10, 12, 20, 30   # Experiment 2: Gewichtsverteilungen
EX3_INSTANCES = 30                                                           # Experiment 3: Reihenfolgen (eine Reihenfolge je Instanz)
EX4_SIZES = ((5, 30, 40), (8, 30, 40), (12, 20, 30), (16, 12, 20))              # Experiment 4: (Standorte, Instanzen, Reihenfolgen)
EX5_N, EX5_INSTANCES, EX5_ORDERS = 60, 40, 40                                # Experiment 5: Kosten der Stichprobe

COLOR_CHOSEN = "#2F6B65"
COLOR_OTHER = "rgba(150,150,150,0.55)"
COLOR_OPT = "rgba(217,95,2,0.45)"
COLOR_REJECT = "#b85c5c"
COLOR_NODE = "#4c78a8"
COLOR_ERST = "#b0b0b0"
COLOR_FEST = "#4c78a8"
COLOR_WACHS = "#2F6B65"
COLOR_TEIL = "#d95f02"

PRESETS = {
    "Standardfall (Voreinstellung)": {"inst": "gross", "v": 12, "seed": 8, "wdist": "geometrisch", "cons": "wald", "k": 3, "oseed": 7, "okind": "zufall"},
    "Gutartige Gewichte": {"inst": "plan", "v": 12, "seed": 6, "wdist": "gleich", "cons": "wald", "k": 3, "oseed": 1, "okind": "zufall"},
    "Absteigende Reihenfolge": {"inst": "gross", "v": 12, "seed": 8, "wdist": "geometrisch", "cons": "card", "k": 10, "oseed": 7, "okind": "absteigend"},
    "Farben": {"inst": "gross", "v": 12, "seed": 8, "wdist": "gleich", "cons": "farbe", "k": 6, "oseed": 7, "okind": "zufall"},
    "Freie Wahl": {"inst": "plan", "v": 12, "seed": 8, "wdist": "gleich", "cons": "card", "k": 14, "oseed": 1, "okind": "zufall"},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Großer Plan mit 12 Standorten (66 Leitungen), verdoppelnde Nutzen, keine geschlossenen Ringe, zufällige Reihenfolge. Die wachsende Stichprobe erreicht 0,56 des Offline-Optimums, erst kommt, erst bekommt nur 0,21.",
    "Gutartige Gewichte": "Plan der Reihe (8 Standorte, 14 Leitungen), gleichverteilte Nutzen, keine Ringe: Hier gewinnt erst kommt, erst bekommt (0,84 gegen 0,55 der wachsenden Stichprobe). Das Beobachten zahlt sich erst bei schiefen Nutzen aus.",
    "Absteigende Reihenfolge": "Kardinalität 10, die wertvollsten Angebote kommen zuerst: Beide Stichprobenregeln nehmen nichts an (0,00), erst kommt, erst bekommt ist optimal (1,00). Die Zufallsreihenfolge ist die tragende Annahme.",
    "Farben": "66 Leitungen in 6 Kabelfarben, höchstens eine je Farbe, gleichverteilte Nutzen: Die klassische 1/e-Regel je Farbe erreicht 0,64, die wachsende Stichprobe 0,55, erst kommt, erst bekommt 0,51.",
    "Freie Wahl": "Plan der Reihe mit Kardinalität 14: Alle 14 Leitungen dürfen mit. Erst kommt, erst bekommt ist optimal (1,00), die Stichprobe kostet ihren Anteil (0,64).",
}
