from slime_mould.model_functions import build_adjacency_matrix

class SlimeMouldGraph:
    def __init__(self, edges_dict: dict[int, list[int]], source_nodes: list[int], sink_nodes: list[int]):
        self.adjacency_matrix = build_adjacency_matrix(edges_dict)
        self.number_of_nodes = len(edges_dict)
        self.source_nodes = source_nodes
        self.sink_nodes = sink_nodes

    def get_adjacency_matrix(self):
        return self.adjacency_matrix

    def get_number_of_nodes(self):
        return self.number_of_nodes