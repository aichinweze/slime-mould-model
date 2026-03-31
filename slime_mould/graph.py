from slime_mould.model_functions import build_adjacency_matrix

class SlimeMouldGraph:
    """
        Represents the graph structure used by the slime mould model.

        The graph is defined by a dictionary of edges and a set of source
        and sink nodes. The adjacency matrix is built from the edge dictionary
        at initialisation.
    """

    def __init__(self, edges_dict: dict[int, list[int]], source_nodes: list[int], sink_nodes: list[int]):
        """
        Args:
            edges_dict: adjacency list mapping each node index to its neighbours.
            source_nodes: list of node indices where flow originates.
            sink_nodes: list of node indices where flow terminates.
        """
        self.adjacency_matrix = build_adjacency_matrix(edges_dict)
        self.number_of_nodes = len(edges_dict)
        self.source_nodes = source_nodes
        self.sink_nodes = sink_nodes

    def get_adjacency_matrix(self):
        """Return the adjacency matrix as a numpy array."""
        return self.adjacency_matrix

    def get_number_of_nodes(self):
        """Return the total number of nodes in the graph."""
        return self.number_of_nodes