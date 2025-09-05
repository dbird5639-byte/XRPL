#!/usr/bin/env python3
"""
XRPL Yield Farming Web Games
Interactive games that gamify yield farming and DeFi participation
"""

import asyncio
import logging
import time
import json
import random
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GameType(Enum):
    """Types of yield farming games"""
    LIQUIDITY_CHALLENGE = "liquidity_challenge"
    FLASH_LOAN_MASTER = "flash_loan_master"
    YIELD_OPTIMIZER = "yield_optimizer"
    RISK_MANAGER = "risk_manager"
    ARBITRAGE_HUNTER = "arbitrage_hunter"
    POOL_MASTER = "pool_master"

class AchievementType(Enum):
    """Types of achievements"""
    FIRST_STAKE = "first_stake"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    FLASH_LOAN_EXPERT = "flash_loan_expert"
    RISK_MASTER = "risk_master"
    ARBITRAGE_KING = "arbitrage_king"
    POOL_CREATOR = "pool_creator"
    HIGH_APY = "high_apy"
    CONSISTENT_EARNER = "consistent_earner"

@dataclass
class GameSession:
    """Game session information"""
    id: str
    user_address: str
    game_type: GameType
    start_time: float
    end_time: Optional[float] = None
    score: int = 0
    level: int = 1
    completed: bool = False
    rewards_earned: Decimal = Decimal('0')
    achievements: List[str] = field(default_factory=list)

@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    icon: str
    points: int
    rarity: str  # common, rare, epic, legendary
    requirements: Dict[str, Any]
    reward_multiplier: float = 1.0

@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    user_address: str
    username: str
    total_score: int
    games_played: int
    achievements_count: int
    total_rewards: Decimal
    rank: int = 0
    last_updated: float = field(default_factory=time.time)

