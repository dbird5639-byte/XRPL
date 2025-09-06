"""
Scoring Categories for XRP Health Score Platform
===============================================

This module defines the different categories that contribute to a user's health score,
along with their weights and scoring algorithms.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Callable, Any
import math


class ScoringCategory(Enum):
    """Main categories that contribute to health score"""
    
    # Financial Health (40% weight)
    FINANCIAL_STABILITY = "financial_stability"      # 15%
    BLOCKCHAIN_ACTIVITY = "blockchain_activity"     # 15%
    INVESTMENT_BEHAVIOR = "investment_behavior"     # 10%
    
    # Community Engagement (30% weight)
    COMMUNITY_PARTICIPATION = "community_participation"  # 15%
    KNOWLEDGE_SHARING = "knowledge_sharing"             # 10%
    MENTORSHIP = "mentorship"                           # 5%
    
    # Social Responsibility (20% weight)
    ENVIRONMENTAL_IMPACT = "environmental_impact"    # 8%
    SOCIAL_GOOD = "social_good"                      # 7%
    GOVERNANCE_PARTICIPATION = "governance_participation"  # 5%
    
    # Personal Development (10% weight)
    SKILL_DEVELOPMENT = "skill_development"         # 5%
    HEALTH_WELLNESS = "health_wellness"             # 3%
    EDUCATION = "education"                         # 2%


@dataclass
class CategoryWeight:
    """Weight configuration for scoring categories"""
    category: ScoringCategory
    weight: float  # Percentage weight (0.0 to 1.0)
    max_points: float  # Maximum points possible in this category
    decay_factor: float = 0.95  # How quickly points decay over time
    
    def __post_init__(self):
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {self.weight}")
        if self.max_points <= 0:
            raise ValueError(f"Max points must be positive, got {self.max_points}")


class ScoringAlgorithm:
    """Base class for scoring algorithms"""
    
    def __init__(self, category: ScoringCategory, weight: CategoryWeight):
        self.category = category
        self.weight = weight
    
    def calculate_score(self, activities: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate score for this category based on activities and user profile"""
        raise NotImplementedError("Subclasses must implement calculate_score")
    
    def apply_decay(self, score: float, days_since_activity: int) -> float:
        """Apply time decay to score based on recency of activities"""
        return score * (self.weight.decay_factor ** days_since_activity)


