import * as Types from "../types";
import { useState } from "react";
import { generateMessages } from "../utils";
import { SOURCE_CURRENCIES, TARGET_CURRENCIES } from "../constants";

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

function ConfigureScreenButtonPanel({
  step,
  sourceCurrenciesLength,
  targetCurrenciesLength,
  onNextClick,
  onBackClick,
}: {
  step: Types.ConfigureScreenStep;
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

function GeneratedMessagesTable({ messages }: { messages: Types.Message[] }) {
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

export function ConfigureScreen({
  onReturnHome,
  onStartRun,
}: {
  onReturnHome: () => void;
  onStartRun: (messages: Types.Message[]) => void;
}) {
  const [step, setStep] = useState<Types.ConfigureScreenStep>("configure");
  const [batchSize, setBatchSize] = useState<number>(1);
  const [sourceCurrencies, setSourceCurrencies] = useState<string[]>([]);
  const [targetCurrencies, setTargetCurrencies] = useState<string[]>([]);
  const [messages, setMessages] = useState<Types.Message[]>([]);

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
