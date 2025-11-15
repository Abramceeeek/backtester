import requests
import json

# Test the streaming endpoint
url = "http://localhost:8000/api/backtest/stream"

config = {
    "strategy_code": """def strategy(data, state):
    close = data['close'].values
    if len(close) < 20:
        return {'signal': None}
    
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
        return {'signal': 'buy', 'stop_loss': 0.97, 'take_profit': 1.08}
    elif has_position and current_rsi > 60:
        state['has_position'] = False
        return {'signal': 'sell'}
    
    return {'signal': None}
""",
    "universe": "sp500",
    "start_date": "2014-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 100000,
    "position_size": 0.1,
    "max_positions": 10,
    "commission": 0.001,
    "slippage": 0.0005,
    "interval": "1d",
    "limit_tickers": 5  # Test with just 5 stocks
}

print("Sending backtest request...")
response = requests.post(url, json=config, stream=True, timeout=300)

print(f"Status: {response.status_code}")
print("Streaming response:")

for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        print(decoded_line)
        if decoded_line.startswith('data: '):
            data = json.loads(decoded_line[6:])
            print(f"  -> Type: {data.get('type')}, Message: {data.get('message', 'N/A')}")

print("\nTest complete!")
