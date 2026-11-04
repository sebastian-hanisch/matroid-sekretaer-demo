# Matroid-Sekretärproblem – Angebote nacheinander – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-matroid-sekretaer-demo.streamlit.app/)** -->

Dreizehntes Stück der Reihe **Matroide und Submodularität** (Bereich Kombinatorik; ein **gelbes** Stück, einzeln nach Stück 12 entschieden) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Stücke davor haben alle Leitungsangebote **vorher** gesehen. Hier kommen sie **nacheinander** in zufälliger Reihenfolge, jedes ist **sofort anzunehmen oder zu verwerfen, endgültig**, und das Angenommene muss unabhängig bleiben (höchstens k Leitungen, höchstens eine je Farbe, keine geschlossenen Ringe). Die Frage: **Wie viel vom Offline-Optimum (Greedy, Stück 1 und 5) bleibt?** Drei Regeln auf **derselben Reihenfolge**: **erst kommt, erst bekommt**, **feste Stichprobe** und **wachsende Stichprobe**; bei Farben dazu die **klassische 1/e-Regel je Farbe**.

**Einordnung in die Reihe:** Nachfolger von [ueber-greedy-demo](../ueber-greedy-demo) (Stück 12), [greedy-optimalitaet-demo](../greedy-optimalitaet-demo) (Stück 5) und [greedy-austausch-demo](../greedy-austausch-demo) (Stück 1). **Abgrenzung:** `sekretaerproblem-demo` (Online-Algorithmen) zeigt das klassische Problem mit **einem** Zuschlag und der 1/e-Regel; hier mehrere Zuschläge unter einer Matroidschranke mit **Nutzen**. Streaming (Stück 12) ist ein anderes Modell: beliebige Reihenfolge, knapper Speicher. Bandits (Stück 14, gelb) lernen Nutzen über viele Runden; hier gibt es einen einzigen Durchlauf.

## Warum dieses Problem

Wer Angebote erst nach und nach sieht, kennt das Optimum nicht, wenn er entscheiden muss. Offen ist, wie viel ein einfaches Verfahren von Greedys Optimum retten kann, wovon das abhängt (Nutzen, Reihenfolge, Rang, Struktur der Nebenbedingung) und wann das **Zusehen** mehr kostet, als es bringt.

## Befunde und Korrekturen gegenüber dem Plan

- **Die Stichprobe ist kein Gewinn an sich.** Bei gleichverteilten Nutzen und kleinen Plänen schlägt „erst kommt, erst bekommt“ die Regeln mit Stichprobe (Preset „Gutartige Gewichte“: 14 Angebote bei Rang 7). Die Stichprobe zahlt sich aus, wenn es deutlich mehr Angebote als Plätze (Rang) gibt, bei ungleichen Nutzen noch mehr (Experiment 2 und 4).
- **Die Reihenfolge ist die Annahme, nicht ein Detail:** Kommen die wertvollsten Angebote zuerst, nehmen beide Stichprobenregeln in der Regel nichts an (Median 0,000; beim Wald in einzelnen Instanzen doch etwas), „erst kommt, erst bekommt“ ist dort optimal.
- **Die allgemeine Regel ist nicht die beste Spezialregel:** Bei 6 Farben zu je 10 Angeboten schlägt die klassische 1/e-Regel je Farbe die Matroid-Regel (0,645 gegen 0,594); bei Klassen der Größe 2 ist sie gleich „erst kommt, erst bekommt“ (Experiment 5).
- **Das beste f hängt von k ab.** 1/e ist bei Kardinalität 1 die richtige Zahl für die Wahrscheinlichkeit, das **beste** Angebot zu wählen; für den erwarteten **Gewichtsanteil** ist bei gleichverteilten Nutzen ein kleineres f besser (bestes f des Gitters 0,1 bis 0,7: 0,1 bei k = 1, 0,3 bei k = 10 und 20; Experiment 1).
- **Bei Kardinalität 1 und bei Farben mit Kapazität 1 sind feste und wachsende Stichprobe gleich** (gemessen und getestet). Grund: Wäre vor einem Angebot e ein schwereres Angebot derselben Farbe nach der Stichprobe gekommen, hätte die feste Regel dieses schon angenommen und die Farbe wäre belegt; so entscheiden beide Regeln gleich.
- **Die Vermutung „konstanter Faktor für alle Matroide“ ist offen;** die Messung widerlegt sie nicht (der Anteil fällt von Rang 4 bis 15 nicht), beweist sie aber auch nicht. Konkrete Faktoren der Literatur sind **nicht** belegt und deshalb in der Demo nicht genannt.
- **Die Regeln „feste“ und „wachsende Stichprobe“ sind Bezeichnungen dieser Demo,** keine zitierten Algorithmen.
- **Port 9353;** Repo `matroid-sekretaer-demo`, Präfix `msk_`; nur Streamlit, Plotly und fpdf2 zur Laufzeit (reine Python-Ganzzahlen, kein numpy). Die Zahlen der App weichen von den Messungen der Planung leicht ab (ganze Nutzen, andere Instanzen und Seeds).