class YieldFarmingGames:
    """Interactive yield farming games system"""
    
    def __init__(self, yield_farming_engine, dex_tools):
        self.yield_farming = yield_farming_engine
        self.dex_tools = dex_tools
        self.active_sessions: Dict[str, GameSession] = {}
        self.leaderboard: List[LeaderboardEntry] = []
        self.achievements: Dict[str, Achievement] = {}
        self.user_stats: Dict[str, Dict] = {}
        
        # Initialize games
        self._initialize_achievements()
        self._initialize_leaderboard()
    
    def _initialize_achievements(self):
        """Initialize achievement system"""
        achievements_data = [
            {
                "id": "first_stake",
                "name": "First Stake",
                "description": "Make your first stake in a yield pool",
                "icon": "🌱",
                "points": 100,
                "rarity": "common",
                "requirements": {"first_stake": True}
            },
            {
                "id": "liquidity_provider",
                "name": "Liquidity Provider",
                "description": "Provide liquidity to 5 different pools",
                "icon": "💧",
                "points": 500,
                "rarity": "rare",
                "requirements": {"pools_provided": 5}
            },
            {
                "id": "flash_loan_expert",
                "name": "Flash Loan Expert",
                "description": "Successfully execute 10 flash loans",
                "icon": "⚡",
                "points": 1000,
                "rarity": "epic",
                "requirements": {"flash_loans_executed": 10}
            },
            {
                "id": "risk_master",
                "name": "Risk Master",
                "description": "Maintain a risk score below 20 for 30 days",
                "icon": "🛡️",
                "points": 2000,
                "rarity": "legendary",
                "requirements": {"low_risk_days": 30}
            },
            {
                "id": "arbitrage_king",
                "name": "Arbitrage King",
                "description": "Find and execute 50 arbitrage opportunities",
                "icon": "👑",
                "points": 3000,
                "rarity": "legendary",
                "requirements": {"arbitrage_opportunities": 50}
            }
        ]
        
        for achievement_data in achievements_data:
            achievement = Achievement(**achievement_data)
            self.achievements[achievement.id] = achievement
    
    def _initialize_leaderboard(self):
        """Initialize leaderboard"""
        # This would load from persistent storage
        self.leaderboard = []
    
    async def start_game(self, user_address: str, game_type: GameType) -> str:
        """Start a new game session"""
        try:
            # Check if user already has an active session
            active_session = self._get_active_session(user_address, game_type)
            if active_session:
                return active_session.id
            
            # Create new session
            session_id = f"game_{game_type.value}_{user_address}_{int(time.time())}"
            session = GameSession(
                id=session_id,
                user_address=user_address,
                game_type=game_type,
                start_time=time.time()
            )
            
            self.active_sessions[session_id] = session
            
            # Initialize user stats if not exists
            if user_address not in self.user_stats:
                self.user_stats[user_address] = {
                    "total_score": 0,
                    "games_played": 0,
                    "achievements": [],
                    "total_rewards": Decimal('0'),
                    "last_game": time.time()
                }
            
            logger.info(f"Started {game_type.value} game for user {user_address}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start game: {e}")
            return ""
    
    def _get_active_session(self, user_address: str, game_type: GameType) -> Optional[GameSession]:
        """Get user's active session for a specific game type"""
        for session in self.active_sessions.values():
            if (session.user_address == user_address and 
                session.game_type == game_type and 
                not session.completed):
                return session
        return None
    
    async def play_liquidity_challenge(self, session_id: str, actions: List[Dict]) -> Dict[str, Any]:
        """Play the liquidity challenge game"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.completed:
                raise ValueError("Invalid or completed session")
            
            score = 0
            rewards = Decimal('0')
            achievements = []
            
            # Simulate liquidity challenge gameplay
            for action in actions:
                if action.get('type') == 'stake':
                    # Stake action
                    amount = Decimal(str(action.get('amount', 0)))
                    pool_id = action.get('pool_id')
                    
                    # Calculate score based on stake amount and pool selection
                    pool_info = await self.yield_farming.get_pool_info(pool_id)
                    if pool_info:
                        apy = float(pool_info['apy'])
                        risk_level = pool_info['risk_level']
                        
                        # Score based on APY and risk management
                        action_score = int(amount * apy * 100)
                        if risk_level <= 5:  # Low risk bonus
                            action_score += 50
                        
                        score += action_score
                        rewards += amount * Decimal(str(apy)) * Decimal('0.1')  # 10% of APY as reward
                
                elif action.get('type') == 'rebalance':
                    # Rebalancing action
                    score += 25
                    rewards += Decimal('0.01')
                
                elif action.get('type') == 'withdraw':
                    # Withdrawal action
                    score += 10
            
            # Update session
            session.score += score
            session.rewards_earned += rewards
            session.level = min(10, session.score // 1000 + 1)
            
            # Check for achievements
            new_achievements = await self._check_achievements(session.user_address, session)
            achievements.extend(new_achievements)
            
            # Update user stats
            if session.user_address in self.user_stats:
                self.user_stats[session.user_address]['total_score'] += score
                self.user_stats[session.user_address]['total_rewards'] += rewards
            
            return {
                "score": score,
                "total_score": session.score,
                "level": session.level,
                "rewards": str(rewards),
                "achievements": achievements,
                "game_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Liquidity challenge failed: {e}")
            return {"error": str(e)}
    
    async def play_flash_loan_master(self, session_id: str, loan_data: Dict) -> Dict[str, Any]:
        """Play the flash loan master game"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.completed:
                raise ValueError("Invalid or completed session")
            
            # Simulate flash loan execution
            borrowed_amount = Decimal(str(loan_data.get('borrowed_amount', 0)))
            arbitrage_trades = loan_data.get('arbitrage_trades', [])
            
            # Calculate score based on loan complexity and profit
            base_score = int(borrowed_amount * 10)
            trade_score = len(arbitrage_trades) * 50
            
            # Simulate profit calculation
            total_profit = Decimal('0')
            for trade in arbitrage_trades:
                profit = Decimal(str(trade.get('profit', 0)))
                total_profit += profit
            
            profit_score = int(total_profit * 1000)
            total_score = base_score + trade_score + profit_score
            
            # Calculate rewards (1% of profit)
            rewards = total_profit * Decimal('0.01')
            
            # Update session
            session.score += total_score
            session.rewards_earned += rewards
            
            # Check for achievements
            achievements = await self._check_achievements(session.user_address, session)
            
            return {
                "score": total_score,
                "total_score": session.score,
                "profit": str(total_profit),
                "rewards": str(rewards),
                "achievements": achievements,
                "game_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Flash loan master failed: {e}")
            return {"error": str(e)}
    
    async def play_yield_optimizer(self, session_id: str, optimization_data: Dict) -> Dict[str, Any]:
        """Play the yield optimizer game"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or session.completed:
                raise ValueError("Invalid or completed session")
            
            # Simulate yield optimization
            pools_optimized = len(optimization_data.get('pools', []))
            total_allocation = Decimal(str(optimization_data.get('total_allocation', 0)))
            
            # Calculate score based on optimization effectiveness
            optimization_score = pools_optimized * 100
            
            # Bonus for large allocations
            allocation_bonus = min(500, int(total_allocation / 1000) * 50)
            
            total_score = optimization_score + allocation_bonus
            
            # Calculate rewards based on optimization
            rewards = total_allocation * Decimal('0.001')  # 0.1% reward
            
            # Update session
            session.score += total_score
            session.rewards_earned += rewards
            
            return {
                "score": total_score,
                "total_score": session.score,
                "pools_optimized": pools_optimized,
                "rewards": str(rewards),
                "game_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Yield optimizer failed: {e}")
            return {"error": str(e)}
    
    async def complete_game(self, session_id: str) -> Dict[str, Any]:
        """Complete a game session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError("Session not found")
            
            # Mark session as completed
            session.completed = True
            session.end_time = time.time()
            
            # Calculate final rewards and bonuses
            time_bonus = self._calculate_time_bonus(session)
            level_bonus = session.level * 10
            
            final_rewards = session.rewards_earned + Decimal(str(time_bonus + level_bonus))
            
            # Update user stats
            if session.user_address in self.user_stats:
                self.user_stats[session.user_address]['games_played'] += 1
                self.user_stats[session.user_address]['total_rewards'] += final_rewards
                self.user_stats[session.user_address]['last_game'] = time.time()
            
            # Update leaderboard
            await self._update_leaderboard(session.user_address)
            
            # Check for level-up achievements
            level_achievements = await self._check_level_achievements(session)
            
            return {
                "final_score": session.score,
                "level": session.level,
                "final_rewards": str(final_rewards),
                "time_bonus": time_bonus,
                "level_bonus": level_bonus,
                "achievements": level_achievements,
                "game_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Game completion failed: {e}")
            return {"error": str(e)}
    
    def _calculate_time_bonus(self, session: GameSession) -> int:
        """Calculate time-based bonus"""
        if not session.end_time:
            return 0
        
        duration = session.end_time - session.start_time
        # Bonus for completing games quickly (under 5 minutes)
        if duration < 300:  # 5 minutes
            return 100
        elif duration < 600:  # 10 minutes
            return 50
        else:
            return 25
    
    async def _check_achievements(self, user_address: str, session: GameSession) -> List[str]:
        """Check for new achievements"""
        new_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id in session.achievements:
                continue
            
            # Check if user meets achievement requirements
            if await self._meets_achievement_requirements(user_address, achievement):
                session.achievements.append(achievement_id)
                new_achievements.append(achievement_id)
                
                # Add achievement points to score
                session.score += achievement.points
                
                logger.info(f"User {user_address} earned achievement: {achievement.name}")
        
        return new_achievements
    
    async def _meets_achievement_requirements(self, user_address: str, achievement: Achievement) -> bool:
        """Check if user meets achievement requirements"""
        try:
            requirements = achievement.requirements
            
            if achievement.id == "first_stake":
                # Check if user has made their first stake
                positions = await self.yield_farming.get_user_positions(user_address)
                return len(positions) > 0
            
            elif achievement.id == "liquidity_provider":
                # Check if user has provided liquidity to 5 pools
                positions = await self.yield_farming.get_user_positions(user_address)
                unique_pools = set(pos['pool_id'] for pos in positions)
                return len(unique_pools) >= 5
            
            elif achievement.id == "flash_loan_expert":
                # Check flash loan count (this would need to be tracked)
                return True  # Placeholder
            
            elif achievement.id == "risk_master":
                # Check risk score (this would need to be tracked)
                return True  # Placeholder
            
            elif achievement.id == "arbitrage_king":
                # Check arbitrage opportunities (this would need to be tracked)
                return True  # Placeholder
            
            return False
            
        except Exception as e:
            logger.error(f"Achievement requirement check failed: {e}")
            return False
    
    async def _check_level_achievements(self, session: GameSession) -> List[str]:
        """Check for level-based achievements"""
        level_achievements = []
        
        if session.level >= 5 and "level_5" not in session.achievements:
            level_achievements.append("level_5")
            session.achievements.append("level_5")
        
        if session.level >= 10 and "level_10" not in session.achievements:
            level_achievements.append("level_10")
            session.achievements.append("level_10")
        
        return level_achievements
    
    async def _update_leaderboard(self, user_address: str):
        """Update leaderboard with user's performance"""
        try:
            user_stats = self.user_stats.get(user_address, {})
            
            # Find existing entry or create new one
            existing_entry = None
            for entry in self.leaderboard:
                if entry.user_address == user_address:
                    existing_entry = entry
                    break
            
            if existing_entry:
                # Update existing entry
                existing_entry.total_score = user_stats.get('total_score', 0)
                existing_entry.games_played = user_stats.get('games_played', 0)
                existing_entry.achievements_count = len(user_stats.get('achievements', []))
                existing_entry.total_rewards = user_stats.get('total_rewards', Decimal('0'))
                existing_entry.last_updated = time.time()
            else:
                # Create new entry
                new_entry = LeaderboardEntry(
                    user_address=user_address,
                    username=f"User_{user_address[:8]}",
                    total_score=user_stats.get('total_score', 0),
                    games_played=user_stats.get('games_played', 0),
                    achievements_count=len(user_stats.get('achievements', [])),
                    total_rewards=user_stats.get('total_rewards', Decimal('0'))
                )
                self.leaderboard.append(new_entry)
            
            # Sort leaderboard by total score
            self.leaderboard.sort(key=lambda x: x.total_score, reverse=True)
            
            # Update ranks
            for i, entry in enumerate(self.leaderboard):
                entry.rank = i + 1
            
        except Exception as e:
            logger.error(f"Leaderboard update failed: {e}")
    
    async def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get leaderboard entries"""
        try:
            return [
                {
                    "rank": entry.rank,
                    "username": entry.username,
                    "total_score": entry.total_score,
                    "games_played": entry.games_played,
                    "achievements_count": entry.achievements_count,
                    "total_rewards": str(entry.total_rewards),
                    "last_updated": entry.last_updated
                }
                for entry in self.leaderboard[:limit]
            ]
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return []
    
    async def get_user_stats(self, user_address: str) -> Dict[str, Any]:
        """Get user's game statistics"""
        try:
            user_stats = self.user_stats.get(user_address, {})
            
            # Get active sessions
            active_sessions = [
                {
                    "id": session.id,
                    "game_type": session.game_type.value,
                    "score": session.score,
                    "level": session.level,
                    "start_time": session.start_time
                }
                for session in self.active_sessions.values()
                if session.user_address == user_address and not session.completed
            ]
            
            # Get achievements
            achievements = []
            for achievement_id in user_stats.get('achievements', []):
                if achievement_id in self.achievements:
                    achievement = self.achievements[achievement_id]
                    achievements.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon,
                        "points": achievement.points,
                        "rarity": achievement.rarity
                    })
            
            return {
                "total_score": user_stats.get('total_score', 0),
                "games_played": user_stats.get('games_played', 0),
                "achievements": achievements,
                "total_rewards": str(user_stats.get('total_rewards', Decimal('0'))),
                "active_sessions": active_sessions,
                "last_game": user_stats.get('last_game', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}
    
    async def get_available_games(self) -> List[Dict]:
        """Get list of available games"""
        return [
            {
                "type": GameType.LIQUIDITY_CHALLENGE.value,
                "name": "Liquidity Challenge",
                "description": "Optimize your liquidity provision across multiple pools",
                "difficulty": "Easy",
                "estimated_duration": "5-10 minutes",
                "max_score": 10000
            },
            {
                "type": GameType.FLASH_LOAN_MASTER.value,
                "name": "Flash Loan Master",
                "description": "Master the art of flash loan arbitrage",
                "difficulty": "Hard",
                "estimated_duration": "10-15 minutes",
                "max_score": 25000
            },
            {
                "type": GameType.YIELD_OPTIMIZER.value,
                "name": "Yield Optimizer",
                "description": "Optimize your yield farming strategy for maximum returns",
                "difficulty": "Medium",
                "estimated_duration": "8-12 minutes",
                "max_score": 15000
            }
        ]
