import { useState } from "react";
import "./App.css";

function Sidebar() {
  return (
    <ul>
      <li>
        <a href="/">Home</a>
      </li>
      <li>
        <a href="run-adaptimould">Run Me!</a>
      </li>
    </ul>
  );
}

// For Home Page
function HomePage() {
  return (
    <div className="home-page">
      <h1>Adaptimould</h1>
      <h3>Welcome to the Adaptimould App!</h3>
      <p>Click the button below to get started.</p>
      <ToRunAdaptimouldButton />
    </div>
  );
}

// TODO: Make this button accept props?
function ToRunAdaptimouldButton() {
  return (
    <a href="run-adaptimould">
      <button className="button">Begin</button>
    </a>
  );
}

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

const SOURCE_CURRENCIES = ["BTC", "ETH", "ADA", "LINK", "DOT", "SOL"];
const TARGET_CURRENCIES = ["USD", "GBP", "EUR", "JPY"];

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
  //onStartRun,
}: {
  onReturnHome: () => void;
  //onStartRun: () => void;
}) {
  const [step, setStep] = useState<ConfigureScreenStep>("configure");
  const [batchSize, setBatchSize] = useState<number>(1);
  const [sourceCurrencies, setSourceCurrencies] = useState<string[]>([]);
  const [targetCurrencies, setTargetCurrencies] = useState<string[]>([]);

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
      setStep("review");
    } else {
      // TODO: move state to the Results screen
      // onStartRun();
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
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("welcome");

  function handleBegin() {
    setScreen("configure");
  }

  function handleReturnHome() {
    setScreen("welcome");
  }

  if (screen === "welcome") {
    return <WelcomeScreen onBegin={handleBegin} />;
  } else if (screen === "configure") {
    return <ConfigureScreen onReturnHome={handleReturnHome} />;
  } else {
    return <div>Results</div>;
  }
}

// return (
//   <div className="app">
//     <div className="sidenav">
//       <Sidebar />
//     </div>

//     <div className="content">
//       {/* <HomePage /> */}
//       <GeneratePage />
//     </div>
//   </div>
// );

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <section id="center">
//         <div className="hero">
//           <img src={heroImg} className="base" width="170" height="179" alt="" />
//           <img src={reactLogo} className="framework" alt="React logo" />
//           <img src={viteLogo} className="vite" alt="Vite logo" />
//         </div>
//         <div>
//           <h1>Get started</h1>
//           <p>
//             Edit <code>src/App.tsx</code> and save to test <code>HMR</code>
//           </p>
//         </div>
//         <button
//           className="counter"
//           onClick={() => setCount((count) => count + 1)}
//         >
//           Count is {count}
//         </button>
//       </section>

//       <div className="ticks"></div>

//       <section id="next-steps">
//         <div id="docs">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#documentation-icon"></use>
//           </svg>
//           <h2>Documentation</h2>
//           <p>Your questions, answered</p>
//           <ul>
//             <li>
//               <a href="https://vite.dev/" target="_blank">
//                 <img className="logo" src={viteLogo} alt="" />
//                 Explore Vite
//               </a>
//             </li>
//             <li>
//               <a href="https://react.dev/" target="_blank">
//                 <img className="button-icon" src={reactLogo} alt="" />
//                 Learn more
//               </a>
//             </li>
//           </ul>
//         </div>
//         <div id="social">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#social-icon"></use>
//           </svg>
//           <h2>Connect with us</h2>
//           <p>Join the Vite community</p>
//           <ul>
//             <li>
//               <a href="https://github.com/vitejs/vite" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#github-icon"></use>
//                 </svg>
//                 GitHub
//               </a>
//             </li>
//             <li>
//               <a href="https://chat.vite.dev/" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#discord-icon"></use>
//                 </svg>
//                 Discord
//               </a>
//             </li>
//             <li>
//               <a href="https://x.com/vite_js" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#x-icon"></use>
//                 </svg>
//                 X.com
//               </a>
//             </li>
//             <li>
//               <a href="https://bsky.app/profile/vite.dev" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#bluesky-icon"></use>
//                 </svg>
//                 Bluesky
//               </a>
//             </li>
//           </ul>
//         </div>
//       </section>

//       <div className="ticks"></div>
//       <section id="spacer"></section>
//     </>
//   )
// }

// export default App
