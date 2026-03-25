import { useEffect, useState } from "react";
import "./App.css";

type Screen = "welcome" | "configure" | "results";

function BatchSizeInput({
  value,
  onChange,
}: {
  value: number;
  onChange: (input: number) => void;
}) {
  return (
    <div className="select-message-batch-size">
      <h2>Select Batch Size</h2>
      <p>
        Please select the number of messages to send to Adaptimould. (1 to
        2,000)
      </p>
      <input
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
    <div className="table-container">
      <table className="checkbox-table">
        <thead>
          <tr>
            <th>{title}</th>
          </tr>
        </thead>
        <tbody>
          {currencies.map((currency) => (
            <tr key={currency}>
              <td>
                <label>
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
    <div className="overflow-y-auto max-h-screen shadow-md rounded-lg">
      <table className="messages-table">
        <thead className="sticky top-0">
          <tr>
            <th>Source Currency</th>
            <th>Target Currency</th>
          </tr>
        </thead>
        <tbody>
          {messages.map((message, index) => (
            <tr key={index}>
              <td>{message.source}</td>
              <td>{message.target}</td>
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
      <header className="text-4xl">AdaptiMould</header>

      <p className="text-sm max-w-2xl">
        <b>AdaptiMould</b> uses a mathematical model of{" "}
        <em>Physarum polycephalum</em> (slime mould) to adaptively route
        requests between three worker functions based on real latency feedback.
        Watch the algorithm self-optimise in real time.
      </p>

      <p className="text-sm max-w-2xl">
        <b>How it works:</b> Configure a batch of cryptocurrency price requests
        → AdaptiMould routes them across workers → results show how the
        algorithm adapted routing weights over time.
      </p>

      <button
        className="bg-brand text-black px-6 py-2 rounded-md text-lg hover:opacity-90 hover:text-white transition-opacity"
        onClick={onBegin}
      >
        Begin
      </button>
    </div>
  );
}

type ConfigureScreenStep = "configure" | "review";
type Message = {
  source: string;
  target: string;
};

type ResultsScreenStep = "loading" | "display";
type Results = {
  // TODO: add later
};

const SOURCE_CURRENCIES = ["BTC", "ETH", "ADA", "LINK", "DOT", "SOL"];
const TARGET_CURRENCIES = ["USD", "GBP", "EUR", "JPY"];

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
    messages.push({ source, target });
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
        className="bg-brand text-black px-6 py-2 rounded-md text-lg hover:opacity-90 hover:text-white transition-opacity"
        onClick={onBackClick}
      >
        {backButtonText}
      </button>

      <button
        disabled={
          step === "configure" &&
          (sourceCurrenciesLength === 0 || targetCurrenciesLength === 0)
        }
        className="bg-brand text-black px-6 py-2 rounded-md text-lg 
                  hover:opacity-90 hover:text-white transition-opacity
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
        <h2>Configure Adaptimould</h2>
        <p>Here you can configure the parameters for your Adaptimould run.</p>

        <BatchSizeInput value={batchSize} onChange={onBatchInputChange} />
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
        <h2>Review</h2>
        <p>
          Here you can review the messages generated by your configuration
          before you proceed
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

function ResultsScreen({ messages }: { messages: Message[] }) {
  const [step, setStep] = useState<ResultsScreenStep>("loading");

  useEffect(() => {
    // Simulate loading time for results
    const timer = setTimeout(() => {
      setStep("display");
    }, 2000); // 2 second loading time

    return () => clearTimeout(timer);
  }, []);

  const displayText = step === "loading" ? "Loading..." : "Results go here";

  return <div>{displayText}</div>;
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
