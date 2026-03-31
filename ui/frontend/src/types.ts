export type Screen = "welcome" | "configure" | "results";

export type ConfigureScreenStep = "configure" | "review";
export type ResultsScreenStep =
  | "publishing"
  | "contacting_fc"
  | "loading_fs"
  | "loading_ps"
  | "display"
  | "error";

export type Message = {
  source_currency: string;
  target_currency: string;
};

export type RunMetadata = {
  published: number;
  flow_control_invocations: number;
  start_time: string;
};
export type FlowControlMetadata = {
  flow_control_invocations: number;
};

export type FirestoreResults = {
  route_weight_history: {
    iteration: number;
    timestamp: string;
    weights: { edge_id: string; conductivity: number }[];
  }[];
  edge_latency_history: {
    iteration: number;
    latencies: { edge_id: string; avg_latency: number }[];
  }[];
};
export type PubSubResults = {
  message_counts: {
    edge_id: string;
    success: number;
    error: number;
  }[];
};
