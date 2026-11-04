"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import msk_constants as C

REASON_COLORS = {"stichprobe": "#9ecae1", "aufgespannt": "#c9c9c9", "abhaengig": "#d9a0a0", "angenommen": C.COLOR_CHOSEN}
REASON_NAMES = {"stichprobe": "nur angesehen (Stichprobe)", "aufgespannt": "von schwereren aufgespannt", "abhaengig": "abhängig vom Angenommenen", "angenommen": "angenommen"}


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _lines(inst, ids):
    xs, ys = [], []
    for e in ids:
        u, v = inst.edges[e]
        (x0, y0), (x1, y1) = inst.points[u], inst.points[v]
        xs += [x0, x1, None]
        ys += [y0, y1, None]
    return xs, ys


def build_map(inst, chosen=(), opt=(), label_weights=False, height=430):
    """Leitungen (dünn grau), das Offline-Optimum (orange unterlegt) und die angenommenen Leitungen (dick blaugrün) auf dem Plan der Standorte."""
    chosen = list(chosen)
    fig = go.Figure()
    rest = [e for e in range(inst.m) if e not in set(chosen)]
    if rest:
        xs, ys = _lines(inst, rest)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_OTHER, width=1.2), name="nicht angenommen", hoverinfo="skip"))
    if opt:
        xs, ys = _lines(inst, list(opt))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_OPT, width=14), name="Offline-Optimum", hoverinfo="skip"))
    if chosen:
        xs, ys = _lines(inst, chosen)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_CHOSEN, width=5), name="angenommen", hoverinfo="skip"))
    if label_weights:
        mids = [((inst.points[inst.edges[e][0]][0] + inst.points[inst.edges[e][1]][0]) / 2, (inst.points[inst.edges[e][0]][1] + inst.points[inst.edges[e][1]][1]) / 2) for e in range(inst.m)]
        fig.add_trace(go.Scatter(x=[p[0] for p in mids], y=[p[1] for p in mids], mode="text", text=[str(inst.weights[e]) for e in range(inst.m)], textfont=dict(size=11), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[p[0] for p in inst.points], y=[p[1] for p in inst.points], mode="markers+text", text=[inst.name(i) for i in range(inst.n)], textposition="top center", textfont=dict(size=13),
                             marker=dict(size=13, symbol="square", color=C.COLOR_NODE, line=dict(color="white", width=1.2)), hovertemplate="%{text}<extra></extra>", showlegend=False))
    fig.add_trace(go.Scatter(x=[-0.05, 1.05], y=[-0.05, 1.05], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    return _base(fig, height)


def build_arrivals(trace, height=300):
    """Ein Balken je Angebot in der Reihenfolge der Ankunft: Höhe = Nutzen (logarithmisch), Farbe = was die Regel getan hat."""
    fig = go.Figure()
    for why in ("stichprobe", "aufgespannt", "abhaengig", "angenommen"):
        pts = [(pos + 1, w) for pos, e, w, ok, r in trace if r == why]
        if pts:
            fig.add_trace(go.Bar(x=[p[0] for p in pts], y=[p[1] for p in pts], width=0.85, marker_color=REASON_COLORS[why], name=REASON_NAMES[why], hovertemplate="Angebot %{x}: Nutzen %{y}<extra></extra>"))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title_text="Reihenfolge der Ankunft")
    fig.update_yaxes(title_text="Nutzen (logarithmisch)", type="log")
    return _base(fig, height)


def build_rule_bars(rows, height=300):
    """Anteil am Optimum je Regel: rows = [(Name, Wert, Farbe)]."""
    fig = go.Figure(go.Bar(x=[r[0] for r in rows], y=[r[1] for r in rows], marker_color=[r[2] for r in rows], hovertemplate="%{x}: %{y:.3f}<extra></extra>"))
    fig.update_yaxes(title_text="Anteil am Offline-Optimum", range=[0, 1.05])
    fig.update_xaxes(type="category")
    return _base(fig, height)


def build_f_curves(rows, key="wachs", height=340):
    """Anteil am Optimum gegen den Stichprobenanteil f, eine Linie je k; gestrichelt die Marke von erst kommt, erst bekommt."""
    fig = go.Figure()
    palette = ["#4c78a8", "#2F6B65", "#d95f02", "#7b4ea3"]
    for i, r in enumerate(rows):
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(x=list(C.F_CHOICES), y=[r[key][f] for f in C.F_CHOICES], mode="lines+markers", name=f"k = {r['k']}", line=dict(color=color, width=2.5), hovertemplate="f = %{x}: %{y:.3f}<extra>k = " + str(r["k"]) + "</extra>"))
        fig.add_trace(go.Scatter(x=[C.F_CHOICES[0], C.F_CHOICES[-1]], y=[r["erst"], r["erst"]], mode="lines", line=dict(color=color, width=1, dash="dot"), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(title_text="Stichprobenanteil f", tickvals=list(C.F_CHOICES))
    fig.update_yaxes(title_text="Anteil am Offline-Optimum", range=[0, 1.02])
    return _base(fig, height)


def build_grouped_bars(categories, series, x_title, y_title, height=340):
    """Gruppierte Balken: series = [(Name, Werte, Farbe)]."""
    fig = go.Figure([go.Bar(name=name, x=list(categories), y=list(values), marker_color=color, hovertemplate=name + ": %{y:.3f}<extra></extra>") for name, values, color in series])
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text=x_title, type="category")
    fig.update_yaxes(title_text=y_title, range=[0, 1.05])
    return _base(fig, height)
