/**
 * Backtest page component - Main interface for strategy backtesting
 *
 * Enhanced with:
 * - Dark theme UI matching design mockup
 * - Tabbed results view (Summary Statistics, Equity Curve, Trade List)
 * - Code editor with syntax highlighting
 * - Educational tooltips and help section
 */

import { useState } from 'react';
import BacktestForm from '../components/BacktestForm';
import ResultsDisplay from '../components/ResultsDisplay';
import EquityChart from '../components/EquityChart';
import TradeList from '../components/TradeList';
import EducationSection from '../components/EducationSection';
import ProgressBar from '../components/ProgressBar';
import StockResults from '../components/StockResults';

export default function BacktestPage() {
  const [backtestResult, setBacktestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  // Streaming progress state
  const [progress, setProgress] = useState({ completed: 0, total: 0, currentTicker: '' });
  const [stockResults, setStockResults] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState('');

  const handleBacktestSubmit = async (config) => {
    setLoading(true);
    setError(null);
    setBacktestResult(null);
    setStockResults([]);
    setProgress({ completed: 0, total: 0, currentTicker: '' });
    setLoadingStatus('Connecting to server...');

    try {
      // Use streaming endpoint for real-time progress
      const response = await fetch('http://localhost:8000/api/backtest/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        throw new Error('Failed to start backtest');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        // Decode the chunk
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.substring(6));

            if (data.type === 'init') {
              setProgress({ completed: 0, total: data.total_tickers, currentTicker: '' });
              setLoadingStatus(`Testing ${data.total_tickers} stocks...`);
            } else if (data.type === 'loading') {
              setLoadingStatus(data.message);
            } else if (data.type === 'progress') {
              setProgress({
                completed: data.completed,
                total: data.total,
                currentTicker: data.ticker
              });
              // Add stock result
              if (data.ticker_result && data.ticker_result.success) {
                setStockResults(prev => [...prev, data.ticker_result]);
              }
            } else if (data.type === 'complete') {
              setBacktestResult(data.result);
              setActiveTab('summary');
              setLoading(false);
            } else if (data.type === 'error') {
              setError(data.message);
              setLoading(false);
            }
          }
        }
      }
    } catch (err) {
      setError(`Failed to run backtest: ${err.message}`);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-5xl font-bold text-white mb-3 tracking-tight">
            Test Your Trading Strategies
          </h1>
          <p className="text-gray-300 text-lg max-w-3xl mx-auto">
            Once your backtest completes, the results appear here. Analyze key performance metrics and visualize trading algorithms.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Backtest Form */}
          <BacktestForm
            onSubmit={handleBacktestSubmit}
            loading={loading}
          />

          {/* Right Column - Results */}
          <div className="space-y-6">
            {/* Loading State with Progress */}
            {loading && (
              <>
                {/* Loading Status Message */}
                {loadingStatus && (
                  <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-400 mr-3"></div>
                      <p className="text-gray-300 font-medium">{loadingStatus}</p>
                    </div>
                  </div>
                )}

                {/* Progress Bar (only show after data is loaded) */}
                {progress.total > 0 && (
                  <ProgressBar
                    completed={progress.completed}
                    total={progress.total}
                    currentTicker={progress.currentTicker}
                  />
                )}

                {/* Show stock results as they come in */}
                {stockResults.length > 0 && (
                  <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                    <StockResults stockResults={stockResults} />
                  </div>
                )}
              </>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6">
                <div className="flex items-start">
                  <svg className="w-6 h-6 text-red-400 mt-0.5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h3 className="text-red-300 font-semibold text-lg mb-1">Error</h3>
                    <p className="text-red-200">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results Display with Tabs */}
            {backtestResult && backtestResult.success && (
              <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                {/* Tab Navigation */}
                <div className="flex border-b border-gray-700 bg-gray-850 overflow-x-auto">
                  <button
                    onClick={() => setActiveTab('summary')}
                    className={`flex-1 px-4 py-4 text-sm font-medium transition-colors whitespace-nowrap ${
                      activeTab === 'summary'
                        ? 'text-green-400 bg-gray-800 border-b-2 border-green-400'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }`}
                  >
                    Summary Statistics
                  </button>
                  <button
                    onClick={() => setActiveTab('equity')}
                    className={`flex-1 px-4 py-4 text-sm font-medium transition-colors whitespace-nowrap ${
                      activeTab === 'equity'
                        ? 'text-green-400 bg-gray-800 border-b-2 border-green-400'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }`}
                  >
                    Equity Curve
                  </button>
                  <button
                    onClick={() => setActiveTab('stocks')}
                    className={`flex-1 px-4 py-4 text-sm font-medium transition-colors whitespace-nowrap ${
                      activeTab === 'stocks'
                        ? 'text-green-400 bg-gray-800 border-b-2 border-green-400'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }`}
                  >
                    Per-Stock Results
                  </button>
                  <button
                    onClick={() => setActiveTab('trades')}
                    className={`flex-1 px-4 py-4 text-sm font-medium transition-colors whitespace-nowrap ${
                      activeTab === 'trades'
                        ? 'text-green-400 bg-gray-800 border-b-2 border-green-400'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }`}
                  >
                    Trade List
                  </button>
                </div>

                {/* Tab Content */}
                <div className="p-6">
                  {activeTab === 'summary' && (
                    <ResultsDisplay result={backtestResult} />
                  )}
                  {activeTab === 'equity' && (
                    <EquityChart data={backtestResult.equity_curve} />
                  )}
                  {activeTab === 'stocks' && (
                    <StockResults stockResults={stockResults} />
                  )}
                  {activeTab === 'trades' && (
                    <TradeList trades={backtestResult.sample_trades || []} />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Educational Section */}
        {!backtestResult && !loading && (
          <EducationSection />
        )}
      </div>
    </div>
  );
}
