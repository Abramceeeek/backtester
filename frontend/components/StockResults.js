/**
 * StockResults component - Displays per-stock backtest results
 */

import { useState } from 'react';

export default function StockResults({ stockResults }) {
  const [sortBy, setSortBy] = useState('pnl'); // 'pnl', 'ticker', 'trades', 'winRate'
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterType, setFilterType] = useState('all'); // 'all', 'winners', 'losers'

  if (!stockResults || stockResults.length === 0) {
    return null;
  }

  const formatCurrency = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return `$${num.toLocaleString(undefined, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const formatPercent = (num, decimals = 2) => {
    if (num === null || num === undefined) return 'N/A';
    return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
  };

  // Filter stocks
  let filteredStocks = [...stockResults];
  if (filterType === 'winners') {
    filteredStocks = filteredStocks.filter(s => s.total_pnl > 0);
  } else if (filterType === 'losers') {
    filteredStocks = filteredStocks.filter(s => s.total_pnl < 0);
  }

  // Sort stocks
  filteredStocks.sort((a, b) => {
    let aVal, bVal;

    switch (sortBy) {
      case 'pnl':
        aVal = a.total_pnl || 0;
        bVal = b.total_pnl || 0;
        break;
      case 'ticker':
        aVal = a.ticker;
        bVal = b.ticker;
        break;
      case 'trades':
        aVal = a.total_trades || 0;
        bVal = b.total_trades || 0;
        break;
      case 'winRate':
        aVal = a.win_rate || 0;
        bVal = b.win_rate || 0;
        break;
      default:
        aVal = 0;
        bVal = 0;
    }

    if (sortBy === 'ticker') {
      return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }

    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
  });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const SortIcon = ({ field }) => {
    if (sortBy !== field) return null;
    return (
      <svg className="w-4 h-4 inline ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        {sortOrder === 'asc' ? (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        ) : (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        )}
      </svg>
    );
  };

  const winners = stockResults.filter(s => s.total_pnl > 0).length;
  const losers = stockResults.filter(s => s.total_pnl < 0).length;

  return (
    <div className="space-y-4">
      {/* Header with filters */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold text-gray-200">
          Per-Stock Performance ({filteredStocks.length} stocks)
        </h3>

        {/* Filter buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setFilterType('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterType === 'all'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All ({stockResults.length})
          </button>
          <button
            onClick={() => setFilterType('winners')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterType === 'winners'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Winners ({winners})
          </button>
          <button
            onClick={() => setFilterType('losers')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterType === 'losers'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Losers ({losers})
          </button>
        </div>
      </div>

      {/* Desktop Table View */}
      <div className="hidden md:block overflow-x-auto bg-gray-750 rounded-lg border border-gray-700">
        <table className="w-full">
          <thead className="bg-gray-800 border-b border-gray-700">
            <tr>
              <th
                onClick={() => handleSort('ticker')}
                className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider cursor-pointer hover:text-green-400"
              >
                Ticker <SortIcon field="ticker" />
              </th>
              <th
                onClick={() => handleSort('trades')}
                className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider cursor-pointer hover:text-green-400"
              >
                Trades <SortIcon field="trades" />
              </th>
              <th
                onClick={() => handleSort('winRate')}
                className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider cursor-pointer hover:text-green-400"
              >
                Win Rate <SortIcon field="winRate" />
              </th>
              <th
                onClick={() => handleSort('pnl')}
                className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider cursor-pointer hover:text-green-400"
              >
                P&L <SortIcon field="pnl" />
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Return %
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Best / Worst
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50">
            {filteredStocks.map((stock, idx) => (
              <tr
                key={stock.ticker}
                className="hover:bg-gray-800 transition-colors"
              >
                <td className="py-3 px-4">
                  <span className="font-semibold text-gray-100">{stock.ticker}</span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-300">
                  {stock.total_trades}
                  <span className="text-xs text-gray-500 ml-1">
                    ({stock.winning_trades}W / {stock.losing_trades}L)
                  </span>
                </td>
                <td className="py-3 px-4 text-sm">
                  <span className={`font-medium ${
                    stock.win_rate > 0.5 ? 'text-green-400' : 'text-gray-300'
                  }`}>
                    {formatPercent(stock.win_rate * 100, 1)}
                  </span>
                </td>
                <td className={`py-3 px-4 font-semibold ${
                  stock.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {formatCurrency(stock.total_pnl)}
                </td>
                <td className={`py-3 px-4 font-medium text-sm ${
                  stock.total_pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {formatPercent(stock.total_pnl_percent)}
                </td>
                <td className="py-3 px-4 text-xs">
                  <div className="text-green-400">{formatCurrency(stock.best_trade)}</div>
                  <div className="text-red-400">{formatCurrency(stock.worst_trade)}</div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-3">
        {filteredStocks.map((stock) => (
          <div
            key={stock.ticker}
            className="bg-gray-750 rounded-lg p-4 border border-gray-700"
          >
            <div className="flex justify-between items-start mb-3">
              <span className="font-bold text-xl text-gray-100">{stock.ticker}</span>
              <span className={`font-bold text-xl ${
                stock.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatCurrency(stock.total_pnl)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-gray-500 text-xs">Trades</p>
                <p className="text-gray-300">{stock.total_trades}</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Win Rate</p>
                <p className="text-gray-300">{formatPercent(stock.win_rate * 100, 1)}</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Return</p>
                <p className={stock.total_pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {formatPercent(stock.total_pnl_percent)}
                </p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">W / L</p>
                <p className="text-gray-300">
                  {stock.winning_trades} / {stock.losing_trades}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
