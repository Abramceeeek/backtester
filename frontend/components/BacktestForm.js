/**
 * BacktestForm component - Form for configuring and submitting backtests
 */

import { useState, useEffect } from 'react';
import StrategyLibrary from './StrategyLibrary';

const DEFAULT_STRATEGY = `def strategy(data, state):
    """
    Simple RSI mean reversion strategy - more aggressive for testing.
    Buy when RSI < 40 (oversold), sell when RSI > 60 (overbought).
    Note: pd (pandas) and np (numpy) are pre-loaded, no import needed.
    """
    close = data['close'].values

    # Need at least 20 bars for RSI
    if len(close) < 20:
        return {'signal': None}

    # Calculate RSI (14 period)
    period = 14
    delta = pd.Series(close).diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    # Track if we have an open position
    has_position = state.get('has_position', False)

    if not has_position and current_rsi < 40:
        # Oversold - buy signal
        state['has_position'] = True
        return {
            'signal': 'buy',
            'stop_loss': 0.97,      # 3% stop loss
            'take_profit': 1.08     # 8% take profit
        }
    elif has_position and current_rsi > 60:
        # Overbought - sell signal
        state['has_position'] = False
        return {'signal': 'sell'}

    return {'signal': None}
`;

export default function BacktestForm({ onSubmit, loading }) {
  const [strategyCode, setStrategyCode] = useState(DEFAULT_STRATEGY);
  const [config, setConfig] = useState({
    universe: 'sp500',
    start_date: '2014-01-01',
    end_date: '2024-01-01',
    initial_capital: 100000,
    position_size: 0.1,
    max_positions: 10,
    commission: 0.001,
    slippage: 0.0005,
    interval: '1d',
    limit_tickers: null, // For quick testing
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [quickTest, setQuickTest] = useState(false);
  const [showLibrary, setShowLibrary] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    const backtestConfig = {
      strategy_code: strategyCode,
      ...config,
      limit_tickers: quickTest ? 20 : null, // Quick test uses 20 stocks
    };

    onSubmit(backtestConfig);
  };

  const handleConfigChange = (field, value) => {
    setConfig((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const loadTemplate = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/strategy/template');
      const data = await response.json();
      setStrategyCode(data.template);
    } catch (err) {
      console.error('Failed to load template:', err);
    }
  };

  const handleSelectStrategy = (strategy) => {
    setStrategyCode(strategy.code);
    setShowLibrary(false);
  };

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <form onSubmit={handleSubmit}>
        {/* Strategy Code Editor */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-3">
            <label className="block text-sm font-semibold text-gray-200">
              Your Strategy Code
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShowLibrary(!showLibrary)}
                className="text-sm text-green-400 hover:text-green-300 font-medium transition-colors flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Browse Library
              </button>
              <button
                type="button"
                onClick={loadTemplate}
                className="text-sm text-green-400 hover:text-green-300 font-medium transition-colors"
              >
                Load Template
              </button>
            </div>
          </div>

          {/* Strategy Library Modal */}
          {showLibrary && (
            <div className="mb-4">
              <StrategyLibrary onSelectStrategy={handleSelectStrategy} />
            </div>
          )}
          <div className="relative">
            <textarea
              value={strategyCode}
              onChange={(e) => setStrategyCode(e.target.value)}
              className="w-full h-96 font-mono text-sm bg-gray-900 text-gray-100 border border-gray-600 rounded-lg p-4 focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
              placeholder="Enter your strategy code here..."
              spellCheck="false"
              required
            />
            <div className="absolute top-3 right-3 text-xs text-gray-500 bg-gray-800/80 px-2 py-1 rounded">
              Python
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">
            Define a function named 'strategy' that takes (data, state) and returns a signal dict. <span className="text-green-400">pd</span> and <span className="text-green-400">np</span> are pre-loaded.
          </p>
        </div>

        {/* Basic Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={config.start_date}
              onChange={(e) => handleConfigChange('start_date', e.target.value)}
              className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={config.end_date}
              onChange={(e) => handleConfigChange('end_date', e.target.value)}
              className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Initial Capital ($)
            </label>
            <input
              type="number"
              value={config.initial_capital}
              onChange={(e) => handleConfigChange('initial_capital', parseFloat(e.target.value))}
              className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              min="1000"
              step="1000"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Position Size (0-1)
            </label>
            <input
              type="number"
              value={config.position_size}
              onChange={(e) => handleConfigChange('position_size', parseFloat(e.target.value))}
              className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              min="0.01"
              max="1"
              step="0.01"
              required
            />
          </div>
        </div>

        {/* Advanced Configuration Toggle */}
        <div className="mb-4">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-green-400 hover:text-green-300 font-medium transition-colors flex items-center"
          >
            <svg className={`w-4 h-4 mr-1 transform transition-transform ${showAdvanced ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Advanced Settings
          </button>
        </div>

        {/* Advanced Configuration */}
        {showAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-900/50 rounded-lg border border-gray-700">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Max Positions
              </label>
              <input
                type="number"
                value={config.max_positions}
                onChange={(e) => handleConfigChange('max_positions', parseInt(e.target.value))}
                className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500"
                min="1"
                max="100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Commission (%)
              </label>
              <input
                type="number"
                value={config.commission * 100}
                onChange={(e) => handleConfigChange('commission', parseFloat(e.target.value) / 100)}
                className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500"
                min="0"
                max="1"
                step="0.01"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Slippage (%)
              </label>
              <input
                type="number"
                value={config.slippage * 100}
                onChange={(e) => handleConfigChange('slippage', parseFloat(e.target.value) / 100)}
                className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
          </div>
        )}

        {/* Quick Test Toggle */}
        <div className="mb-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={quickTest}
              onChange={(e) => setQuickTest(e.target.checked)}
              className="w-5 h-5 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
            />
            <div className="ml-3">
              <span className="text-sm font-semibold text-blue-300">Quick Test Mode (20 stocks)</span>
              <p className="text-xs text-gray-400 mt-1">
                Test with only 20 stocks (~30 seconds) instead of all 503 stocks (~2-3 minutes)
              </p>
            </div>
          </label>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-3">
          <button
            type="submit"
            disabled={loading}
            className={`px-8 py-3 rounded-lg font-semibold text-white transition-all transform hover:scale-105 ${
              loading
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-500 shadow-lg shadow-green-500/30'
            }`}
          >
            {loading ? 'Running...' : quickTest ? 'Run Quick Test' : 'Run Full Backtest'}
          </button>
        </div>
      </form>
    </div>
  );
}
