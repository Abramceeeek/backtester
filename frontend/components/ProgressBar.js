/**
 * ProgressBar component - Shows real-time backtest progress
 */

export default function ProgressBar({ completed, total, currentTicker }) {
  const percentage = total > 0 ? (completed / total) * 100 : 0;

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-200">
            Running Backtest...
          </h3>
          <span className="text-sm font-medium text-green-400">
            {completed} / {total} stocks
          </span>
        </div>

        {/* Progress Bar */}
        <div className="relative">
          <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-green-400 transition-all duration-300 ease-out rounded-full"
              style={{ width: `${percentage}%` }}
            >
              {/* Animated shimmer effect */}
              <div className="h-full w-full bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-shimmer"></div>
            </div>
          </div>
          <div className="absolute -top-6 right-0 text-sm font-bold text-green-400">
            {percentage.toFixed(1)}%
          </div>
        </div>

        {/* Current Ticker */}
        {currentTicker && (
          <div className="flex items-center text-sm text-gray-400">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-400 mr-2"></div>
            <span>Processing: <span className="text-green-400 font-semibold">{currentTicker}</span></span>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 pt-2">
          <div className="text-center">
            <div className="text-xs text-gray-500">Completed</div>
            <div className="text-lg font-bold text-green-400">{completed}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500">Remaining</div>
            <div className="text-lg font-bold text-gray-300">{total - completed}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500">Total</div>
            <div className="text-lg font-bold text-gray-300">{total}</div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
}
