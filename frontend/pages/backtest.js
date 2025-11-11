/**
 * Backtest page component - Main interface for strategy backtesting
 *
 * This is a Next.js page component that provides:
 * - Strategy code editor
 * - Configuration form
 * - Results display with metrics and charts
 */

import { useState } from 'react';
import BacktestForm from '../components/BacktestForm';
import ResultsDisplay from '../components/ResultsDisplay';
import EquityChart from '../components/EquityChart';

export default function BacktestPage() {
  const [backtestResult, setBacktestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleBacktestSubmit = async (config) => {
    setLoading(true);
    setError(null);
    setBacktestResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      const result = await response.json();

      if (result.success) {
        setBacktestResult(result);
      } else {
        setError(result.message || 'Backtest failed');
      }
    } catch (err) {
      setError(`Failed to run backtest: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Strategy Backtester
          </h1>
          <p className="text-gray-600">
            Test your trading strategies on S&P 500 stocks with 10+ years of historical data
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 gap-8">
          {/* Backtest Form */}
          <BacktestForm
            onSubmit={handleBacktestSubmit}
            loading={loading}
          />

          {/* Loading State */}
          {loading && (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Running backtest... This may take a few minutes.</p>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="text-red-800 font-semibold mb-2">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Results Display */}
          {backtestResult && backtestResult.success && (
            <>
              <ResultsDisplay result={backtestResult} />
              <EquityChart data={backtestResult.equity_curve} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
