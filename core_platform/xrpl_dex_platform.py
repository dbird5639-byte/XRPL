#!/usr/bin/env python3
"""
XRPL DEX Platform - Complete Integration
Advanced decentralized exchange with yield farming, flash loans, and security
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from decimal import Decimal

from core.xrpl_client import XRPLClient
from dex.dex_engine import DEXEngine, OrderBook, Order, OrderSide, OrderType
from defi.yield_farming import YieldFarmingEngine
from security.fort_knox_security import FortKnoxSecurity
from tools.dex_tools import DEXTools
from frontend.yield_farming_games import YieldFarmingGames

logger = logging.getLogger(__name__)

@dataclass
class PlatformStatus:
    """Platform status information"""
    is_online: bool
    total_users: int
    total_volume_24h: Decimal
    total_liquidity: Decimal
    security_alerts: int
    active_games: int
    last_updated: float

class XRPLDEXPlatform:
    """Complete XRPL DEX Platform with all features"""
    
    def __init__(self, network: str = "testnet"):
        self.network = network
        self.is_initialized = False
        
        # Core components
        self.xrpl_client: Optional[XRPLClient] = None
        self.dex_engine: Optional[DEXEngine] = None
        self.yield_farming: Optional[YieldFarmingEngine] = None
        self.security: Optional[FortKnoxSecurity] = None
        self.dex_tools: Optional[DEXTools] = None
        self.games: Optional[YieldFarmingGames] = None
        
        # Platform state
        self.platform_status = PlatformStatus(
            is_online=False,
            total_users=0,
            total_volume_24h=Decimal('0'),
            total_liquidity=Decimal('0'),
            security_alerts=0,
            active_games=0,
            last_updated=time.time()
        )
        
        # User sessions
        self.active_users: Dict[str, Dict] = {}
        
        logger.info("XRPL DEX Platform initialized")
    
    async def initialize(self) -> bool:
        """Initialize the complete platform"""
        try:
            logger.info("Initializing XRPL DEX Platform...")
            
            # Initialize XRPL client
            self.xrpl_client = XRPLClient(network=self.network)
            await self.xrpl_client.connect()
            
            # Initialize DEX engine
            self.dex_engine = DEXEngine(self.xrpl_client)
            
            # Initialize security system
            self.security = FortKnoxSecurity()
            
            # Initialize yield farming
            self.yield_farming = YieldFarmingEngine(self.xrpl_client)
            
            # Initialize DEX tools
            self.dex_tools = DEXTools(self.xrpl_client, self.yield_farming, self.security)
            
            # Initialize games
            self.games = YieldFarmingGames(self.yield_farming, self.dex_tools)
            
            # Mark as initialized
            self.is_initialized = True
            self.platform_status.is_online = True
            
            logger.info("XRPL DEX Platform initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Platform initialization failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the platform gracefully"""
        try:
            logger.info("Shutting down XRPL DEX Platform...")
            
            if self.xrpl_client:
                await self.xrpl_client.disconnect()
            
            self.platform_status.is_online = False
            self.is_initialized = False
            
            logger.info("Platform shutdown completed")
            
        except Exception as e:
            logger.error(f"Platform shutdown failed: {e}")
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get current platform status"""
        try:
            if not self.is_initialized:
                return {"error": "Platform not initialized"}
            
            # Update status
            self.platform_status.last_updated = time.time()
            self.platform_status.total_users = len(self.active_users)
            self.platform_status.active_games = len(self.games.active_sessions)
            
            # Get security status
            security_status = await self.security.get_security_status()
            self.platform_status.security_alerts = security_status.get('total_events', 0)
            
            return {
                "is_online": self.platform_status.is_online,
                "network": self.network,
                "total_users": self.platform_status.total_users,
                "total_volume_24h": str(self.platform_status.total_volume_24h),
                "total_liquidity": str(self.platform_status.total_liquidity),
                "security_alerts": self.platform_status.security_alerts,
                "active_games": self.platform_status.active_games,
                "last_updated": self.platform_status.last_updated,
                "components": {
                    "xrpl_client": self.xrpl_client is not None,
                    "dex_engine": self.dex_engine is not None,
                    "yield_farming": self.yield_farming is not None,
                    "security": self.security is not None,
                    "dex_tools": self.dex_tools is not None,
                    "games": self.games is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform status: {e}")
            return {"error": str(e)}
    
    async def create_user_session(self, user_address: str, wallet_info: Dict) -> str:
        """Create a new user session"""
        try:
            if not self.is_initialized:
                raise ValueError("Platform not initialized")
            
            # Security check
            threat_detected, actions, risk_score = await self.security.analyze_transaction({
                "from_address": user_address,
                "to_address": "platform",
                "amount": "0",
                "currency": "XRP"
            })
            
            if threat_detected:
                await self.security.record_security_event(
                    SecurityEventType.SUSPICIOUS_TRANSACTION,
                    ThreatLevel.HIGH,
                    f"High-risk user attempting to create session: {user_address}",
                    user_address=user_address,
                    amount=Decimal('0')
                )
                raise ValueError("User failed security check")
            
            # Create session
            session_id = f"session_{user_address}_{int(time.time())}"
            self.active_users[user_address] = {
                "session_id": session_id,
                "wallet_info": wallet_info,
                "created_at": time.time(),
                "last_activity": time.time(),
                "risk_score": risk_score,
                "permissions": self._get_user_permissions(risk_score)
            }
            
            logger.info(f"Created user session: {session_id} for {user_address}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            raise
    
    def _get_user_permissions(self, risk_score: int) -> List[str]:
        """Get user permissions based on risk score"""
        permissions = ["basic_trading", "view_pools"]
        
        if risk_score < 30:
            permissions.extend(["yield_farming", "flash_loans", "advanced_tools"])
        elif risk_score < 60:
            permissions.extend(["yield_farming", "basic_tools"])
        
        return permissions
    
    async def execute_trade(self, user_address: str, trade_data: Dict) -> Dict[str, Any]:
        """Execute a trade with security checks"""
        try:
            if not self.is_initialized:
                raise ValueError("Platform not initialized")
            
            # Security analysis
            threat_detected, actions, risk_score = await self.security.analyze_transaction(trade_data)
            
            if threat_detected:
                await self.security.record_security_event(
                    SecurityEventType.SUSPICIOUS_TRANSACTION,
                    ThreatLevel.MEDIUM,
                    f"Suspicious trade detected: {trade_data}",
                    user_address=user_address,
                    amount=Decimal(str(trade_data.get('amount', 0))),
                    currency=trade_data.get('currency', 'XRP')
                )
                
                # Apply security actions
                if SecurityAction.BLOCK in actions:
                    raise ValueError("Trade blocked by security system")
                elif SecurityAction.THROTTLE in actions:
                    await asyncio.sleep(5)  # Throttle execution
            
            # Execute trade on DEX
            if self.dex_engine:
                trade_result = await self.dex_engine.execute_trade(trade_data)
                
                # Update user session
                if user_address in self.active_users:
                    self.active_users[user_address]['last_activity'] = time.time()
                
                return {
                    "success": True,
                    "trade_id": trade_result.get('trade_id'),
                    "executed_price": trade_result.get('executed_price'),
                    "amount": trade_result.get('amount'),
                    "security_status": "passed",
                    "risk_score": risk_score
                }
            else:
                raise ValueError("DEX engine not available")
                
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def stake_in_pool(self, user_address: str, pool_id: str, amount: Decimal) -> Dict[str, Any]:
        """Stake tokens in a yield farming pool"""
        try:
            if not self.is_initialized:
                raise ValueError("Platform not initialized")
            
            # Check user permissions
            if user_address not in self.active_users:
                raise ValueError("User session not found")
            
            user_permissions = self.active_users[user_address]['permissions']
            if "yield_farming" not in user_permissions:
                raise ValueError("User not authorized for yield farming")
            
            # Execute staking
            success = await self.yield_farming.stake_tokens(user_address, pool_id, amount)
            
            if success:
                # Update platform status
                self.platform_status.total_liquidity += amount
                
                return {
                    "success": True,
                    "pool_id": pool_id,
                    "staked_amount": str(amount),
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "Staking failed"}
                
        except Exception as e:
            logger.error(f"Staking failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_flash_loan(self, user_address: str, loan_data: Dict) -> Dict[str, Any]:
        """Execute a flash loan with security checks"""
        try:
            if not self.is_initialized:
                raise ValueError("Platform not initialized")
            
            # Check user permissions
            if user_address not in self.active_users:
                raise ValueError("User session not found")
            
            user_permissions = self.active_users[user_address]['permissions']
            if "flash_loans" not in user_permissions:
                raise ValueError("User not authorized for flash loans")
            
            # Security analysis
            threat_detected, actions, risk_score = await self.security.analyze_transaction(loan_data)
            
            if threat_detected:
                await self.security.record_security_event(
                    SecurityEventType.FLASH_LOAN_ATTACK,
                    ThreatLevel.HIGH,
                    f"Potential flash loan attack: {loan_data}",
                    user_address=user_address,
                    amount=Decimal(str(loan_data.get('borrowed_amount', 0)))
                )
                
                if SecurityAction.BLOCK in actions:
                    raise ValueError("Flash loan blocked by security system")
            
            # Execute flash loan
            flash_loan_id = await self.yield_farming.execute_flash_loan(
                user_address,
                Decimal(str(loan_data.get('borrowed_amount', 0))),
                loan_data.get('borrowed_currency', 'XRP'),
                Decimal(str(loan_data.get('collateral_amount', 0))),
                loan_data.get('collateral_currency', 'XRP'),
                loan_data.get('arbitrage_trades', [])
            )
            
            if flash_loan_id:
                return {
                    "success": True,
                    "flash_loan_id": flash_loan_id,
                    "status": "executing",
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "Flash loan execution failed"}
                
        except Exception as e:
            logger.error(f"Flash loan failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_yield_farming_game(self, user_address: str, game_type: str) -> Dict[str, Any]:
        """Start a yield farming game"""
        try:
            if not self.is_initialized:
                raise ValueError("Platform not initialized")
            
            # Convert game type string to enum
            try:
                game_enum = GameType(game_type)
            except ValueError:
                raise ValueError(f"Invalid game type: {game_type}")
            
            # Start game
            session_id = await self.games.start_game(user_address, game_enum)
            
            if session_id:
                return {
                    "success": True,
                    "game_session_id": session_id,
                    "game_type": game_type,
                    "status": "started",
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "Failed to start game"}
                
        except Exception as e:
            logger.error(f"Game start failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def play_game(self, session_id: str, game_data: Dict) -> Dict[str, Any]:
        """Play a yield farming game"""
        try:
            if not self.is_initialized:
                raise ValueError("Platform not initialized")
            
            session = self.games.active_sessions.get(session_id)
            if not session:
                raise ValueError("Game session not found")
            
            game_type = session.game_type
            
            if game_type == GameType.LIQUIDITY_CHALLENGE:
                result = await self.games.play_liquidity_challenge(session_id, game_data.get('actions', []))
            elif game_type == GameType.FLASH_LOAN_MASTER:
                result = await self.games.play_flash_loan_master(session_id, game_data.get('loan_data', {}))
            elif game_type == GameType.YIELD_OPTIMIZER:
                result = await self.games.play_yield_optimizer(session_id, game_data.get('optimization_data', {}))
            else:
                raise ValueError(f"Unsupported game type: {game_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"Game play failed: {e}")
            return {"error": str(e)}
    
    async def complete_game(self, session_id: str) -> Dict[str, Any]:
        """Complete a yield farming game"""
        try:
            if not self.is_initialized:
                raise ValueError("Platform not initialized")
            
            result = await self.games.complete_game(session_id)
            return result
            
        except Exception as e:
            logger.error(f"Game completion failed: {e}")
            return {"error": str(e)}
    
    async def get_trading_signals(self, symbol: str, timeframe: str = "1h") -> List[Dict]:
        """Get trading signals from DEX tools"""
        try:
            if not self.is_initialized:
                return []
            
            signals = await self.dex_tools.get_trading_signals(symbol, timeframe)
            
            # Convert to serializable format
            serializable_signals = []
            for signal in signals:
                serializable_signals.append({
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type,
                    "confidence": signal.confidence,
                    "price_target": str(signal.price_target),
                    "stop_loss": str(signal.stop_loss) if signal.stop_loss else None,
                    "take_profit": str(signal.take_profit) if signal.take_profit else None,
                    "reasoning": signal.reasoning,
                    "timestamp": signal.timestamp,
                    "indicators": signal.indicators
                })
            
            return serializable_signals
            
        except Exception as e:
            logger.error(f"Failed to get trading signals: {e}")
            return []
    
    async def find_arbitrage_opportunities(self, min_profit_threshold: float = 0.01) -> List[Dict]:
        """Find arbitrage opportunities"""
        try:
            if not self.is_initialized:
                return []
            
            opportunities = await self.dex_tools.find_arbitrage_opportunities(min_profit_threshold)
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to find arbitrage opportunities: {e}")
            return []
    
    async def analyze_portfolio(self, user_address: str) -> Dict[str, Any]:
        """Analyze user portfolio"""
        try:
            if not self.is_initialized:
                return {}
            
            portfolio_data = await self.dex_tools.analyze_portfolio(user_address)
            
            # Calculate risk metrics
            risk_metrics = await self.dex_tools.calculate_risk_metrics(portfolio_data)
            
            # Convert to serializable format
            serializable_risk_metrics = {
                "total_value": str(risk_metrics.total_value),
                "volatility": risk_metrics.volatility,
                "sharpe_ratio": risk_metrics.sharpe_ratio,
                "max_drawdown": risk_metrics.max_drawdown,
                "var_95": risk_metrics.var_95,
                "beta": risk_metrics.beta,
                "risk_score": risk_metrics.risk_score
            }
            
            return {
                "portfolio": portfolio_data,
                "risk_metrics": serializable_risk_metrics
            }
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {}
    
    async def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get game leaderboard"""
        try:
            if not self.is_initialized:
                return []
            
            return await self.games.get_leaderboard(limit)
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return []
    
    async def get_user_stats(self, user_address: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            if not self.is_initialized:
                return {}
            
            return await self.games.get_user_stats(user_address)
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}
    
    async def get_available_games(self) -> List[Dict]:
        """Get list of available games"""
        try:
            if not self.is_initialized:
                return []
            
            return await self.games.get_available_games()
            
        except Exception as e:
            logger.error(f"Failed to get available games: {e}")
            return []

# Example usage and testing
async def main():
    """Main function for testing the platform"""
    try:
        # Initialize platform
        platform = XRPLDEXPlatform(network="testnet")
        
        # Initialize components
        success = await platform.initialize()
        if not success:
            logger.error("Platform initialization failed")
            return
        
        # Get platform status
        status = await platform.get_platform_status()
        logger.info(f"Platform status: {json.dumps(status, indent=2)}")
        
        # Example: Create user session
        user_address = "rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        wallet_info = {"type": "test_wallet"}
        
        session_id = await platform.create_user_session(user_address, wallet_info)
        logger.info(f"Created user session: {session_id}")
        
        # Example: Get available games
        games = await platform.get_available_games()
        logger.info(f"Available games: {json.dumps(games, indent=2)}")
        
        # Example: Start a game
        game_result = await platform.start_yield_farming_game(user_address, "liquidity_challenge")
        logger.info(f"Game start result: {json.dumps(game_result, indent=2)}")
        
        # Keep platform running
        logger.info("Platform is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Shutting down platform...")
        await platform.shutdown()
    except Exception as e:
        logger.error(f"Platform error: {e}")
        await platform.shutdown()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the platform
    asyncio.run(main())
