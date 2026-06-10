import plotly.express as px
import plotly.graph_objects as go
from utils.styles import PLOTLY_LAYOUT, PLATFORM_COLORS, apply_layout


def _hex_to_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def line_trend(df, x, y, color=None, title="", color_map=None):
    kwargs = dict(x=x, y=y, title=title, markers=True)
    if color:
        kwargs["color"] = color
        if color_map:
            kwargs["color_discrete_map"] = color_map
    fig = px.line(df, **kwargs)
    return apply_layout(fig, title)


def bar_rank(df, x, y, color=None, title="", orientation="h", color_map=None):
    kwargs = dict(x=x, y=y, title=title, orientation=orientation)
    if color:
        kwargs["color"] = color
        if color_map:
            kwargs["color_discrete_map"] = color_map
    fig = px.bar(df, **kwargs)
    return apply_layout(fig, title)


def heatmap_px(df_pivot, title="", color_scale="Blues"):
    fig = px.imshow(
        df_pivot,
        text_auto=".1f",
        color_continuous_scale=color_scale,
        title=title,
        aspect="auto",
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_coloraxes(colorbar=dict(tickfont=dict(color="#94A3B8")))
    return fig


def scatter_bubble(df, x, y, size, color, title="", color_map=None, hover_name=None):
    kwargs = dict(x=x, y=y, size=size, color=color, title=title, size_max=50)
    if color_map:
        kwargs["color_discrete_map"] = color_map
    if hover_name:
        kwargs["hover_name"] = hover_name
    fig = px.scatter(df, **kwargs)
    return apply_layout(fig, title)


def donut_chart(df, names, values, title="", color_map=None):
    kwargs = dict(names=names, values=values, title=title, hole=0.45)
    if color_map:
        kwargs["color_discrete_map"] = color_map
    fig = px.pie(df, **kwargs)
    fig.update_traces(textfont_color="#F1F5F9")
    return apply_layout(fig, title)


def radar_chart(categories, traces: dict, title=""):
    """traces: {브랜드명: [값, ...]}"""
    fig = go.Figure()
    colors = ["#2563EB", "#64748B", "#94A3B8", "#475569", "#334155"]
    for i, (name, values) in enumerate(traces.items()):
        vals = values + [values[0]]
        cats = categories + [categories[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats, fill="toself",
            name=name,
            line=dict(color=colors[i % len(colors)]),
            fillcolor=_hex_to_rgba(colors[i % len(colors)], 0.15),
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            radialaxis=dict(visible=True, gridcolor="#334155", tickfont=dict(color="#94A3B8")),
            angularaxis=dict(gridcolor="#334155", tickfont=dict(color="#94A3B8")),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(text=title, font=dict(color="#F1F5F9", size=14)),
    )
    return fig
