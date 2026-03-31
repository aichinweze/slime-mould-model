export function RenderLoadingMessage({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-6 min-h-screen">
      <div className="w-12 h-12 rounded-full border-4 border-gray-200 border-t-brand animate-spin" />
      <p className="text-sm text-gray-600">{message}</p>
    </div>
  );
}
