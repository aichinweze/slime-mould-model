import * as Types from "../types";
import { useEffect, useState } from "react";
import { transformEdgeLatencies, transformRouteWeights } from "../utils";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  BarChart,
  ResponsiveContainer,
} from "recharts";
import { RenderLoadingMessage } from "./shared/LoadingScreen";
import { RenderErrorMessage } from "./shared/ErrorScreen";

function ChartCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border border-gray-200 rounded-lg p-6 w-full">
      <h3 className="text-lg font-medium text-gray-800">{title}</h3>
      <p className="text-sm text-gray-500 mb-4">{subtitle}</p>
      {children}
    </div>
  );
}

function RenderMessageCounts({
  data,
}: {
  data: Types.PubSubResults["message_counts"];
}) {
  const filteredData = data
    .filter((entry) => entry.edge_id !== "N_A")
    .sort((a, b) => a.edge_id.localeCompare(b.edge_id));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart width={800} height={400} data={filteredData}>
        <Bar dataKey="success" fill="#059b02" />
        <Bar dataKey="error" fill="#E24B4A" />
        <XAxis dataKey="edge_id" />
        <YAxis />
        <Tooltip />
        <Legend />
      </BarChart>
    </ResponsiveContainer>
  );
}

function RenderEdgeLatencyHistory({
  data,
}: {
  data: Types.FirestoreResults["edge_latency_history"];
}) {
  const transformedData = transformEdgeLatencies(data);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={transformedData}>
        <XAxis
          dataKey="iteration"
          label={{ value: "Iteration", position: "insideBottom", offset: -5 }}
        />
        <YAxis
          label={{
            value: "Edge Latency",
            angle: -90,
            position: "insideLeft",
            offset: 10,
          }}
        />
        <Tooltip />
        <Legend />
        <Line dataKey="0>>1" stroke="#059b02" />
        <Line dataKey="0>>2" stroke="#ff7300" />
        <Line dataKey="0>>3" stroke="#0088fe" />
      </LineChart>
    </ResponsiveContainer>
  );
}

function RenderRouteWeightHistory({
  data,
}: {
  data: Types.FirestoreResults["route_weight_history"];
}) {
  const transformedData = transformRouteWeights(data);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={transformedData}>
        <XAxis
          dataKey="iteration"
          label={{ value: "Iteration", position: "insideBottom", offset: -5 }}
        />
        <YAxis
          label={{
            value: "Route Weight",
            angle: -90,
            position: "insideLeft",
            offset: 10,
          }}
        />
        <Tooltip />
        <Legend />
        <Line dataKey="0>>1" stroke="#059b02" />
        <Line dataKey="0>>2" stroke="#ff7300" />
        <Line dataKey="0>>3" stroke="#0088fe" />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function ResultsScreen({ messages }: { messages: Types.Message[] }) {
  const [step, setStep] = useState<Types.ResultsScreenStep>("publishing");
  const [metadata, setMetadata] = useState<Types.RunMetadata | null>(null);
  const [fsResults, setFirestoreResults] =
    useState<Types.FirestoreResults | null>(null);
  const [psResults, setPubSubResults] = useState<Types.PubSubResults | null>(
    null,
  );

  const messageBatchSize = messages.length;

  useEffect(() => {
    async function getFirestoreResults(start_time: string) {
      const response = await fetch(
        `/api/results?start_time=${encodeURIComponent(start_time)}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (!response.ok) {
        setStep("error");
        console.error(
          "Adaptimould encountered error while fetching history from GCP:",
          response.statusText,
        );
        return;
      }

      const data = (await response.json()) as Types.FirestoreResults;
      console.log("Firestore results data received from GCP:", data);
      setFirestoreResults(data);
    }

    async function getPubSubResults(start_time: string) {
      const response = await fetch(
        `/api/message-counts?start_time=${encodeURIComponent(start_time)}&batch_size=${messageBatchSize}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (!response.ok) {
        setStep("error");
        console.error(
          "Adaptimould encountered error while fetching message counts from Pub/Sub:",
          response.statusText,
        );
        return;
      }

      const data = (await response.json()) as Types.PubSubResults;
      console.log("Pub/Sub results data received from GCP:", data);
      setPubSubResults(data);
      setStep("display");
    }

    async function startRun(start_time: string) {
      const response = await fetch(`/api/run?batch_size=${messageBatchSize}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        setStep("error");
        console.error(
          "Adaptimould encountered error while communicating with Flow Control: ",
          response.statusText,
        );
        return;
      }

      const data = (await response.json()) as Types.FlowControlMetadata;
      console.log("Flow control metadata received from GCP:", data);

      setStep("loading_fs");
      await getFirestoreResults(start_time);

      setStep("loading_ps");
      await getPubSubResults(start_time);
    }

    async function runAdaptimould() {
      const response = await fetch("/api/publish", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages }),
      });

      if (!response.ok) {
        setStep("error");
        console.error(
          "Adaptimould encountered error while publishing messages to GCP:",
          response.statusText,
        );
        return;
      }

      const data = (await response.json()) as Types.RunMetadata;

      setMetadata(data);

      console.log("Run metadata received from GCP:", data);

      setStep("contacting_fc");
      startRun(data.start_time);
    }

    runAdaptimould();
  }, []);

  if (step === "publishing") {
    return (
      <RenderLoadingMessage message="Publishing messages to Adaptimould..." />
    );
  } else if (step === "contacting_fc") {
    return (
      <RenderLoadingMessage message="Contacting Flow Control for Adaptimould cycles..." />
    );
  } else if (step === "loading_fs") {
    return (
      <RenderLoadingMessage message="Loading Adaptimould results from Firestore..." />
    );
  } else if (step === "loading_ps") {
    return (
      <RenderLoadingMessage message="Loading Adaptimould results from Pub/Sub..." />
    );
  } else if (step === "display") {
    if (!fsResults || !psResults) {
      console.error("Results data is null or undefined");
      return (
        <RenderErrorMessage message="Sorry, an error occurred. Please try again." />
      );
    }

    return (
      <div className="flex flex-col items-center gap-8 py-12 px-8 max-w-4xl mx-auto">
        <div className="text-center">
          <h2 className="text-3xl font-medium text-brand">Results</h2>
          <div className="w-10 h-0.5 bg-brand rounded-full mx-auto mt-2" />
        </div>

        <ChartCard
          title="Route Weight Evolution"
          subtitle="Conductivity per worker edge across iterations — higher means more traffic routed through that worker"
        >
          <RenderRouteWeightHistory data={fsResults.route_weight_history} />
        </ChartCard>

        <ChartCard
          title="Rolling Latency per Worker"
          subtitle="Weighted average latency per worker edge across iterations — the signal driving the algorithm"
        >
          <RenderEdgeLatencyHistory data={fsResults.edge_latency_history} />
        </ChartCard>

        <ChartCard
          title="Messages Processed per Worker"
          subtitle="Total successful and failed messages processed by each worker"
        >
          <RenderMessageCounts data={psResults?.message_counts || []} />
        </ChartCard>

        <button
          className="border border-brand text-brand px-6 py-2 rounded-md text-lg hover:bg-green-50 transition-colors"
          onClick={() => window.location.reload()}
        >
          Return home
        </button>
      </div>
    );
  } else {
    return (
      <RenderErrorMessage message="Sorry, an error occurred. Please try again." />
    );
  }
}
