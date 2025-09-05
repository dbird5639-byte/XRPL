# XRPL Arbitrage Bot

An automated arbitrage bot that identifies and executes profitable trades across multiple exchanges for XRP and other cryptocurrencies.

## Features

- **Multi-Exchange Support**: Binance, Coinbase, Kraken integration
- **Real-time Price Monitoring**: WebSocket connections for live price feeds
- **Automated Trading**: Execute buy/sell orders automatically
- **Risk Management**: Configurable position sizes and stop-losses
- **Profit Optimization**: Calculate optimal trade sizes for maximum profit
- **Notification System**: Telegram and email alerts for trades

## Revenue Model

- **Arbitrage Profits**: Earn from price differences between exchanges
- **Volume-based Fees**: Reduced trading fees with high volume
- **Performance Bonuses**: Additional profits from successful trades

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure API keys
cp config.json.example config.json
# Edit config.json with your API keys
```

## Configuration

### API Keys Setup

1. **Binance**:
   - Go to Binance API Management
   - Create new API key with trading permissions
   - Add to `config.json`

2. **Coinbase**:
   - Go to Coinbase Pro API settings
   - Create new API key with trading permissions
   - Add to `config.json`

3. **Kraken**:
   - Go to Kraken API settings
   - Create new API key with trading permissions
   - Add to `config.json`

### Risk Management Settings

```json
{
  "min_profit_threshold": "0.5",  // Minimum 0.5% profit
  "max_position_size": "1000",    // Maximum 1000 XRP per trade
  "max_daily_loss": "100",        // Maximum $100 daily loss
  "stop_loss_percentage": "2.0"   // 2% stop loss
}
```

## Usage

### Basic Usage

```bash
# Run the bot
python arbitrage_bot.py

# Run with specific configuration
python arbitrage_bot.py --config custom_config.json
```

### Advanced Usage

```python
from arbitrage_bot import XRPLArbitrageBot

# Create bot instance
bot = XRPLArbitrageBot("config.json")

# Run bot
await bot.run()
```

## Trading Strategy

### Arbitrage Detection

1. **Price Monitoring**: Continuously monitor prices across exchanges
2. **Opportunity Identification**: Detect price differences above threshold
3. **Profit Calculation**: Calculate potential profit after fees
4. **Risk Assessment**: Evaluate trade size and risk factors
5. **Execution**: Execute buy/sell orders simultaneously

### Profit Calculation

```
Profit = (Sell Price - Buy Price) - Trading Fees - Gas Fees
Profit % = (Profit / Buy Price) * 100
```

### Risk Management

- **Position Sizing**: Limit maximum trade size
- **Stop Loss**: Automatic stop-loss on losing trades
- **Daily Limits**: Maximum daily loss limits
- **Exchange Limits**: Respect exchange trading limits

## Supported Exchanges

### Binance
- **Trading Fee**: 0.1%
- **Withdrawal Fee**: 0.5 XRP
- **Min Trade**: 10 XRP
- **Max Trade**: 10,000 XRP

### Coinbase
- **Trading Fee**: 0.5%
- **Withdrawal Fee**: 1 XRP
- **Min Trade**: 25 XRP
- **Max Trade**: 50,000 XRP

### Kraken
- **Trading Fee**: 0.26%
- **Withdrawal Fee**: 0.02 XRP
- **Min Trade**: 5 XRP
- **Max Trade**: 20,000 XRP

## Monitoring and Alerts

### Telegram Notifications

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "your_bot_token",
    "chat_id": "your_chat_id"
  }
}
```

### Email Alerts

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "your_email@gmail.com",
    "password": "your_password"
  }
}
```

## Performance Metrics

### Key Performance Indicators

- **Total Profit**: Cumulative profit from all trades
- **Win Rate**: Percentage of profitable trades
- **Average Profit**: Average profit per trade
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return metric

### Reporting

```python
# Get performance report
report = bot.get_performance_report()
print(f"Total Profit: ${report['total_profit']}")
print(f"Win Rate: {report['win_rate']:.2f}%")
print(f"Total Trades: {report['total_trades']}")
```

## Security Features

- **API Key Encryption**: Encrypted storage of API keys
- **Rate Limiting**: Respect exchange rate limits
- **Error Handling**: Comprehensive error handling
- **Logging**: Detailed logging of all activities
- **Backup**: Automatic backup of configuration

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify API keys and permissions
2. **Insufficient Balance**: Check account balances
3. **Network Issues**: Check internet connection
4. **Exchange Maintenance**: Monitor exchange status

### Debug Mode

```bash
# Run with debug logging
python arbitrage_bot.py --debug
```

## Legal Disclaimer

This bot is for educational purposes only. Trading cryptocurrencies involves risk. Always:

- Test with small amounts first
- Understand the risks involved
- Comply with local regulations
- Monitor your trades closely

## License

MIT
