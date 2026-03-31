import { useEffect, useState } from "react";
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
import "./App.css";
import * from "./types.ts";

const SOURCE_CURRENCIES = ["BTC", "ETH", "ADA", "LINK", "SOL"];
const TARGET_CURRENCIES = ["USD", "GBP", "EUR", "JPY", "HKD"];

function BatchSizeInput({
  value,
  onChange,
}: {
  value: number;
  onChange: (input: number) => void;
}) {
  return (
    <div className="flex items-center justify-center flex-col gap-2">
      <h2 className="text-2xl font-large text-brand">Select Batch Size</h2>
      <p className="text-sm text-gray-800 max-w-xl text-center">
        Please select the number of messages to send to Adaptimould. (1 to
        2,000)
      </p>
      <input
        className="border border-gray-200 rounded-md px-3 py-2 w-32 text-center"
        type="number"
        min="1"
        max="2000"
        placeholder="Enter batch size"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
      />
    </div>
  );
}

function CurrencyTable({
  title,
  currencies,
  selected,
  onChange,
}: {
  title: string;
  currencies: string[];
  selected: string[];
  onChange: (currency: string) => void;
}) {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden w-64">
      <table className="flex-1 w-full">
        <thead>
          <tr>
            <th className="px-4 py-3 text-left text-medium font-medium text-gray-800 bg-gray-50 border-b border-gray-200">
              {title}
            </th>
          </tr>
        </thead>
        <tbody>
          {currencies.map((currency) => (
            <tr key={currency}>
              <td className="px-4 py-2 border-b border-gray-100">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selected.includes(currency)}
                    onChange={() => onChange(currency)}
                  />
                  {currency}
                </label>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GeneratedMessagesTable({ messages }: { messages: Message[] }) {
  return (
    <div className="overflow-y-auto max-h-96 rounded-lg border border-gray-200 w-96">
      <table className="w-full text-sm">
        <thead className="sticky top-0 bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-center text-medium font-medium text-gray-800 bg-gray-50 border-b border-r border-gray-200">
              Source Currency
            </th>
            <th className="px-4 py-3 text-center text-medium font-medium text-gray-800 bg-gray-50 border-b border-r border-gray-200">
              Target Currency
            </th>
          </tr>
        </thead>
        <tbody>
          {messages.map((message, index) => (
            <tr
              key={index}
              className="border-b border-r border-gray-100 hover:bg-gray-50"
            >
              <td className="px-4 py-2 text-gray-800 border-r text-center">
                {message.source_currency}
              </td>
              <td className="px-4 py-2 text-gray-800 border-r text-center">
                {message.target_currency}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function WelcomeScreen({ onBegin }: { onBegin: () => void }) {
  return (
    // min-h-screen is needed to vertically center the content, otherwise it will be towards the top of the page
    <div className="flex items-center justify-center flex-col gap-4 min-h-screen">
      <span className="text-xs bg-green-50 text-green-800 px-3 py-1 rounded-full">
        bio-inspired load balancing
      </span>

      <header className="text-6xl font-medium text-brand">AdaptiMould</header>

      <div className="w-10 h-0.5 bg-brand rounded-full" />

      <p className="text-sm text-gray-800 max-w-xl text-center">
        <b>AdaptiMould</b> uses a mathematical model of{" "}
        <em>Physarum polycephalum</em> (slime mould) to adaptively route
        requests between three worker functions based on real latency feedback.
        Watch the algorithm self-optimise in real time.
      </p>

      <p className="text-sm text-gray-800 max-w-xl text-center">
        <b>How it works:</b> Configure a batch of cryptocurrency price requests
        → AdaptiMould routes them across workers → results show how the
        algorithm adapted routing weights over time.
      </p>

      <button
        className="bg-brand text-white px-6 py-2 rounded-md text-lg hover:opacity-80 hover:text-white transition-opacity"
        onClick={onBegin}
      >
        Begin
      </button>
    </div>
  );
}

function generateMessages(
  sourceCurrencies: string[],
  targetCurrencies: string[],
  batchSize: number,
): Message[] {
  const messages: Message[] = [];

  for (let i = 0; i < batchSize; i++) {
    const source =
      sourceCurrencies[Math.floor(Math.random() * sourceCurrencies.length)];
    const target =
      targetCurrencies[Math.floor(Math.random() * targetCurrencies.length)];
    messages.push({ source_currency: source, target_currency: target });
  }
  return messages;
}

function ConfigureScreenButtonPanel({
  step,
  sourceCurrenciesLength,
  targetCurrenciesLength,
  onNextClick,
  onBackClick,
}: {
  step: ConfigureScreenStep;
  sourceCurrenciesLength: number;
  targetCurrenciesLength: number;
  onNextClick: () => void;
  onBackClick: () => void;
}) {
  const backButtonText = step === "configure" ? "Return Home" : "Back";
  const nextButtonText = step === "configure" ? "Next" : "Start Run!";

  return (
    <div className="flex items-center justify-center flex-row gap-4">
      <button
        //className="bg-brand text-black px-6 py-2 rounded-md text-lg hover:opacity-90 hover:text-white transition-opacity"
        className="border border-brand text-brand px-6 py-2 rounded-md text-lg hover:bg-green-50 transition-colors"
        onClick={onBackClick}
      >
        {backButtonText}
      </button>

      <button
        disabled={
          step === "configure" &&
          (sourceCurrenciesLength === 0 || targetCurrenciesLength === 0)
        }
        className="bg-brand text-white px-6 py-2 rounded-md text-lg 
                  hover:opacity-80 hover:text-white transition-opacity
                  disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={onNextClick}
      >
        {nextButtonText}
      </button>
    </div>
  );
}

function ConfigureScreen({
  onReturnHome,
  onStartRun,
}: {
  onReturnHome: () => void;
  onStartRun: (messages: Message[]) => void;
}) {
  const [step, setStep] = useState<ConfigureScreenStep>("configure");
  const [batchSize, setBatchSize] = useState<number>(1);
  const [sourceCurrencies, setSourceCurrencies] = useState<string[]>([]);
  const [targetCurrencies, setTargetCurrencies] = useState<string[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);

  function onSourceCurrencyChange(currency: string) {
    setSourceCurrencies((prev) =>
      prev.includes(currency)
        ? prev.filter((c) => c !== currency)
        : [...prev, currency],
    );
  }

  function onTargetCurrencyChange(currency: string) {
    setTargetCurrencies((prev) =>
      prev.includes(currency)
        ? prev.filter((c) => c !== currency)
        : [...prev, currency],
    );
  }

  function onBatchInputChange(input: number) {
    if (!isNaN(input) && input >= 1 && input <= 2000) {
      setBatchSize(input);
    }
  }

  function handleNextClick() {
    if (step === "configure") {
      setMessages(
        generateMessages(sourceCurrencies, targetCurrencies, batchSize),
      );
      setStep("review");
    } else {
      onStartRun(messages);
    }
  }

  function handleBackClick() {
    if (step === "configure") {
      setBatchSize(1);
      setSourceCurrencies([]);
      setTargetCurrencies([]);
      onReturnHome();
    } else {
      setStep("configure");
    }
  }

  if (step === "configure") {
    return (
      <div className="flex items-center justify-center flex-col gap-4 min-h-screen">
        <h2 className="text-3xl font-medium text-brand">
          Configure Adaptimould
        </h2>

        <div className="w-20 h-0.5 bg-brand rounded-full" />

        <p className="text-sm text-gray-800 max-w-xl text-center">
          Here you can configure the parameters for your Adaptimould run.
        </p>

        <BatchSizeInput value={batchSize} onChange={onBatchInputChange} />

        <div className="flex items-center justify-center flex-col gap-2">
          <h2 className="text-2xl font-large text-brand">Select Currencies</h2>
          <p className="text-sm text-gray-800 max-w-xl text-center">
            Please select the currencies you would like to use as options for
            currency conversions.
          </p>

          <div className="flex-row gap-8 flex items-start justify-center">
            <CurrencyTable
              title="Source Currencies"
              currencies={SOURCE_CURRENCIES}
              selected={sourceCurrencies}
              onChange={onSourceCurrencyChange}
            />
            <CurrencyTable
              title="Target Currencies"
              currencies={TARGET_CURRENCIES}
              selected={targetCurrencies}
              onChange={onTargetCurrencyChange}
            />
          </div>
        </div>

        <ConfigureScreenButtonPanel
          step={step}
          sourceCurrenciesLength={sourceCurrencies.length}
          targetCurrenciesLength={targetCurrencies.length}
          onNextClick={handleNextClick}
          onBackClick={handleBackClick}
        />
      </div>
    );
  } else {
    return (
      <div className="flex items-center justify-center flex-col gap-4 min-h-screen">
        <h2 className="text-3xl font-medium text-brand">Review</h2>

        <div className="w-20 h-0.5 bg-brand rounded-full" />

        <p className="text-sm text-gray-800 max-w-xl text-center">
          Here you can review the messages generated by your configuration
          before you proceed
        </p>

        <p className="text-sm text-gray-500">
          {messages.length} messages generated
        </p>

        <GeneratedMessagesTable messages={messages} />
        <ConfigureScreenButtonPanel
          step={step}
          sourceCurrenciesLength={sourceCurrencies.length}
          targetCurrenciesLength={targetCurrencies.length}
          onNextClick={handleNextClick}
          onBackClick={handleBackClick}
        />
      </div>
    );
  }
}

function RenderMessageCounts({
  data,
}: {
  data: PubSubResults["message_counts"];
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

function transformEdgeLatencies(
  data: FirestoreResults["edge_latency_history"],
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

function RenderEdgeLatencyHistory({
  data,
}: {
  data: FirestoreResults["edge_latency_history"];
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

function transformRouteWeights(data: FirestoreResults["route_weight_history"]) {
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

function RenderRouteWeightHistory({
  data,
}: {
  data: FirestoreResults["route_weight_history"];
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

function RenderLoadingMessage({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-6 min-h-screen">
      <div className="w-12 h-12 rounded-full border-4 border-gray-200 border-t-brand animate-spin" />
      <p className="text-sm text-gray-600">{message}</p>
    </div>
  );
}

function RenderErrorMessage({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-6 min-h-screen">
      <div className="text-center gap-6">
        <h2 className="text-3xl font-medium text-brand mb-2">Error</h2>
        <div className="w-10 h-0.5 bg-brand rounded-full mx-auto mt-2" />
        <p className="text-sm text-gray-800 mt-4">{message}</p>
      </div>
      <div>
        <button
          className="border border-brand text-brand px-6 py-2 rounded-md text-lg hover:bg-green-50 transition-colors"
          onClick={() => window.location.reload()}
        >
          Return home
        </button>
      </div>
    </div>
  );
}

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

function ResultsScreen({ messages }: { messages: Message[] }) {
  const [step, setStep] = useState<ResultsScreenStep>("publishing");
  const [metadata, setMetadata] = useState<RunMetadata | null>(null);
  const [fsResults, setFirestoreResults] = useState<FirestoreResults | null>(
    null,
  );
  const [psResults, setPubSubResults] = useState<PubSubResults | null>(null);

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

      const data = (await response.json()) as FirestoreResults;
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

      const data = (await response.json()) as PubSubResults;
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

      const data = (await response.json()) as FlowControlMetadata;
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

      const data = (await response.json()) as RunMetadata;

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

export default function App() {
  const [screen, setScreen] = useState<Screen>("welcome");
  const [messages, setMessages] = useState<Message[]>([]);

  function handleBegin() {
    setScreen("configure");
  }

  function handleReturnHome() {
    setScreen("welcome");
  }

  function handleStartRun(messages: Message[]) {
    setMessages(messages);
    setScreen("results");
  }

  if (screen === "welcome") {
    return <WelcomeScreen onBegin={handleBegin} />;
  } else if (screen === "configure") {
    return (
      <ConfigureScreen
        onReturnHome={handleReturnHome}
        onStartRun={handleStartRun}
      />
    );
  } else {
    return <ResultsScreen messages={messages} />;
  }
}
