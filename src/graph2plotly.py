import math
from typing import Optional

import networkx as nx
import plotly.graph_objects as go

from src.types_ import ArrowPosition, TaskInfo


def get_edge_data(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    length_frac: int = 1,
    arrow_length=0.025,
    arrow_angle=30,
    dot_size=20,
    arrow_pos: Optional[ArrowPosition] = None,
) -> tuple[list[Optional[float]], list[Optional[float]]]:
    edge_x: list[Optional[float]] = []
    edge_y: list[Optional[float]] = []

    length = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    dot_size_conversion = 0.0565 / 20  # length units per dot size
    converted_dot_diameter = dot_size * dot_size_conversion
    length_frac_reduction = converted_dot_diameter / length
    lengthFrac = length_frac - length_frac_reduction

    # If the line segment should not cover the entire distance, get actual start and end coords
    skipX = (x1 - x0) * (1 - lengthFrac)
    skipY = (y1 - y0) * (1 - lengthFrac)
    x0 = x0 + skipX / 2
    x1 = x1 - skipX / 2
    y0 = y0 + skipY / 2
    y1 = y1 - skipY / 2

    # Append line corresponding to the edge
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)  # Prevents a line being drawn from end of this edge to start of next edge
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

    # Draw arrow
    if arrow_pos is not None:

        # Find the point of the arrow; assume is at end unless told middle
        pointx = x1
        pointy = y1
        eta = math.degrees(math.atan((x1 - x0) / (y1 - y0)))

        if arrow_pos == ArrowPosition.Middle:
            pointx = x0 + (x1 - x0) / 2
            pointy = y0 + (y1 - y0) / 2

        # Find the directions the arrows are pointing
        signx = (x1 - x0) / abs(x1 - x0)
        signy = (y1 - y0) / abs(y1 - y0)

        # Append first arrowhead
        dx = arrow_length * math.sin(math.radians(eta + arrow_angle))
        dy = arrow_length * math.cos(math.radians(eta + arrow_angle))
        edge_x.append(pointx)
        edge_x.append(pointx - signx ** 2 * signy * dx)
        edge_x.append(None)
        edge_y.append(pointy)
        edge_y.append(pointy - signx ** 2 * signy * dy)
        edge_y.append(None)

        # And second arrowhead
        dx = arrow_length * math.sin(math.radians(eta - arrow_angle))
        dy = arrow_length * math.cos(math.radians(eta - arrow_angle))
        edge_x.append(pointx)
        edge_x.append(pointx - signx ** 2 * signy * dx)
        edge_x.append(None)
        edge_y.append(pointy)
        edge_y.append(pointy - signx ** 2 * signy * dy)
        edge_y.append(None)

    return edge_x, edge_y


def fig_from_graph(
    graph: nx.DiGraph,
    length_frac: int = 1,
    arrow_length=0.025,
    arrow_angle=30,
    dot_size=20,
    arrow_pos: Optional[ArrowPosition] = ArrowPosition.End,
    node_color="Blue",
    node_size=15,
    line_width=2,
    line_color="#000000",
) -> go.Figure:
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = graph.nodes[edge[0]]["pos"]
        x1, y1 = graph.nodes[edge[1]]["pos"]
        edge_x_, edge_y_ = get_edge_data(
            x0,
            y0,
            x1,
            y1,
            arrow_pos=arrow_pos,
            dot_size=dot_size,
            arrow_angle=arrow_angle,
            arrow_length=arrow_length,
            length_frac=length_frac,
        )
        edge_x += edge_x_
        edge_y += edge_y_

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=line_width, color=line_color),
        hoverinfo="none",
        mode="lines",
    )

    node_x = []
    node_y = []
    for node in graph.nodes():
        x, y = graph.nodes[node]["pos"]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(showscale=False, color=node_color, size=node_size),
    )

    node_text = []
    for node in graph.nodes:
        node_info: TaskInfo = graph.nodes[node].get("task_info", {"Id": node})
        text = "<br>".join(f"{k}={v}" for k, v in node_info.items())
        node_text.append(text)
    node_trace.text = node_text

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    return fig
