from model_functions import *
from params import SlimeMouldParams
from graph import SlimeMouldGraph

class SlimeMouldModel:
    def __init__(
            self,
            slime_mould_params: SlimeMouldParams,
            graph: SlimeMouldGraph,
            efficiency_matrix: NDArray[float]=None,
            conductivity_matrix: NDArray[float]=None,
            pressure_loop: int = 25
    ):
        self.slime_mould_params = slime_mould_params
        self.graph = graph
        self.efficiency_matrix = efficiency_matrix
        self.conductivity_matrix = conductivity_matrix
        self.pressure_loop = pressure_loop

    def run_model(self):
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


edges_dict_1 = {
    0: [1, 2, 3],
    1: [0, 4],
    2: [0, 4],
    3: [0, 4],
    4: [1, 2, 3]
}

graph = SlimeMouldGraph(edges_dict=edges_dict_1, source_nodes=[0], sink_nodes=[4])
model_params = SlimeMouldParams(alpha=0.013, mu=0.022, epsilon=0.3, d_max=1.75, d_min=1e-4)
model = SlimeMouldModel(slime_mould_params=model_params, graph=graph)

pressure, conductivity = model.run_model()

print(pressure)
print(conductivity)
