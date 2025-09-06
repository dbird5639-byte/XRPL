"""
Achievement System for XRP Health Score Platform
==============================================

This module implements a comprehensive achievement system that rewards users
for various activities and milestones, encouraging continued engagement and
positive behavior.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import json

from ..core.data_models import ActivityType, CoinTier, UserProfile, ActivityRecord


class AchievementCategory(Enum):
    """Categories of achievements"""
    FINANCIAL = "financial"
    BLOCKCHAIN = "blockchain"
    COMMUNITY = "community"
    SOCIAL = "social"
    PERSONAL = "personal"
    SPECIAL = "special"


class AchievementRarity(Enum):
    """Rarity levels for achievements"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """Individual achievement definition"""
    achievement_id: str
    title: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    
    # Requirements
    required_activities: List[ActivityType]
    required_count: int
    required_value: float
    required_conditions: Dict[str, Any]  # Additional conditions
    
    # Rewards
    points_reward: float
    coin_reward: Dict[CoinTier, int]
    badge_icon: str
    badge_color: str
    
    # Metadata
    created_at: datetime
    is_active: bool = True
    is_hidden: bool = False  # Hidden until unlocked
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'achievement_id': self.achievement_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'rarity': self.rarity.value,
            'required_activities': [activity.value for activity in self.required_activities],
            'required_count': self.required_count,
            'required_value': self.required_value,
            'required_conditions': self.required_conditions,
            'points_reward': self.points_reward,
            'coin_reward': {tier.value: amount for tier, amount in self.coin_reward.items()},
            'badge_icon': self.badge_icon,
            'badge_color': self.badge_color,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'is_hidden': self.is_hidden
        }


@dataclass
class UserAchievement:
    """User's achievement progress and status"""
    user_id: str
    achievement_id: str
    progress: float  # 0.0 to 1.0
    unlocked: bool
    unlocked_at: Optional[datetime]
    progress_data: Dict[str, Any]  # Additional progress tracking
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'progress': self.progress,
            'unlocked': self.unlocked,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress_data': self.progress_data
        }


