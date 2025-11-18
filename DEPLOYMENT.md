# Backtester Deployment Guide

This guide will help you deploy the trading strategy backtester to production.

## Quick Start

### Option 1: Single-Stock Backtester (Recommended for Small Traders)

The single-stock backtester is faster (5-10 seconds) and perfect for learning. It's already integrated into your website at:
- `Final-website/backtester/single-stock.html`

**No deployment needed!** Just:
1. Deploy your backend (see below)
2. Update `Final-website/backtester/config.js` with your backend URL
3. Deploy your website

### Option 2: Full Portfolio Backtester

For the full portfolio backtester with iframe integration, you need to deploy both backend and frontend.

---

## Backend Deployment

### Option A: Render.com (Recommended - Free Tier Available)

1. **Create a new Web Service on Render:**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Name:** `backtester-api`
   - **Root Directory:** `backtester/backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables:**
   ```
   ALLOWED_ORIGINS=https://your-website.com,https://your-frontend.vercel.app
   PORT=8000
   ```

4. **Get your backend URL:**
   - Render will provide: `https://backtester-api.onrender.com`
   - Update `Final-website/backtester/config.js`:
     ```javascript
     API_URL: 'https://backtester-api.onrender.com'
     ```

### Option B: Railway.app

1. **Create a new project on Railway:**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"

2. **Configure:**
   - Root directory: `backtester/backend`
   - Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables:**
   ```
   ALLOWED_ORIGINS=https://your-website.com
   ```

### Option C: Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create fly.toml in `backtester/backend/`:**
   ```toml
   app = "your-backtester-api"
   primary_region = "iad"

   [build]

   [http_service]
     internal_port = 8000
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0

   [[services]]
     protocol = "tcp"
     internal_port = 8000
   ```

3. **Deploy:**
   ```bash
   cd backtester/backend
   fly launch
   ```

---

## Frontend Deployment (Full Portfolio Only)

### Option A: Vercel (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd backtester/frontend
   vercel
   ```

3. **Set Environment Variable:**
   - In Vercel dashboard → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=https://your-backend-url.com`

4. **Update `backtester/frontend/pages/backtest.js`:**
   ```javascript
   const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
   ```

5. **Get your frontend URL:**
   - Vercel will provide: `https://your-app.vercel.app`
   - Update `Final-website/backtester/config.js`:
     ```javascript
     FRONTEND_URL: 'https://your-app.vercel.app'
     ```

### Option B: Netlify

1. **Create `backtester/frontend/netlify.toml`:**
   ```toml
   [build]
     command = "npm run build"
     publish = ".next"

   [[plugins]]
     package = "@netlify/plugin-nextjs"
   ```

2. **Deploy:**
   - Connect GitHub repo to Netlify
   - Set build directory: `backtester/frontend`
   - Add environment variable: `NEXT_PUBLIC_API_URL`

---

## Website Deployment

### Update Configuration

1. **Edit `Final-website/backtester/config.js`:**
   ```javascript
   const BACKTESTER_CONFIG = {
     API_URL: 'https://your-backend-url.com',  // Your deployed backend
     FRONTEND_URL: 'https://your-frontend-url.com',  // Your deployed frontend (if using full portfolio)
     // ... rest of config
   };
   ```

2. **Deploy your website** (GitHub Pages, Netlify, Vercel, etc.)

---

## Testing Deployment

### Test Backend

```bash
curl https://your-backend-url.com/health
```

Should return:
```json
{"status": "healthy", "timestamp": "..."}
```

### Test Single-Stock Backtester

1. Open `https://your-website.com/backtester/single-stock.html`
2. Select a stock (e.g., AAPL)
3. Click "Run Backtest"
4. Should complete in 5-10 seconds

### Test Full Portfolio Backtester

1. Open `https://your-website.com/backtester/`
2. Click "Full Portfolio Backtester"
3. Should load the iframe with the backtester

---

## Performance Optimization

### Backend Optimizations

1. **Enable caching:**
   - Data is already cached in `backend/data_cache/`
   - Cache persists between deployments on most platforms

2. **Use environment variables:**
   ```bash
   # In your deployment platform
   DATA_CACHE_DIR=./data_cache
   TICKER_CACHE_DAYS=30
   OHLCV_CACHE_DAYS=7
   ```

3. **For Render.com free tier:**
   - Service sleeps after 15 minutes of inactivity
   - First request after sleep takes ~30 seconds
   - Consider upgrading to paid tier for always-on service

### Frontend Optimizations

1. **Enable compression:**
   - Vercel/Netlify do this automatically
   - For custom servers, enable gzip

2. **Optimize bundle size:**
   ```bash
   cd backtester/frontend
   npm run build
   # Check .next/analyze for bundle size
   ```

---

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError`
- **Solution:** Ensure `requirements.txt` is in `backtester/backend/`
- Check build logs for missing dependencies

**Error:** `Port already in use`
- **Solution:** Use `$PORT` environment variable (Render/Railway set this automatically)

### CORS Errors

**Error:** `CORS policy blocked`
- **Solution:** Update `ALLOWED_ORIGINS` environment variable with your actual domain
- Check backend logs for CORS errors

### Frontend Can't Connect to Backend

**Error:** `Failed to fetch`
- **Solution:** 
  1. Check backend is running: `curl https://your-backend-url.com/health`
  2. Verify `API_URL` in `config.js` matches your backend URL
  3. Check browser console for detailed error

### Slow Performance

**Issue:** First request is slow
- **Solution:** 
  - This is normal - data needs to be downloaded/cached
  - Subsequent requests are much faster
  - Consider pre-warming cache with a scheduled job

---

## Security Checklist

- [ ] Update `ALLOWED_ORIGINS` to only your domains (remove `*`)
- [ ] Use HTTPS for all deployments
- [ ] Set up rate limiting (optional, for production)
- [ ] Monitor API usage and costs
- [ ] Keep dependencies updated

---

## Cost Estimates

### Free Tier Options

- **Render.com:** Free tier available (sleeps after 15 min inactivity)
- **Railway.app:** $5/month minimum
- **Fly.io:** Free tier available (limited resources)
- **Vercel:** Free tier available (generous limits)
- **Netlify:** Free tier available

### Recommended Setup (Free)

- Backend: Render.com (free tier)
- Frontend: Vercel (free tier)
- Website: GitHub Pages (free)

**Total Cost: $0/month**

---

## Next Steps

1. ✅ Deploy backend to Render/Railway/Fly.io
2. ✅ Update `config.js` with backend URL
3. ✅ Test single-stock backtester
4. ✅ (Optional) Deploy frontend for full portfolio backtester
5. ✅ Deploy your website
6. ✅ Test everything end-to-end

---

## Support

If you encounter issues:
1. Check backend logs in your deployment platform
2. Check browser console for frontend errors
3. Verify all URLs in `config.js` are correct
4. Test backend health endpoint: `/health`

---

**Last Updated:** November 2024

