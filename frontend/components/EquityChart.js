/**
 * EquityChart component - Displays equity curve chart with dark theme
 * Enhanced SVG-based line chart for equity visualization
 */

import { useMemo } from 'react';

export default function EquityChart({ data }) {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return null;

    const width = 1000;
    const height = 400;
    const padding = { top: 40, right: 40, bottom: 60, left: 80 };

    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Extract equity values
    const equityValues = data.map((d) => d.equity);
    const minEquity = Math.min(...equityValues);
    const maxEquity = Math.max(...equityValues);

    // Create scales
    const xScale = (index) => (index / (data.length - 1)) * chartWidth;
    const yScale = (value) =>
      chartHeight - ((value - minEquity) / (maxEquity - minEquity)) * chartHeight;

    // Generate path
    const pathData = data
      .map((point, index) => {
        const x = xScale(index);
        const y = yScale(point.equity);
        return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
      })
      .join(' ');

    // Generate grid lines
    const yGridLines = [];
    const numYLines = 5;
    for (let i = 0; i <= numYLines; i++) {
      const value = minEquity + ((maxEquity - minEquity) * i) / numYLines;
      const y = yScale(value);
      yGridLines.push({
        y,
        value,
      });
    }

    // Generate x-axis labels (show 5 dates)
    const xLabels = [];
    const labelInterval = Math.floor((data.length - 1) / 4);
    for (let i = 0; i < 5; i++) {
      const index = i * labelInterval;
      if (index < data.length) {
        xLabels.push({
          x: xScale(index),
          date: data[index].date,
        });
      }
    }

    return {
      pathData,
      yGridLines,
      xLabels,
      width,
      height,
      padding,
      chartWidth,
      chartHeight,
      minEquity,
      maxEquity,
    };
  }, [data]);

  if (!chartData) {
    return (
      <div className="text-center py-12">
        <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p className="text-gray-400 text-lg">No equity data available</p>
        <p className="text-gray-500 text-sm mt-2">Run a backtest to see the equity curve</p>
      </div>
    );
  }

  const formatCurrency = (num) => {
    if (num >= 1000000) {
      return `$${(num / 1000000).toFixed(1)}M`;
    }
    return `$${(num / 1000).toFixed(0)}K`;
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  };

  const isProfit = data[data.length - 1].equity >= data[0].equity;

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-200">Portfolio Equity Over Time</h3>

      <div className="overflow-x-auto bg-gray-750 rounded-lg p-4 border border-gray-700">
        <svg
          width={chartData.width}
          height={chartData.height}
          className="mx-auto"
          style={{ maxWidth: '100%', height: 'auto' }}
        >
          {/* Background */}
          <rect
            x={chartData.padding.left}
            y={chartData.padding.top}
            width={chartData.chartWidth}
            height={chartData.chartHeight}
            fill="#1f2937"
            rx="4"
          />

          {/* Grid lines */}
          {chartData.yGridLines.map((line, idx) => (
            <g key={idx}>
              <line
                x1={chartData.padding.left}
                y1={chartData.padding.top + line.y}
                x2={chartData.padding.left + chartData.chartWidth}
                y2={chartData.padding.top + line.y}
                stroke="#374151"
                strokeWidth="1"
                strokeDasharray="4,4"
              />
              <text
                x={chartData.padding.left - 10}
                y={chartData.padding.top + line.y + 4}
                textAnchor="end"
                fontSize="11"
                fill="#9ca3af"
                fontFamily="monospace"
              >
                {formatCurrency(line.value)}
              </text>
            </g>
          ))}

          {/* X-axis labels */}
          {chartData.xLabels.map((label, idx) => (
            <text
              key={idx}
              x={chartData.padding.left + label.x}
              y={chartData.padding.top + chartData.chartHeight + 25}
              textAnchor="middle"
              fontSize="11"
              fill="#9ca3af"
            >
              {formatDate(label.date)}
            </text>
          ))}

          {/* Area under curve */}
          <path
            d={`${chartData.pathData} L ${chartData.chartWidth} ${chartData.chartHeight} L 0 ${chartData.chartHeight} Z`}
            fill={`url(#gradient-${isProfit ? 'green' : 'red'})`}
            opacity="0.2"
            transform={`translate(${chartData.padding.left}, ${chartData.padding.top})`}
          />

          {/* Equity line */}
          <path
            d={chartData.pathData}
            fill="none"
            stroke={isProfit ? '#10b981' : '#ef4444'}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            transform={`translate(${chartData.padding.left}, ${chartData.padding.top})`}
          />

          {/* Gradient definitions */}
          <defs>
            <linearGradient id="gradient-green" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="gradient-red" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Y-axis label */}
          <text
            x={25}
            y={chartData.height / 2}
            textAnchor="middle"
            fontSize="12"
            fill="#9ca3af"
            fontWeight="500"
            transform={`rotate(-90, 25, ${chartData.height / 2})`}
          >
            Portfolio Value
          </text>

          {/* X-axis label */}
          <text
            x={chartData.width / 2}
            y={chartData.height - 5}
            textAnchor="middle"
            fontSize="12"
            fill="#9ca3af"
            fontWeight="500"
          >
            Time Period
          </text>
        </svg>
      </div>

      {/* Summary stats below chart */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
          <p className="text-xs text-gray-400 mb-1">Starting Equity</p>
          <p className="font-bold text-lg text-gray-100">
            {formatCurrency(data[0].equity)}
          </p>
        </div>
        <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
          <p className="text-xs text-gray-400 mb-1">Final Equity</p>
          <p className={`font-bold text-lg ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
            {formatCurrency(data[data.length - 1].equity)}
          </p>
        </div>
        <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
          <p className="text-xs text-gray-400 mb-1">Total Return</p>
          <p className={`font-bold text-lg ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
            {(
              ((data[data.length - 1].equity - data[0].equity) / data[0].equity) *
              100
            ).toFixed(2)}
            %
          </p>
        </div>
      </div>
    </div>
  );
}
