"""
Rehabilitation Tracker for Personal Growth
=========================================

This module tracks personal growth, rehabilitation progress, and helps users
overcome past challenges through positive community contribution and
innovative project development.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json

from ..core.data_models import UserProfile, ActivityRecord, ActivityType, CoinTier


class RehabilitationStage(Enum):
    """Stages of rehabilitation and personal growth"""
    ACKNOWLEDGMENT = "acknowledgment"           # Acknowledging past mistakes
    COMMITMENT = "commitment"                   # Committing to change
    ACTION = "action"                          # Taking positive actions
    CONSISTENCY = "consistency"                # Maintaining positive behavior
    LEADERSHIP = "leadership"                  # Leading others in positive change
    MASTERY = "mastery"                       # Achieving mastery in positive impact


class GrowthCategory(Enum):
    """Categories of personal growth and development"""
    SELF_IMPROVEMENT = "self_improvement"
    COMMUNITY_SERVICE = "community_service"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    MENTORSHIP = "mentorship"
    INNOVATION = "innovation"
    SOCIAL_IMPACT = "social_impact"
    FINANCIAL_LITERACY = "financial_literacy"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"


@dataclass
class RehabilitationProfile:
    """Extended profile for rehabilitation tracking"""
    user_id: str
    base_profile: UserProfile
    
    # Personal background (voluntarily shared)
    background_info: Dict[str, Any]
    challenges_faced: List[str]
    growth_goals: List[str]
    
    # Rehabilitation tracking
    current_stage: RehabilitationStage
    stage_progress: float  # 0.0 to 1.0
    stage_start_date: datetime
    
    # Growth metrics
    growth_categories: Dict[GrowthCategory, float]  # Progress in each category
    total_growth_score: float
    
    # Project portfolio
    projects: List['RehabilitationProject']
    project_impact_score: float
    
    # Community validation
    community_endorsements: List['CommunityEndorsement']
    peer_validation_score: float
    
    # Redemption progress
    redemption_percentage: float  # 0.0 to 100.0
    background_impact_reduction: float  # How much past background impact is reduced
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'base_profile': self.base_profile.to_dict(),
            'background_info': self.background_info,
            'challenges_faced': self.challenges_faced,
            'growth_goals': self.growth_goals,
            'current_stage': self.current_stage.value,
            'stage_progress': self.stage_progress,
            'stage_start_date': self.stage_start_date.isoformat(),
            'growth_categories': {category.value: score for category, score in self.growth_categories.items()},
            'total_growth_score': self.total_growth_score,
            'projects': [project.to_dict() for project in self.projects],
            'project_impact_score': self.project_impact_score,
            'community_endorsements': [endorsement.to_dict() for endorsement in self.community_endorsements],
            'peer_validation_score': self.peer_validation_score,
            'redemption_percentage': self.redemption_percentage,
            'background_impact_reduction': self.background_impact_reduction
        }


@dataclass
class RehabilitationProject:
    """Project that contributes to rehabilitation and community impact"""
    project_id: str
    user_id: str
    title: str
    description: str
    category: str  # government, community, healthcare, finance, etc.
    
    # Project details
    start_date: datetime
    end_date: Optional[datetime]
    status: str  # planning, active, completed, paused
    
    # Impact metrics
    target_beneficiaries: int
    actual_beneficiaries: int
    impact_score: float
    innovation_score: float
    
    # Validation
    verified: bool
    verification_method: Optional[str]
    verification_data: Dict[str, Any]
    
    # Community feedback
    community_ratings: List[float]
    expert_reviews: List['ExpertReview']
    
    # Rewards
    points_earned: float
    coins_earned: Dict[CoinTier, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'project_id': self.project_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'target_beneficiaries': self.target_beneficiaries,
            'actual_beneficiaries': self.actual_beneficiaries,
            'impact_score': self.impact_score,
            'innovation_score': self.innovation_score,
            'verified': self.verified,
            'verification_method': self.verification_method,
            'verification_data': self.verification_data,
            'community_ratings': self.community_ratings,
            'expert_reviews': [review.to_dict() for review in self.expert_reviews],
            'points_earned': self.points_earned,
            'coins_earned': {tier.value: amount for tier, amount in self.coins_earned.items()}
        }


@dataclass
class CommunityEndorsement:
    """Community endorsement of user's rehabilitation progress"""
    endorsement_id: str
    endorser_id: str
    endorser_type: str  # peer, mentor, community_leader, expert
    user_id: str
    
    # Endorsement details
    category: GrowthCategory
    endorsement_text: str
    rating: float  # 1.0 to 10.0
    timestamp: datetime
    
    # Verification
    verified: bool
    verification_method: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'endorsement_id': self.endorsement_id,
            'endorser_id': self.endorser_id,
            'endorser_type': self.endorser_type,
            'user_id': self.user_id,
            'category': self.category.value,
            'endorsement_text': self.endorsement_text,
            'rating': self.rating,
            'timestamp': self.timestamp.isoformat(),
            'verified': self.verified,
            'verification_method': self.verification_method
        }


