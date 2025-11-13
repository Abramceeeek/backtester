/**
 * TradeList component - Displays individual trades in a formatted table
 */

export default function TradeList({ trades }) {
  const formatNumber = (num, decimals = 2) => {
    if (num === null || num === undefined) return 'N/A';
    return num.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  const formatPercent = (num, decimals = 2) => {
    if (num === null || num === undefined) return 'N/A';
    return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
  };

  const formatCurrency = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return `$${num.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (!trades || trades.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-gray-400 text-lg">No trades to display</p>
        <p className="text-gray-500 text-sm mt-2">Run a backtest to see individual trades</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-200">
          Sample Trades ({trades.length} shown)
        </h3>
        <div className="text-sm text-gray-400">
          Showing most recent trades
        </div>
      </div>

      {/* Desktop Table View */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Ticker
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Entry
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Exit
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                P&L
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Return
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Exit Reason
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50">
            {trades.map((trade, idx) => (
              <tr
                key={idx}
                className="hover:bg-gray-750 transition-colors"
              >
                <td className="py-3 px-4">
                  <span className="font-semibold text-gray-100">{trade.ticker}</span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-300">
                  <div>{formatDate(trade.entry_date)}</div>
                  <div className="text-xs text-gray-500">${formatNumber(trade.entry_price)}</div>
                </td>
                <td className="py-3 px-4 text-sm text-gray-300">
                  <div>{formatDate(trade.exit_date)}</div>
                  <div className="text-xs text-gray-500">${formatNumber(trade.exit_price)}</div>
                </td>
                <td className={`py-3 px-4 font-semibold ${
                  trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {formatCurrency(trade.pnl)}
                </td>
                <td className={`py-3 px-4 font-semibold ${
                  trade.pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {formatPercent(trade.pnl_percent)}
                </td>
                <td className="py-3 px-4 text-sm text-gray-400">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-gray-300">
                    {trade.exit_reason || 'Signal'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-3">
        {trades.map((trade, idx) => (
          <div
            key={idx}
            className="bg-gray-750 rounded-lg p-4 border border-gray-700"
          >
            <div className="flex justify-between items-start mb-3">
              <span className="font-bold text-lg text-gray-100">{trade.ticker}</span>
              <span className={`font-bold text-lg ${
                trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatPercent(trade.pnl_percent)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <p className="text-gray-500 text-xs">Entry</p>
                <p className="text-gray-300">{formatDate(trade.entry_date)}</p>
                <p className="text-gray-500 text-xs">${formatNumber(trade.entry_price)}</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Exit</p>
                <p className="text-gray-300">{formatDate(trade.exit_date)}</p>
                <p className="text-gray-500 text-xs">${formatNumber(trade.exit_price)}</p>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-700 flex justify-between items-center">
              <span className={`font-semibold ${
                trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatCurrency(trade.pnl)}
              </span>
              <span className="text-xs text-gray-400 px-2.5 py-0.5 rounded-full bg-gray-700">
                {trade.exit_reason || 'Signal'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
