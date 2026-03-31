import * as Types from "./types";

export function generateMessages(
  sourceCurrencies: string[],
  targetCurrencies: string[],
  batchSize: number,
): Types.Message[] {
  const messages: Types.Message[] = [];

  for (let i = 0; i < batchSize; i++) {
    const source =
      sourceCurrencies[Math.floor(Math.random() * sourceCurrencies.length)];
    const target =
      targetCurrencies[Math.floor(Math.random() * targetCurrencies.length)];
    messages.push({ source_currency: source, target_currency: target });
  }
  return messages;
}

export function transformEdgeLatencies(
  data: Types.FirestoreResults["edge_latency_history"],
) {
  return data
    .sort((a, b) => a.iteration - b.iteration)
    .map((entry, index) => {
      const iteration = index + 1;
      const edge_latencies = entry.latencies.reduce(
        (acc, latency) => {
          acc[latency.edge_id] = latency.avg_latency;
          return acc;
        },
        {} as Record<string, number>,
      );

      return { iteration, ...edge_latencies };
    });
}

export function transformRouteWeights(
  data: Types.FirestoreResults["route_weight_history"],
) {
  return data
    .sort((a, b) => a.iteration - b.iteration)
    .map((entry, index) => {
      const iteration = index + 1;
      const edge_weights = entry.weights.reduce(
        (acc, weight) => {
          acc[weight.edge_id] = weight.conductivity;
          return acc;
        },
        {} as Record<string, number>,
      );

      return { iteration, ...edge_weights };
    });
}
