"""Kennzahlen, Experimente und Verdikte. Alle sichtbaren Zahlen kommen aus diesen Funktionen."""

import random
import statistics
from dataclasses import dataclass
from functools import lru_cache

import msk_algorithm as A
import msk_constants as C
from msk_scenario import arrival_order, complete_edges, draw_weights, make_instance


def de(x: float, digits: int = 1) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def num(x: float) -> str:
    """Ganze Zahl ohne, sonst mit bis zu drei Nachkommastellen (Dezimalkomma)."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.3f}".rstrip("0").rstrip(".").replace(".", ",")


def prozent(x: float, digits: int = 1) -> str:
    return de(100.0 * x, digits)


def zahl(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


def anteil(x: float) -> str:
    """Anteil am Optimum mit drei Nachkommastellen (Dezimalkomma)."""
    return de(x, 3)


def leitungen(k: int) -> str:
    return "1 Leitung" if k == 1 else f"{k} Leitungen"


@dataclass(frozen=True)
class Settings:
    inst: str = "gross"
    v: int = C.DEFAULT_V                  # Standorte der großen Instanz
    seed: int = C.DEFAULT_SEED
    wdist: str = "geometrisch"
    cons: str = "wald"
    k: int = C.DEFAULT_K
    oseed: int = 7
    okind: str = "zufall"


# --- Instanz und Läufe ----------------------------------------------------------------------------------------------------------------------------


@lru_cache(maxsize=64)
def build(s: Settings) -> dict:
    ins = make_instance(s.inst, s.v, s.seed, s.wdist)
    mat = A.make_matroid(s.cons, ins.m, s.k, ins.edges, ins.n)
    order = arrival_order(ins.weights, s.okind, s.oseed)
    return {"inst": ins, "mat": mat, "order": order, "w": ins.weights}


def rules_for(cons: str) -> tuple[str, ...]:
    return ("erst", "fest", "wachs", "teil") if cons == "farbe" else ("erst", "fest", "wachs")


@lru_cache(maxsize=128)
def run_view(s: Settings, f: float = C.DEFAULT_F) -> dict:
    b = build(s)
    opt, opt_chosen = A.offline(b["mat"], b["w"])
    runs = {rule: A.run_any(b["mat"], b["w"], b["order"], rule, f) for rule in rules_for(s.cons)}
    return {"b": b, "f": f, "opt": opt, "opt_chosen": opt_chosen, "runs": runs, "m": b["mat"].n, "rank": b["mat"].rank()}


def rule_rows(s: Settings, v: dict) -> list[dict]:
    rows = [{"Regel": "Offline-Optimum (alles vorher bekannt)", "Wert": v["opt"], "Anteil am Optimum": "1,000", "angenommen": len(v["opt_chosen"]), "nur angesehen": "–"}]
    for rule, r in v["runs"].items():
        rows.append({"Regel": C.RULE_NAMES[rule], "Wert": r["value"], "Anteil am Optimum": anteil(r["value"] / v["opt"]), "angenommen": len(r["chosen"]), "nur angesehen": str(r["sample"]) if rule != "erst" else "–"})
    return rows


def trace_rows(v: dict, rule: str) -> list[dict]:
    ins = v["b"]["inst"]
    return [{"Nr.": pos + 1, "Leitung": ins.label(e), "Nutzen": zahl(w), "Entscheidung": "angenommen" if ok else "verworfen", "Grund": A.REASONS[why]} for pos, e, w, ok, why in v["runs"][rule]["trace"]]


def verdict_run(s: Settings, v: dict) -> tuple[str, str]:
    opt, runs = v["opt"], v["runs"]
    if any(r["value"] > opt for r in runs.values()):
        return "error", "Ein Online-Verfahren übertrifft das Offline-Optimum: Das ist ein Fehler in der Rechnung."
    wa, fe, er = runs["wachs"], runs["fest"], runs["erst"]
    text = (f"Offline (alle **{zahl(v['m'])}** Angebote vorher bekannt, Greedy) ergibt **{zahl(opt)}** mit {leitungen(len(v['opt_chosen']))}. "
            f"Wachsende Stichprobe (f = {de(v['f'], 2)}, {wa['sample']} nur angesehen): **{zahl(wa['value'])}** ({prozent(wa['value'] / opt)} %); "
            f"feste Stichprobe: **{zahl(fe['value'])}** ({prozent(fe['value'] / opt)} %); erst kommt, erst bekommt: **{zahl(er['value'])}** ({prozent(er['value'] / opt)} %). ")
    if "teil" in runs:
        text += f"Klassische 1/e-Regel je Farbe: **{zahl(runs['teil']['value'])}** ({prozent(runs['teil']['value'] / opt)} %). "
    best = max(runs.values(), key=lambda r: r["value"])["value"]
    winners = [C.RULE_NAMES[k] for k, r in runs.items() if r["value"] == best]
    text += f"Am besten ist hier: **{' und '.join(winners)}**."
    if wa["value"] == 0 and fe["value"] == 0:
        text += " Die Stichprobenregeln nehmen nichts an: Das wertvollste Angebot liegt in der Stichprobe, alles Spätere wird davon aufgespannt."
    return "info", text


# --- Messreihen -----------------------------------------------------------------------------------------------------------------------------------


def _stats(xs):
    xs = sorted(xs)
    return {"med": statistics.median(xs), "mean": statistics.mean(xs), "min": xs[0]}


def measure(make, rules: dict, instances: int, orders: int, seed: int, okind: str = "zufall") -> dict:
    """Je Instanz: Mittel von Wert/Optimum über zufällige Reihenfolgen (bei fester Reihenfolge ist es eine); danach Median, Mittel und Minimum über die Instanzen.
    make(rng, i) liefert (Matroid, Nutzen); rules: {Name: (Regel, f)}."""
    rng = random.Random(seed)
    res = {key: [] for key in rules}
    for i in range(instances):
        mat, w = make(rng, i)
        opt = A.offline(mat, w)[0]
        acc = {key: 0.0 for key in rules}
        count = orders if okind == "zufall" else 1
        for _ in range(count):
            order = arrival_order(w, okind, rng.randrange(10 ** 9))
            for key, (rule, f) in rules.items():
                acc[key] += A.run_any(mat, w, order, rule, f)["value"] / opt
        for key in rules:
            res[key].append(acc[key] / count)
    return {key: _stats(vals) for key, vals in res.items()}


def _card(n, k, dist):
    def make(rng, i):
        return A.make_matroid("card", n, k), draw_weights(dist, n, rng)
    return make


def _wald(v, dist):
    edges = complete_edges(v)

    def make(rng, i):
        return A.make_matroid("wald", len(edges), 0, edges, v), draw_weights(dist, len(edges), rng)
    return make


def _farbe(n, classes, dist):
    def make(rng, i):
        return A.make_matroid("farbe", n, classes), draw_weights(dist, n, rng)
    return make


# Experiment 1: Stichprobenanteil gegen k (Kardinalität)


def ex1_series() -> list[dict]:
    rows = []
    for k in C.EX1_KS:
        rules = {"erst": ("erst", 0.0)}
        for f in C.F_CHOICES:
            rules[f"fest{f}"] = ("fest", f)
            rules[f"wachs{f}"] = ("wachs", f)
        r = measure(_card(C.EX1_N, k, "gleich"), rules, C.EX1_INSTANCES, C.EX1_ORDERS, C.SERIES_SEED + k)
        fest = {f: r[f"fest{f}"]["med"] for f in C.F_CHOICES}
        wachs = {f: r[f"wachs{f}"]["med"] for f in C.F_CHOICES}
        rows.append({"k": k, "erst": r["erst"]["med"], "fest": fest, "wachs": wachs, "best_fest": max(fest, key=fest.get), "best_wachs": max(wachs, key=wachs.get)})
    return rows


def ex1_table(rows) -> list[dict]:
    out = []
    for r in rows:
        for name, key in (("Feste Stichprobe", "fest"), ("Wachsende Stichprobe", "wachs")):
            row = {"k": r["k"], "Regel": name}
            for f in C.F_CHOICES:
                row[f"f = {de(f, 2)}"] = anteil(r[key][f])
            row["erst kommt"] = anteil(r["erst"])
            out.append(row)
    return out


def verdict_ex1(rows) -> tuple[str, str]:
    bad = [r for r in rows if max(r["fest"].values()) > 1 + 1e-9 or max(r["wachs"].values()) > 1 + 1e-9]
    if bad:
        return "error", "Ein Anteil liegt über 1: Das ist ein Fehler in der Rechnung."
    ks = " / ".join(str(r["k"]) for r in rows)
    bf = " / ".join(de(r["best_wachs"], 2) for r in rows)
    bv = " / ".join(anteil(r["wachs"][r["best_wachs"]]) for r in rows)
    er = " / ".join(anteil(r["erst"]) for r in rows)
    w7 = " bis ".join(anteil(x) for x in (min(r["wachs"][0.7] for r in rows), max(r["wachs"][0.7] for r in rows)))
    return "info", (f"Bei k = {ks} liegt das beste f der wachsenden Stichprobe bei **{bf}** mit Anteil **{bv}** am Offline-Optimum; erst kommt, erst bekommt erreicht **{er}**. "
                    f"Das beste f hängt von k ab (nicht überall 1/e); mit f = 0,7 sind es nur **{w7}**: Wer zu lange nur zusieht, verschenkt die Plätze.")


# Experiment 2: Gewichtsverteilungen


def ex2_series() -> list[dict]:
    rules = {"erst": ("erst", 0.0), "fest": ("fest", 0.5), "wachs": ("wachs", 0.37)}
    rows = []
    for name, mk in (("Kardinalität 10 (100 Angebote)", lambda d: _card(C.EX2_CARD_N, C.EX2_CARD_K, d)), (f"Wald (vollständiger Graph, {C.EX2_WALD_V} Standorte)", lambda d: _wald(C.EX2_WALD_V, d))):
        for dist in C.WEIGHTS:
            r = measure(mk(dist), rules, C.EX2_INSTANCES, C.EX2_ORDERS, C.SERIES_SEED + 20)
            rows.append({"matroid": name, "dist": dist, "erst": r["erst"]["med"], "fest": r["fest"]["med"], "wachs": r["wachs"]["med"], "wachs_min": r["wachs"]["min"], "erst_min": r["erst"]["min"]})
    return rows


def ex2_table(rows) -> list[dict]:
    return [{"Nebenbedingung": r["matroid"], "Nutzen": C.WEIGHT_NAMES[r["dist"]], "erst kommt": anteil(r["erst"]), "feste Stichprobe (f = 0,5)": anteil(r["fest"]), "wachsende Stichprobe (f = 0,37)": anteil(r["wachs"]), "Minimum (wachsend)": anteil(r["wachs_min"])} for r in rows]


def verdict_ex2(rows) -> tuple[str, str]:
    if any(max(r["erst"], r["fest"], r["wachs"]) > 1 + 1e-9 for r in rows):
        return "error", "Ein Anteil liegt über 1: Das ist ein Fehler in der Rechnung."
    by = {(r["matroid"][:4], r["dist"]): r for r in rows}
    kg, wg = by[("Kard", "geometrisch")], by[("Wald", "geometrisch")]
    kl, wl = by[("Kard", "gleich")], by[("Wald", "gleich")]
    kc = by[("Kard", "konstant")]
    return "info", (f"Bei gleichverteilten Nutzen: Kardinalität erst **{anteil(kl['erst'])}**, wachsend **{anteil(kl['wachs'])}**; Wald erst **{anteil(wl['erst'])}**, wachsend **{anteil(wl['wachs'])}**. "
                    f"Bei verdoppelnden Nutzen: Kardinalität erst **{anteil(kg['erst'])}**, wachsend **{anteil(kg['wachs'])}**; Wald erst **{anteil(wg['erst'])}**, wachsend **{anteil(wg['wachs'])}**. "
                    f"Sind alle Nutzen gleich, ist alles optimal (**{anteil(kc['erst'])}**): Dann gibt es nichts Schwereres, das aufspannt. Bei ungleichen Nutzen (verdoppelnd) ist der Gewinn der Stichprobe größer als bei gleichverteilten.")


# Experiment 3: Reihenfolge


def ex3_series() -> list[dict]:
    rules = {"erst": ("erst", 0.0), "fest": ("fest", 0.5), "wachs": ("wachs", 0.37)}
    rows = []
    for name, mk in (("Kardinalität 10 (100 Angebote)", _card(C.EX2_CARD_N, C.EX2_CARD_K, "gleich")), (f"Wald ({C.EX2_WALD_V} Standorte)", _wald(C.EX2_WALD_V, "gleich"))):
        for kind in C.ORDERS:
            r = measure(mk, rules, C.EX3_INSTANCES if kind != "zufall" else C.EX2_INSTANCES, C.EX2_ORDERS, C.SERIES_SEED + 30, okind=kind)
            rows.append({"matroid": name, "okind": kind, "erst": r["erst"]["med"], "fest": r["fest"]["med"], "wachs": r["wachs"]["med"]})
    return rows


def ex3_table(rows) -> list[dict]:
    return [{"Nebenbedingung": r["matroid"], "Reihenfolge": C.ORDER_NAMES[r["okind"]].split(" (")[0], "erst kommt": anteil(r["erst"]), "feste Stichprobe (f = 0,5)": anteil(r["fest"]), "wachsende Stichprobe (f = 0,37)": anteil(r["wachs"])} for r in rows]


def verdict_ex3(rows) -> tuple[str, str]:
    by = {(r["matroid"][:4], r["okind"]): r for r in rows}
    kz, ka, kd = (by[("Kard", k)] for k in C.ORDERS)
    wz, wa, wd = (by[("Wald", k)] for k in C.ORDERS)
    if kd["wachs"] > 1e-9 or wd["wachs"] > 1e-9:
        return "error", "Bei absteigender Reihenfolge darf eine Stichprobenregel nichts annehmen: Das ist ein Fehler in der Rechnung."
    return "info", (f"Bei zufälliger Reihenfolge: wachsende Stichprobe **{anteil(kz['wachs'])}** (Kardinalität) und **{anteil(wz['wachs'])}** (Wald). "
                    f"**Absteigend** (wertvolle zuerst) nehmen beide Stichprobenregeln in der Regel **nichts** an (Median **{anteil(kd['wachs'])}**), erst kommt, erst bekommt ist dort optimal (**{anteil(kd['erst'])}**). "
                    f"**Aufsteigend** (wertvolle zuletzt) fällt erst kommt, erst bekommt auf **{anteil(ka['erst'])}** und **{anteil(wa['erst'])}**. Die Zufallsreihenfolge ist die tragende Annahme.")


# Experiment 4: Rang


def ex4_series() -> list[dict]:
    rules = {"erst": ("erst", 0.0), "fest": ("fest", 0.3), "wachs": ("wachs", 0.37)}
    rows = []
    for dist in ("gleich", "geometrisch"):
        for v, inst, orders in C.EX4_SIZES:
            r = measure(_wald(v, dist), rules, inst, orders, C.SERIES_SEED + 40 + v)
            rows.append({"dist": dist, "v": v, "rank": v - 1, "erst": r["erst"]["med"], "fest": r["fest"]["med"], "wachs": r["wachs"]["med"], "wachs_min": r["wachs"]["min"]})
    return rows


def ex4_table(rows) -> list[dict]:
    return [{"Nutzen": C.WEIGHT_NAMES[r["dist"]].split(" (")[0], "Standorte": r["v"], "Rang": r["rank"], "erst kommt": anteil(r["erst"]), "feste Stichprobe (f = 0,3)": anteil(r["fest"]), "wachsende Stichprobe (f = 0,37)": anteil(r["wachs"]), "Minimum (wachsend)": anteil(r["wachs_min"])} for r in rows]


def verdict_ex4(rows) -> tuple[str, str]:
    if any(max(r["erst"], r["fest"], r["wachs"]) > 1 + 1e-9 for r in rows):
        return "error", "Ein Anteil liegt über 1: Das ist ein Fehler in der Rechnung."
    g = [r for r in rows if r["dist"] == "geometrisch"]
    q = [r for r in rows if r["dist"] == "gleich"]
    ranks = " / ".join(str(r["rank"]) for r in g)
    return "info", (f"Bei verdoppelnden Nutzen und Rang {ranks} liegt die wachsende Stichprobe bei **{' / '.join(anteil(r['wachs']) for r in g)}**, erst kommt, erst bekommt bei **{' / '.join(anteil(r['erst']) for r in g)}**. "
                    f"Bei gleichverteilten Nutzen: wachsend **{' / '.join(anteil(r['wachs']) for r in q)}**, erst **{' / '.join(anteil(r['erst']) for r in q)}**. "
                    f"Der Anteil der Stichprobenregel fällt in diesem Bereich nicht mit dem Rang; ob ein konstanter Faktor für **alle** Matroide möglich ist, ist offen, und diese kleinen Fälle beweisen dazu nichts.")


# Experiment 5: Kosten der Stichprobe, allgemeine gegen spezielle Regel


def ex5_series() -> list[dict]:
    n = C.EX5_N
    cases = (("Freies Matroid (alles darf mit)", _card(n, n, "gleich"), False), ("60 Einerklassen (jede Farbe einmal)", _farbe(n, n, "gleich"), False),
             ("30 Farben zu je 2 Angeboten", _farbe(n, n // 2, "gleich"), True), ("6 Farben zu je 10 Angeboten", _farbe(n, 6, "gleich"), True))
    rows = []
    for i, (name, mk, has_teil) in enumerate(cases):
        rules = {"erst": ("erst", 0.0), "fest": ("fest", 0.5), "wachs": ("wachs", 0.37)}
        if has_teil:
            rules["teil"] = ("teil", 0.0)
        r = measure(mk, rules, C.EX5_INSTANCES, C.EX5_ORDERS, C.SERIES_SEED + 50 + i)
        rows.append({"case": name, "erst": r["erst"]["med"], "fest": r["fest"]["med"], "wachs": r["wachs"]["med"], "teil": r["teil"]["med"] if has_teil else None})
    return rows


def ex5_table(rows) -> list[dict]:
    return [{"Fall": r["case"], "erst kommt": anteil(r["erst"]), "feste Stichprobe (f = 0,5)": anteil(r["fest"]), "wachsende Stichprobe (f = 0,37)": anteil(r["wachs"]), "klassische 1/e-Regel je Farbe": anteil(r["teil"]) if r["teil"] is not None else "–"} for r in rows]


def verdict_ex5(rows) -> tuple[str, str]:
    if any(max(r["erst"], r["fest"], r["wachs"], r["teil"] or 0) > 1 + 1e-9 for r in rows):
        return "error", "Ein Anteil liegt über 1: Das ist ein Fehler in der Rechnung."
    free, six = rows[0], rows[3]
    return "info", (f"Beim **freien Matroid** (alles darf mit) ist erst kommt, erst bekommt optimal (**{anteil(free['erst'])}**); die Stichprobe kostet ihren Anteil: f = 0,5 liefert **{anteil(free['fest'])}**, f = 0,37 wachsend **{anteil(free['wachs'])}**. "
                    f"Bei 6 Farben zu je 10 Angeboten schlägt die **klassische Regel je Farbe** (**{anteil(six['teil'])}**) die allgemeine Matroid-Regel (**{anteil(six['wachs'])}**): Wer die Struktur kennt, nutzt sie.")


# --- Spielwiese: Sie sind der Planer ---------------------------------------------------------------------------------------------------------------


def play_state(s: Settings, decisions: list[bool]) -> dict:
    """Stand der Spielwiese: decisions[i] ist Ihre Entscheidung zu Angebot i der Reihenfolge (True = angenommen). Zeigt das nächste Angebot und ob es annehmbar ist."""
    b = build(s)
    order, mat, w = b["order"], b["mat"], b["w"]
    chosen = [order[i] for i, d in enumerate(decisions) if d]
    pos = len(decisions)
    done = pos >= len(order)
    nxt = None if done else order[pos]
    return {"b": b, "chosen": chosen, "pos": pos, "done": done, "next": nxt, "can_accept": False if done else mat.can_add(chosen, nxt), "value": sum(w[e] for e in chosen)}


def verdict_play(s: Settings, state: dict, v: dict) -> tuple[str, str]:
    """v: run_view der Einstellungen. Während des Spiels eine Zeile, am Ende der Vergleich."""
    ins, w = state["b"]["inst"], state["b"]["w"]
    if not state["done"]:
        e = state["next"]
        hint = "" if state["can_accept"] else " Sie können es nur verwerfen: Mit dem Angenommenen entstünde ein Ring (oder die Grenze wäre erreicht)."
        return "info", f"Angebot {state['pos'] + 1} von {zahl(len(state['b']['order']))}: Leitung **{ins.label(e)}** mit Nutzen **{zahl(w[e])}**. Bisher angenommen: {leitungen(len(state['chosen']))} (Wert **{zahl(state['value'])}**).{hint}"
    opt = v["opt"]
    wa, er = v["runs"]["wachs"]["value"], v["runs"]["erst"]["value"]
    if state["value"] > opt:
        return "error", "Ihr Wert liegt über dem Offline-Optimum: Das ist ein Fehler in der Rechnung."
    kind = "success" if state["value"] >= wa else "info"
    return kind, (f"Fertig: Sie haben **{zahl(state['value'])}** ({prozent(state['value'] / opt)} % des Offline-Optimums **{zahl(opt)}**). Die wachsende Stichprobe (f = {de(v['f'], 2)}) hätte **{zahl(wa)}** erreicht, "
                  f"erst kommt, erst bekommt **{zahl(er)}**.")
