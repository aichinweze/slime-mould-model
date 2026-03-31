export function WelcomeScreen({ onBegin }: { onBegin: () => void }) {
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
