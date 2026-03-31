import { useState } from "react";
import * as Types from "./types";
import { WelcomeScreen } from "./components/WelcomeScreen";
import { ConfigureScreen } from "./components/ConfigureScreen";
import { ResultsScreen } from "./components/ResultsScreen";

export default function App() {
  const [screen, setScreen] = useState<Types.Screen>("welcome");
  const [messages, setMessages] = useState<Types.Message[]>([]);

  function handleBegin() {
    setScreen("configure");
  }

  function handleReturnHome() {
    setScreen("welcome");
  }

  function handleStartRun(messages: Types.Message[]) {
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
