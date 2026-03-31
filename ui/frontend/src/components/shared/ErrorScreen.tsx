export function RenderErrorMessage({ message }: { message: string }) {
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
