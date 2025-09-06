"""
Health Scorer for XRP Health Score Platform
==========================================

This module implements the core health scoring algorithm that goes far beyond
traditional credit scoring, incorporating multiple dimensions of user behavior
and community contribution.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import math

from .data_models import UserProfile, ActivityRecord, ScoreHistory, ActivityType
from .scoring_categories import ScoringCategory, get_scoring_algorithm, get_category_weights
from .citizen_coin import CitizenCoinSystem


@dataclass
class HealthScore:
    """Comprehensive health score result"""
    user_id: str
    timestamp: datetime
    total_score: float
    max_possible_score: float
    score_percentage: float
    
    # Category breakdown
    category_scores: Dict[ScoringCategory, float]
    category_weights: Dict[ScoringCategory, float]
    
    # Additional metrics
    activity_count: int
    recent_activity_score: float
    consistency_score: float
    community_impact_score: float
    
    # Recommendations
    improvement_areas: List[str]
    strength_areas: List[str]
    next_goals: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'total_score': self.total_score,
            'max_possible_score': self.max_possible_score,
            'score_percentage': self.score_percentage,
            'category_scores': {category.value: score for category, score in self.category_scores.items()},
            'category_weights': {category.value: weight for category, weight in self.category_weights.items()},
            'activity_count': self.activity_count,
            'recent_activity_score': self.recent_activity_score,
            'consistency_score': self.consistency_score,
            'community_impact_score': self.community_impact_score,
            'improvement_areas': self.improvement_areas,
            'strength_areas': self.strength_areas,
            'next_goals': self.next_goals
        }


class HealthScorer:
    """
    Advanced health scoring system that evaluates users across multiple dimensions:
    - Financial stability and blockchain activity
    - Community engagement and knowledge sharing
    - Social responsibility and environmental impact
    - Personal development and skill building
    """
    
    def __init__(self):
        self.citizen_coin_system = CitizenCoinSystem()
        self.category_weights = get_category_weights()
        self.scoring_algorithms = {
            category: get_scoring_algorithm(category)
            for category in ScoringCategory
        }
    
    def calculate_health_score(self, user_profile: UserProfile, 
                             include_recommendations: bool = True) -> HealthScore:
        """Calculate comprehensive health score for a user"""
        
        # Get activities from the last 90 days for scoring
        cutoff_date = datetime.now() - timedelta(days=90)
        recent_activities = [
            activity for activity in user_profile.activities
            if activity.timestamp >= cutoff_date
        ]
        
        # Convert activities to scoring format
        activity_data = [self._activity_to_scoring_format(activity) for activity in recent_activities]
        user_data = self._user_profile_to_scoring_format(user_profile)
        
        # Calculate scores for each category
        category_scores = {}
        for category in ScoringCategory:
            algorithm = self.scoring_algorithms.get(category)
            if algorithm:
                category_scores[category] = algorithm.calculate_score(activity_data, user_data)
            else:
                category_scores[category] = 0.0
        
        # Calculate weighted total score
        total_score = sum(
            score * self.category_weights[category]
            for category, score in category_scores.items()
        )
        
        # Calculate additional metrics
        recent_activity_score = self._calculate_recent_activity_score(recent_activities)
        consistency_score = self._calculate_consistency_score(recent_activities)
        community_impact_score = self._calculate_community_impact_score(recent_activities)
        
        # Calculate max possible score
        max_possible_score = sum(
            algorithm.weight.max_points * self.category_weights[category]
            for category, algorithm in self.scoring_algorithms.items()
        )
        
        score_percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        # Generate recommendations if requested
        improvement_areas = []
        strength_areas = []
        next_goals = []
        
        if include_recommendations:
            improvement_areas = self._identify_improvement_areas(category_scores)
            strength_areas = self._identify_strength_areas(category_scores)
            next_goals = self._generate_next_goals(category_scores, recent_activities)
        
        return HealthScore(
            user_id=user_profile.user_id,
            timestamp=datetime.now(),
            total_score=total_score,
            max_possible_score=max_possible_score,
            score_percentage=score_percentage,
            category_scores=category_scores,
            category_weights=self.category_weights,
            activity_count=len(recent_activities),
            recent_activity_score=recent_activity_score,
            consistency_score=consistency_score,
            community_impact_score=community_impact_score,
            improvement_areas=improvement_areas,
            strength_areas=strength_areas,
            next_goals=next_goals
        )
    
    def _activity_to_scoring_format(self, activity: ActivityRecord) -> Dict[str, Any]:
        """Convert ActivityRecord to format expected by scoring algorithms"""
        return {
            'activity_type': activity.activity_type.value,
            'timestamp': activity.timestamp.isoformat(),
            'value': activity.value,
            'metadata': activity.metadata,
            'verified': activity.verified,
            'points_earned': activity.points_earned
        }
    
    def _user_profile_to_scoring_format(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Convert UserProfile to format expected by scoring algorithms"""
        return {
            'user_id': user_profile.user_id,
            'xrp_address': user_profile.xrp_address,
            'created_at': user_profile.created_at.isoformat(),
            'citizen_coins': {tier.value: amount for tier, amount in user_profile.citizen_coins.items()},
            'connections': user_profile.connections,
            'communities': user_profile.communities
        }
    
    def _calculate_recent_activity_score(self, activities: List[ActivityRecord]) -> float:
        """Calculate score based on recent activity frequency and quality"""
        if not activities:
            return 0.0
        
        # Weight activities by recency
        now = datetime.now()
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for activity in activities:
            days_old = (now - activity.timestamp).days
            # Recent activities get higher weight
            weight = math.exp(-days_old / 30)  # Exponential decay over 30 days
            
            # Base score from activity points
            base_score = activity.points_earned
            
            # Quality multiplier
            quality_multiplier = activity.metadata.get('quality_score', 5) / 10.0
            
            # Verification bonus
            verification_bonus = 1.2 if activity.verified else 1.0
            
            activity_score = base_score * quality_multiplier * verification_bonus
            total_weighted_score += activity_score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_consistency_score(self, activities: List[ActivityRecord]) -> float:
        """Calculate score based on activity consistency over time"""
        if len(activities) < 2:
            return 0.0
        
        # Group activities by week
        weekly_activity = {}
        for activity in activities:
            week_key = activity.timestamp.isocalendar()[:2]  # (year, week)
            if week_key not in weekly_activity:
                weekly_activity[week_key] = []
            weekly_activity[week_key].append(activity)
        
        if len(weekly_activity) < 2:
            return 0.0
        
        # Calculate consistency as inverse of variance in weekly activity counts
        weekly_counts = [len(week_activities) for week_activities in weekly_activity.values()]
        mean_count = sum(weekly_counts) / len(weekly_counts)
        
        if mean_count == 0:
            return 0.0
        
        variance = sum((count - mean_count) ** 2 for count in weekly_counts) / len(weekly_counts)
        consistency = max(0, 100 - (variance / mean_count) * 10)  # Higher variance = lower consistency
        
        return min(100, consistency)
    
    def _calculate_community_impact_score(self, activities: List[ActivityRecord]) -> float:
        """Calculate score based on community impact of activities"""
        community_activities = [
            activity for activity in activities
            if activity.activity_type in [
                ActivityType.COMMUNITY_SERVICE,
                ActivityType.MENTORSHIP,
                ActivityType.KNOWLEDGE_SHARING,
                ActivityType.EVENT_PARTICIPATION
            ]
        ]
        
        if not community_activities:
            return 0.0
        
        total_impact = 0.0
        for activity in community_activities:
            # Base impact score
            base_impact = activity.points_earned
            
            # Community impact multiplier from metadata
            community_multiplier = activity.metadata.get('community_impact', 1.0)
            
            # Engagement multiplier (likes, shares, etc.)
            engagement_score = activity.metadata.get('engagement_score', 0)
            engagement_multiplier = 1.0 + (engagement_score / 100.0)
            
            activity_impact = base_impact * community_multiplier * engagement_multiplier
            total_impact += activity_impact
        
        # Normalize to 0-100 scale
        max_possible_impact = len(community_activities) * 50  # Assume max 50 points per activity
        return min(100, (total_impact / max_possible_impact) * 100) if max_possible_impact > 0 else 0
    
    def _identify_improvement_areas(self, category_scores: Dict[ScoringCategory, float]) -> List[str]:
        """Identify areas where the user can improve their score"""
        improvements = []
        
        # Find categories with lowest scores
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])
        
        for category, score in sorted_categories[:3]:  # Top 3 lowest scores
            if score < 50:  # Below 50% of max possible
                improvements.append(self._get_improvement_suggestion(category))
        
        return improvements
    
    def _identify_strength_areas(self, category_scores: Dict[ScoringCategory, float]) -> List[str]:
        """Identify areas where the user is performing well"""
        strengths = []
        
        # Find categories with highest scores
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        for category, score in sorted_categories[:3]:  # Top 3 highest scores
            if score > 70:  # Above 70% of max possible
                strengths.append(self._get_strength_description(category))
        
        return strengths
    
    def _generate_next_goals(self, category_scores: Dict[ScoringCategory, float], 
                           activities: List[ActivityRecord]) -> List[str]:
        """Generate specific goals for the user to improve their score"""
        goals = []
        
        # Activity frequency goals
        recent_activities = [a for a in activities if (datetime.now() - a.timestamp).days <= 7]
        if len(recent_activities) < 5:
            goals.append("Complete at least 5 activities this week to improve consistency")
        
        # Category-specific goals
        for category, score in category_scores.items():
            if score < 60:
                goals.append(self._get_category_goal(category))
        
        # Community engagement goals
        community_activities = [a for a in activities if a.activity_type in [
            ActivityType.COMMUNITY_SERVICE, ActivityType.MENTORSHIP, ActivityType.KNOWLEDGE_SHARING
        ]]
        if len(community_activities) < 3:
            goals.append("Participate in at least 3 community activities this month")
        
        return goals[:5]  # Limit to 5 goals
    
    def _get_improvement_suggestion(self, category: ScoringCategory) -> str:
        """Get specific improvement suggestion for a category"""
        suggestions = {
            ScoringCategory.FINANCIAL_STABILITY: "Increase XRP transaction frequency and consider staking for long-term stability",
            ScoringCategory.BLOCKCHAIN_ACTIVITY: "Participate in more DeFi protocols, mining, or farming activities",
            ScoringCategory.COMMUNITY_PARTICIPATION: "Join community events, share knowledge, or mentor others",
            ScoringCategory.SOCIAL_GOOD: "Engage in charitable activities or environmental initiatives",
            ScoringCategory.SKILL_DEVELOPMENT: "Complete educational courses or develop new skills"
        }
        return suggestions.get(category, "Focus on activities in this category to improve your score")
    
    def _get_strength_description(self, category: ScoringCategory) -> str:
        """Get description of user's strength in a category"""
        descriptions = {
            ScoringCategory.FINANCIAL_STABILITY: "Excellent financial management and blockchain activity",
            ScoringCategory.BLOCKCHAIN_ACTIVITY: "Strong participation in blockchain ecosystem",
            ScoringCategory.COMMUNITY_PARTICIPATION: "Active community member and contributor",
            ScoringCategory.SOCIAL_GOOD: "Making positive social and environmental impact",
            ScoringCategory.SKILL_DEVELOPMENT: "Consistent learner and skill developer"
        }
        return descriptions.get(category, "Strong performance in this area")
    
    def _get_category_goal(self, category: ScoringCategory) -> str:
        """Get specific goal for a category"""
        goals = {
            ScoringCategory.FINANCIAL_STABILITY: "Complete 10 XRP transactions and start staking",
            ScoringCategory.BLOCKCHAIN_ACTIVITY: "Try 3 different DeFi protocols or start mining",
            ScoringCategory.COMMUNITY_PARTICIPATION: "Attend 2 community events and share knowledge",
            ScoringCategory.SOCIAL_GOOD: "Participate in 1 charitable or environmental activity",
            ScoringCategory.SKILL_DEVELOPMENT: "Complete 1 educational course or certification"
        }
        return goals.get(category, "Increase activity in this category")
    
    def get_score_history(self, user_profile: UserProfile, days: int = 30) -> List[ScoreHistory]:
        """Get historical score changes for a user"""
        # This would typically be stored in a database
        # For now, we'll simulate by calculating scores for different time periods
        
        history = []
        now = datetime.now()
        
        for i in range(days):
            date = now - timedelta(days=i)
            
            # Get activities up to this date
            cutoff_date = date - timedelta(days=90)
            activities_up_to_date = [
                activity for activity in user_profile.activities
                if cutoff_date <= activity.timestamp <= date
            ]
            
            if activities_up_to_date:
                # Calculate score for this period
                activity_data = [self._activity_to_scoring_format(activity) for activity in activities_up_to_date]
                user_data = self._user_profile_to_scoring_format(user_profile)
                
                category_scores = {}
                for category in ScoringCategory:
                    algorithm = self.scoring_algorithms.get(category)
                    if algorithm:
                        category_scores[category] = algorithm.calculate_score(activity_data, user_data)
                    else:
                        category_scores[category] = 0.0
                
                total_score = sum(
                    score * self.category_weights[category]
                    for category, score in category_scores.items()
                )
                
                previous_score = history[-1].new_score if history else 0
                
                history.append(ScoreHistory(
                    user_id=user_profile.user_id,
                    timestamp=date,
                    previous_score=previous_score,
                    new_score=total_score,
                    score_change=total_score - previous_score,
                    contributing_activities=[activity.activity_id for activity in activities_up_to_date[-5:]],  # Last 5 activities
                    category_breakdown={category.value: score for category, score in category_scores.items()}
                ))
        
        return list(reversed(history))  # Return in chronological order
    
    def compare_with_community(self, user_score: HealthScore, 
                             community_scores: List[HealthScore]) -> Dict[str, Any]:
        """Compare user's score with community averages"""
        if not community_scores:
            return {}
        
        # Calculate community statistics
        total_scores = [score.total_score for score in community_scores]
        avg_score = sum(total_scores) / len(total_scores)
        max_score = max(total_scores)
        min_score = min(total_scores)
        
        # Calculate percentiles
        sorted_scores = sorted(total_scores)
        user_rank = sum(1 for score in sorted_scores if score < user_score.total_score)
        percentile = (user_rank / len(sorted_scores)) * 100
        
        return {
            'user_score': user_score.total_score,
            'community_average': avg_score,
            'community_max': max_score,
            'community_min': min_score,
            'percentile_rank': percentile,
            'performance_level': self._get_performance_level(percentile),
            'score_gap': user_score.total_score - avg_score
        }
    
    def _get_performance_level(self, percentile: float) -> str:
        """Get performance level based on percentile rank"""
        if percentile >= 90:
            return "Exceptional"
        elif percentile >= 75:
            return "Excellent"
        elif percentile >= 50:
            return "Good"
        elif percentile >= 25:
            return "Average"
        else:
            return "Needs Improvement"
