"""
Data Models for XRP Health Score Platform
=========================================

This module defines the core data structures used throughout the platform.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json


class ActivityType(Enum):
    """Types of activities that can contribute to health score"""
    # Financial Activities
    XRP_TRANSACTION = "xrp_transaction"
    STAKING = "staking"
    FARMING = "farming"
    MINING = "mining"
    DEFI_PARTICIPATION = "defi_participation"
    
    # Community Activities
    COMMUNITY_SERVICE = "community_service"
    MENTORSHIP = "mentorship"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    EVENT_PARTICIPATION = "event_participation"
    
    # Social Activities
    AIRDROP_PARTICIPATION = "airdrop_participation"
    NFT_CREATION = "nft_creation"
    NFT_TRADING = "nft_trading"
    GOVERNANCE_VOTING = "governance_voting"
    
    # Health & Wellness
    FITNESS_ACTIVITY = "fitness_activity"
    MENTAL_HEALTH = "mental_health"
    EDUCATION = "education"
    SKILL_DEVELOPMENT = "skill_development"


class CoinTier(Enum):
    """Citizen Coin tiers similar to satoshi system"""
    COPPER = "copper"      # 1:1 ratio (base unit)
    SILVER = "silver"      # 100:1 ratio (100 copper = 1 silver)
    GOLD = "gold"          # 10,000:1 ratio (100 silver = 1 gold)
    PLATINUM = "platinum"  # 1,000,000:1 ratio (100 gold = 1 platinum)
    DIAMOND = "diamond"    # 100,000,000:1 ratio (100 platinum = 1 diamond)


@dataclass
class UserProfile:
    """Comprehensive user profile for health scoring"""
    user_id: str
    xrp_address: str
    created_at: datetime
    last_updated: datetime
    
    # Personal Information
    username: str
    email: str
    country: Optional[str] = None
    timezone: Optional[str] = None
    
    # Health Score Components
    current_health_score: float = 0.0
    max_health_score: float = 1000.0
    
    # Citizen Coin Holdings
    citizen_coins: Dict[CoinTier, int] = field(default_factory=lambda: {
        tier: 0 for tier in CoinTier
    })
    
    # Activity History
    activities: List['ActivityRecord'] = field(default_factory=list)
    
    # Preferences
    privacy_settings: Dict[str, bool] = field(default_factory=dict)
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    
    # Social Connections
    connections: List[str] = field(default_factory=list)
    communities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'xrp_address': self.xrp_address,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'username': self.username,
            'email': self.email,
            'country': self.country,
            'timezone': self.timezone,
            'current_health_score': self.current_health_score,
            'max_health_score': self.max_health_score,
            'citizen_coins': {tier.value: amount for tier, amount in self.citizen_coins.items()},
            'activities': [activity.to_dict() for activity in self.activities],
            'privacy_settings': self.privacy_settings,
            'notification_preferences': self.notification_preferences,
            'connections': self.connections,
            'communities': self.communities
        }


@dataclass
class ActivityRecord:
    """Record of a user activity that contributes to health score"""
    activity_id: str
    user_id: str
    activity_type: ActivityType
    timestamp: datetime
    
    # Activity Details
    description: str
    value: float  # Monetary or quantitative value
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Scoring Impact
    points_earned: float = 0.0
    coins_earned: Dict[CoinTier, int] = field(default_factory=lambda: {
        tier: 0 for tier in CoinTier
    })
    
    # Verification
    verified: bool = False
    verification_method: Optional[str] = None
    verification_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'activity_id': self.activity_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type.value,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'value': self.value,
            'metadata': self.metadata,
            'points_earned': self.points_earned,
            'coins_earned': {tier.value: amount for tier, amount in self.coins_earned.items()},
            'verified': self.verified,
            'verification_method': self.verification_method,
            'verification_timestamp': self.verification_timestamp.isoformat() if self.verification_timestamp else None
        }


@dataclass
class ScoreHistory:
    """Historical record of health score changes"""
    user_id: str
    timestamp: datetime
    previous_score: float
    new_score: float
    score_change: float
    contributing_activities: List[str]  # Activity IDs
    category_breakdown: Dict[str, float]  # Score by category
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'previous_score': self.previous_score,
            'new_score': self.new_score,
            'score_change': self.score_change,
            'contributing_activities': self.contributing_activities,
            'category_breakdown': self.category_breakdown
        }


@dataclass
class CommunityChallenge:
    """Community-wide challenges that users can participate in"""
    challenge_id: str
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    
    # Challenge Requirements
    required_activities: List[ActivityType]
    minimum_participants: int
    target_goal: float
    
    # Rewards
    reward_coins: Dict[CoinTier, int]
    bonus_multiplier: float = 1.0
    
    # Status
    active: bool = True
    participants: List[str] = field(default_factory=list)
    current_progress: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'challenge_id': self.challenge_id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'required_activities': [activity.value for activity in self.required_activities],
            'minimum_participants': self.minimum_participants,
            'target_goal': self.target_goal,
            'reward_coins': {tier.value: amount for tier, amount in self.reward_coins.items()},
            'bonus_multiplier': self.bonus_multiplier,
            'active': self.active,
            'participants': self.participants,
            'current_progress': self.current_progress
        }


@dataclass
class Achievement:
    """Individual achievements that users can earn"""
    achievement_id: str
    title: str
    description: str
    category: str
    
    # Requirements
    required_activities: List[ActivityType]
    required_count: int
    required_value: float
    
    # Rewards
    points_reward: float
    coin_reward: Dict[CoinTier, int]
    
    # Status
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'achievement_id': self.achievement_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'required_activities': [activity.value for activity in self.required_activities],
            'required_count': self.required_count,
            'required_value': self.required_value,
            'points_reward': self.points_reward,
            'coin_reward': {tier.value: amount for tier, amount in self.coin_reward.items()},
            'unlocked': self.unlocked,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None
        }
