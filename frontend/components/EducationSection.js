/**
 * EducationSection component - Educational content about backtesting
 */

export default function EducationSection() {
  const InfoCard = ({ icon, title, description }) => (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 hover:border-green-500/50 transition-colors">
      <div className="flex items-start">
        <div className="flex-shrink-0 text-4xl mr-4">
          {icon}
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-200 mb-2">{title}</h3>
          <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="mt-12 space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-3">
          Understanding Your Backtest
        </h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Backtest results are hypothetical and do not guarantee future results. Past performance is not indicative of future returns.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard
          icon="📊"
          title="How to Read Summary Statistics"
          description="Look at the performance metrics that matter most to you: total returns, risk-adjusted returns (Sharpe Ratio), and drawdowns. Compare these metrics to a buy-and-hold strategy to evaluate the value added by your strategy."
        />

        <InfoCard
          icon="📈"
          title="Interpreting the Equity Curve"
          description="Up close you'll see a scatter-and-stair line that slowly controls the patterns your equity tends over time. A smooth upward curve indicates consistent performance, while volatile swings suggest higher risk. Watch for extended drawdown periods."
        />

        <InfoCard
          icon="🎯"
          title="Analyzing Your Trades"
          description="To shed careful, try adding an extra dollar value to draw the risk, the club leads drawdown. Review individual trades to understand what works and what doesn't. Look for patterns in winning vs losing trades and consider refining entry/exit rules."
        />
      </div>

      <div className="bg-gradient-to-br from-green-900/20 to-blue-900/20 rounded-xl border border-green-500/30 p-8">
        <div className="flex items-start">
          <svg className="w-8 h-8 text-green-400 mr-4 flex-shrink-0 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <div>
            <h3 className="text-xl font-bold text-green-400 mb-3">Key Metrics Explained</h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-300 font-semibold mb-1">Sharpe Ratio</p>
                <p className="text-gray-400">Measures risk-adjusted returns. Values &gt;1 are good, &gt;2 are excellent. Higher is better.</p>
              </div>
              <div>
                <p className="text-gray-300 font-semibold mb-1">Max Drawdown</p>
                <p className="text-gray-400">Largest peak-to-trough decline. Indicates the worst-case loss scenario during the backtest period.</p>
              </div>
              <div>
                <p className="text-gray-300 font-semibold mb-1">Win Rate</p>
                <p className="text-gray-400">Percentage of profitable trades. A 50%+ win rate with proper risk management can be profitable.</p>
              </div>
              <div>
                <p className="text-gray-300 font-semibold mb-1">Profit Factor</p>
                <p className="text-gray-400">Ratio of gross profit to gross loss. Values &gt;1.5 indicate a robust strategy.</p>
              </div>
              <div>
                <p className="text-gray-300 font-semibold mb-1">CAGR</p>
                <p className="text-gray-400">Compound Annual Growth Rate - the average yearly return over the backtest period.</p>
              </div>
              <div>
                <p className="text-gray-300 font-semibold mb-1">Sortino Ratio</p>
                <p className="text-gray-400">Similar to Sharpe but only penalizes downside volatility. Better for asymmetric strategies.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start">
          <svg className="w-6 h-6 text-yellow-400 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h4 className="text-yellow-400 font-semibold mb-2">Important Disclaimers</h4>
            <ul className="text-gray-400 text-sm space-y-1">
              <li>• Backtest results are based on historical data and may not reflect future performance</li>
              <li>• Real trading involves additional costs like slippage, fees, and market impact</li>
              <li>• Be aware of overfitting - strategies that work too well on historical data may fail in live trading</li>
              <li>• Always validate strategies with out-of-sample testing before live deployment</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
