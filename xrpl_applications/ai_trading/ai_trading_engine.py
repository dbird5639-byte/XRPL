#!/usr/bin/env python3
"""
AI Trading Engine Module
Advanced AI-powered trading strategies and portfolio management
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ML imports
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error

from core.xrpl_client import XRPLClient, XRPLAccount
from dex.dex_engine import DEXTradingEngine, OrderSide, OrderType
from config import AI_CONFIG

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """Trading strategy types"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    GRID_TRADING = "grid_trading"
    DCA = "dollar_cost_averaging"
    MACHINE_LEARNING = "machine_learning"

class SignalType(Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class ModelType(Enum):
    """ML model types"""
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"

@dataclass
class TradingSignal:
    """Trading signal representation"""
    id: str
    strategy: StrategyType
    signal_type: SignalType
    base_currency: str
    quote_currency: str
    price: Decimal
    confidence: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TradingPosition:
    """Trading position representation"""
    id: str
    base_currency: str
    quote_currency: str
    side: OrderSide
    entry_price: Decimal
    current_price: Decimal
    amount: Decimal
    pnl: Decimal
    pnl_percentage: float
    timestamp: float
    strategy: StrategyType
    status: str = "open"

@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: Decimal
    total_pnl: Decimal
    total_pnl_percentage: float
    daily_pnl: Decimal
    daily_pnl_percentage: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profitable_trades: int

class MLModel:
    """Base class for machine learning models"""
    
    def __init__(self, model_type: ModelType, config: Dict[str, Any]):
        self.model_type = model_type
        self.config = config
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training/prediction"""
        # Feature engineering
        features = self._create_features(data)
        
        # Create target (next period return)
        data['returns'] = data['close'].pct_change()
        data['target'] = data['returns'].shift(-1)
        
        # Remove NaN values
        data = data.dropna()
        
        # Prepare X and y
        X = features.values
        y = data['target'].values
        
        return X, y
    
    def _create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create technical indicators and features"""
        # Price-based features
        data['price_change'] = data['close'].pct_change()
        data['price_change_2'] = data['close'].pct_change(2)
        data['price_change_5'] = data['close'].pct_change(5)
        
        # Volume features
        data['volume_change'] = data['volume'].pct_change()
        data['volume_ma'] = data['volume'].rolling(20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_ma']
        
        # Technical indicators
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        data['ema_12'] = data['close'].ewm(span=12).mean()
        data['ema_26'] = data['close'].ewm(span=26).mean()
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        data['macd'] = data['ema_12'] - data['ema_50']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # Bollinger Bands
        data['bb_middle'] = data['close'].rolling(20).mean()
        bb_std = data['close'].rolling(20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])
        
        # Remove columns with NaN values
        feature_columns = [col for col in data.columns if col not in ['open', 'high', 'low', 'close', 'volume', 'returns', 'target']]
        return data[feature_columns]
    
    def train(self, data: pd.DataFrame) -> bool:
        """Train the model"""
        try:
            X, y = self.prepare_data(data)
            
            if len(X) < 100:  # Need sufficient data
                logger.warning("Insufficient data for training")
                return False
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model based on type
            if self.model_type == ModelType.RANDOM_FOREST:
                self.model = RandomForestRegressor(
                    n_estimators=self.config.get('n_estimators', 100),
                    max_depth=self.config.get('max_depth', 10),
                    random_state=42
                )
            elif self.model_type == ModelType.GRADIENT_BOOSTING:
                self.model = GradientBoostingRegressor(
                    n_estimators=self.config.get('n_estimators', 100),
                    learning_rate=self.config.get('learning_rate', 0.1),
                    max_depth=self.config.get('max_depth', 5),
                    random_state=42
                )
            elif self.model_type == ModelType.LSTM and TENSORFLOW_AVAILABLE:
                self.model = self._create_lstm_model(X_train_scaled.shape[1])
            elif self.model_type == ModelType.GRU and TENSORFLOW_AVAILABLE:
                self.model = self._create_gru_model(X_train_scaled.shape[1])
            else:
                logger.error(f"Unsupported model type: {self.model_type}")
                return False
            
            # Train
            if self.model_type in [ModelType.RANDOM_FOREST, ModelType.GRADIENT_BOOSTING]:
                self.model.fit(X_train_scaled, y_train)
            else:
                # For neural networks
                X_train_reshaped = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
                X_test_reshaped = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
                
                self.model.fit(
                    X_train_reshaped, y_train,
                    epochs=self.config.get('epochs', 50),
                    batch_size=self.config.get('batch_size', 32),
                    validation_data=(X_test_reshaped, y_test),
                    verbose=0
                )
            
            # Evaluate
            if self.model_type in [ModelType.RANDOM_FOREST, ModelType.GRADIENT_BOOSTING]:
                y_pred = self.model.predict(X_test_scaled)
            else:
                y_pred = self.model.predict(X_test_reshaped).flatten()
            
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            logger.info(f"Model trained successfully. MSE: {mse:.6f}, MAE: {mae:.6f}")
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            return False
    
    def predict(self, data: pd.DataFrame) -> Optional[float]:
        """Make prediction"""
        if not self.is_trained or self.model is None:
            logger.warning("Model not trained")
            return None
        
        try:
            X, _ = self.prepare_data(data)
            if len(X) == 0:
                return None
            
            # Use last row for prediction
            X_pred = X[-1:].reshape(1, -1)
            X_pred_scaled = self.scaler.transform(X_pred)
            
            if self.model_type in [ModelType.RANDOM_FOREST, ModelType.GRADIENT_BOOSTING]:
                prediction = self.model.predict(X_pred_scaled)[0]
            else:
                # For neural networks
                X_pred_reshaped = X_pred_scaled.reshape((1, 1, X_pred_scaled.shape[1]))
                prediction = self.model.predict(X_pred_reshaped)[0][0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Failed to make prediction: {e}")
            return None
    
    def _create_lstm_model(self, input_dim: int) -> keras.Model:
        """Create LSTM model"""
        model = keras.Sequential([
            keras.layers.LSTM(
                units=self.config.get('lstm_units', 128),
                return_sequences=True,
                input_shape=(1, input_dim),
                dropout=self.config.get('dropout_rate', 0.2)
            ),
            keras.layers.LSTM(
                units=self.config.get('lstm_units', 128) // 2,
                dropout=self.config.get('dropout_rate', 0.2)
            ),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(self.config.get('dropout_rate', 0.2)),
            keras.layers.Dense(1)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.get('learning_rate', 0.001)),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _create_gru_model(self, input_dim: int) -> keras.Model:
        """Create GRU model"""
        model = keras.Sequential([
            keras.layers.GRU(
                units=self.config.get('lstm_units', 128),
                return_sequences=True,
                input_shape=(1, input_dim),
                dropout=self.config.get('dropout_rate', 0.2)
            ),
            keras.layers.GRU(
                units=self.config.get('lstm_units', 128) // 2,
                dropout=self.config.get('dropout_rate', 0.2)
            ),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(self.config.get('dropout_rate', 0.2)),
            keras.layers.Dense(1)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.get('learning_rate', 0.001)),
            loss='mse',
            metrics=['mae']
        )
        
        return model

class AITradingEngine:
    """Main AI trading engine"""
    
    def __init__(self, xrpl_client: XRPLClient, dex_engine: DEXTradingEngine):
        self.xrpl_client = xrpl_client
        self.dex_engine = dex_engine
        
        # ML models
        self.models: Dict[str, MLModel] = {}
        
        # Trading signals
        self.signals: List[TradingSignal] = []
        
        # Trading positions
        self.positions: Dict[str, TradingPosition] = {}
        
        # Portfolio tracking
        self.portfolio_history: List[Dict[str, Any]] = []
        
        # Strategy configurations
        self.strategy_configs: Dict[StrategyType, Dict[str, Any]] = {
            StrategyType.MOMENTUM: {
                'lookback_period': 20,
                'threshold': 0.02,
                'position_size': 0.1
            },
            StrategyType.MEAN_REVERSION: {
                'lookback_period': 50,
                'std_dev_threshold': 2.0,
                'position_size': 0.05
            },
            StrategyType.ARBITRAGE: {
                'min_spread': 0.005,
                'position_size': 0.2
            },
            StrategyType.GRID_TRADING: {
                'grid_levels': 10,
                'grid_spacing': 0.01,
                'position_size': 0.05
            }
        }
        
        # Initialize models
        self._init_models()
    
    def _init_models(self):
        """Initialize machine learning models"""
        try:
            # LSTM model
            if TENSORFLOW_AVAILABLE:
                self.models[ModelType.LSTM] = MLModel(
                    ModelType.LSTM,
                    {
                        'lstm_units': AI_CONFIG.lstm_units,
                        'dropout_rate': AI_CONFIG.dropout_rate,
                        'learning_rate': AI_CONFIG.learning_rate,
                        'epochs': 50,
                        'batch_size': AI_CONFIG.batch_size
                    }
                )
            
            # Random Forest model
            self.models[ModelType.RANDOM_FOREST] = MLModel(
                ModelType.RANDOM_FOREST,
                {
                    'n_estimators': 100,
                    'max_depth': 10
                }
            )
            
            # Gradient Boosting model
            self.models[ModelType.GRADIENT_BOOSTING] = MLModel(
                ModelType.GRADIENT_BOOSTING,
                {
                    'n_estimators': 100,
                    'learning_rate': 0.1,
                    'max_depth': 5
                }
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
    
    async def train_models(self, historical_data: Dict[str, pd.DataFrame]) -> bool:
        """Train all models with historical data"""
        try:
            for currency_pair, data in historical_data.items():
                logger.info(f"Training models for {currency_pair}")
                
                for model_type, model in self.models.items():
                    logger.info(f"Training {model_type.value} model...")
                    success = model.train(data)
                    
                    if success:
                        logger.info(f"{model_type.value} model trained successfully for {currency_pair}")
                    else:
                        logger.warning(f"Failed to train {model_type.value} model for {currency_pair}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train models: {e}")
            return False
    
    async def generate_signals(self, market_data: Dict[str, pd.DataFrame]) -> List[TradingSignal]:
        """Generate trading signals using AI models and strategies"""
        signals = []
        
        try:
            for currency_pair, data in market_data.items():
                if len(data) < 100:  # Need sufficient data
                    continue
                
                # Get AI predictions
                ai_signals = await self._get_ai_signals(currency_pair, data)
                signals.extend(ai_signals)
                
                # Get strategy signals
                strategy_signals = await self._get_strategy_signals(currency_pair, data)
                signals.extend(strategy_signals)
            
            # Store signals
            self.signals.extend(signals)
            
            logger.info(f"Generated {len(signals)} trading signals")
            return signals
            
        except Exception as e:
            logger.error(f"Failed to generate signals: {e}")
            return []
    
    async def _get_ai_signals(self, currency_pair: str, data: pd.DataFrame) -> List[TradingSignal]:
        """Get signals from AI models"""
        signals = []
        
        try:
            for model_type, model in self.models.items():
                if not model.is_trained:
                    continue
                
                prediction = model.predict(data)
                if prediction is None:
                    continue
                
                # Convert prediction to signal
                signal_type = self._prediction_to_signal(prediction)
                confidence = abs(prediction)
                
                if confidence >= AI_CONFIG.confidence_threshold:
                    signal = TradingSignal(
                        id=f"ai_signal_{int(time.time())}_{len(signals)}",
                        strategy=StrategyType.MACHINE_LEARNING,
                        signal_type=signal_type,
                        base_currency=currency_pair.split('_')[0],
                        quote_currency=currency_pair.split('_')[1],
                        price=Decimal(str(data['close'].iloc[-1])),
                        confidence=confidence,
                        timestamp=time.time(),
                        metadata={
                            'model_type': model_type.value,
                            'prediction': prediction,
                            'currency_pair': currency_pair
                        }
                    )
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Failed to get AI signals: {e}")
            return []
    
    async def _get_strategy_signals(self, currency_pair: str, data: pd.DataFrame) -> List[TradingSignal]:
        """Get signals from trading strategies"""
        signals = []
        
        try:
            # Momentum strategy
            momentum_signal = self._momentum_strategy(data, currency_pair)
            if momentum_signal:
                signals.append(momentum_signal)
            
            # Mean reversion strategy
            mean_rev_signal = self._mean_reversion_strategy(data, currency_pair)
            if mean_rev_signal:
                signals.append(mean_rev_signal)
            
            # Arbitrage strategy
            arbitrage_signal = self._arbitrage_strategy(data, currency_pair)
            if arbitrage_signal:
                signals.append(arbitrage_signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Failed to get strategy signals: {e}")
            return []
    
    def _prediction_to_signal(self, prediction: float) -> SignalType:
        """Convert ML prediction to trading signal"""
        if prediction > 0.01:  # Strong positive return expected
            return SignalType.STRONG_BUY
        elif prediction > 0.005:  # Positive return expected
            return SignalType.BUY
        elif prediction < -0.01:  # Strong negative return expected
            return SignalType.STRONG_SELL
        elif prediction < -0.005:  # Negative return expected
            return SignalType.SELL
        else:
            return SignalType.HOLD
    
    def _momentum_strategy(self, data: pd.DataFrame, currency_pair: str) -> Optional[TradingSignal]:
        """Momentum trading strategy"""
        try:
            config = self.strategy_configs[StrategyType.MOMENTUM]
            lookback = config['lookback_period']
            threshold = config['threshold']
            
            if len(data) < lookback:
                return None
            
            # Calculate momentum
            current_price = data['close'].iloc[-1]
            past_price = data['close'].iloc[-lookback]
            momentum = (current_price - past_price) / past_price
            
            if abs(momentum) < threshold:
                return None
            
            signal_type = SignalType.BUY if momentum > 0 else SignalType.SELL
            confidence = min(abs(momentum) / threshold, 1.0)
            
            return TradingSignal(
                id=f"momentum_signal_{int(time.time())}",
                strategy=StrategyType.MOMENTUM,
                signal_type=signal_type,
                base_currency=currency_pair.split('_')[0],
                quote_currency=currency_pair.split('_')[1],
                price=Decimal(str(current_price)),
                confidence=confidence,
                timestamp=time.time(),
                metadata={
                    'momentum': momentum,
                    'lookback_period': lookback,
                    'threshold': threshold
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate momentum signal: {e}")
            return None
    
    def _mean_reversion_strategy(self, data: pd.DataFrame, currency_pair: str) -> Optional[TradingSignal]:
        """Mean reversion trading strategy"""
        try:
            config = self.strategy_configs[StrategyType.MEAN_REVERSION]
            lookback = config['lookback_period']
            std_threshold = config['std_dev_threshold']
            
            if len(data) < lookback:
                return None
            
            # Calculate mean and standard deviation
            prices = data['close'].tail(lookback)
            mean_price = prices.mean()
            std_price = prices.std()
            current_price = data['close'].iloc[-1]
            
            # Calculate z-score
            z_score = (current_price - mean_price) / std_price
            
            if abs(z_score) < std_threshold:
                return None
            
            # Mean reversion: if price is high, sell; if low, buy
            signal_type = SignalType.SELL if z_score > 0 else SignalType.BUY
            confidence = min(abs(z_score) / std_threshold, 1.0)
            
            return TradingSignal(
                id=f"mean_rev_signal_{int(time.time())}",
                strategy=StrategyType.MEAN_REVERSION,
                signal_type=signal_type,
                base_currency=currency_pair.split('_')[0],
                quote_currency=currency_pair.split('_')[1],
                price=Decimal(str(current_price)),
                confidence=confidence,
                timestamp=time.time(),
                metadata={
                    'z_score': z_score,
                    'mean_price': mean_price,
                    'std_price': std_price,
                    'threshold': std_threshold
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate mean reversion signal: {e}")
            return None
    
    def _arbitrage_strategy(self, data: pd.DataFrame, currency_pair: str) -> Optional[TradingSignal]:
        """Arbitrage trading strategy"""
        try:
            config = self.strategy_configs[StrategyType.ARBITRAGE]
            min_spread = config['min_spread']
            
            # This is a simplified arbitrage check
            # In practice, you'd compare prices across different exchanges
            current_price = data['close'].iloc[-1]
            
            # Simulate finding arbitrage opportunity
            # In reality, you'd check multiple exchanges
            spread = 0.01  # Simulated spread
            
            if spread < min_spread:
                return None
            
            return TradingSignal(
                id=f"arbitrage_signal_{int(time.time())}",
                strategy=StrategyType.ARBITRAGE,
                signal_type=SignalType.BUY,  # Arbitrage is always buy on one side, sell on other
                base_currency=currency_pair.split('_')[0],
                quote_currency=currency_pair.split('_')[1],
                price=Decimal(str(current_price)),
                confidence=0.8,
                timestamp=time.time(),
                metadata={
                    'spread': spread,
                    'min_spread': min_spread
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate arbitrage signal: {e}")
            return None
    
    async def execute_signals(self, signals: List[TradingSignal]) -> List[str]:
        """Execute trading signals"""
        executed_orders = []
        
        try:
            for signal in signals:
                if signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                    order_id = await self._execute_buy_signal(signal)
                    if order_id:
                        executed_orders.append(order_id)
                
                elif signal.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]:
                    order_id = await self._execute_sell_signal(signal)
                    if order_id:
                        executed_orders.append(order_id)
            
            logger.info(f"Executed {len(executed_orders)} orders from signals")
            return executed_orders
            
        except Exception as e:
            logger.error(f"Failed to execute signals: {e}")
            return []
    
    async def _execute_buy_signal(self, signal: TradingSignal) -> Optional[str]:
        """Execute buy signal"""
        try:
            # Calculate position size based on confidence and strategy
            position_size = self._calculate_position_size(signal)
            
            # Place buy order
            order = await self.dex_engine.place_order(
                user_address=signal.metadata.get('user_address', 'ai_trader'),
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                base_currency=signal.base_currency,
                quote_currency=signal.quote_currency,
                base_amount=float(position_size)
            )
            
            if order:
                # Create position
                position = TradingPosition(
                    id=f"pos_{order.id}",
                    base_currency=signal.base_currency,
                    quote_currency=signal.quote_currency,
                    side=OrderSide.BUY,
                    entry_price=signal.price,
                    current_price=signal.price,
                    amount=position_size,
                    pnl=Decimal('0'),
                    pnl_percentage=0.0,
                    timestamp=time.time(),
                    strategy=signal.strategy
                )
                
                self.positions[position.id] = position
                logger.info(f"Buy order executed: {order.id}")
                return order.id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to execute buy signal: {e}")
            return None
    
    async def _execute_sell_signal(self, signal: TradingSignal) -> Optional[str]:
        """Execute sell signal"""
        try:
            # Find existing position to close
            position = self._find_position(signal.base_currency, signal.quote_currency)
            
            if not position:
                logger.warning(f"No position found to close for {signal.base_currency}")
                return None
            
            # Calculate position size
            position_size = position.amount
            
            # Place sell order
            order = await self.dex_engine.place_order(
                user_address=signal.metadata.get('user_address', 'ai_trader'),
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                base_currency=signal.base_currency,
                quote_currency=signal.quote_currency,
                base_amount=float(position_size)
            )
            
            if order:
                # Close position
                position.status = "closed"
                position.current_price = signal.price
                position.pnl = (signal.price - position.entry_price) * position.amount
                position.pnl_percentage = float(position.pnl / (position.entry_price * position.amount) * 100)
                
                logger.info(f"Sell order executed: {order.id}")
                return order.id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to execute sell signal: {e}")
            return None
    
    def _calculate_position_size(self, signal: TradingSignal) -> Decimal:
        """Calculate position size based on signal confidence and strategy"""
        base_size = AI_CONFIG.max_position_size
        
        # Adjust based on confidence
        confidence_multiplier = signal.confidence
        
        # Adjust based on strategy
        strategy_multiplier = 1.0
        if signal.strategy == StrategyType.ARBITRAGE:
            strategy_multiplier = 0.5  # Smaller positions for arbitrage
        elif signal.strategy == StrategyType.MACHINE_LEARNING:
            strategy_multiplier = 0.8  # Moderate positions for ML signals
        
        position_size = base_size * confidence_multiplier * strategy_multiplier
        
        return Decimal(str(position_size))
    
    def _find_position(self, base_currency: str, quote_currency: str) -> Optional[TradingPosition]:
        """Find existing position for currency pair"""
        for position in self.positions.values():
            if (position.base_currency == base_currency and 
                position.quote_currency == quote_currency and 
                position.status == "open"):
                return position
        return None
    
    def update_portfolio(self, current_prices: Dict[str, float]):
        """Update portfolio with current prices"""
        try:
            total_value = Decimal('0')
            total_pnl = Decimal('0')
            
            for position in self.positions.values():
                if position.status != "open":
                    continue
                
                # Update current price
                price_key = f"{position.base_currency}_{position.quote_currency}"
                if price_key in current_prices:
                    position.current_price = Decimal(str(current_prices[price_key]))
                    
                    # Calculate PnL
                    if position.side == OrderSide.BUY:
                        position.pnl = (position.current_price - position.entry_price) * position.amount
                    else:
                        position.pnl = (position.entry_price - position.current_price) * position.amount
                    
                    position.pnl_percentage = float(position.pnl / (position.entry_price * position.amount) * 100)
                    
                    # Add to totals
                    position_value = position.current_price * position.amount
                    total_value += position_value
                    total_pnl += position.pnl
            
            # Store portfolio snapshot
            portfolio_snapshot = {
                'timestamp': time.time(),
                'total_value': float(total_value),
                'total_pnl': float(total_pnl),
                'positions_count': len([p for p in self.positions.values() if p.status == "open"])
            }
            
            self.portfolio_history.append(portfolio_snapshot)
            
            # Keep only last 1000 snapshots
            if len(self.portfolio_history) > 1000:
                self.portfolio_history = self.portfolio_history[-1000:]
            
        except Exception as e:
            logger.error(f"Failed to update portfolio: {e}")
    
    def get_portfolio_metrics(self) -> PortfolioMetrics:
        """Calculate portfolio performance metrics"""
        try:
            if not self.portfolio_history:
                return PortfolioMetrics(
                    total_value=Decimal('0'),
                    total_pnl=Decimal('0'),
                    total_pnl_percentage=0.0,
                    daily_pnl=Decimal('0'),
                    daily_pnl_percentage=0.0,
                    sharpe_ratio=0.0,
                    max_drawdown=0.0,
                    win_rate=0.0,
                    total_trades=0,
                    profitable_trades=0
                )
            
            # Current values
            current_snapshot = self.portfolio_history[-1]
            total_value = Decimal(str(current_snapshot['total_value']))
            total_pnl = Decimal(str(current_snapshot['total_pnl']))
            
            # Calculate daily PnL
            one_day_ago = time.time() - 86400
            daily_snapshots = [s for s in self.portfolio_history if s['timestamp'] >= one_day_ago]
            
            if len(daily_snapshots) >= 2:
                daily_pnl = Decimal(str(daily_snapshots[-1]['total_pnl'])) - Decimal(str(daily_snapshots[0]['total_pnl']))
                daily_pnl_percentage = float(daily_pnl / total_value * 100) if total_value > 0 else 0.0
            else:
                daily_pnl = Decimal('0')
                daily_pnl_percentage = 0.0
            
            # Calculate Sharpe ratio (simplified)
            if len(self.portfolio_history) > 1:
                returns = []
                for i in range(1, len(self.portfolio_history)):
                    prev_value = self.portfolio_history[i-1]['total_value']
                    curr_value = self.portfolio_history[i]['total_value']
                    if prev_value > 0:
                        returns.append((curr_value - prev_value) / prev_value)
                
                if returns:
                    avg_return = np.mean(returns)
                    std_return = np.std(returns)
                    sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0
                else:
                    sharpe_ratio = 0.0
            else:
                sharpe_ratio = 0.0
            
            # Calculate max drawdown
            max_drawdown = 0.0
            if len(self.portfolio_history) > 1:
                peak = self.portfolio_history[0]['total_value']
                for snapshot in self.portfolio_history:
                    if snapshot['total_value'] > peak:
                        peak = snapshot['total_value']
                    else:
                        drawdown = (peak - snapshot['total_value']) / peak
                        max_drawdown = max(max_drawdown, drawdown)
            
            # Calculate win rate
            closed_positions = [p for p in self.positions.values() if p.status == "closed"]
            total_trades = len(closed_positions)
            profitable_trades = len([p for p in closed_positions if p.pnl > 0])
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0.0
            
            return PortfolioMetrics(
                total_value=total_value,
                total_pnl=total_pnl,
                total_pnl_percentage=float(total_pnl / total_value * 100) if total_value > 0 else 0.0,
                daily_pnl=daily_pnl,
                daily_pnl_percentage=daily_pnl_percentage,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                total_trades=total_trades,
                profitable_trades=profitable_trades
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio metrics: {e}")
            return PortfolioMetrics(
                total_value=Decimal('0'),
                total_pnl=Decimal('0'),
                total_pnl_percentage=0.0,
                daily_pnl=Decimal('0'),
                daily_pnl_percentage=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                total_trades=0,
                profitable_trades=0
            )
    
    def get_trading_signals(self, limit: int = 100) -> List[TradingSignal]:
        """Get recent trading signals"""
        return sorted(self.signals, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_open_positions(self) -> List[TradingPosition]:
        """Get all open positions"""
        return [p for p in self.positions.values() if p.status == "open"]
    
    def get_closed_positions(self) -> List[TradingPosition]:
        """Get all closed positions"""
        return [p for p in self.positions.values() if p.status == "closed"]
