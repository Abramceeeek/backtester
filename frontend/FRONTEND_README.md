# Trading Strategy Backtester - Frontend Guide

## Overview

The frontend has been completely redesigned with a modern dark theme UI inspired by professional trading platforms. It features an intuitive interface with tabbed navigation, interactive tooltips, and comprehensive educational content.

## Key Features

### 🎨 Modern Dark Theme Design
- Professional dark UI matching the design mockup
- Green accent colors for positive metrics, red for negative
- Smooth animations and hover effects
- Fully responsive design (mobile, tablet, desktop)

### 📊 Enhanced Results Display
- **Summary Statistics Tab**: Key performance indicators with interactive tooltips
- **Equity Curve Tab**: Beautiful SVG chart showing portfolio growth over time
- **Trade List Tab**: Detailed table of individual trades with mobile-friendly card view

### 💡 Educational Features
- Comprehensive "Understanding Your Backtest" section
- Interactive tooltips explaining each metric
- Key metrics glossary
- Important disclaimers and best practices

### ⌨️ Code Editor
- Syntax-aware textarea for Python strategy code
- Dark theme with monospace font
- Load template button for quick starts
- Real-time validation feedback

## Installation & Setup

### Prerequisites
- Node.js 16+ and npm
- Backend API running on `http://localhost:8000` (see backtester/backend)

### Install Dependencies

```bash
cd C:\Users\HP\Documents\GitHub\backtester\frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

Visit http://localhost:3000/backtest to use the backtester.

### Build for Production

```bash
npm run build
npm start
```

## File Structure

```
frontend/
├── pages/
│   └── backtest.js              # Main backtester page (updated with dark theme)
├── components/
│   ├── BacktestForm.js          # Strategy input form (dark theme)
│   ├── ResultsDisplay.js        # Metrics with tooltips (dark theme)
│   ├── EquityChart.js           # SVG equity curve chart (dark theme)
│   ├── TradeList.js             # Individual trades table (NEW)
│   └── EducationSection.js      # Educational content (NEW)
├── styles/
│   └── globals.css              # Global styles
├── tailwind.config.js           # Tailwind config with custom colors
├── package.json                 # Dependencies
└── FRONTEND_README.md           # This file
```

## Component Details

### BacktestForm Component
**Location**: `components/BacktestForm.js`

Features:
- Dark theme code editor with Python syntax indicator
- Configurable parameters: dates, capital, position size
- Advanced settings (collapsible): max positions, commission, slippage
- Load template button to fetch example strategies from backend
- Responsive grid layout

### ResultsDisplay Component
**Location**: `components/ResultsDisplay.js`

Features:
- 8 key performance indicator cards with tooltips
- Color-coded metrics (green for positive, red for negative)
- Additional metrics section with 8 more data points
- Interactive hover effects
- Tooltip explanations for each metric

Metrics shown:
- Initial Capital, Final Equity, Net Profit, Annualized Return
- Sharpe Ratio, Max Drawdown, Winning Trades, Profit Factor
- Volatility, Sortino Ratio, Win Rate, Total Trades
- Avg Win/Loss, Best/Worst Trade

### EquityChart Component
**Location**: `components/EquityChart.js`

Features:
- Pure SVG chart (no external libraries)
- Dynamic scaling based on data range
- Gradient fill under the curve
- Grid lines and axis labels
- Dark theme with color-coded performance (green for profit, red for loss)
- Summary cards below chart (starting equity, final equity, total return)

### TradeList Component
**Location**: `components/TradeList.js`

Features:
- Desktop: Full table with sortable columns
- Mobile: Card-based layout
- Color-coded P&L (green/red)
- Date formatting and currency display
- Exit reason badges
- Empty state with helpful message

### EducationSection Component
**Location**: `components/EducationSection.js`

Features:
- Three info cards explaining backtesting concepts
- Detailed metrics glossary
- Important disclaimers section
- Icons and visual hierarchy
- Gradient backgrounds and hover effects

## Customization

### Colors

The app uses Tailwind CSS with custom gray shades for the dark theme:

```javascript
// tailwind.config.js
colors: {
  gray: {
    750: '#2d3748',  // Used for cards and containers
    850: '#1a202c',  // Used for tab backgrounds
  },
}
```

Primary colors:
- **Green** (#10b981): Positive metrics, success states, primary buttons
- **Red** (#ef4444): Negative metrics, error states
- **Gray**: Background, text, borders in various shades

### Adding New Metrics

To add a new metric to the results display:

1. Open `components/ResultsDisplay.js`
2. Add a new `<MetricCard>` component:

```jsx
<MetricCard
  label="Your Metric Name"
  value={formatNumber(metrics.your_metric)}
  isPositive={metrics.your_metric > threshold}
  tooltip="Explanation of what this metric means"
