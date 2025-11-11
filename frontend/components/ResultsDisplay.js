/**
 * ResultsDisplay component - Displays backtest metrics and results
 */

export default function ResultsDisplay({ result }) {
  const { metrics, top_performers, worst_performers, sample_trades } = result;

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

  return (
    <div className="space-y-6">
      {/* Summary Metrics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Performance Summary
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Total Return */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Total Return</p>
            <p className={`text-2xl font-bold ${metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(metrics.total_return_percent)}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {formatCurrency(metrics.total_return)}
            </p>
          </div>

          {/* CAGR */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">CAGR</p>
            <p className={`text-2xl font-bold ${metrics.cagr >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(metrics.cagr)}
            </p>
          </div>

          {/* Sharpe Ratio */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Sharpe Ratio</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatNumber(metrics.sharpe_ratio, 2)}
            </p>
          </div>

          {/* Max Drawdown */}
          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Max Drawdown</p>
            <p className="text-2xl font-bold text-red-600">
              {formatPercent(metrics.max_drawdown_percent)}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {formatCurrency(metrics.max_drawdown)}
            </p>
          </div>

          {/* Win Rate */}
          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Win Rate</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatPercent(metrics.win_rate * 100, 1)}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {metrics.winning_trades}W / {metrics.losing_trades}L
            </p>
          </div>

          {/* Total Trades */}
          <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Total Trades</p>
            <p className="text-2xl font-bold text-gray-900">
              {metrics.total_trades}
            </p>
          </div>

          {/* Profit Factor */}
          <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Profit Factor</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatNumber(metrics.profit_factor, 2)}
            </p>
          </div>

          {/* Avg Trade */}
          <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Avg Trade P&L</p>
            <p className={`text-2xl font-bold ${metrics.avg_trade_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(metrics.avg_trade_pnl)}
            </p>
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Volatility (Annual)</p>
              <p className="font-semibold text-gray-900">{formatPercent(metrics.volatility)}</p>
            </div>
            <div>
              <p className="text-gray-600">Sortino Ratio</p>
              <p className="font-semibold text-gray-900">{formatNumber(metrics.sortino_ratio, 2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Avg Win</p>
              <p className="font-semibold text-green-600">{formatCurrency(metrics.avg_win)}</p>
            </div>
            <div>
              <p className="text-gray-600">Avg Loss</p>
              <p className="font-semibold text-red-600">{formatCurrency(metrics.avg_loss)}</p>
            </div>
            <div>
              <p className="text-gray-600">Best Trade</p>
              <p className="font-semibold text-green-600">{formatCurrency(metrics.best_trade)}</p>
            </div>
            <div>
              <p className="text-gray-600">Worst Trade</p>
              <p className="font-semibold text-red-600">{formatCurrency(metrics.worst_trade)}</p>
            </div>
            <div>
              <p className="text-gray-600">Consecutive Wins</p>
              <p className="font-semibold text-gray-900">{metrics.consecutive_wins}</p>
            </div>
            <div>
              <p className="text-gray-600">Consecutive Losses</p>
              <p className="font-semibold text-gray-900">{metrics.consecutive_losses}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Top/Worst Performers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Performers */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Top 10 Performers
          </h3>
          <div className="space-y-2">
            {top_performers?.map((perf, idx) => (
              <div
                key={perf.ticker}
                className="flex justify-between items-center p-3 bg-green-50 rounded-md"
              >
                <div>
                  <span className="font-semibold text-gray-900">
                    {idx + 1}. {perf.ticker}
                  </span>
                  <span className="text-sm text-gray-600 ml-2">
                    ({perf.total_trades} trades)
                  </span>
                </div>
                <div className="text-right">
                  <p className="font-bold text-green-600">
                    {formatCurrency(perf.total_pnl)}
                  </p>
                  <p className="text-xs text-gray-600">
                    {formatPercent(perf.total_pnl_percent)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Worst Performers */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Worst 10 Performers
          </h3>
          <div className="space-y-2">
            {worst_performers?.map((perf, idx) => (
              <div
                key={perf.ticker}
                className="flex justify-between items-center p-3 bg-red-50 rounded-md"
              >
                <div>
                  <span className="font-semibold text-gray-900">
                    {idx + 1}. {perf.ticker}
                  </span>
                  <span className="text-sm text-gray-600 ml-2">
                    ({perf.total_trades} trades)
                  </span>
                </div>
                <div className="text-right">
                  <p className="font-bold text-red-600">
                    {formatCurrency(perf.total_pnl)}
                  </p>
                  <p className="text-xs text-gray-600">
                    {formatPercent(perf.total_pnl_percent)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sample Trades */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Recent Trades
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ticker
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entry
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Exit
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  P&L
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Return
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Exit Reason
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sample_trades?.map((trade, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-4 py-3 whitespace-nowrap font-semibold text-gray-900">
                    {trade.ticker}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    {trade.entry_date}
                    <br />
                    <span className="text-xs">${formatNumber(trade.entry_price)}</span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    {trade.exit_date}
                    <br />
                    <span className="text-xs">${formatNumber(trade.exit_price)}</span>
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap font-semibold ${
                    trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(trade.pnl)}
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap font-semibold ${
                    trade.pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercent(trade.pnl_percent)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    {trade.exit_reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
