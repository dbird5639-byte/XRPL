/**
 * Advanced Trading Agent for XRPL Agent Ecosystem
 * Implements sophisticated trading strategies with risk management
 */

class AdvancedTradingAgent {
  constructor(config) {
    this.config = {
      maxPositionSize: config.maxPositionSize || 0.1, // 10% of portfolio
      stopLoss: config.stopLoss || 0.05, // 5% stop loss
      takeProfit: config.takeProfit || 0.15, // 15% take profit
      riskPerTrade: config.riskPerTrade || 0.02, // 2% risk per trade
      maxTrades: config.maxTrades || 5,
      ...config
    };
    
    this.portfolio = {
      balance: 0,
      positions: [],
      totalPnL: 0,
      winRate: 0,
      sharpeRatio: 0
    };
    
    this.indicators = {
      sma: new SimpleMovingAverage(20),
      ema: new ExponentialMovingAverage(12),
      rsi: new RelativeStrengthIndex(14),
      macd: new MACD(12, 26, 9),
      bollinger: new BollingerBands(20, 2)
    };
    
    this.isActive = false;
    this.tradeHistory = [];
  }

  /**
   * Initialize the agent
   */
  async initialize() {
    try {
      console.log("🤖 Initializing Advanced Trading Agent...");
      
      // Connect to XRPL and EVM networks
      await this.connectToNetworks();
      
      // Load historical data
      await this.loadHistoricalData();
      
      // Initialize indicators
      this.initializeIndicators();
      
      // Set up event listeners
      this.setupEventListeners();
      
      this.isActive = true;
      console.log("✅ Advanced Trading Agent initialized successfully");
      
      return { success: true, message: "Agent initialized" };
    } catch (error) {
      console.error("❌ Failed to initialize agent:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Main execution function
   */
  async execute(inputData) {
    try {
      if (!this.isActive) {
        throw new Error("Agent not initialized");
      }

      const { action, symbol, amount, price } = inputData;
      
      switch (action) {
        case 'analyze':
          return await this.analyzeMarket(symbol);
          
        case 'trade':
          return await this.executeTrade(symbol, amount, price);
          
        case 'manage':
          return await this.managePositions();
          
        case 'report':
          return await this.generateReport();
          
        default:
          throw new Error(`Unknown action: ${action}`);
      }
    } catch (error) {
      console.error("❌ Execution error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Analyze market conditions
   */
  async analyzeMarket(symbol) {
    try {
      // Get current market data
      const marketData = await this.getMarketData(symbol);
      
      // Calculate technical indicators
      const analysis = {
        symbol: symbol,
        price: marketData.price,
        volume: marketData.volume,
        timestamp: Date.now(),
        indicators: {
          sma: this.indicators.sma.calculate(marketData.price),
          ema: this.indicators.ema.calculate(marketData.price),
          rsi: this.indicators.rsi.calculate(marketData.price),
          macd: this.indicators.macd.calculate(marketData.price),
          bollinger: this.indicators.bollinger.calculate(marketData.price)
        },
        signals: this.generateSignals(marketData),
        risk: this.calculateRisk(marketData)
      };
      
      return { success: true, analysis };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Execute a trade
   */
  async executeTrade(symbol, amount, price) {
    try {
      // Validate trade parameters
      const validation = this.validateTrade(symbol, amount, price);
      if (!validation.valid) {
        return { success: false, error: validation.error };
      }
      
      // Check risk limits
      const riskCheck = this.checkRiskLimits(amount, price);
      if (!riskCheck.valid) {
        return { success: false, error: riskCheck.error };
      }
      
      // Execute the trade
      const tradeResult = await this.placeOrder(symbol, amount, price);
      
      if (tradeResult.success) {
        // Update portfolio
        this.updatePortfolio(tradeResult.trade);
        
        // Log trade
        this.logTrade(tradeResult.trade);
        
        return { success: true, trade: tradeResult.trade };
      } else {
        return { success: false, error: tradeResult.error };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Manage existing positions
   */
  async managePositions() {
    try {
      const actions = [];
      
      for (const position of this.portfolio.positions) {
        const currentPrice = await this.getCurrentPrice(position.symbol);
        const pnl = this.calculatePnL(position, currentPrice);
        
        // Check stop loss
        if (pnl <= -this.config.stopLoss * position.amount) {
          const action = await this.closePosition(position, 'stop_loss');
          actions.push(action);
        }
        
        // Check take profit
        if (pnl >= this.config.takeProfit * position.amount) {
          const action = await this.closePosition(position, 'take_profit');
          actions.push(action);
        }
        
        // Check trailing stop
        if (this.shouldTrailStop(position, currentPrice)) {
          const action = await this.updateTrailingStop(position, currentPrice);
          actions.push(action);
        }
      }
      
      return { success: true, actions };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Generate trading signals
   */
  generateSignals(marketData) {
    const signals = {
      buy: false,
      sell: false,
      hold: true,
      confidence: 0,
      reasons: []
    };
    
    const { sma, ema, rsi, macd, bollinger } = this.indicators;
    
    // RSI signals
    if (rsi.value < 30) {
      signals.buy = true;
      signals.confidence += 0.3;
      signals.reasons.push("RSI oversold");
    } else if (rsi.value > 70) {
      signals.sell = true;
      signals.confidence += 0.3;
      signals.reasons.push("RSI overbought");
    }
    
    // MACD signals
    if (macd.histogram > 0 && macd.signal > macd.macd) {
      signals.buy = true;
      signals.confidence += 0.2;
      signals.reasons.push("MACD bullish crossover");
    } else if (macd.histogram < 0 && macd.signal < macd.macd) {
      signals.sell = true;
      signals.confidence += 0.2;
      signals.reasons.push("MACD bearish crossover");
    }
    
    // Bollinger Bands signals
    if (marketData.price < bollinger.lower) {
      signals.buy = true;
      signals.confidence += 0.2;
      signals.reasons.push("Price below lower Bollinger Band");
    } else if (marketData.price > bollinger.upper) {
      signals.sell = true;
      signals.confidence += 0.2;
      signals.reasons.push("Price above upper Bollinger Band");
    }
    
    // Moving average signals
    if (ema.value > sma.value) {
      signals.buy = true;
      signals.confidence += 0.1;
      signals.reasons.push("EMA above SMA");
    } else if (ema.value < sma.value) {
      signals.sell = true;
      signals.confidence += 0.1;
      signals.reasons.push("EMA below SMA");
    }
    
    // Determine final signal
    if (signals.buy && signals.sell) {
      signals.hold = true;
      signals.buy = false;
      signals.sell = false;
      signals.confidence = 0;
      signals.reasons.push("Conflicting signals");
    }
    
    return signals;
  }

  /**
   * Calculate portfolio risk
   */
  calculateRisk(marketData) {
    const totalExposure = this.portfolio.positions.reduce((sum, pos) => sum + pos.amount, 0);
    const maxAllowedExposure = this.portfolio.balance * this.config.maxPositionSize;
    
    return {
      totalExposure,
      maxAllowedExposure,
      exposureRatio: totalExposure / maxAllowedExposure,
      riskLevel: totalExposure > maxAllowedExposure ? 'HIGH' : 'NORMAL',
      recommendations: this.getRiskRecommendations(totalExposure, maxAllowedExposure)
    };
  }

  /**
   * Get risk recommendations
   */
  getRiskRecommendations(exposure, maxExposure) {
    const recommendations = [];
    
    if (exposure > maxExposure) {
      recommendations.push("Reduce position sizes");
      recommendations.push("Close some positions");
    }
    
    if (this.portfolio.positions.length >= this.config.maxTrades) {
      recommendations.push("Maximum number of trades reached");
    }
    
    return recommendations;
  }

  /**
   * Connect to networks
   */
  async connectToNetworks() {
    // Connect to XRPL
    this.xrplClient = new XRPLClient({
      server: 'wss://xrplcluster.com',
      account: this.config.xrplAccount
    });
    
    // Connect to EVM sidechain
    this.evmProvider = new ethers.providers.JsonRpcProvider(this.config.evmRpcUrl);
    this.evmWallet = new ethers.Wallet(this.config.privateKey, this.evmProvider);
    
    console.log("✅ Connected to XRPL and EVM networks");
  }

  /**
   * Load historical data
   */
  async loadHistoricalData() {
    // Load price history for indicators
    const history = await this.getPriceHistory(this.config.symbol, 100);
    this.priceHistory = history;
    
    console.log(`✅ Loaded ${history.length} historical data points`);
  }

  /**
   * Initialize technical indicators
   */
  initializeIndicators() {
    // Warm up indicators with historical data
    for (const price of this.priceHistory) {
      this.indicators.sma.calculate(price);
      this.indicators.ema.calculate(price);
      this.indicators.rsi.calculate(price);
      this.indicators.macd.calculate(price);
      this.indicators.bollinger.calculate(price);
    }
    
    console.log("✅ Technical indicators initialized");
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Listen for price updates
    this.xrplClient.on('price_update', (data) => {
      this.handlePriceUpdate(data);
    });
    
    // Listen for order fills
    this.xrplClient.on('order_fill', (data) => {
      this.handleOrderFill(data);
    });
    
    console.log("✅ Event listeners setup");
  }

  /**
   * Generate performance report
   */
  async generateReport() {
    const report = {
      timestamp: Date.now(),
      portfolio: this.portfolio,
      performance: {
        totalTrades: this.tradeHistory.length,
        winningTrades: this.tradeHistory.filter(t => t.pnl > 0).length,
        losingTrades: this.tradeHistory.filter(t => t.pnl < 0).length,
        winRate: this.calculateWinRate(),
        averageWin: this.calculateAverageWin(),
        averageLoss: this.calculateAverageLoss(),
        profitFactor: this.calculateProfitFactor(),
        sharpeRatio: this.calculateSharpeRatio()
      },
      risk: this.calculatePortfolioRisk(),
      recommendations: this.getPerformanceRecommendations()
    };
    
    return { success: true, report };
  }

  /**
   * Calculate win rate
   */
  calculateWinRate() {
    if (this.tradeHistory.length === 0) return 0;
    const winningTrades = this.tradeHistory.filter(t => t.pnl > 0).length;
    return (winningTrades / this.tradeHistory.length) * 100;
  }

  /**
   * Calculate Sharpe ratio
   */
  calculateSharpeRatio() {
    if (this.tradeHistory.length < 2) return 0;
    
    const returns = this.tradeHistory.map(t => t.pnl);
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);
    
    return stdDev === 0 ? 0 : avgReturn / stdDev;
  }

  /**
   * Get performance recommendations
   */
  getPerformanceRecommendations() {
    const recommendations = [];
    
    if (this.calculateWinRate() < 40) {
      recommendations.push("Consider improving entry criteria");
    }
    
    if (this.calculateSharpeRatio() < 1) {
      recommendations.push("Risk-adjusted returns could be improved");
    }
    
    if (this.portfolio.positions.length > this.config.maxTrades * 0.8) {
      recommendations.push("Approaching maximum position limit");
    }
    
    return recommendations;
  }
}

// Technical Indicator Classes
class SimpleMovingAverage {
  constructor(period) {
    this.period = period;
    this.values = [];
  }
  
  calculate(value) {
    this.values.push(value);
    if (this.values.length > this.period) {
      this.values.shift();
    }
    
    if (this.values.length < this.period) {
      return null;
    }
    
    this.value = this.values.reduce((sum, v) => sum + v, 0) / this.period;
    return this.value;
  }
}

class ExponentialMovingAverage {
  constructor(period) {
    this.period = period;
    this.alpha = 2 / (period + 1);
    this.value = null;
  }
  
  calculate(value) {
    if (this.value === null) {
      this.value = value;
    } else {
      this.value = this.alpha * value + (1 - this.alpha) * this.value;
    }
    return this.value;
  }
}

class RelativeStrengthIndex {
  constructor(period) {
    this.period = period;
    this.gains = [];
    this.losses = [];
    this.value = null;
  }
  
  calculate(value) {
    if (this.gains.length === 0) {
      this.gains.push(0);
      this.losses.push(0);
      return null;
    }
    
    const change = value - this.lastValue;
    const gain = change > 0 ? change : 0;
    const loss = change < 0 ? -change : 0;
    
    this.gains.push(gain);
    this.losses.push(loss);
    
    if (this.gains.length > this.period) {
      this.gains.shift();
      this.losses.shift();
    }
    
    if (this.gains.length < this.period) {
      this.lastValue = value;
      return null;
    }
    
    const avgGain = this.gains.reduce((sum, g) => sum + g, 0) / this.period;
    const avgLoss = this.losses.reduce((sum, l) => sum + l, 0) / this.period;
    
    if (avgLoss === 0) {
      this.value = 100;
    } else {
      const rs = avgGain / avgLoss;
      this.value = 100 - (100 / (1 + rs));
    }
    
    this.lastValue = value;
    return this.value;
  }
}

class MACD {
  constructor(fastPeriod, slowPeriod, signalPeriod) {
    this.fastEMA = new ExponentialMovingAverage(fastPeriod);
    this.slowEMA = new ExponentialMovingAverage(slowPeriod);
    this.signalEMA = new ExponentialMovingAverage(signalPeriod);
    this.macd = null;
    this.signal = null;
    this.histogram = null;
  }
  
  calculate(value) {
    const fastValue = this.fastEMA.calculate(value);
    const slowValue = this.slowEMA.calculate(value);
    
    if (fastValue === null || slowValue === null) {
      return null;
    }
    
    this.macd = fastValue - slowValue;
    this.signal = this.signalEMA.calculate(this.macd);
    
    if (this.signal !== null) {
      this.histogram = this.macd - this.signal;
    }
    
    return {
      macd: this.macd,
      signal: this.signal,
      histogram: this.histogram
    };
  }
}

class BollingerBands {
  constructor(period, stdDev) {
    this.period = period;
    this.stdDev = stdDev;
    this.sma = new SimpleMovingAverage(period);
    this.values = [];
    this.middle = null;
    this.upper = null;
    this.lower = null;
  }
  
  calculate(value) {
    this.middle = this.sma.calculate(value);
    this.values.push(value);
    
    if (this.values.length > this.period) {
      this.values.shift();
    }
    
    if (this.middle === null || this.values.length < this.period) {
      return null;
    }
    
    const variance = this.values.reduce((sum, v) => sum + Math.pow(v - this.middle, 2), 0) / this.period;
    const standardDeviation = Math.sqrt(variance);
    
    this.upper = this.middle + (this.stdDev * standardDeviation);
    this.lower = this.middle - (this.stdDev * standardDeviation);
    
    return {
      upper: this.upper,
      middle: this.middle,
      lower: this.lower
    };
  }
}

module.exports = AdvancedTradingAgent;
