"""
Citizen Coin System for XRP Health Score Platform
===============================================

This module implements the Citizen Coin tokenization system with a tiered structure
similar to satoshis to Bitcoin, providing multiple levels of rewards and recognition.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import json

from .data_models import CoinTier, ActivityType, ActivityRecord, UserProfile


@dataclass
class CoinConversion:
    """Conversion rates between coin tiers"""
    from_tier: CoinTier
    to_tier: CoinTier
    conversion_rate: int  # How many from_tier coins = 1 to_tier coin
    
    def convert(self, amount: int) -> int:
        """Convert amount from from_tier to to_tier"""
        return amount // self.conversion_rate
    
    def reverse_convert(self, amount: int) -> int:
        """Convert amount from to_tier to from_tier"""
        return amount * self.conversion_rate


class CitizenCoinSystem:
    """
    Citizen Coin System with tiered structure:
    - Copper: Base unit (1:1 ratio)
    - Silver: 100 copper = 1 silver
    - Gold: 100 silver = 1 gold (10,000 copper)
    - Platinum: 100 gold = 1 platinum (1,000,000 copper)
    - Diamond: 100 platinum = 1 diamond (100,000,000 copper)
    """
    
    # Conversion rates between tiers
    CONVERSION_RATES = {
        (CoinTier.COPPER, CoinTier.SILVER): 100,
        (CoinTier.SILVER, CoinTier.GOLD): 100,
        (CoinTier.GOLD, CoinTier.PLATINUM): 100,
        (CoinTier.PLATINUM, CoinTier.DIAMOND): 100,
    }
    
    # Base rewards for different activity types
    BASE_REWARDS = {
        ActivityType.XRP_TRANSACTION: {CoinTier.COPPER: 1},
        ActivityType.STAKING: {CoinTier.COPPER: 5, CoinTier.SILVER: 0.01},
        ActivityType.FARMING: {CoinTier.COPPER: 3, CoinTier.SILVER: 0.005},
        ActivityType.MINING: {CoinTier.COPPER: 2, CoinTier.SILVER: 0.002},
        ActivityType.DEFI_PARTICIPATION: {CoinTier.COPPER: 4, CoinTier.SILVER: 0.008},
        ActivityType.COMMUNITY_SERVICE: {CoinTier.COPPER: 10, CoinTier.SILVER: 0.02},
        ActivityType.MENTORSHIP: {CoinTier.COPPER: 15, CoinTier.SILVER: 0.03},
        ActivityType.KNOWLEDGE_SHARING: {CoinTier.COPPER: 8, CoinTier.SILVER: 0.015},
        ActivityType.EVENT_PARTICIPATION: {CoinTier.COPPER: 5, CoinTier.SILVER: 0.01},
        ActivityType.AIRDROP_PARTICIPATION: {CoinTier.COPPER: 3, CoinTier.SILVER: 0.005},
        ActivityType.NFT_CREATION: {CoinTier.COPPER: 20, CoinTier.SILVER: 0.05},
        ActivityType.NFT_TRADING: {CoinTier.COPPER: 5, CoinTier.SILVER: 0.01},
        ActivityType.GOVERNANCE_VOTING: {CoinTier.COPPER: 12, CoinTier.SILVER: 0.025},
        ActivityType.FITNESS_ACTIVITY: {CoinTier.COPPER: 6, CoinTier.SILVER: 0.012},
        ActivityType.MENTAL_HEALTH: {CoinTier.COPPER: 8, CoinTier.SILVER: 0.015},
        ActivityType.EDUCATION: {CoinTier.COPPER: 10, CoinTier.SILVER: 0.02},
        ActivityType.SKILL_DEVELOPMENT: {CoinTier.COPPER: 7, CoinTier.SILVER: 0.014},
    }
    
    def __init__(self):
        self.conversion_rates = self._build_conversion_rates()
    
    def _build_conversion_rates(self) -> Dict[Tuple[CoinTier, CoinTier], int]:
        """Build conversion rates between all coin tiers"""
        rates = {}
        
        # Direct conversions
        for (from_tier, to_tier), rate in self.CONVERSION_RATES.items():
            rates[(from_tier, to_tier)] = rate
            rates[(to_tier, from_tier)] = 1 / rate
        
        # Indirect conversions (e.g., copper to gold)
        tiers = list(CoinTier)
        for i, from_tier in enumerate(tiers):
            for j, to_tier in enumerate(tiers):
                if i != j and (from_tier, to_tier) not in rates:
                    # Calculate indirect conversion rate
                    rate = self._calculate_indirect_rate(from_tier, to_tier)
                    if rate is not None:
                        rates[(from_tier, to_tier)] = rate
        
        return rates
    
    def _calculate_indirect_rate(self, from_tier: CoinTier, to_tier: CoinTier) -> Optional[int]:
        """Calculate indirect conversion rate between tiers"""
        tiers = list(CoinTier)
        from_index = tiers.index(from_tier)
        to_index = tiers.index(to_tier)
        
        if from_index == to_index:
            return 1
        
        # Calculate rate by going through intermediate tiers
        rate = 1
        if from_index < to_index:
            # Going up in tiers (e.g., copper to gold)
            for i in range(from_index, to_index):
                direct_rate = self.CONVERSION_RATES.get((tiers[i], tiers[i + 1]))
                if direct_rate is None:
                    return None
                rate *= direct_rate
        else:
            # Going down in tiers (e.g., gold to copper)
            for i in range(from_index, to_index, -1):
                direct_rate = self.CONVERSION_RATES.get((tiers[i], tiers[i - 1]))
                if direct_rate is None:
                    return None
                rate *= direct_rate
        
        return int(rate) if rate >= 1 else 1 / rate
    
    def calculate_activity_rewards(self, activity: ActivityRecord) -> Dict[CoinTier, int]:
        """Calculate coin rewards for a specific activity"""
        base_rewards = self.BASE_REWARDS.get(activity.activity_type, {})
        rewards = {}
        
        # Apply base rewards
        for tier, base_amount in base_rewards.items():
            if tier == CoinTier.COPPER:
                rewards[tier] = int(base_amount)
            else:
                # Convert fractional amounts to copper
                copper_amount = int(base_amount * self.conversion_rates.get((tier, CoinTier.COPPER), 1))
                rewards[CoinTier.COPPER] = rewards.get(CoinTier.COPPER, 0) + copper_amount
        
        # Apply multipliers based on activity value and metadata
        multiplier = self._calculate_multiplier(activity)
        for tier in rewards:
            rewards[tier] = int(rewards[tier] * multiplier)
        
        # Apply bonus tiers for high-value activities
        total_copper = rewards.get(CoinTier.COPPER, 0)
        if total_copper >= 1000000:  # 1 million copper = 1 diamond
            diamond_amount = total_copper // 1000000
            rewards[CoinTier.DIAMOND] = diamond_amount
            rewards[CoinTier.COPPER] = total_copper % 1000000
        elif total_copper >= 10000:  # 10,000 copper = 1 gold
            gold_amount = total_copper // 10000
            rewards[CoinTier.GOLD] = gold_amount
            rewards[CoinTier.COPPER] = total_copper % 10000
        elif total_copper >= 100:  # 100 copper = 1 silver
            silver_amount = total_copper // 100
            rewards[CoinTier.SILVER] = silver_amount
            rewards[CoinTier.COPPER] = total_copper % 100
        
        return rewards
    
    def _calculate_multiplier(self, activity: ActivityRecord) -> float:
        """Calculate multiplier for activity rewards based on various factors"""
        multiplier = 1.0
        
        # Value-based multiplier
        if activity.value > 0:
            # Higher value activities get higher multipliers (capped at 5x)
            value_multiplier = min(5.0, 1.0 + math.log10(activity.value + 1) * 0.5)
            multiplier *= value_multiplier
        
        # Verification bonus
        if activity.verified:
            multiplier *= 1.5
        
        # Quality bonus from metadata
        quality_score = activity.metadata.get('quality_score', 5)
        if quality_score > 5:
            multiplier *= (1.0 + (quality_score - 5) * 0.1)
        
        # Community impact bonus
        community_impact = activity.metadata.get('community_impact', 0)
        if community_impact > 0:
            multiplier *= (1.0 + community_impact * 0.2)
        
        # Time-based bonus (recent activities get slight bonus)
        days_old = (datetime.now() - activity.timestamp).days
        if days_old < 7:
            multiplier *= 1.1
        elif days_old < 30:
            multiplier *= 1.05
        
        return multiplier
    
    def convert_coins(self, amount: int, from_tier: CoinTier, to_tier: CoinTier) -> int:
        """Convert coins from one tier to another"""
        if from_tier == to_tier:
            return amount
        
        conversion_rate = self.conversion_rates.get((from_tier, to_tier))
        if conversion_rate is None:
            raise ValueError(f"No conversion rate available from {from_tier} to {to_tier}")
        
        if from_tier.value < to_tier.value:  # Going up in tiers
            return amount // conversion_rate
        else:  # Going down in tiers
            return amount * conversion_rate
    
    def get_total_copper_value(self, coin_holdings: Dict[CoinTier, int]) -> int:
        """Convert all coin holdings to copper equivalent"""
        total_copper = 0
        
        for tier, amount in coin_holdings.items():
            if tier == CoinTier.COPPER:
                total_copper += amount
            else:
                copper_amount = self.convert_coins(amount, tier, CoinTier.COPPER)
                total_copper += copper_amount
        
        return total_copper
    
    def get_coin_breakdown(self, total_copper: int) -> Dict[CoinTier, int]:
        """Break down total copper into optimal coin distribution"""
        breakdown = {tier: 0 for tier in CoinTier}
        
        # Start from highest tier and work down
        tiers = [CoinTier.DIAMOND, CoinTier.PLATINUM, CoinTier.GOLD, CoinTier.SILVER, CoinTier.COPPER]
        
        remaining = total_copper
        for tier in tiers:
            if tier == CoinTier.COPPER:
                breakdown[tier] = remaining
            else:
                conversion_rate = self.conversion_rates.get((CoinTier.COPPER, tier))
                if conversion_rate:
                    breakdown[tier] = remaining // conversion_rate
                    remaining = remaining % conversion_rate
        
        return breakdown
    
    def calculate_compound_rewards(self, user_profile: UserProfile, days: int = 30) -> Dict[CoinTier, int]:
        """Calculate compound rewards based on user's activity history"""
        # Get activities from the last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_activities = [
            activity for activity in user_profile.activities
            if activity.timestamp >= cutoff_date
        ]
        
        total_rewards = {tier: 0 for tier in CoinTier}
        
        for activity in recent_activities:
            activity_rewards = self.calculate_activity_rewards(activity)
            for tier, amount in activity_rewards.items():
                total_rewards[tier] += amount
        
        # Apply compound bonus for consistent activity
        activity_count = len(recent_activities)
        if activity_count >= 20:  # Very active user
            compound_multiplier = 1.2
        elif activity_count >= 10:  # Active user
            compound_multiplier = 1.1
        else:
            compound_multiplier = 1.0
        
        for tier in total_rewards:
            total_rewards[tier] = int(total_rewards[tier] * compound_multiplier)
        
        return total_rewards
    
    def get_user_coin_summary(self, user_profile: UserProfile) -> Dict[str, any]:
        """Get a comprehensive summary of user's coin holdings and activity"""
        total_copper = self.get_total_copper_value(user_profile.citizen_coins)
        breakdown = self.get_coin_breakdown(total_copper)
        
        # Calculate recent earning rate
        recent_rewards = self.calculate_compound_rewards(user_profile, 7)  # Last 7 days
        weekly_earnings = self.get_total_copper_value(recent_rewards)
        
        return {
            'total_copper_value': total_copper,
            'coin_breakdown': {tier.value: amount for tier, amount in breakdown.items()},
            'weekly_earnings': weekly_earnings,
            'daily_average': weekly_earnings / 7,
            'tier_levels': self._calculate_tier_levels(total_copper),
            'next_tier_progress': self._calculate_next_tier_progress(total_copper)
        }
    
    def _calculate_tier_levels(self, total_copper: int) -> Dict[str, int]:
        """Calculate user's level in each coin tier"""
        levels = {}
        
        for tier in CoinTier:
            if tier == CoinTier.COPPER:
                levels[tier.value] = total_copper
            else:
                conversion_rate = self.conversion_rates.get((CoinTier.COPPER, tier))
                if conversion_rate:
                    levels[tier.value] = total_copper // conversion_rate
                else:
                    levels[tier.value] = 0
        
        return levels
    
    def _calculate_next_tier_progress(self, total_copper: int) -> Dict[str, Dict[str, int]]:
        """Calculate progress toward next tier in each category"""
        progress = {}
        
        for tier in [CoinTier.SILVER, CoinTier.GOLD, CoinTier.PLATINUM, CoinTier.DIAMOND]:
            conversion_rate = self.conversion_rates.get((CoinTier.COPPER, tier))
            if conversion_rate:
                current_amount = total_copper % conversion_rate
                needed_amount = conversion_rate - current_amount
                progress[tier.value] = {
                    'current': current_amount,
                    'needed': needed_amount,
                    'progress_percentage': (current_amount / conversion_rate) * 100
                }
        
        return progress
    
    def validate_transaction(self, from_user: UserProfile, to_user: UserProfile, 
                           amount: int, from_tier: CoinTier) -> bool:
        """Validate a coin transfer between users"""
        # Check if sender has enough coins
        if from_user.citizen_coins.get(from_tier, 0) < amount:
            return False
        
        # Check if amount is positive
        if amount <= 0:
            return False
        
        # Additional validation rules can be added here
        return True
    
    def execute_transfer(self, from_user: UserProfile, to_user: UserProfile,
                        amount: int, from_tier: CoinTier) -> bool:
        """Execute a coin transfer between users"""
        if not self.validate_transaction(from_user, to_user, amount, from_tier):
            return False
        
        # Deduct from sender
        from_user.citizen_coins[from_tier] -= amount
        
        # Add to receiver
        to_user.citizen_coins[from_tier] = to_user.citizen_coins.get(from_tier, 0) + amount
        
        return True
