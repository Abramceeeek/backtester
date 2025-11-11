/**
 * BacktestForm component - Form for configuring and submitting backtests
 */

import { useState, useEffect } from 'react';

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
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    const backtestConfig = {
      strategy_code: strategyCode,
      ...config,
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

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <form onSubmit={handleSubmit}>
        {/* Strategy Code Editor */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-semibold text-gray-700">
              Strategy Code
            </label>
            <button
              type="button"
              onClick={loadTemplate}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Load Template
            </button>
          </div>
          <textarea
            value={strategyCode}
            onChange={(e) => setStrategyCode(e.target.value)}
            className="w-full h-96 font-mono text-sm border border-gray-300 rounded-md p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your strategy code here..."
            required
          />
          <p className="mt-2 text-xs text-gray-500">
            Define a function named 'strategy' that takes (data, state) and returns a signal dict
          </p>
        </div>

        {/* Basic Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={config.start_date}
              onChange={(e) => handleConfigChange('start_date', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={config.end_date}
              onChange={(e) => handleConfigChange('end_date', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Initial Capital ($)
            </label>
            <input
              type="number"
              value={config.initial_capital}
              onChange={(e) => handleConfigChange('initial_capital', parseFloat(e.target.value))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500"
              min="1000"
              step="1000"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Position Size (0-1)
            </label>
            <input
              type="number"
              value={config.position_size}
              onChange={(e) => handleConfigChange('position_size', parseFloat(e.target.value))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500"
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
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            {showAdvanced ? '▼' : '▶'} Advanced Settings
          </button>
        </div>

        {/* Advanced Configuration */}
        {showAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Positions
              </label>
              <input
                type="number"
                value={config.max_positions}
                onChange={(e) => handleConfigChange('max_positions', parseInt(e.target.value))}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                min="1"
                max="100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Commission (%)
              </label>
              <input
                type="number"
                value={config.commission * 100}
                onChange={(e) => handleConfigChange('commission', parseFloat(e.target.value) / 100)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                min="0"
                max="1"
                step="0.01"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Slippage (%)
              </label>
              <input
                type="number"
                value={config.slippage * 100}
                onChange={(e) => handleConfigChange('slippage', parseFloat(e.target.value) / 100)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className={`px-6 py-3 rounded-md font-semibold text-white transition-colors ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {loading ? 'Running Backtest...' : 'Run Backtest'}
          </button>
        </div>
      </form>
    </div>
  );
}
