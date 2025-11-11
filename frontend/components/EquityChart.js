/**
 * EquityChart component - Displays equity curve chart
 * Simple SVG-based line chart for equity visualization
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
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-600">No equity data available</p>
      </div>
    );
  }

  const formatCurrency = (num) => {
    return `$${(num / 1000).toFixed(0)}K`;
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Equity Curve</h3>

      <div className="overflow-x-auto">
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
            fill="#f9fafb"
          />

          {/* Grid lines */}
          {chartData.yGridLines.map((line, idx) => (
            <g key={idx}>
              <line
                x1={chartData.padding.left}
                y1={chartData.padding.top + line.y}
                x2={chartData.padding.left + chartData.chartWidth}
                y2={chartData.padding.top + line.y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
              <text
                x={chartData.padding.left - 10}
                y={chartData.padding.top + line.y + 4}
                textAnchor="end"
                fontSize="12"
                fill="#6b7280"
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
              y={chartData.padding.top + chartData.chartHeight + 20}
              textAnchor="middle"
              fontSize="12"
              fill="#6b7280"
            >
              {formatDate(label.date)}
            </text>
          ))}

          {/* Equity line */}
          <path
            d={chartData.pathData}
            fill="none"
            stroke="#2563eb"
            strokeWidth="2"
            transform={`translate(${chartData.padding.left}, ${chartData.padding.top})`}
          />

          {/* Area under curve */}
          <path
            d={`${chartData.pathData} L ${chartData.chartWidth} ${chartData.chartHeight} L 0 ${chartData.chartHeight} Z`}
            fill="url(#gradient)"
            opacity="0.3"
            transform={`translate(${chartData.padding.left}, ${chartData.padding.top})`}
          />

          {/* Gradient definition */}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#2563eb" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#2563eb" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Chart title */}
          <text
            x={chartData.width / 2}
            y={20}
            textAnchor="middle"
            fontSize="14"
            fontWeight="600"
            fill="#111827"
          >
            Portfolio Equity Over Time
          </text>

          {/* Y-axis label */}
          <text
            x={20}
            y={chartData.height / 2}
            textAnchor="middle"
            fontSize="12"
            fill="#6b7280"
            transform={`rotate(-90, 20, ${chartData.height / 2})`}
          >
            Equity ($)
          </text>

          {/* X-axis label */}
          <text
            x={chartData.width / 2}
            y={chartData.height - 10}
            textAnchor="middle"
            fontSize="12"
            fill="#6b7280"
          >
            Date
          </text>
        </svg>
      </div>

      {/* Summary stats below chart */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-600">Starting Equity</p>
            <p className="font-semibold text-gray-900">
              {formatCurrency(data[0].equity)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600">Final Equity</p>
            <p className="font-semibold text-gray-900">
              {formatCurrency(data[data.length - 1].equity)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600">Total Change</p>
            <p
              className={`font-semibold ${
                data[data.length - 1].equity >= data[0].equity
                  ? 'text-green-600'
                  : 'text-red-600'
              }`}
            >
              {(
                ((data[data.length - 1].equity - data[0].equity) / data[0].equity) *
                100
              ).toFixed(2)}
              %
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
