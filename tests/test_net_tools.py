import networkx as nx
import pytest

from src.net_tools import add_positions, build_graph


@pytest.fixture()
def test_graph():
    yield build_graph(
        [
            (
                "task_id",
                {"task_info": {"Id": "task_id", "Label": "Label", "Тип": "Тип"}},
            ),
            (
                "task_id_1",
                {"task_info": {"Id": "task_id_1", "Label": "Label", "Тип": "Тип"}},
            ),
        ],
        edges=[("task_id", "task_id_1")],
    )


def test_build_graph(test_graph: nx.DiGraph):
    assert test_graph.nodes["task_id"]["task_info"] == {
        "Id": "task_id",
        "Label": "Label",
        "Тип": "Тип",
    }


def test_add_positions(test_graph):
    add_positions(test_graph)
    assert "pos" in test_graph.nodes["task_id"]