/>
```

### Modifying the Chart

The equity chart is built with pure SVG. To customize:

1. Open `components/EquityChart.js`
2. Modify colors in the gradient definitions
3. Adjust padding, dimensions in the `chartData` useMemo
4. Change grid line spacing in the `yGridLines` loop

## API Integration

The frontend connects to the backend API at `http://localhost:8000`.

### Main Endpoint

**POST** `/api/backtest`

Request body:
```json
{
  "strategy_code": "def strategy(data, state): ...",
  "universe": "sp500",
  "start_date": "2014-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "position_size": 0.1,
  "max_positions": 10,
  "commission": 0.001,
  "slippage": 0.0005
}
```

Response:
```json
{
  "success": true,
  "metrics": { ... },
  "equity_curve": [ ... ],
  "sample_trades": [ ... ]
}
```

### Template Endpoint

**GET** `/api/strategy/template`

Returns a strategy code template with documentation.

## Integration with Final-website

A standalone page has been created at:
`C:\Users\HP\Documents\GitHub\Final-website\backtester\index.html`

This page:
- Matches the styling of your main website
- Includes navigation to other sections
- Embeds the backtester in an iframe
- Provides context and instructions

### To Use This Page:

1. Make sure both backend and frontend are running:
   ```bash
   # Terminal 1 - Backend
   cd C:\Users\HP\Documents\GitHub\backtester\backend
   python api.py

   # Terminal 2 - Frontend
   cd C:\Users\HP\Documents\GitHub\backtester\frontend
   npm run dev
   ```

2. Open the integration page:
   - If using a local server for Final-website, navigate to: `http://localhost:PORT/backtester/`
   - Or open the HTML file directly in a browser

3. The iframe will load the backtester from localhost:3000

### Alternative: Direct Link

You can also add a link to the backtester in your services page:

```html
<a href="http://localhost:3000/backtest" target="_blank" class="service-link">
  Launch Backtester
</a>
```

## User Experience Enhancements

### Tooltips
Hover over the info icons (ℹ️) next to metric labels to see detailed explanations. Great for users learning about trading metrics.

### Tabbed Interface
Results are organized into three tabs:
1. **Summary Statistics**: Overview of performance metrics
2. **Equity Curve**: Visual representation of portfolio growth
3. **Trade List**: Individual trade details

### Responsive Design
- Desktop: Full two-column layout with side-by-side form and results
- Tablet: Stacked layout with collapsible sections
- Mobile: Card-based layouts, simplified tables, touch-friendly buttons

### Loading States
- Animated spinner during backtest execution
- Disabled submit button to prevent double submissions
- Progress indicators

### Error Handling
- Clear error messages with icons
- Validation feedback
- Helpful hints for common issues

## Testing

### Test Strategy

Use this simple RSI strategy to test the system:

```python
def strategy(data, state):
    """
    Simple RSI mean reversion strategy
    """
    close = data['close'].values

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

    has_position = state.get('has_position', False)

    if not has_position and current_rsi < 40:
        state['has_position'] = True
        return {
            'signal': 'buy',
            'stop_loss': 0.97,
            'take_profit': 1.08
        }
    elif has_position and current_rsi > 60:
        state['has_position'] = False
        return {'signal': 'sell'}

    return {'signal': None}
```

### Test Parameters
- Start Date: 2014-01-01
- End Date: 2024-01-01
- Initial Capital: $100,000
- Position Size: 0.1 (10% of capital per trade)

## Troubleshooting

### Frontend Won't Start
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend Connection Failed
- Verify backend is running: http://localhost:8000
- Check CORS settings in backend `api.py`
- Verify firewall isn't blocking port 8000

### Charts Not Displaying
- Check browser console for errors
- Verify equity_curve data is in correct format
- Try resizing browser window to trigger re-render

### Styling Issues
```bash
# Rebuild Tailwind CSS
npm run build
```

## Performance Optimization

### For Production:

1. **Enable Static Generation**
   ```bash
   npm run build
   npm run export
   ```

2. **Optimize Images** (if adding any)
   - Use Next.js Image component
   - Compress with imageoptim or similar

3. **Code Splitting**
   - Already handled by Next.js automatically
   - Components load only when needed

4. **API Caching**
   - Consider adding React Query for API state management
   - Cache template and universe data

## Future Enhancements

Potential improvements:

1. **Syntax Highlighting**: Integrate CodeMirror or Monaco Editor for better code editing
2. **Strategy Library**: Save and load favorite strategies
3. **Comparison Mode**: Compare multiple strategy results side-by-side
4. **Export Reports**: Generate PDF reports with charts and metrics
5. **Dark/Light Toggle**: Allow users to switch themes
6. **Advanced Charts**: Add drawdown charts, rolling metrics, etc.
7. **Real-time Updates**: WebSocket connection for live backtest progress
8. **Authentication**: User accounts to save strategies and results

## Support

For issues or questions:
- Check the main README.md in the backtester root
- Review the backend API documentation
- Check browser console for error messages
- Ensure all dependencies are up to date

## License

MIT License - Part of the Trading Strategy Backtester project
