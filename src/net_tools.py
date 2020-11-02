from typing import Iterable

import networkx as nx

from src.types_ import TaskInfo


def get_all_graphs(edges: list[tuple[str, str]]) -> dict[str, set[str]]:
    """

    :param edges: Список ребер графа
    :return: Все названия узлов и какие другие узлы им соответсвуют
    """
    graphs: dict[str, set[str]] = {}
    for e in edges:
        if e[0] in graphs or e[1] in graphs:
            graph = graphs.get(e[0], graphs.get(e[1], set()))
        else:
            graph = set()
        graph.add(e[0])
        graph.add(e[1])
        graphs[e[0]] = graph
        graphs[e[1]] = graph
    return graphs


def build_graph(
    nodes: Iterable[tuple[str, TaskInfo]], edges: Iterable[tuple[str, str]]
) -> nx.DiGraph:
    """"""
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for edg in edges:
        G.add_edge(*edg)
    return G


def add_positions(graph: nx.DiGraph) -> None:
    """Add position coordinates to graph"""
    pos = nx.spring_layout(graph, k=0.1, iterations=20)
    for node in graph.nodes:
        graph.nodes[node]["pos"] = pos[node]
