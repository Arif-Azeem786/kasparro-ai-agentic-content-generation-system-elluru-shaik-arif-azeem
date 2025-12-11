# src/graph/state_graph.py
from typing import Callable, Dict, Any, Optional, Tuple

NodeFn = Callable[[Dict[str, Any]], Dict[str, Any]]

class StateGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, NodeFn] = {}
        self.edges: Dict[str, str] = {}  # simple linear edge (node -> next_node)
        self.conditional_edges: Dict[str, Callable[[Dict[str, Any]], str]] = {}
        self.start_node: Optional[str] = None
        self.end_nodes = set()

    def add_node(self, name: str, fn: NodeFn) -> None:
        self.nodes[name] = fn
        if self.start_node is None:
            self.start_node = name

    def add_edge(self, src: str, dst: str) -> None:
        self.edges[src] = dst

    def add_conditional_edge(self, src: str, decision_fn: Callable[[Dict[str, Any]], str]) -> None:
        """
        decision_fn returns the name of the next node to execute given the state.
        """
        self.conditional_edges[src] = decision_fn

    def set_end(self, node: str) -> None:
        self.end_nodes.add(node)

    def invoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        if not self.start_node:
            raise RuntimeError("No start node defined")
        state = dict(initial_state)
        current = self.start_node
        visited = 0
        # note: add simple safety to avoid infinite loops
        while current is not None:
            visited += 1
            if visited > 200:
                raise RuntimeError("Graph invoked too many steps (possible infinite loop)")
            if current not in self.nodes:
                raise RuntimeError(f"Node not found: {current}")
            node_fn = self.nodes[current]
            state = node_fn(state) or state
            # conditional?
            if current in self.conditional_edges:
                next_node = self.conditional_edges[current](state)
            else:
                next_node = self.edges.get(current)
            if next_node is None or next_node in self.end_nodes:
                break
            current = next_node
        return state
