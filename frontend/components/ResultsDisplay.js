/**
 * ResultsDisplay component - Displays backtest metrics with tooltips and dark theme
 */

export default function ResultsDisplay({ result }) {
  const { metrics } = result;

  const exportToJSON = () => {
    const dataStr = JSON.stringify(result, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `backtest-results-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    if (!result.sample_trades || result.sample_trades.length === 0) {
      alert('No trade data available to export');
      return;
    }

    const headers = ['Ticker', 'Entry Date', 'Entry Price', 'Exit Date', 'Exit Price', 'P&L', 'P&L %', 'Exit Reason'];
    const rows = result.sample_trades.map(trade => [
      trade.ticker,
      trade.entry_date,
      trade.entry_price,
      trade.exit_date || 'N/A',
      trade.exit_price || 'N/A',
      trade.pnl || 'N/A',
      trade.pnl_percent || 'N/A',
      trade.exit_reason || 'N/A'
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `backtest-trades-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

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
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const Tooltip = ({ text }) => (
    <div className="group relative inline-block ml-2">
      <svg className="w-4 h-4 text-green-400 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div className="opacity-0 group-hover:opacity-100 absolute z-10 w-64 p-3 bg-gray-900 text-gray-100 text-xs rounded-lg shadow-xl -right-2 top-6 transition-opacity duration-200 pointer-events-none border border-gray-700">
        {text}
        <div className="absolute -top-1 right-4 w-2 h-2 bg-gray-900 border-l border-t border-gray-700 transform rotate-45"></div>
      </div>
    </div>
  );

  const MetricCard = ({ label, value, subValue, isPositive, tooltip }) => (
    <div className="bg-gray-750 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-gray-400">{label}</p>
        {tooltip && <Tooltip text={tooltip} />}
      </div>
      <p className={`text-2xl font-bold ${
        isPositive === true ? 'text-green-400' :
        isPositive === false ? 'text-red-400' :
        'text-gray-100'
      }`}>
        {value}
      </p>
      {subValue && (
        <p className="text-xs text-gray-500 mt-1">{subValue}</p>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Export Buttons */}
      <div className="flex justify-end gap-2">
        <button
          onClick={exportToCSV}
          className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export CSV
        </button>
        <button
          onClick={exportToJSON}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
          Export JSON
        </button>
      </div>

      {/* Key Performance Indicators Section */}
      <div>
        <h2 className="text-xl font-bold text-gray-200 mb-4">
          Key Performance Indicators
        </h2>

        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            label="Initial Capital"
            value={formatCurrency(metrics.initial_capital)}
            isPositive={null}
            tooltip="The starting amount of money allocated for trading"
          />

          <MetricCard
            label="Final Equity"
            value={formatCurrency(metrics.final_equity)}
            subValue={formatPercent(metrics.total_return_percent)}
            isPositive={metrics.total_return >= 0}
            tooltip="The total portfolio value at the end of the backtest period"
          />

          <MetricCard
            label="Net Profit"
            value={formatCurrency(metrics.total_return)}
            isPositive={metrics.total_return >= 0}
            tooltip="Total profit or loss after all trades and fees"
          />

          <MetricCard
            label="Annualized Return"
            value={formatPercent(metrics.cagr)}
            isPositive={metrics.cagr >= 0}
            tooltip="Compound Annual Growth Rate - average yearly return"
          />

          <MetricCard
            label="Sharpe Ratio"
            value={formatNumber(metrics.sharpe_ratio, 2)}
            isPositive={metrics.sharpe_ratio > 1}
            tooltip="Risk-adjusted return measure. >1 is good, >2 is excellent"
          />

          <MetricCard
            label="Max Drawdown"
            value={formatPercent(metrics.max_drawdown_percent)}
            isPositive={false}
            tooltip="Largest peak-to-trough decline in portfolio value"
          />

          <MetricCard
            label="Winning Trades"
            value={metrics.winning_trades}
            subValue={`${metrics.losing_trades} losing`}
            isPositive={metrics.winning_trades > metrics.losing_trades}
            tooltip="Number of profitable vs unprofitable trades"
          />

          <MetricCard
            label="Profit Factor"
            value={formatNumber(metrics.profit_factor, 2)}
            isPositive={metrics.profit_factor > 1}
            tooltip="Ratio of gross profit to gross loss. >1.5 is good"
          />
        </div>
      </div>

      {/* Additional Metrics */}
      <div>
        <h3 className="text-lg font-semibold text-gray-200 mb-3">
          Additional Metrics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Volatility</p>
            <p className="font-semibold text-gray-100">{formatPercent(metrics.volatility)}</p>
          </div>
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Sortino Ratio</p>
            <p className="font-semibold text-gray-100">{formatNumber(metrics.sortino_ratio, 2)}</p>
          </div>
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Win Rate</p>
            <p className="font-semibold text-gray-100">{formatPercent(metrics.win_rate * 100, 1)}</p>
          </div>
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Total Trades</p>
            <p className="font-semibold text-gray-100">{metrics.total_trades}</p>
          </div>
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Avg Win</p>
            <p className="font-semibold text-green-400">{formatCurrency(metrics.avg_win)}</p>
          </div>
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Avg Loss</p>
            <p className="font-semibold text-red-400">{formatCurrency(metrics.avg_loss)}</p>
          </div>
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Best Trade</p>
            <p className="font-semibold text-green-400">{formatCurrency(metrics.best_trade)}</p>
          </div>
          <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
            <p className="text-gray-400 mb-1">Worst Trade</p>
            <p className="font-semibold text-red-400">{formatCurrency(metrics.worst_trade)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
