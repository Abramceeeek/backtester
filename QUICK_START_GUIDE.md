# Quick Start Guide - Trading Strategy Backtester

## 🚀 How to Run and Test

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd C:\Users\HP\Documents\GitHub\backtester\backend
python api.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Keep this terminal open!**

### Step 2: Start the Frontend Development Server

Open a **new terminal** and run:

```bash
cd C:\Users\HP\Documents\GitHub\backtester\frontend
npm install  # Only needed first time
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Keep this terminal open too!**

### Step 3: Open the Backtester

Open your web browser and go to:

**http://localhost:3000/backtest**

You should now see the dark-themed backtester interface!

## ✅ Testing the Backtester

### Quick Test

1. The code editor should already have a default RSI strategy loaded
2. Leave the default parameters as-is
3. Click **"Run Backtest"** button
4. Wait 30-60 seconds for results
5. You should see:
   - Summary Statistics tab with performance metrics
   - Equity Curve tab with a chart
   - Trade List tab with individual trades

### Understanding the Results

#### Real-Time Progress ⭐ NEW!
While the backtest runs, you'll see:
- **Progress Bar** - Shows completion percentage (e.g., "125 / 503 stocks - 24.9%")
- **Current Ticker** - Which stock is being processed right now
- **Live Stock Results** - Individual stock performance appearing in real-time

#### Summary Statistics Tab
- **Green numbers** = Profitable/Good metrics
- **Red numbers** = Loss/Negative metrics
- **Hover over ℹ️ icons** for detailed explanations

#### Equity Curve Tab
- Shows your portfolio value over time
- **Green line** = Profitable strategy
- **Red line** = Losing strategy

#### Per-Stock Results Tab ⭐ NEW!
- See performance for each individual stock
- Sort by ticker, P&L, trades, or win rate
- Filter to show All / Winners / Losers
- Click column headers to change sorting

#### Trade List Tab
- Individual trades with entry/exit prices
- P&L for each trade
- Exit reason (signal, stop loss, take profit)

## 🌐 Adding to Your Website (Final-website)

### Option 1: Use the Integration Page

I've created a standalone page that matches your website's style:

1. Make sure both servers are running (backend and frontend)

2. Open: `C:\Users\HP\Documents\GitHub\Final-website\backtester\index.html`

3. Or add a link in your services page:

```html
<a href="backtester/index.html" class="service-link">
  <div class="service-card">
    <h3>Trading Strategy Backtester</h3>
    <p>Test algorithmic trading strategies on historical S&P 500 data</p>
  </div>
</a>
```

### Option 2: Deploy the Frontend Separately

If you want to deploy this as a standalone app:

1. Build the production version:
```bash
cd C:\Users\HP\Documents\GitHub\backtester\frontend
npm run build
```

2. The built files will be in `.next/` folder

3. Deploy to:
   - **Vercel** (free, built for Next.js) - Recommended
   - **Netlify** (free tier available)
   - **Your own server**

4. Update the backend URL in the code if needed

## 📋 Pre-Flight Checklist

Before showing this to others, make sure:

- [ ] Backend is running (http://localhost:8000)
- [ ] Frontend is running (http://localhost:3000)
- [ ] You can load the backtester page
- [ ] Test strategy runs successfully
- [ ] All three tabs show data
- [ ] Charts render correctly
- [ ] Mobile view works (resize browser)

## 🎨 What's New in the UI

### Dark Theme Design
- Professional dark interface matching the design mockup
- Green accents for positive metrics
- Red accents for negative metrics
- Smooth animations and transitions

### Tabbed Results
- **Summary Statistics**: Key performance metrics with tooltips
- **Equity Curve**: Beautiful chart showing portfolio growth
- **Trade List**: Detailed trade-by-trade breakdown

### Interactive Tooltips
- Hover over info icons for metric explanations
- Learn what each metric means as you go

### Educational Content
- "Understanding Your Backtest" section below results
- Key metrics glossary
- Important disclaimers

### Mobile Responsive
- Works on desktop, tablet, and mobile
- Touch-friendly buttons
- Adaptive layouts

## 🔧 Common Issues & Fixes

### "Failed to run backtest" Error

**Problem**: Backend not running or wrong URL

**Fix**:
```bash
# Check if backend is running
curl http://localhost:8000

# If not, start it:
cd C:\Users\HP\Documents\GitHub\backtester\backend
python api.py
```

### Page Shows "Module Not Found"

**Problem**: Dependencies not installed

**Fix**:
```bash
cd C:\Users\HP\Documents\GitHub\backtester\frontend
rm -rf node_modules
npm install
```

### Styling Looks Broken

**Problem**: Tailwind CSS needs rebuilding

**Fix**:
```bash
cd C:\Users\HP\Documents\GitHub\backtester\frontend
npm run dev
# Refresh browser with Ctrl+Shift+R (hard refresh)
```

### "Cannot connect to backend"

**Problem**: CORS or firewall blocking

**Fix**: Check `backend/api.py` has CORS enabled:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Testing on Mobile

To test on your phone:

1. Find your computer's local IP:
```bash
ipconfig  # Windows
# Look for IPv4 Address, e.g., 192.168.1.100
```

2. Update frontend to allow external connections:
```bash
cd C:\Users\HP\Documents\GitHub\backtester\frontend
npm run dev -- -H 0.0.0.0
```

3. On your phone's browser, go to:
```
http://192.168.1.100:3000/backtest
```

4. Backend might also need to allow external connections:
```python
# In backend/api.py, change:
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🎯 Next Steps

1. **Test with Your Own Strategies**
   - Click "Load Template" for examples
   - Modify the strategy code
   - Run multiple backtests

2. **Customize the UI**
   - Colors: Edit `tailwind.config.js`
   - Layout: Modify component files
   - Add features: Extend existing components

3. **Deploy to Production**
   - See FRONTEND_README.md for detailed deployment guide
   - Consider using Vercel or Netlify
   - Update API URLs for production

4. **Share Your Results**
   - Take screenshots of your best strategies
   - Export equity curves
   - Share performance metrics

## 📚 Documentation

- **Frontend Details**: See `frontend/FRONTEND_README.md`
- **Backend Details**: See `backend/README.md` (if exists) or main `README.md`
- **Strategy Examples**: Check `examples/` folder

## 🆘 Need Help?

If you run into issues:

1. Check the browser console (F12) for errors
2. Check both terminal windows for error messages
3. Make sure you're using Node.js 16+ and Python 3.8+
4. Try restarting both servers
5. Clear browser cache (Ctrl+Shift+R)

## 🎉 You're All Set!

Your backtester should now be running with:
- ✅ Modern dark theme UI
- ✅ Interactive tooltips
- ✅ Beautiful charts
- ✅ Mobile responsive design
- ✅ Educational content
- ✅ Professional styling

Enjoy testing your trading strategies!
