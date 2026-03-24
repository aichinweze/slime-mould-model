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

// For Generate Page
function SelectMessageBatchSize() {
  return (
    <div className="select-message-batch-size">
      <h2>Select Batch Size</h2>
      <p>
        Please select the number of messages to send to Adaptimould. (1 to
        2,000)
      </p>
      <input
        type="text"
        inputMode="numeric"
        pattern="[0-9]*"
        placeholder="Enter batch size"
      />
    </div>
  );
}

function SourceCurrencyTable() {
  const sourceCurrencies = [
    "Bitcoin (BTC)",
    "Ethereum (ETH)",
    "Cardano (ADA)",
    "Chainlink (LINK)",
    "Polkadot (DOT)",
    "Solana (SOL)",
  ];

  return sourceCurrencies.map((currency) => {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    const cellLabel = document.createElement("label");
    const cellCheckbox = document.createElement("input");

    cellCheckbox.type = "checkbox";
    cellCheckbox.value = currency;

    cellLabel.appendChild(cellCheckbox);
    cellLabel.appendChild(document.createTextNode(" " + currency));
    cell.appendChild(cellLabel);
    row.appendChild(cell);
  });
}

function CurrencySelection() {
  const targetCurrencies = [
    "US Dollar (USD)",
    "Pound Sterling (GBP)",
    "Japanese Yen (JPY)",
    "Bitcoin (BTC)",
  ];

  const sourceCurrencyTableBody = document.getElementById(
    "source-currency-table",
  );

  return (
    <div className="table-container">
      <table className="checkbox-table">
        <thead>
          <tr>
            <th>Source Currencies</th>
          </tr>
        </thead>
        <tbody id="source-currency-table"></tbody>
      </table>

      {/* <table className="checkbox-table">
        <thead>
          <tr>
            <th>Target Currencies</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <label>
                <input type="checkbox" /> Option 2A
              </label>
            </td>
          </tr>
          <tr>
            <td>
              <label>
                <input type="checkbox" /> Option 2B
              </label>
            </td>
          </tr>
          <tr>
            <td>
              <label>
                <input type="checkbox" /> Option 2C
              </label>
            </td>
          </tr>
        </tbody>
      </table> */}
    </div>
  );
}

function GeneratePage() {
  return (
    <div className="configure-page">
      <h2>Configure Adaptimould</h2>
      <p>Here you can configure the parameters for your Adaptimould run.</p>
      <SelectMessageBatchSize />
      <CurrencySelection />
    </div>
  );
}

type Screen = "welcome" | "configure" | "results";

function BatchSizeInput() {
  return (
    <div className="select-message-batch-size">
      <h2>Select Batch Size</h2>
      <p>
        Please select the number of messages to send to Adaptimould. (1 to
        2,000)
      </p>
      <input
        type="text"
        inputMode="numeric"
        pattern="[0-9]*"
        placeholder="Enter batch size"
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

function ConfigureScreen() {
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

  return (
    <div className="flex items-center justify-center flex-col gap-4 min-h-screen">
      <h2>Configure Adaptimould</h2>
      <p>Here you can configure the parameters for your Adaptimould run.</p>

      <BatchSizeInput />
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
  );
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("welcome");

  function handleBegin() {
    setScreen("configure");
  }

  if (screen === "welcome") {
    return <WelcomeScreen onBegin={handleBegin} />;
  } else if (screen === "configure") {
    return <ConfigureScreen />;
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