@dataclass
class ExpertReview:
    """Expert review of a rehabilitation project"""
    review_id: str
    expert_id: str
    expert_credentials: str
    project_id: str
    
    # Review details
    technical_score: float
    impact_score: float
    innovation_score: float
    feasibility_score: float
    overall_score: float
    
    review_text: str
    recommendations: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'review_id': self.review_id,
            'expert_id': self.expert_id,
            'expert_credentials': self.expert_credentials,
            'project_id': self.project_id,
            'technical_score': self.technical_score,
            'impact_score': self.impact_score,
            'innovation_score': self.innovation_score,
            'feasibility_score': self.feasibility_score,
            'overall_score': self.overall_score,
            'review_text': self.review_text,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }


class RehabilitationTracker:
    """
    Tracks and manages rehabilitation progress for users overcoming past challenges
    """
    
    def __init__(self):
        self.rehabilitation_profiles: Dict[str, RehabilitationProfile] = {}
        self.stage_requirements = self._initialize_stage_requirements()
        self.growth_weights = self._initialize_growth_weights()
    
    def _initialize_stage_requirements(self) -> Dict[RehabilitationStage, Dict[str, Any]]:
        """Initialize requirements for each rehabilitation stage"""
        return {
            RehabilitationStage.ACKNOWLEDGMENT: {
                "required_activities": 5,
                "required_projects": 0,
                "required_endorsements": 0,
                "min_growth_score": 0,
                "description": "Acknowledge past mistakes and commit to change"
            },
            RehabilitationStage.COMMITMENT: {
                "required_activities": 15,
                "required_projects": 1,
                "required_endorsements": 2,
                "min_growth_score": 100,
                "description": "Demonstrate commitment to positive change"
            },
            RehabilitationStage.ACTION: {
                "required_activities": 30,
                "required_projects": 3,
                "required_endorsements": 5,
                "min_growth_score": 250,
                "description": "Take consistent positive actions"
            },
            RehabilitationStage.CONSISTENCY: {
                "required_activities": 60,
                "required_projects": 5,
                "required_endorsements": 10,
                "min_growth_score": 500,
                "description": "Maintain consistent positive behavior over time"
            },
            RehabilitationStage.LEADERSHIP: {
                "required_activities": 100,
                "required_projects": 8,
                "required_endorsements": 20,
                "min_growth_score": 750,
                "description": "Lead others in positive change"
            },
            RehabilitationStage.MASTERY: {
                "required_activities": 200,
                "required_projects": 12,
                "required_endorsements": 50,
                "min_growth_score": 1000,
                "description": "Achieve mastery in positive community impact"
            }
        }
    
    def _initialize_growth_weights(self) -> Dict[GrowthCategory, float]:
        """Initialize weights for different growth categories"""
        return {
            GrowthCategory.SELF_IMPROVEMENT: 0.15,
            GrowthCategory.COMMUNITY_SERVICE: 0.20,
            GrowthCategory.KNOWLEDGE_SHARING: 0.15,
            GrowthCategory.MENTORSHIP: 0.20,
            GrowthCategory.INNOVATION: 0.15,
            GrowthCategory.SOCIAL_IMPACT: 0.10,
            GrowthCategory.FINANCIAL_LITERACY: 0.03,
            GrowthCategory.EMOTIONAL_INTELLIGENCE: 0.02
        }
    
    def create_rehabilitation_profile(self, user_profile: UserProfile, 
                                   background_info: Dict[str, Any]) -> RehabilitationProfile:
        """Create a rehabilitation profile for a user"""
        
        rehabilitation_profile = RehabilitationProfile(
            user_id=user_profile.user_id,
            base_profile=user_profile,
            background_info=background_info,
            challenges_faced=background_info.get('challenges', []),
            growth_goals=background_info.get('goals', []),
            current_stage=RehabilitationStage.ACKNOWLEDGMENT,
            stage_progress=0.0,
            stage_start_date=datetime.now(),
            growth_categories={category: 0.0 for category in GrowthCategory},
            total_growth_score=0.0,
            projects=[],
            project_impact_score=0.0,
            community_endorsements=[],
            peer_validation_score=0.0,
            redemption_percentage=0.0,
            background_impact_reduction=0.0
        )
        
        self.rehabilitation_profiles[user_profile.user_id] = rehabilitation_profile
        return rehabilitation_profile
    
    def add_project(self, user_id: str, project_data: Dict[str, Any]) -> RehabilitationProject:
        """Add a rehabilitation project for a user"""
        if user_id not in self.rehabilitation_profiles:
            raise ValueError(f"Rehabilitation profile not found for user {user_id}")
        
        project = RehabilitationProject(
            project_id=f"project_{datetime.now().timestamp()}",
            user_id=user_id,
            title=project_data['title'],
            description=project_data['description'],
            category=project_data['category'],
            start_date=datetime.now(),
            end_date=project_data.get('end_date'),
            status='planning',
            target_beneficiaries=project_data.get('target_beneficiaries', 0),
            actual_beneficiaries=0,
            impact_score=0.0,
            innovation_score=0.0,
            verified=False,
            verification_method=None,
            verification_data={},
            community_ratings=[],
            expert_reviews=[],
            points_earned=0.0,
            coins_earned={tier: 0 for tier in CoinTier}
        )
        
        self.rehabilitation_profiles[user_id].projects.append(project)
        return project
    
    def update_project_progress(self, project_id: str, progress_data: Dict[str, Any]) -> bool:
        """Update project progress and impact metrics"""
        for profile in self.rehabilitation_profiles.values():
            for project in profile.projects:
                if project.project_id == project_id:
                    # Update project data
                    project.actual_beneficiaries = progress_data.get('actual_beneficiaries', project.actual_beneficiaries)
                    project.impact_score = progress_data.get('impact_score', project.impact_score)
                    project.innovation_score = progress_data.get('innovation_score', project.innovation_score)
                    project.status = progress_data.get('status', project.status)
                    
                    if progress_data.get('end_date'):
                        project.end_date = datetime.fromisoformat(progress_data['end_date'])
                    
                    # Recalculate project impact score
                    self._calculate_project_impact_score(profile)
                    
                    return True
        
        return False
    
    def add_community_endorsement(self, user_id: str, endorsement_data: Dict[str, Any]) -> CommunityEndorsement:
        """Add a community endorsement for a user"""
        if user_id not in self.rehabilitation_profiles:
            raise ValueError(f"Rehabilitation profile not found for user {user_id}")
        
        endorsement = CommunityEndorsement(
            endorsement_id=f"endorsement_{datetime.now().timestamp()}",
            endorser_id=endorsement_data['endorser_id'],
            endorser_type=endorsement_data['endorser_type'],
            user_id=user_id,
            category=GrowthCategory(endorsement_data['category']),
            endorsement_text=endorsement_data['endorsement_text'],
            rating=endorsement_data['rating'],
            timestamp=datetime.now(),
            verified=endorsement_data.get('verified', False),
            verification_method=endorsement_data.get('verification_method')
        )
        
        self.rehabilitation_profiles[user_id].community_endorsements.append(endorsement)
        self._calculate_peer_validation_score(user_id)
        
        return endorsement
    
    def calculate_growth_score(self, user_id: str) -> float:
        """Calculate overall growth score for a user"""
        if user_id not in self.rehabilitation_profiles:
            return 0.0
        
        profile = self.rehabilitation_profiles[user_id]
        
        # Calculate category scores
        for category in GrowthCategory:
            category_score = self._calculate_category_score(profile, category)
            profile.growth_categories[category] = category_score
        
        # Calculate weighted total
        total_score = sum(
            score * self.growth_weights[category]
            for category, score in profile.growth_categories.items()
        )
        
        profile.total_growth_score = total_score
        return total_score
    
    def _calculate_category_score(self, profile: RehabilitationProfile, 
                                category: GrowthCategory) -> float:
        """Calculate score for a specific growth category"""
        score = 0.0
        
        if category == GrowthCategory.SELF_IMPROVEMENT:
            # Based on educational activities, personal development
            score = self._count_activities_by_type(profile, [
                ActivityType.EDUCATION, ActivityType.SKILL_DEVELOPMENT,
                ActivityType.FITNESS_ACTIVITY, ActivityType.MENTAL_HEALTH
            ]) * 10
        
        elif category == GrowthCategory.COMMUNITY_SERVICE:
            # Based on community service activities
            score = self._count_activities_by_type(profile, [
                ActivityType.COMMUNITY_SERVICE
            ]) * 15
        
        elif category == GrowthCategory.KNOWLEDGE_SHARING:
            # Based on knowledge sharing activities
            score = self._count_activities_by_type(profile, [
                ActivityType.KNOWLEDGE_SHARING
            ]) * 12
        
        elif category == GrowthCategory.MENTORSHIP:
            # Based on mentorship activities
            score = self._count_activities_by_type(profile, [
                ActivityType.MENTORSHIP
            ]) * 20
        
        elif category == GrowthCategory.INNOVATION:
            # Based on innovative projects
            score = sum(project.innovation_score for project in profile.projects)
        
        elif category == GrowthCategory.SOCIAL_IMPACT:
            # Based on project impact and social activities
            score = profile.project_impact_score + self._count_activities_by_type(profile, [
                ActivityType.GOVERNANCE_VOTING
            ]) * 8
        
        elif category == GrowthCategory.FINANCIAL_LITERACY:
            # Based on financial activities and education
            score = self._count_activities_by_type(profile, [
                ActivityType.XRP_TRANSACTION, ActivityType.STAKING,
                ActivityType.DEFI_PARTICIPATION
            ]) * 5
        
        elif category == GrowthCategory.EMOTIONAL_INTELLIGENCE:
            # Based on community endorsements and peer validation
            score = profile.peer_validation_score
        
        return min(score, 100.0)  # Cap at 100
    
    def _count_activities_by_type(self, profile: RehabilitationProfile, 
                                activity_types: List[ActivityType]) -> int:
        """Count activities of specific types"""
        return len([
            activity for activity in profile.base_profile.activities
            if activity.activity_type in activity_types
        ])
    
    def _calculate_project_impact_score(self, profile: RehabilitationProfile):
        """Calculate overall project impact score"""
        if not profile.projects:
            profile.project_impact_score = 0.0
            return
        
        total_impact = 0.0
        for project in profile.projects:
            # Weight by project status and verification
            weight = 1.0
            if project.verified:
                weight *= 1.5
            if project.status == 'completed':
                weight *= 1.2
            elif project.status == 'active':
                weight *= 1.0
            else:
                weight *= 0.5
            
            total_impact += project.impact_score * weight
        
        profile.project_impact_score = total_impact
    
    def _calculate_peer_validation_score(self, user_id: str):
        """Calculate peer validation score based on endorsements"""
        profile = self.rehabilitation_profiles[user_id]
        
        if not profile.community_endorsements:
            profile.peer_validation_score = 0.0
            return
        
        # Calculate weighted average rating
        total_rating = 0.0
        total_weight = 0.0
        
        for endorsement in profile.community_endorsements:
            if endorsement.verified:
                # Weight by endorser type
                weight = {
                    'peer': 1.0,
                    'mentor': 1.5,
                    'community_leader': 2.0,
                    'expert': 2.5
                }.get(endorsement.endorser_type, 1.0)
                
                total_rating += endorsement.rating * weight
                total_weight += weight
        
        profile.peer_validation_score = (total_rating / total_weight) * 10 if total_weight > 0 else 0.0
    
    def check_stage_progression(self, user_id: str) -> Tuple[bool, Optional[RehabilitationStage]]:
        """Check if user can progress to next rehabilitation stage"""
        if user_id not in self.rehabilitation_profiles:
            return False, None
        
        profile = self.rehabilitation_profiles[user_id]
        current_stage = profile.current_stage
        requirements = self.stage_requirements[current_stage]
        
        # Check if requirements are met
        activity_count = len(profile.base_profile.activities)
        project_count = len(profile.projects)
        endorsement_count = len(profile.community_endorsements)
        growth_score = profile.total_growth_score
        
        if (activity_count >= requirements['required_activities'] and
            project_count >= requirements['required_projects'] and
            endorsement_count >= requirements['required_endorsements'] and
            growth_score >= requirements['min_growth_score']):
            
            # Progress to next stage
            stage_list = list(RehabilitationStage)
            current_index = stage_list.index(current_stage)
            
            if current_index < len(stage_list) - 1:
                next_stage = stage_list[current_index + 1]
                profile.current_stage = next_stage
                profile.stage_progress = 0.0
                profile.stage_start_date = datetime.now()
                return True, next_stage
        
        return False, None
    
    def calculate_redemption_percentage(self, user_id: str) -> float:
        """Calculate redemption percentage based on rehabilitation progress"""
        if user_id not in self.rehabilitation_profiles:
            return 0.0
        
        profile = self.rehabilitation_profiles[user_id]
        
        # Base redemption from stage progression
        stage_redemption = {
            RehabilitationStage.ACKNOWLEDGMENT: 10.0,
            RehabilitationStage.COMMITMENT: 25.0,
            RehabilitationStage.ACTION: 40.0,
            RehabilitationStage.CONSISTENCY: 60.0,
            RehabilitationStage.LEADERSHIP: 80.0,
            RehabilitationStage.MASTERY: 100.0
        }
        
        base_redemption = stage_redemption[profile.current_stage]
        
        # Add bonus for exceptional performance
        growth_bonus = min(20.0, profile.total_growth_score / 50.0)
        project_bonus = min(15.0, profile.project_impact_score / 100.0)
        community_bonus = min(10.0, profile.peer_validation_score / 10.0)
        
        total_redemption = min(100.0, base_redemption + growth_bonus + project_bonus + community_bonus)
        
        profile.redemption_percentage = total_redemption
        profile.background_impact_reduction = total_redemption / 100.0
        
        return total_redemption
    
    def get_rehabilitation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive rehabilitation summary for a user"""
        if user_id not in self.rehabilitation_profiles:
            return {}
        
        profile = self.rehabilitation_profiles[user_id]
        
        # Calculate current metrics
        growth_score = self.calculate_growth_score(user_id)
        redemption_percentage = self.calculate_redemption_percentage(user_id)
        can_progress, next_stage = self.check_stage_progression(user_id)
        
        return {
            'user_id': user_id,
            'current_stage': profile.current_stage.value,
            'stage_progress': profile.stage_progress,
            'total_growth_score': growth_score,
            'redemption_percentage': redemption_percentage,
            'background_impact_reduction': profile.background_impact_reduction,
            'can_progress': can_progress,
            'next_stage': next_stage.value if next_stage else None,
            'growth_categories': {category.value: score for category, score in profile.growth_categories.items()},
            'project_count': len(profile.projects),
            'project_impact_score': profile.project_impact_score,
            'endorsement_count': len(profile.community_endorsements),
            'peer_validation_score': profile.peer_validation_score,
            'recommendations': self._generate_recommendations(profile)
        }
    
    def _generate_recommendations(self, profile: RehabilitationProfile) -> List[str]:
        """Generate personalized recommendations for continued growth"""
        recommendations = []
        
        # Stage-specific recommendations
        if profile.current_stage == RehabilitationStage.ACKNOWLEDGMENT:
            recommendations.append("Share your story and growth journey with the community")
            recommendations.append("Start documenting your learning and development process")
        
        elif profile.current_stage == RehabilitationStage.COMMITMENT:
            recommendations.append("Begin working on your first community project")
            recommendations.append("Seek mentorship from experienced community members")
        
        elif profile.current_stage == RehabilitationStage.ACTION:
            recommendations.append("Focus on completing projects that have measurable impact")
            recommendations.append("Start mentoring others who are beginning their journey")
        
        elif profile.current_stage == RehabilitationStage.CONSISTENCY:
            recommendations.append("Take on leadership roles in community initiatives")
            recommendations.append("Share your expertise through teaching and content creation")
        
        elif profile.current_stage == RehabilitationStage.LEADERSHIP:
            recommendations.append("Mentor multiple people through their rehabilitation journey")
            recommendations.append("Lead large-scale community impact projects")
        
        elif profile.current_stage == RehabilitationStage.MASTERY:
            recommendations.append("Become a platform ambassador and help others succeed")
            recommendations.append("Contribute to platform development and improvement")
        
        # Category-specific recommendations
        for category, score in profile.growth_categories.items():
            if score < 50:
                if category == GrowthCategory.SELF_IMPROVEMENT:
                    recommendations.append("Focus on personal development activities and education")
                elif category == GrowthCategory.COMMUNITY_SERVICE:
                    recommendations.append("Increase your community service involvement")
                elif category == GrowthCategory.MENTORSHIP:
                    recommendations.append("Start mentoring others to share your knowledge")
                elif category == GrowthCategory.INNOVATION:
                    recommendations.append("Work on innovative projects that solve real problems")
        
        return recommendations[:5]  # Limit to 5 recommendations
