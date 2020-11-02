import base64
import io
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.utils import PlotlyJSONEncoder

from src.graph2plotly import fig_from_graph
from src.net_tools import add_positions, build_graph, get_all_graphs

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
        html.Div(
            dcc.Dropdown(
                id="subgraph-dropdown",
                options=[],
            )
        ),
        html.Div(id="plot"),
    ]
)


def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df


@app.callback(
    Output("subgraph-dropdown", "options"),
    [
        Input("upload-data", "contents"),
    ],
    [State("upload-data", "filename")],
)
def update_output(list_of_contents, list_of_names):
    has_edges: bool = False
    edges = None
    nodes = None
    if list_of_contents is not None:
        for filename, content in zip(list_of_names, list_of_contents):
            if not has_edges and "edges" in filename:
                has_edges = True
            if "edges" in filename:
                edges = parse_contents(content, filename)
            elif "nodes" in filename:
                nodes = parse_contents(content, filename)

        if not has_edges:
            raise Exception("No edges.csv files was provided")

        unique_nodes = set(edges.to_numpy().ravel())
        if nodes is not None:
            nodes = [(v["Id"], {"task_info": v}) for v in nodes.to_dict("records")]
        else:
            nodes = unique_nodes
        edges_list = [tuple(e) for e in edges.to_numpy()]

        G = build_graph(nodes, edges_list)
        all_graphs_dict = get_all_graphs(edges_list)
        all_graphs = set(tuple(g) for g in all_graphs_dict.values())

        all_graphs_ = {}
        for graph in all_graphs:
            sub_g = G.subgraph(graph)
            add_positions(sub_g)
            fig = fig_from_graph(sub_g)
            fig.layout.height = 700
            all_graphs_[graph] = fig

        task2graph = {}
        for k, v in all_graphs_dict.items():
            task2graph[k] = all_graphs_[tuple(v)]

        return [
            {"label": k, "value": json.dumps(v, cls=PlotlyJSONEncoder)}
            for k, v in task2graph.items()
        ]
    return []


@app.callback(Output("plot", "children"), [Input("subgraph-dropdown", "value")])
def update_plot(value):
    if value is not None:
        plot = json.loads(value)
        fig = go.Figure(**plot)
        return html.Div([dcc.Graph(figure=fig)])


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
