"""
Demo Platform for XRP Health Score System
========================================

This script demonstrates the complete XRP Health Score platform with
all features including health scoring, citizen coins, achievements, and more.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import platform components
from ..core.health_scorer import HealthScorer
from ..core.citizen_coin import CitizenCoinSystem, CoinTier
from ..core.data_models import UserProfile, ActivityRecord, ActivityType
from ..blockchain.xrp_integration import XRPLedgerIntegration
from ..gamification.achievement_system import AchievementSystem
from ..api.rest_api import HealthScoreAPI


class XRPHealthScoreDemo:
    """
    Comprehensive demo of the XRP Health Score platform
    """
    
    def __init__(self):
        # Initialize all platform components
        self.health_scorer = HealthScorer()
        self.citizen_coin_system = CitizenCoinSystem()
        self.xrp_integration = XRPLedgerIntegration()
        self.achievement_system = AchievementSystem()
        
        # Demo users
        self.demo_users: List[UserProfile] = []
        self.setup_demo_users()
    
    def setup_demo_users(self):
        """Create demo users with different activity patterns"""
        
        # User 1: Active DeFi user
        user1 = UserProfile(
            user_id="defi_master_001",
            xrp_address="rDefiMaster123456789",
            created_at=datetime.now() - timedelta(days=90),
            last_updated=datetime.now(),
            username="DeFi_Master",
            email="defi@example.com",
            country="USA",
            timezone="America/New_York"
        )
        
        # User 2: Community-focused user
        user2 = UserProfile(
            user_id="community_hero_002",
            xrp_address="rCommunityHero987654321",
            created_at=datetime.now() - timedelta(days=60),
            last_updated=datetime.now(),
            username="Community_Hero",
            email="community@example.com",
            country="Canada",
            timezone="America/Toronto"
        )
        
        # User 3: New user
        user3 = UserProfile(
            user_id="newbie_003",
            xrp_address="rNewbie456789123",
            created_at=datetime.now() - timedelta(days=7),
            last_updated=datetime.now(),
            username="Crypto_Newbie",
            email="newbie@example.com",
            country="UK",
            timezone="Europe/London"
        )
        
        self.demo_users = [user1, user2, user3]
    
    def generate_demo_activities(self, user: UserProfile) -> List[ActivityRecord]:
        """Generate realistic demo activities for a user"""
        activities = []
        base_date = datetime.now() - timedelta(days=30)
        
        if user.user_id == "defi_master_001":
            # DeFi Master activities
            activities.extend([
                ActivityRecord(
                    activity_id=f"xrp_tx_{i}",
                    user_id=user.user_id,
                    activity_type=ActivityType.XRP_TRANSACTION,
                    timestamp=base_date + timedelta(days=i),
                    description=f"XRP Transaction #{i+1}",
                    value=100.0 + i * 10,
                    metadata={"tx_hash": f"mock_tx_{i}", "fee": 0.000012},
                    verified=True,
                    verification_method="xrp_ledger"
                )
                for i in range(25)
            ])
            
            # DeFi activities
            defi_protocols = ["Uniswap", "Compound", "Aave", "Curve", "SushiSwap"]
            for i, protocol in enumerate(defi_protocols):
                activities.append(ActivityRecord(
                    activity_id=f"defi_{protocol.lower()}_{i}",
                    user_id=user.user_id,
                    activity_type=ActivityType.DEFI_PARTICIPATION,
                    timestamp=base_date + timedelta(days=i*5),
                    description=f"Used {protocol} protocol",
                    value=1000.0 + i * 200,
                    metadata={"protocol": protocol, "apy": 5.0 + i},
                    verified=True,
                    verification_method="smart_contract"
                ))
            
            # Staking activities
            activities.append(ActivityRecord(
                activity_id="staking_long_term",
                user_id=user.user_id,
                activity_type=ActivityType.STAKING,
                timestamp=base_date,
                description="Long-term XRP staking",
                value=5000.0,
                metadata={"duration_days": 365, "apy": 6.5, "validator": "validator_1"},
                verified=True,
                verification_method="xrp_ledger"
            ))
        
        elif user.user_id == "community_hero_002":
            # Community Hero activities
            activities.extend([
                ActivityRecord(
                    activity_id=f"community_service_{i}",
                    user_id=user.user_id,
                    activity_type=ActivityType.COMMUNITY_SERVICE,
                    timestamp=base_date + timedelta(days=i*2),
                    description=f"Community service activity #{i+1}",
                    value=0,
                    metadata={"hours": 4, "activity_type": "volunteer_work", "community_impact": 8},
                    verified=True,
                    verification_method="community_verification"
                )
                for i in range(15)
            ])
            
            # Mentorship activities
            for i in range(8):
                activities.append(ActivityRecord(
                    activity_id=f"mentorship_{i}",
                    user_id=user.user_id,
                    activity_type=ActivityType.MENTORSHIP,
                    timestamp=base_date + timedelta(days=i*3),
                    description=f"Mentored user #{i+1}",
                    value=0,
                    metadata={"hours": 2, "mentee_id": f"mentee_{i}", "topic": "crypto_basics"},
                    verified=True,
                    verification_method="peer_verification"
                ))
            
            # Knowledge sharing
            for i in range(12):
                activities.append(ActivityRecord(
                    activity_id=f"knowledge_share_{i}",
                    user_id=user.user_id,
                    activity_type=ActivityType.KNOWLEDGE_SHARING,
                    timestamp=base_date + timedelta(days=i*2),
                    description=f"Shared knowledge post #{i+1}",
                    value=0,
                    metadata={"platform": "community_forum", "quality_score": 8, "engagement_score": 150},
                    verified=True,
                    verification_method="community_rating"
                ))
        
        else:  # newbie_003
            # New user activities
            activities.extend([
                ActivityRecord(
                    activity_id=f"first_xrp_{i}",
                    user_id=user.user_id,
                    activity_type=ActivityType.XRP_TRANSACTION,
                    timestamp=base_date + timedelta(days=i*3),
                    description=f"Learning XRP transaction #{i+1}",
                    value=10.0 + i * 5,
                    metadata={"tx_hash": f"newbie_tx_{i}", "learning": True},
                    verified=True,
                    verification_method="xrp_ledger"
                )
                for i in range(5)
            ])
            
            # Education activities
            for i in range(8):
                activities.append(ActivityRecord(
                    activity_id=f"education_{i}",
                    user_id=user.user_id,
                    activity_type=ActivityType.EDUCATION,
                    timestamp=base_date + timedelta(days=i*2),
                    description=f"Completed course #{i+1}",
                    value=0,
                    metadata={"course_name": f"Crypto Course {i+1}", "education_type": "course_completion", "hours": 2},
                    verified=True,
                    verification_method="course_completion"
                ))
        
        return activities
    
    def calculate_citizen_coin_rewards(self, activities: List[ActivityRecord]) -> Dict[CoinTier, int]:
        """Calculate citizen coin rewards for activities"""
        total_rewards = {tier: 0 for tier in CoinTier}
        
        for activity in activities:
            activity_rewards = self.citizen_coin_system.calculate_activity_rewards(activity)
            for tier, amount in activity_rewards.items():
                total_rewards[tier] += amount
        
        return total_rewards
    
    def run_demo(self):
        """Run the complete platform demo"""
        print("🚀 XRP Health Score Platform Demo")
        print("=" * 50)
        
        for user in self.demo_users:
            print(f"\n👤 User: {user.username} ({user.user_id})")
            print("-" * 30)
            
            # Generate activities
            activities = self.generate_demo_activities(user)
            user.activities = activities
            
            # Calculate citizen coin rewards
            coin_rewards = self.calculate_citizen_coin_rewards(activities)
            user.citizen_coins = coin_rewards
            
            # Calculate health score
            health_score = self.health_scorer.calculate_health_score(user)
            
            # Update achievement progress
            for activity in activities:
                unlocked_achievements = self.achievement_system.update_achievement_progress(user.user_id, activity)
                if unlocked_achievements:
                    print(f"  🏆 Unlocked achievements: {[a.title for a in unlocked_achievements]}")
            
            # Display results
            print(f"  📊 Health Score: {health_score.total_score:.1f}/{health_score.max_possible_score:.1f} ({health_score.score_percentage:.1f}%)")
            print(f"  🪙 Citizen Coins: {coin_rewards[CoinTier.COPPER]} Copper, {coin_rewards[CoinTier.SILVER]} Silver, {coin_rewards[CoinTier.GOLD]} Gold")
            print(f"  📈 Activities: {len(activities)} total")
            
            # Category breakdown
            print("  📋 Category Scores:")
            for category, score in health_score.category_scores.items():
                print(f"    • {category.value.replace('_', ' ').title()}: {score:.1f}")
            
            # Recommendations
            if health_score.improvement_areas:
                print("  💡 Improvement Areas:")
                for area in health_score.improvement_areas[:3]:
                    print(f"    • {area}")
            
            if health_score.strength_areas:
                print("  💪 Strengths:")
                for strength in health_score.strength_areas[:3]:
                    print(f"    • {strength}")
        
        # Community comparison
        print(f"\n🌍 Community Comparison")
        print("-" * 30)
        
        if len(self.demo_users) >= 2:
            user1_score = self.health_scorer.calculate_health_score(self.demo_users[0])
            community_scores = [
                self.health_scorer.calculate_health_score(user) 
                for user in self.demo_users[1:]
            ]
            
            comparison = self.health_scorer.compare_with_community(user1_score, community_scores)
            print(f"  {self.demo_users[0].username}:")
            print(f"    • Score: {comparison['user_score']:.1f}")
            print(f"    • Community Average: {comparison['community_average']:.1f}")
            print(f"    • Percentile Rank: {comparison['percentile_rank']:.1f}%")
            print(f"    • Performance Level: {comparison['performance_level']}")
        
        # Global statistics
        print(f"\n📊 Global Platform Statistics")
        print("-" * 30)
        
        total_users = len(self.demo_users)
        total_activities = sum(len(user.activities) for user in self.demo_users)
        total_coins = sum(
            self.citizen_coin_system.get_total_copper_value(user.citizen_coins)
            for user in self.demo_users
        )
        
        print(f"  • Total Users: {total_users}")
        print(f"  • Total Activities: {total_activities}")
        print(f"  • Total Citizen Coins: {total_coins:,} Copper")
        print(f"  • Average Health Score: {sum(self.health_scorer.calculate_health_score(user).total_score for user in self.demo_users) / total_users:.1f}")
        
        # Achievement statistics
        print(f"\n🏆 Achievement Statistics")
        print("-" * 30)
        
        for user in self.demo_users:
            stats = self.achievement_system.get_achievement_stats(user.user_id)
            print(f"  {user.username}:")
            print(f"    • Unlocked: {stats['unlocked_achievements']}/{stats['total_achievements']}")
            print(f"    • Completion: {stats['completion_percentage']:.1f}%")
        
        print(f"\n✨ Demo completed! The XRP Health Score platform is ready to revolutionize social scoring.")
        print("   This system makes traditional credit scores look like caveman technology! 🦕➡️🚀")


def main():
    """Main demo function"""
    demo = XRPHealthScoreDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