class AchievementSystem:
    """
    Comprehensive achievement system that tracks user progress and unlocks rewards
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.user_achievements: Dict[str, Dict[str, UserAchievement]] = {}  # user_id -> achievement_id -> UserAchievement
        self._initialize_default_achievements()
    
    def _initialize_default_achievements(self):
        """Initialize default achievement set"""
        
        # Financial Achievements
        self._add_achievement(Achievement(
            achievement_id="first_xrp_transaction",
            title="First Steps",
            description="Complete your first XRP transaction",
            category=AchievementCategory.FINANCIAL,
            rarity=AchievementRarity.COMMON,
            required_activities=[ActivityType.XRP_TRANSACTION],
            required_count=1,
            required_value=0,
            required_conditions={},
            points_reward=10,
            coin_reward={CoinTier.COPPER: 100},
            badge_icon="🚀",
            badge_color="#4CAF50",
            created_at=datetime.now()
        ))
        
        self._add_achievement(Achievement(
            achievement_id="xrp_whale",
            title="XRP Whale",
            description="Complete 100 XRP transactions",
            category=AchievementCategory.FINANCIAL,
            rarity=AchievementRarity.RARE,
            required_activities=[ActivityType.XRP_TRANSACTION],
            required_count=100,
            required_value=0,
            required_conditions={},
            points_reward=100,
            coin_reward={CoinTier.COPPER: 1000, CoinTier.SILVER: 10},
            badge_icon="🐋",
            badge_color="#2196F3",
            created_at=datetime.now()
        ))
        
        self._add_achievement(Achievement(
            achievement_id="staking_master",
            title="Staking Master",
            description="Stake 10,000 XRP for 1 year",
            category=AchievementCategory.FINANCIAL,
            rarity=AchievementRarity.EPIC,
            required_activities=[ActivityType.STAKING],
            required_count=1,
            required_value=10000,
            required_conditions={"duration_days": 365},
            points_reward=500,
            coin_reward={CoinTier.COPPER: 5000, CoinTier.SILVER: 50, CoinTier.GOLD: 1},
            badge_icon="🏆",
            badge_color="#FFD700",
            created_at=datetime.now()
        ))
        
        # Blockchain Achievements
        self._add_achievement(Achievement(
            achievement_id="defi_explorer",
            title="DeFi Explorer",
            description="Use 5 different DeFi protocols",
            category=AchievementCategory.BLOCKCHAIN,
            rarity=AchievementRarity.UNCOMMON,
            required_activities=[ActivityType.DEFI_PARTICIPATION],
            required_count=5,
            required_value=0,
            required_conditions={"unique_protocols": 5},
            points_reward=75,
            coin_reward={CoinTier.COPPER: 750, CoinTier.SILVER: 7},
            badge_icon="🔮",
            badge_color="#9C27B0",
            created_at=datetime.now()
        ))
        
        self._add_achievement(Achievement(
            achievement_id="mining_enthusiast",
            title="Mining Enthusiast",
            description="Mine 1000 tokens",
            category=AchievementCategory.BLOCKCHAIN,
            rarity=AchievementRarity.RARE,
            required_activities=[ActivityType.MINING],
            required_count=1,
            required_value=1000,
            required_conditions={},
            points_reward=150,
            coin_reward={CoinTier.COPPER: 1500, CoinTier.SILVER: 15},
            badge_icon="⛏️",
            badge_color="#FF9800",
            created_at=datetime.now()
        ))
        
        # Community Achievements
        self._add_achievement(Achievement(
            achievement_id="community_hero",
            title="Community Hero",
            description="Complete 50 hours of community service",
            category=AchievementCategory.COMMUNITY,
            rarity=AchievementRarity.EPIC,
            required_activities=[ActivityType.COMMUNITY_SERVICE],
            required_count=1,
            required_value=50,
            required_conditions={"total_hours": 50},
            points_reward=300,
            coin_reward={CoinTier.COPPER: 3000, CoinTier.SILVER: 30, CoinTier.GOLD: 1},
            badge_icon="🦸",
            badge_color="#E91E63",
            created_at=datetime.now()
        ))
        
        self._add_achievement(Achievement(
            achievement_id="mentor_legend",
            title="Mentor Legend",
            description="Mentor 10 different people",
            category=AchievementCategory.COMMUNITY,
            rarity=AchievementRarity.LEGENDARY,
            required_activities=[ActivityType.MENTORSHIP],
            required_count=10,
            required_value=0,
            required_conditions={"unique_mentees": 10},
            points_reward=1000,
            coin_reward={CoinTier.COPPER: 10000, CoinTier.SILVER: 100, CoinTier.GOLD: 5, CoinTier.PLATINUM: 1},
            badge_icon="👑",
            badge_color="#FFD700",
            created_at=datetime.now()
        ))
        
        # Social Achievements
        self._add_achievement(Achievement(
            achievement_id="nft_creator",
            title="NFT Creator",
            description="Create 10 unique NFTs",
            category=AchievementCategory.SOCIAL,
            rarity=AchievementRarity.UNCOMMON,
            required_activities=[ActivityType.NFT_CREATION],
            required_count=10,
            required_value=0,
            required_conditions={},
            points_reward=100,
            coin_reward={CoinTier.COPPER: 1000, CoinTier.SILVER: 10},
            badge_icon="🎨",
            badge_color="#00BCD4",
            created_at=datetime.now()
        ))
        
        # Personal Development Achievements
        self._add_achievement(Achievement(
            achievement_id="lifelong_learner",
            title="Lifelong Learner",
            description="Complete 20 educational activities",
            category=AchievementCategory.PERSONAL,
            rarity=AchievementRarity.RARE,
            required_activities=[ActivityType.EDUCATION, ActivityType.SKILL_DEVELOPMENT],
            required_count=20,
            required_value=0,
            required_conditions={},
            points_reward=200,
            coin_reward={CoinTier.COPPER: 2000, CoinTier.SILVER: 20},
            badge_icon="📚",
            badge_color="#795548",
            created_at=datetime.now()
        ))
        
        # Special Achievements
        self._add_achievement(Achievement(
            achievement_id="early_adopter",
            title="Early Adopter",
            description="Join the platform in the first 1000 users",
            category=AchievementCategory.SPECIAL,
            rarity=AchievementRarity.LEGENDARY,
            required_activities=[],
            required_count=0,
            required_value=0,
            required_conditions={"user_rank": 1000},
            points_reward=500,
            coin_reward={CoinTier.COPPER: 5000, CoinTier.SILVER: 50, CoinTier.GOLD: 2},
            badge_icon="⭐",
            badge_color="#FFD700",
            created_at=datetime.now(),
            is_hidden=True
        ))
    
    def _add_achievement(self, achievement: Achievement):
        """Add an achievement to the system"""
        self.achievements[achievement.achievement_id] = achievement
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID"""
        return self.achievements.get(achievement_id)
    
    def get_all_achievements(self, category: Optional[AchievementCategory] = None) -> List[Achievement]:
        """Get all achievements, optionally filtered by category"""
        achievements = list(self.achievements.values())
        
        if category:
            achievements = [a for a in achievements if a.category == category]
        
        return achievements
    
    def get_user_achievements(self, user_id: str) -> Dict[str, UserAchievement]:
        """Get all achievements for a user"""
        return self.user_achievements.get(user_id, {})
    
    def get_user_achievement(self, user_id: str, achievement_id: str) -> Optional[UserAchievement]:
        """Get a specific user achievement"""
        user_achievements = self.get_user_achievements(user_id)
        return user_achievements.get(achievement_id)
    
    def update_achievement_progress(self, user_id: str, activity: ActivityRecord) -> List[Achievement]:
        """Update achievement progress based on a new activity"""
        unlocked_achievements = []
        
        # Initialize user achievements if needed
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = {}
        
        # Check all achievements for progress updates
        for achievement in self.achievements.values():
            if not achievement.is_active:
                continue
            
            # Skip if already unlocked
            user_achievement = self.get_user_achievement(user_id, achievement.achievement_id)
            if user_achievement and user_achievement.unlocked:
                continue
            
            # Check if this activity contributes to the achievement
            if activity.activity_type in achievement.required_activities:
                # Update or create user achievement
                if not user_achievement:
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.achievement_id,
                        progress=0.0,
                        unlocked=False,
                        unlocked_at=None,
                        progress_data={}
                    )
                
                # Update progress
                new_progress = self._calculate_achievement_progress(
                    user_id, achievement, activity
                )
                
                if new_progress >= 1.0 and not user_achievement.unlocked:
                    # Achievement unlocked!
                    user_achievement.unlocked = True
                    user_achievement.unlocked_at = datetime.now()
                    user_achievement.progress = 1.0
                    unlocked_achievements.append(achievement)
                else:
                    user_achievement.progress = new_progress
                
                # Update progress data
                user_achievement.progress_data = self._get_progress_data(
                    user_id, achievement, activity
                )
                
                self.user_achievements[user_id][achievement.achievement_id] = user_achievement
        
        return unlocked_achievements
    
    def _calculate_achievement_progress(self, user_id: str, achievement: Achievement, 
                                      activity: ActivityRecord) -> float:
        """Calculate progress toward an achievement"""
        # Get user's activity history
        user_activities = self._get_user_activities(user_id)
        
        # Filter activities that match the achievement requirements
        matching_activities = [
            a for a in user_activities
            if a.activity_type in achievement.required_activities
        ]
        
        # Check count requirement
        count_progress = min(1.0, len(matching_activities) / achievement.required_count)
        
        # Check value requirement
        total_value = sum(a.value for a in matching_activities)
        value_progress = min(1.0, total_value / achievement.required_value) if achievement.required_value > 0 else 1.0
        
        # Check additional conditions
        conditions_progress = self._check_achievement_conditions(
            achievement, matching_activities, activity
        )
        
        # Overall progress is the minimum of all requirements
        return min(count_progress, value_progress, conditions_progress)
    
    def _check_achievement_conditions(self, achievement: Achievement, 
                                    matching_activities: List[ActivityRecord],
                                    new_activity: ActivityRecord) -> float:
        """Check additional achievement conditions"""
        conditions = achievement.required_conditions
        
        if not conditions:
            return 1.0
        
        # Check duration conditions
        if "duration_days" in conditions:
            required_duration = conditions["duration_days"]
            if new_activity.metadata.get("duration_days", 0) < required_duration:
                return 0.0
        
        # Check unique protocols condition
        if "unique_protocols" in conditions:
            required_unique = conditions["unique_protocols"]
            unique_protocols = set(
                a.metadata.get("protocol", "") for a in matching_activities
                if a.metadata.get("protocol")
            )
            if len(unique_protocols) < required_unique:
                return len(unique_protocols) / required_unique
        
        # Check unique mentees condition
        if "unique_mentees" in conditions:
            required_unique = conditions["unique_mentees"]
            unique_mentees = set(
                a.metadata.get("mentee_id", "") for a in matching_activities
                if a.metadata.get("mentee_id")
            )
            if len(unique_mentees) < required_unique:
                return len(unique_mentees) / required_unique
        
        # Check total hours condition
        if "total_hours" in conditions:
            required_hours = conditions["total_hours"]
            total_hours = sum(
                a.metadata.get("hours", 0) for a in matching_activities
            )
            if total_hours < required_hours:
                return total_hours / required_hours
        
        return 1.0
    
    def _get_progress_data(self, user_id: str, achievement: Achievement, 
                          activity: ActivityRecord) -> Dict[str, Any]:
        """Get detailed progress data for an achievement"""
        user_activities = self._get_user_activities(user_id)
        matching_activities = [
            a for a in user_activities
            if a.activity_type in achievement.required_activities
        ]
        
        return {
            "total_activities": len(matching_activities),
            "required_activities": achievement.required_count,
            "total_value": sum(a.value for a in matching_activities),
            "required_value": achievement.required_value,
            "last_activity": activity.timestamp.isoformat(),
            "unique_protocols": len(set(
                a.metadata.get("protocol", "") for a in matching_activities
                if a.metadata.get("protocol")
            )),
            "total_hours": sum(
                a.metadata.get("hours", 0) for a in matching_activities
            )
        }
    
    def _get_user_activities(self, user_id: str) -> List[ActivityRecord]:
        """Get user activities (this would typically query a database)"""
        # In a real implementation, this would query the database
        # For now, return empty list - this should be injected or passed in
        return []
    
    def get_achievement_stats(self, user_id: str) -> Dict[str, Any]:
        """Get achievement statistics for a user"""
        user_achievements = self.get_user_achievements(user_id)
        
        total_achievements = len(self.achievements)
        unlocked_achievements = len([ua for ua in user_achievements.values() if ua.unlocked])
        in_progress_achievements = len([ua for ua in user_achievements.values() if not ua.unlocked and ua.progress > 0])
        
        # Count by category
        category_counts = {}
        for achievement in self.achievements.values():
            category = achievement.category.value
            if category not in category_counts:
                category_counts[category] = {"total": 0, "unlocked": 0}
            category_counts[category]["total"] += 1
            
            user_achievement = user_achievements.get(achievement.achievement_id)
            if user_achievement and user_achievement.unlocked:
                category_counts[category]["unlocked"] += 1
        
        # Count by rarity
        rarity_counts = {}
        for achievement in self.achievements.values():
            rarity = achievement.rarity.value
            if rarity not in rarity_counts:
                rarity_counts[rarity] = {"total": 0, "unlocked": 0}
            rarity_counts[rarity]["total"] += 1
            
            user_achievement = user_achievements.get(achievement.achievement_id)
            if user_achievement and user_achievement.unlocked:
                rarity_counts[rarity]["unlocked"] += 1
        
        return {
            "total_achievements": total_achievements,
            "unlocked_achievements": unlocked_achievements,
            "in_progress_achievements": in_progress_achievements,
            "completion_percentage": (unlocked_achievements / total_achievements * 100) if total_achievements > 0 else 0,
            "category_breakdown": category_counts,
            "rarity_breakdown": rarity_counts
        }
    
    def get_recommended_achievements(self, user_id: str, limit: int = 5) -> List[Achievement]:
        """Get recommended achievements for a user based on their activity"""
        user_achievements = self.get_user_achievements(user_id)
        user_activities = self._get_user_activities(user_id)
        
        # Find achievements that are close to being unlocked
        close_achievements = []
        
        for achievement in self.achievements.values():
            if not achievement.is_active:
                continue
            
            user_achievement = user_achievements.get(achievement.achievement_id)
            if user_achievement and user_achievement.unlocked:
                continue
            
            # Calculate current progress
            progress = self._calculate_achievement_progress(
                user_id, achievement, user_activities[-1] if user_activities else None
            )
            
            if 0.5 <= progress < 1.0:  # 50% to 99% complete
                close_achievements.append((achievement, progress))
        
        # Sort by progress (descending) and return top recommendations
        close_achievements.sort(key=lambda x: x[1], reverse=True)
        return [achievement for achievement, _ in close_achievements[:limit]]
    
    def create_custom_achievement(self, achievement: Achievement) -> bool:
        """Create a custom achievement (admin function)"""
        try:
            self._add_achievement(achievement)
            return True
        except Exception as e:
            print(f"Error creating custom achievement: {e}")
            return False
