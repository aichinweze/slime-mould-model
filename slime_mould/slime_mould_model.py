from slime_mould.model_functions import *
from models.models import SlimeMouldParams
from slime_mould.graph import SlimeMouldGraph

class SlimeMouldModel:
    """
        Implements the Physarum polycephalum (slime mould) mathematical model
        for adaptive routing.

        The model iteratively updates pressure and conductivity across the graph,
        converging towards an efficient flow network. An optional efficiency matrix
        can be supplied to bias conductivity updates based on real-world latency feedback.
    """

    def __init__(
            self,
            slime_mould_params: SlimeMouldParams,
            slime_mould_graph: SlimeMouldGraph,
            efficiency_matrix: NDArray[float]=None,
            conductivity_matrix: NDArray[float]=None,
            pressure_loop: int = 25
    ):
        """
        Args:
            slime_mould_params: model parameters controlling decay, growth and bounds.
            slime_mould_graph: the graph structure to run the model over.
            efficiency_matrix: optional matrix biasing conductivity updates. If None,
                the adjacency matrix is used, giving uniform weighting.
            conductivity_matrix: optional initial conductivity state. If None,
                the adjacency matrix is used as the starting point.
            pressure_loop: number of pressure update iterations per model run.
        """
        self.slime_mould_params = slime_mould_params
        self.graph = slime_mould_graph
        self.efficiency_matrix = efficiency_matrix
        self.conductivity_matrix = conductivity_matrix
        self.pressure_loop = pressure_loop

    def run_model(self):
        """
        Run the slime mould model for one cycle.

        Returns:
            A tuple of (pressure_vector, conductivity_matrix) representing
            the final state after all pressure loop iterations.
        """
        if self.conductivity_matrix is None:
            initial_conductivity = self.graph.adjacency_matrix
        else:
            initial_conductivity = self.conductivity_matrix

        if self.efficiency_matrix is None:
            efficiency_matrix = self.graph.adjacency_matrix
        else:
            efficiency_matrix = self.efficiency_matrix

        initial_pressure: NDArray[int] = np.zeros(self.graph.number_of_nodes, dtype=int)

        flow_vector = build_flow_vector(self.graph.number_of_nodes, self.graph.source_nodes, self.graph.sink_nodes)

        last_pressure = initial_pressure
        last_conductivity = initial_conductivity

        for _ in range(self.pressure_loop):
            updated_pressure = np.array([
                update_pressure_at_node(
                    pressure_index=i,
                    pressure_vector=last_pressure,
                    conductivity_by_l_row=last_conductivity[i],
                    flow_at_node=flow_vector[i],
                    epsilon=self.slime_mould_params.epsilon,
                ) for i in range(self.graph.number_of_nodes)
            ])
            last_pressure = updated_pressure

            updated_conductivity = [
                update_conductivity_row(
                    row_index=i,
                    conductivity_row=initial_conductivity[i],
                    efficiency_row=efficiency_matrix[i],
                    pressure_vector=last_pressure,
                    mu=self.slime_mould_params.mu,
                    alpha=self.slime_mould_params.alpha,
                    d_max=self.slime_mould_params.d_max,
                    d_min=self.slime_mould_params.d_min
                )
                for i in range(self.graph.number_of_nodes)
            ]
            last_conductivity = updated_conductivity

        return last_pressure, last_conductivity