## Modell

**Leitungsnetz mit Nutzen:** Standorte im Einheitsquadrat, jede mögliche Leitung hat einen positiven ganzzahligen Nutzen. **Zwei Instanzen:** der **Plan der Reihe** (8 Standorte, 14 zufällige Leitungen, zusammenhängend) und der **große Plan** (alle Leitungen zwischen v = 6 bis 16 Standorten, bis 120 Angebote). **Nutzen:** gleichverteilt (1 bis 100), exponentiell (Mittel 25), schwerer Rand (Pareto, α = 1,5), ein dominantes Angebot (5 000), verdoppelnd (2^(20 i / (m − 1)), also 1 bis 1 048 576, gemischt) oder alle gleich (10). **Nebenbedingung:** Kardinalität (höchstens k), Farben (höchstens eine Leitung je Kabelfarbe; Leitung e hat die Farbe e mod k) oder Wald (keine geschlossenen Ringe). **Reihenfolge:** zufällig nach Seed, aufsteigend oder absteigend nach Nutzen. Formeln: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Offline-Optimum:** `offline`: Greedy nach absteigendem Nutzen (Gleichstand: kleinere Nummer), Rado–Edmonds.
- **Regeln:** `run_rule` (erst, fest, wachs) mit Protokoll je Angebot (Stichprobe / von schwereren Beobachteten aufgespannt / abhängig vom Angenommenen / angenommen); `run_teil` (klassische 1/e-Regel je Farbe, nur Kapazität 1). Aufspannen: bei Kardinalität bei k schwereren Beobachteten, bei Farben bei einem schwereren Beobachteten gleicher Farbe, im Wald bei Verbindung der Endpunkte durch schwerere Beobachtete. Gleichstand spannt nichts auf (Setzung der Demo).
- **Exakt für kleine Fälle:** `expectation` zählt alle n! Reihenfolgen (n ≤ 8) und gibt die Erwartung als Bruch; `classical_success` ist die klassische Formel (t/n) · Σ 1/(j − 1).
- **Messreihen:** `measure` mittelt je Instanz Wert/Optimum über zufällige Reihenfolgen und nimmt dann den Median über die Instanzen; alles über feste Seeds (kein Löser, plattformunabhängig).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py` und werden dort mit den Funktionen der App nachgerechnet. Zufällige Reihenfolgen, f = 0,37 (wo nicht anders genannt).

| Beispiel | Angebote | Rang | Offline | erst kommt | feste Stichprobe | wachsende Stichprobe | 1/e-Regel je Farbe |
|---|---|---|---|---|---|---|---|
| Standardfall (12 Standorte, verdoppelnd, Wald) | 66 | 11 | 4 827 444 | 1 037 873 (0,215) | 1 864 749 (0,386) | 2 710 518 (0,561) | – |
| Gutartige Gewichte (Plan, gleichverteilt, Wald) | 14 | 7 | 405 | 340 (0,840) | 249 (0,615) | 221 (0,546) | – |
| Absteigende Reihenfolge (Kardinalität 10) | 66 | 10 | 4 812 434 | 4 812 434 (1,000) | 0 (0,000) | 0 (0,000) | – |
| Farben (6 Farben, gleichverteilt) | 66 | 6 | 551 | 283 (0,514) | 301 (0,546) | 301 (0,546) | 350 (0,635) |
| Freie Wahl (Plan, Kardinalität 14) | 14 | 14 | 578 | 578 (1,000) | 370 (0,640) | 370 (0,640) | – |

| Frage | Befund |
|---|---|
| **Experiment 1: wie lange zusehen?** (Kardinalität, 100 gleichverteilte Angebote, 30 Instanzen × 40 Reihenfolgen, Median) | Bestes f der wachsenden Stichprobe bei k = 1 / 3 / 10 / 20: **0,10 / 0,20 / 0,30 / 0,30** mit Anteil **0,905 / 0,917 / 0,896 / 0,867**; erst kommt, erst bekommt **0,510 / 0,510 / 0,527 / 0,563**; mit f = 0,7 nur **0,353 bis 0,399** (Gitter f = 0,1 bis 0,7; mit anderen Seeds schwankt schon die zweite Nachkommastelle). |
| **Experiment 2: Verteilung der Nutzen** (Kardinalität 10 mit 100 Angeboten und Wald auf K_12; 20 Instanzen × 30 Reihenfolgen) | Gleichverteilt: Kardinalität erst **0,543**, wachsend **0,851**; Wald erst **0,565**, wachsend **0,762**. Verdoppelnd: Kardinalität erst **0,125**, wachsend **0,630**; Wald erst **0,187**, wachsend **0,540**. Alle Nutzen gleich: **1,000** bei allen Regeln (Median; beim Wald fällt die feste Stichprobe mit f = 0,5 in seltenen Reihenfolgen darunter). |
| **Experiment 3: Reihenfolge** (gleichverteilt, Kardinalität 10 und Wald K_12) | Zufällig: wachsend **0,852** und **0,757**. **Absteigend:** beide Stichprobenregeln **0,000**, erst kommt, erst bekommt **1,000**. **Aufsteigend:** erst kommt, erst bekommt **0,063** und **0,119**. |
| **Experiment 4: Rang** (Wald auf K_v, Rang 4 / 7 / 11 / 15) | Verdoppelnd: wachsend **0,544 / 0,500 / 0,527 / 0,554**, erst **0,394 / 0,270 / 0,198 / 0,165**. Gleichverteilt: wachsend **0,704 / 0,713 / 0,748 / 0,780**, erst **0,642 / 0,597 / 0,562 / 0,555**. |
| **Experiment 5: Kosten der Stichprobe** (60 gleichverteilte Angebote) | Freies Matroid: erst **1,000**, fest 0,5 **0,503**, wachsend **0,634**. 60 Einerklassen: 1,000 / 0,502 / 0,633. 30 Farben zu je 2: erst 0,749, fest 0,447, wachsend 0,538, **klassisch je Farbe 0,749**. 6 Farben zu je 10: erst 0,541, fest 0,495, wachsend **0,594**, **klassisch je Farbe 0,645**. |
| **Handbeispiel Kardinalität 1** (Nutzen 10, 8, 5, 2; alle 24 Reihenfolgen, exakt) | Stichprobe 1: Erwartung **20/3**, bestes Angebot in **11/24** der Reihenfolgen; Stichprobe 2: Erwartung **29/6**, bestes in **10/24**; erst kommt, erst bekommt **25/4** (schlechteste Reihenfolge 2). |
| **Handbeispiel Wald** (Dreieck ab = 9, bc = 6, ac = 4, Pendelkante cd = 1; Optimum 16) | Reihenfolge cd, ac, ab, bc mit wachsender Stichprobe 1: cd gesehen, ac und ab angenommen, bc hängt ab (Dreieck): **13** von 16. Erwartung über alle Reihenfolgen: erst **41/3**, wachsend mit Stichprobe 1 **149/12**. |

## Ehrliche Grenzen

- **Zufällige Reihenfolge.** Das Sekretärmodell setzt sie voraus; absteigend und aufsteigend zeigen, was passiert, wenn sie verletzt ist.
- **Gleichstände spannen nichts auf.** Das ist eine Setzung der Demo (bei gleichen Nutzen sind alle Regeln optimal, wenn genug Angebote nach der Stichprobe bleiben); die Literatur kann es anders regeln.
- **Die Nutzen kommender Angebote sind unbekannt, die Verteilungen auch.** Das Prophet-Modell (Verteilungen bekannt) ist nicht gebaut.
- **Die Regeln sind Bezeichnungen dieser Demo,** keine zitierten Algorithmen; ob sie mit Verfahren der Literatur übereinstimmen, ist nicht geprüft.
- **Nur Kardinalität, Farben und Wald gemessen.** Laminare und Transversal-Matroide fehlen (für sie sind in der Literatur konstante Faktoren bekannt); für allgemeine Matroide ist die Vermutung eines konstanten Faktors offen, kleine Instanzen beweisen dazu nichts.
- **Nutzen aus Verteilungen, nicht von einem Gegner.** Die Zahlen gelten für die gezogenen Instanzen und Seeds (Median über die Instanzen), nicht für den schlechtesten Fall; kein gegnerischer Nutzenentwurf gegen die Regel.
- **Zeit wird nie gemessen.**
- **Quellen nur als Auszüge** (arXiv 2103.04205 zur Äquivalenz mit Contention Resolution, arXiv 2111.04114 zu formalen Schranken; Websuche): konkrete Faktoren und Autoren sind nicht genannt, Primärtexte nicht eingesehen. Die Formel der klassischen Erfolgswahrscheinlichkeit ist bekannt und hier durch Aufzählung geprüft.

## Verifikation

- **Kern:** Offline-Greedy, die drei Regeln, die klassische Regel je Farbe und die exakte Erwartung gegen Handrechnung (`tests/conftest.py`, `tests/test_algorithm.py`); Randfälle: ein und zwei Angebote, leere Stichprobe, Gleichstände, k > Zahl der Angebote, Einerklassen, Instanzerzeugung, Reihenfolgen, Reglerecken, Spielwiese (`tests/test_edge_cases.py`).
- **Orakel** (`tests/test_oracle_sekretaer.py`): „aufgespannt“ gegen die Rangdefinition mit Aufzählung; Rang gegen die größte unabhängige Menge; Offline-Greedy gegen alle unabhängigen Mengen; die schnellen Regeln gegen eine einfache Neufassung auf Zufallsläufen und auf Instanzen der App; die klassische Erfolgswahrscheinlichkeit gegen Aufzählung aller Reihenfolgen (n = 3 bis 7); Erwartung von „erst kommt“ gegen unabhängige Mittelung.
- **Eigenschaften** (`tests/test_properties.py`): jede Ausgabe unabhängig und höchstens so wertvoll wie das Optimum; die Stichprobe wird nie angenommen; Kardinalität 1 gleich der klassischen Regel; Farben mit Kapazität 1: fest gleich wachsend; absteigend: erst optimal, Stichprobenregeln 0; freies Matroid: erst optimal, Stichprobe kostet ihren Anteil; gleiche Nutzen; Reproduzierbarkeit.
- **Verdikte und Presets:** jeder Zweig und jede Zahl der Verdikte; jedes Preset zeigt den versprochenen Effekt; kein einzelner Reglerwechsel trifft ein anderes Preset.
- **Zahlen aus dieser README:** `tests/test_claims.py`.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), Hauptansicht, fünf Experimente, Spielwiese bis zum Ende, Permalink, PDF; Layout (Kopf, Schnellstart, Hervorhebung) und Footer.
- **Umfang:** siehe `pytest --collect-only -q tests`.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: ein Lauf, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `msk_constants.py` | Reglergrenzen, Nutzenverteilungen, Reihenfolgen, Messgrößen, Farben, Presets |
| `msk_scenario.py` | Plan, Leitungen, Nutzen, Reihenfolgen |
| `msk_algorithm.py` | Matroid-Orakel, Offline-Greedy, Regeln mit Protokoll, exakte Erwartung |
| `msk_evaluation.py` | Kennzahlen, Messreihen der Experimente, Spielwiese, Verdikte |
| `msk_visualization.py` | Karte, Ankunftsdiagramm, Balken, Kurven |
| `msk_presets.py` | Permalink, Presets, Zufalls-Seeds |
| `msk_layout.py` | fester Kopf |
| `msk_pdf_export.py` | PDF des aktuellen Beispiels |
| `tests/` | Kern, Orakel, Eigenschaften, Verdikte, Presets, Claims, Randfälle, Oberfläche, Layout, Footer, Importe |

## Bewusst nicht umgesetzt

- Beweise der Faktoren; Prophet-Ungleichungen; Contention Resolution; Online-Matching-Varianten; Sekretärproblem mit Zeit (Einheitsintervall); Knapsack-Sekretär.
- Laminare und Transversal-Matroide; gegnerische Nutzen gegen die Regel.
- Erklärseite „verständlich erklärt“ und Website-Einbindung (erst mit der vollständigen Linie).

## Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pip install -r requirements-dev.txt`, dann `python -m pytest tests -q`. Die CI läuft mit Python 3.12 (`.github/workflows/tests.yml`); die in Streamlit Cloud eingestellte Python-Version ist beim Deploy zu nennen.

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