class FinancialStabilityAlgorithm(ScoringAlgorithm):
    """Algorithm for financial stability scoring"""
    
    def __init__(self):
        super().__init__(
            ScoringCategory.FINANCIAL_STABILITY,
            CategoryWeight(ScoringCategory.FINANCIAL_STABILITY, 0.15, 150.0)
        )
    
    def calculate_score(self, activities: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate financial stability score"""
        score = 0.0
        
        # XRP Transaction History
        xrp_transactions = [a for a in activities if a.get('activity_type') == 'xrp_transaction']
        if xrp_transactions:
            # Regular transaction frequency (not too frequent, not too sparse)
            transaction_frequency = len(xrp_transactions) / 30  # per day over last 30 days
            frequency_score = min(50, max(0, 50 - abs(transaction_frequency - 1) * 10))
            score += frequency_score
            
            # Transaction volume consistency
            volumes = [a.get('value', 0) for a in xrp_transactions]
            if volumes:
                volume_consistency = 1 - (max(volumes) - min(volumes)) / max(volumes) if max(volumes) > 0 else 0
                score += volume_consistency * 30
        
        # Staking Activity
        staking_activities = [a for a in activities if a.get('activity_type') == 'staking']
        if staking_activities:
            staking_duration = sum(a.get('metadata', {}).get('duration_days', 0) for a in staking_activities)
            score += min(40, staking_duration * 0.1)  # Up to 40 points for long-term staking
        
        # DeFi Participation
        defi_activities = [a for a in activities if a.get('activity_type') == 'defi_participation']
        if defi_activities:
            # Diversified DeFi usage
            unique_protocols = len(set(a.get('metadata', {}).get('protocol', '') for a in defi_activities))
            score += min(30, unique_protocols * 5)
        
        return min(score, self.weight.max_points)


class BlockchainActivityAlgorithm(ScoringAlgorithm):
    """Algorithm for blockchain activity scoring"""
    
    def __init__(self):
        super().__init__(
            ScoringCategory.BLOCKCHAIN_ACTIVITY,
            CategoryWeight(ScoringCategory.BLOCKCHAIN_ACTIVITY, 0.15, 150.0)
        )
    
    def calculate_score(self, activities: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate blockchain activity score"""
        score = 0.0
        
        # Mining Activity
        mining_activities = [a for a in activities if a.get('activity_type') == 'mining']
        if mining_activities:
            total_mining_value = sum(a.get('value', 0) for a in mining_activities)
            score += min(40, total_mining_value * 0.01)
        
        # Farming Activity
        farming_activities = [a for a in activities if a.get('activity_type') == 'farming']
        if farming_activities:
            farming_duration = sum(a.get('metadata', {}).get('duration_days', 0) for a in farming_activities)
            score += min(35, farming_duration * 0.2)
        
        # Airdrop Participation
        airdrop_activities = [a for a in activities if a.get('activity_type') == 'airdrop_participation']
        if airdrop_activities:
            # Quality of airdrops (based on value and verification)
            verified_airdrops = [a for a in airdrop_activities if a.get('verified', False)]
            score += len(verified_airdrops) * 5
        
        # NFT Activities
        nft_activities = [a for a in activities if a.get('activity_type') in ['nft_creation', 'nft_trading']]
        if nft_activities:
            # Creative and trading activity
            creation_activities = [a for a in nft_activities if a.get('activity_type') == 'nft_creation']
            trading_activities = [a for a in nft_activities if a.get('activity_type') == 'nft_trading']
            
            score += len(creation_activities) * 8  # Higher reward for creation
            score += len(trading_activities) * 3   # Lower reward for trading
        
        return min(score, self.weight.max_points)


class CommunityParticipationAlgorithm(ScoringAlgorithm):
    """Algorithm for community participation scoring"""
    
    def __init__(self):
        super().__init__(
            ScoringCategory.COMMUNITY_PARTICIPATION,
            CategoryWeight(ScoringCategory.COMMUNITY_PARTICIPATION, 0.15, 150.0)
        )
    
    def calculate_score(self, activities: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate community participation score"""
        score = 0.0
        
        # Community Service
        service_activities = [a for a in activities if a.get('activity_type') == 'community_service']
        if service_activities:
            total_service_hours = sum(a.get('metadata', {}).get('hours', 0) for a in service_activities)
            score += min(50, total_service_hours * 2)
        
        # Event Participation
        event_activities = [a for a in activities if a.get('activity_type') == 'event_participation']
        if event_activities:
            # Different types of events have different values
            event_scores = {
                'conference': 15,
                'workshop': 10,
                'meetup': 5,
                'online_event': 3
            }
            
            for activity in event_activities:
                event_type = activity.get('metadata', {}).get('event_type', 'online_event')
                score += event_scores.get(event_type, 3)
        
        # Knowledge Sharing
        knowledge_activities = [a for a in activities if a.get('activity_type') == 'knowledge_sharing']
        if knowledge_activities:
            # Quality content gets higher scores
            for activity in knowledge_activities:
                quality_score = activity.get('metadata', {}).get('quality_score', 5)
                engagement_score = activity.get('metadata', {}).get('engagement_score', 0)
                score += min(20, quality_score + engagement_score * 0.1)
        
        # Mentorship
        mentorship_activities = [a for a in activities if a.get('activity_type') == 'mentorship']
        if mentorship_activities:
            total_mentorship_hours = sum(a.get('metadata', {}).get('hours', 0) for a in mentorship_activities)
            score += min(40, total_mentorship_hours * 3)
        
        return min(score, self.weight.max_points)


class SocialResponsibilityAlgorithm(ScoringAlgorithm):
    """Algorithm for social responsibility scoring"""
    
    def __init__(self):
        super().__init__(
            ScoringCategory.SOCIAL_GOOD,
            CategoryWeight(ScoringCategory.SOCIAL_GOOD, 0.07, 70.0)
        )
    
    def calculate_score(self, activities: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate social responsibility score"""
        score = 0.0
        
        # Environmental Impact
        environmental_activities = [a for a in activities if a.get('metadata', {}).get('environmental_impact')]
        if environmental_activities:
            total_impact = sum(a.get('metadata', {}).get('environmental_impact', 0) for a in environmental_activities)
            score += min(30, total_impact * 2)
        
        # Charitable Activities
        charitable_activities = [a for a in activities if a.get('metadata', {}).get('charitable')]
        if charitable_activities:
            total_donations = sum(a.get('value', 0) for a in charitable_activities)
            score += min(25, total_donations * 0.1)
        
        # Governance Participation
        governance_activities = [a for a in activities if a.get('activity_type') == 'governance_voting']
        if governance_activities:
            # Active participation in governance
            score += min(15, len(governance_activities) * 2)
        
        return min(score, self.weight.max_points)


class PersonalDevelopmentAlgorithm(ScoringAlgorithm):
    """Algorithm for personal development scoring"""
    
    def __init__(self):
        super().__init__(
            ScoringCategory.SKILL_DEVELOPMENT,
            CategoryWeight(ScoringCategory.SKILL_DEVELOPMENT, 0.05, 50.0)
        )
    
    def calculate_score(self, activities: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate personal development score"""
        score = 0.0
        
        # Education Activities
        education_activities = [a for a in activities if a.get('activity_type') == 'education']
        if education_activities:
            # Different types of education have different values
            education_scores = {
                'certification': 15,
                'course_completion': 10,
                'workshop': 8,
                'tutorial': 3,
                'reading': 2
            }
            
            for activity in education_activities:
                education_type = activity.get('metadata', {}).get('education_type', 'reading')
                score += education_scores.get(education_type, 2)
        
        # Skill Development
        skill_activities = [a for a in activities if a.get('activity_type') == 'skill_development']
        if skill_activities:
            # Track skill progression
            for activity in skill_activities:
                skill_level = activity.get('metadata', {}).get('skill_level', 1)
                hours_invested = activity.get('metadata', {}).get('hours', 0)
                score += min(20, skill_level * hours_invested * 0.5)
        
        # Health & Wellness
        health_activities = [a for a in activities if a.get('activity_type') == 'fitness_activity']
        if health_activities:
            total_health_points = sum(a.get('metadata', {}).get('health_points', 0) for a in health_activities)
            score += min(15, total_health_points * 0.1)
        
        return min(score, self.weight.max_points)


# Registry of all scoring algorithms
SCORING_ALGORITHMS = {
    ScoringCategory.FINANCIAL_STABILITY: FinancialStabilityAlgorithm(),
    ScoringCategory.BLOCKCHAIN_ACTIVITY: BlockchainActivityAlgorithm(),
    ScoringCategory.COMMUNITY_PARTICIPATION: CommunityParticipationAlgorithm(),
    ScoringCategory.SOCIAL_GOOD: SocialResponsibilityAlgorithm(),
    ScoringCategory.SKILL_DEVELOPMENT: PersonalDevelopmentAlgorithm(),
}


def get_scoring_algorithm(category: ScoringCategory) -> ScoringAlgorithm:
    """Get the scoring algorithm for a specific category"""
    return SCORING_ALGORITHMS.get(category)


def get_all_categories() -> List[ScoringCategory]:
    """Get all available scoring categories"""
    return list(ScoringCategory)


def get_category_weights() -> Dict[ScoringCategory, float]:
    """Get the weight distribution across all categories"""
    return {algorithm.category: algorithm.weight.weight for algorithm in SCORING_ALGORITHMS.values()}
