"""
Personal Growth Dashboard for Rehabilitation
==========================================

This module provides a specialized dashboard interface for users going through
rehabilitation and personal growth, focusing on overcoming past challenges
and building a positive future through community contribution.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json

from ..core.data_models import UserProfile, ActivityType, CoinTier
from .rehabilitation_tracker import RehabilitationProfile, RehabilitationStage, GrowthCategory
from .project_validation import ProjectValidator, ProjectCategory


@dataclass
class GrowthMilestone:
    """Personal growth milestone"""
    milestone_id: str
    title: str
    description: str
    category: GrowthCategory
    target_value: float
    current_value: float
    progress_percentage: float
    completed: bool
    completed_at: Optional[datetime]
    rewards: Dict[CoinTier, int]


@dataclass
class RehabilitationProgress:
    """Comprehensive rehabilitation progress tracking"""
    user_id: str
    current_stage: RehabilitationStage
    stage_progress: float
    total_growth_score: float
    redemption_percentage: float
    background_impact_reduction: float
    
    # Growth metrics
    growth_categories: Dict[GrowthCategory, float]
    recent_activities: List[Dict[str, Any]]
    active_projects: List[Dict[str, Any]]
    completed_projects: List[Dict[str, Any]]
    
    # Community validation
    community_endorsements: int
    peer_validation_score: float
    mentorship_activities: int
    
    # Financial progress
    financial_literacy_score: float
    investment_activities: int
    savings_progress: float
    
    # Next steps
    recommended_actions: List[str]
    upcoming_milestones: List[GrowthMilestone]
    potential_opportunities: List[Dict[str, Any]]


class PersonalGrowthDashboard:
    """
    Specialized dashboard for personal growth and rehabilitation
    """
    
    def __init__(self):
        self.rehabilitation_tracker = None  # Will be injected
        self.project_validator = ProjectValidator()
        self.growth_milestones = self._initialize_growth_milestones()
    
    def _initialize_growth_milestones(self) -> List[GrowthMilestone]:
        """Initialize growth milestones for rehabilitation journey"""
        return [
            # Acknowledgment Stage Milestones
            GrowthMilestone(
                milestone_id="ack_001",
                title="Share Your Story",
                description="Openly share your growth journey and lessons learned",
                category=GrowthCategory.SELF_IMPROVEMENT,
                target_value=1.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 500, CoinTier.SILVER: 5}
            ),
            GrowthMilestone(
                milestone_id="ack_002",
                title="First Community Activity",
                description="Participate in your first community service activity",
                category=GrowthCategory.COMMUNITY_SERVICE,
                target_value=1.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 300, CoinTier.SILVER: 3}
            ),
            
            # Commitment Stage Milestones
            GrowthMilestone(
                milestone_id="com_001",
                title="Complete First Project",
                description="Successfully complete your first community impact project",
                category=GrowthCategory.INNOVATION,
                target_value=1.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 1000, CoinTier.SILVER: 10, CoinTier.GOLD: 1}
            ),
            GrowthMilestone(
                milestone_id="com_002",
                title="Financial Education",
                description="Complete 10 hours of financial literacy education",
                category=GrowthCategory.FINANCIAL_LITERACY,
                target_value=10.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 800, CoinTier.SILVER: 8}
            ),
            
            # Action Stage Milestones
            GrowthMilestone(
                milestone_id="act_001",
                title="Mentor Someone",
                description="Successfully mentor someone through their own growth journey",
                category=GrowthCategory.MENTORSHIP,
                target_value=1.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 1500, CoinTier.SILVER: 15, CoinTier.GOLD: 1}
            ),
            GrowthMilestone(
                milestone_id="act_002",
                title="Tech Innovation",
                description="Create an innovative technology solution for community benefit",
                category=GrowthCategory.INNOVATION,
                target_value=1.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 2000, CoinTier.SILVER: 20, CoinTier.GOLD: 2}
            ),
            
            # Consistency Stage Milestones
            GrowthMilestone(
                milestone_id="con_001",
                title="Consistent Service",
                description="Maintain 6 months of consistent community service",
                category=GrowthCategory.COMMUNITY_SERVICE,
                target_value=180.0,  # 6 months in days
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 3000, CoinTier.SILVER: 30, CoinTier.GOLD: 3}
            ),
            GrowthMilestone(
                milestone_id="con_002",
                title="Knowledge Sharing",
                description="Create and share 20 pieces of educational content",
                category=GrowthCategory.KNOWLEDGE_SHARING,
                target_value=20.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 2500, CoinTier.SILVER: 25, CoinTier.GOLD: 2}
            ),
            
            # Leadership Stage Milestones
            GrowthMilestone(
                milestone_id="lead_001",
                title="Community Leadership",
                description="Lead a community initiative with 50+ participants",
                category=GrowthCategory.LEADERSHIP,
                target_value=50.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 5000, CoinTier.SILVER: 50, CoinTier.GOLD: 5, CoinTier.PLATINUM: 1}
            ),
            GrowthMilestone(
                milestone_id="lead_002",
                title="Platform Ambassador",
                description="Become a platform ambassador and help others succeed",
                category=GrowthCategory.MENTORSHIP,
                target_value=1.0,
                current_value=0.0,
                progress_percentage=0.0,
                completed=False,
                completed_at=None,
                rewards={CoinTier.COPPER: 4000, CoinTier.SILVER: 40, CoinTier.GOLD: 4, CoinTier.PLATINUM: 1}
            )
        ]
    
    def get_personal_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive personal growth dashboard for a user"""
        
        # Get rehabilitation profile
        if not self.rehabilitation_tracker or user_id not in self.rehabilitation_tracker.rehabilitation_profiles:
            return self._create_initial_dashboard(user_id)
        
        profile = self.rehabilitation_tracker.rehabilitation_profiles[user_id]
        
        # Calculate current progress
        growth_score = self.rehabilitation_tracker.calculate_growth_score(user_id)
        redemption_percentage = self.rehabilitation_tracker.calculate_redemption_percentage(user_id)
        
        # Get recent activities
        recent_activities = self._get_recent_activities(profile, 10)
        
        # Get project information
        active_projects = [p for p in profile.projects if p.status in ['planning', 'active']]
        completed_projects = [p for p in profile.projects if p.status == 'completed']
        
        # Calculate community metrics
        community_endorsements = len(profile.community_endorsements)
        peer_validation_score = profile.peer_validation_score
        
        # Calculate financial progress
        financial_activities = [a for a in profile.base_profile.activities 
                              if a.activity_type in [ActivityType.XRP_TRANSACTION, ActivityType.STAKING, ActivityType.DEFI_PARTICIPATION]]
        financial_literacy_score = profile.growth_categories.get(GrowthCategory.FINANCIAL_LITERACY, 0.0)
        
        # Get recommendations
        recommendations = self._generate_personalized_recommendations(profile)
        
        # Get upcoming milestones
        upcoming_milestones = self._get_upcoming_milestones(profile)
        
        # Get potential opportunities
        potential_opportunities = self._get_potential_opportunities(profile)
        
        return {
            'user_id': user_id,
            'dashboard_type': 'personal_growth',
            'last_updated': datetime.now().isoformat(),
            
            # Current Status
            'current_stage': profile.current_stage.value,
            'stage_progress': profile.stage_progress,
            'total_growth_score': growth_score,
            'redemption_percentage': redemption_percentage,
            'background_impact_reduction': profile.background_impact_reduction,
            
            # Growth Metrics
            'growth_categories': {category.value: score for category, score in profile.growth_categories.items()},
            'recent_activities': recent_activities,
            'active_projects': [self._format_project_summary(p) for p in active_projects],
            'completed_projects': [self._format_project_summary(p) for p in completed_projects],
            
            # Community Validation
            'community_endorsements': community_endorsements,
            'peer_validation_score': peer_validation_score,
            'mentorship_activities': len([a for a in profile.base_profile.activities if a.activity_type == ActivityType.MENTORSHIP]),
            
            # Financial Progress
            'financial_literacy_score': financial_literacy_score,
            'investment_activities': len(financial_activities),
            'savings_progress': self._calculate_savings_progress(profile),
            
            # Next Steps
            'recommended_actions': recommendations,
            'upcoming_milestones': [self._format_milestone(m) for m in upcoming_milestones],
            'potential_opportunities': potential_opportunities,
            
            # Visualizations
            'growth_chart_data': self._generate_growth_chart_data(profile),
            'stage_progression_chart': self._generate_stage_progression_chart(profile),
            'category_breakdown_chart': self._generate_category_breakdown_chart(profile)
        }
    
    def _create_initial_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Create initial dashboard for new users"""
        return {
            'user_id': user_id,
            'dashboard_type': 'personal_growth',
            'last_updated': datetime.now().isoformat(),
            'message': 'Welcome to your personal growth journey! Start by creating your rehabilitation profile.',
            'next_steps': [
                'Create your rehabilitation profile',
                'Share your growth story',
                'Set your personal goals',
                'Start your first community activity'
            ]
        }
    
    def _get_recent_activities(self, profile: RehabilitationProfile, limit: int) -> List[Dict[str, Any]]:
        """Get recent activities for the dashboard"""
        activities = sorted(profile.base_profile.activities, key=lambda x: x.timestamp, reverse=True)
        return [self._format_activity(a) for a in activities[:limit]]
    
    def _format_activity(self, activity) -> Dict[str, Any]:
        """Format activity for dashboard display"""
        return {
            'activity_id': activity.activity_id,
            'type': activity.activity_type.value,
            'description': activity.description,
            'value': activity.value,
            'timestamp': activity.timestamp.isoformat(),
            'verified': activity.verified,
            'points_earned': activity.points_earned,
            'coins_earned': {tier.value: amount for tier, amount in activity.coins_earned.items()}
        }
    
    def _format_project_summary(self, project) -> Dict[str, Any]:
        """Format project for dashboard display"""
        return {
            'project_id': project.project_id,
            'title': project.title,
            'description': project.description,
            'category': project.category,
            'status': project.status,
            'impact_score': project.impact_score,
            'innovation_score': project.innovation_score,
            'start_date': project.start_date.isoformat(),
            'end_date': project.end_date.isoformat() if project.end_date else None,
            'verified': project.verified,
            'points_earned': project.points_earned,
            'coins_earned': {tier.value: amount for tier, amount in project.coins_earned.items()}
        }
    
    def _format_milestone(self, milestone: GrowthMilestone) -> Dict[str, Any]:
        """Format milestone for dashboard display"""
        return {
            'milestone_id': milestone.milestone_id,
            'title': milestone.title,
            'description': milestone.description,
            'category': milestone.category.value,
            'target_value': milestone.target_value,
            'current_value': milestone.current_value,
            'progress_percentage': milestone.progress_percentage,
            'completed': milestone.completed,
            'completed_at': milestone.completed_at.isoformat() if milestone.completed_at else None,
            'rewards': {tier.value: amount for tier, amount in milestone.rewards.items()}
        }
    
    def _calculate_savings_progress(self, profile: RehabilitationProfile) -> float:
        """Calculate savings progress based on financial activities"""
        # This would be calculated based on actual financial data
        # For now, return a mock calculation
        financial_activities = [a for a in profile.base_profile.activities 
                              if a.activity_type in [ActivityType.XRP_TRANSACTION, ActivityType.STAKING]]
        
        if not financial_activities:
            return 0.0
        
        # Simple calculation based on activity frequency and value
        total_value = sum(a.value for a in financial_activities)
        activity_count = len(financial_activities)
        
        # Assume target is $10,000 in savings
        target_savings = 10000.0
        return min(100.0, (total_value / target_savings) * 100)
    
    def _generate_personalized_recommendations(self, profile: RehabilitationProfile) -> List[str]:
        """Generate personalized recommendations based on user's profile"""
        recommendations = []
        
        # Stage-specific recommendations
        if profile.current_stage == RehabilitationStage.ACKNOWLEDGMENT:
            recommendations.extend([
                "Share your growth story with the community to inspire others",
                "Start documenting your learning journey and insights",
                "Connect with mentors who have overcome similar challenges"
            ])
        
        elif profile.current_stage == RehabilitationStage.COMMITMENT:
            recommendations.extend([
                "Begin working on your first community impact project",
                "Take a financial literacy course to improve your economic knowledge",
                "Join a coding or blockchain study group to enhance your technical skills"
            ])
        
        elif profile.current_stage == RehabilitationStage.ACTION:
            recommendations.extend([
                "Focus on completing projects that have measurable community impact",
                "Start mentoring someone who is beginning their growth journey",
                "Share your technical knowledge through tutorials or workshops"
            ])
        
        elif profile.current_stage == RehabilitationStage.CONSISTENCY:
            recommendations.extend([
                "Take on leadership roles in community initiatives",
                "Create educational content to help others learn from your experience",
                "Develop partnerships with organizations that align with your values"
            ])
        
        elif profile.current_stage == RehabilitationStage.LEADERSHIP:
            recommendations.extend([
                "Mentor multiple people through their rehabilitation journey",
                "Lead large-scale community impact projects",
                "Become a platform ambassador and help others succeed"
            ])
        
        elif profile.current_stage == RehabilitationStage.MASTERY:
            recommendations.extend([
                "Contribute to platform development and improvement",
                "Share your expertise at conferences and events",
                "Help design new features that benefit the community"
            ])
        
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
                elif category == GrowthCategory.FINANCIAL_LITERACY:
                    recommendations.append("Take courses on financial planning and investment")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_upcoming_milestones(self, profile: RehabilitationProfile) -> List[GrowthMilestone]:
        """Get upcoming milestones for the user"""
        # Filter milestones based on current stage
        stage_milestones = {
            RehabilitationStage.ACKNOWLEDGMENT: ['ack_001', 'ack_002'],
            RehabilitationStage.COMMITMENT: ['com_001', 'com_002'],
            RehabilitationStage.ACTION: ['act_001', 'act_002'],
            RehabilitationStage.CONSISTENCY: ['con_001', 'con_002'],
            RehabilitationStage.LEADERSHIP: ['lead_001', 'lead_002'],
            RehabilitationStage.MASTERY: []
        }
        
        current_milestone_ids = stage_milestones.get(profile.current_stage, [])
        upcoming = [m for m in self.growth_milestones if m.milestone_id in current_milestone_ids and not m.completed]
        
        return upcoming[:3]  # Limit to 3 upcoming milestones
    
    def _get_potential_opportunities(self, profile: RehabilitationProfile) -> List[Dict[str, Any]]:
        """Get potential opportunities for the user"""
        opportunities = []
        
        # Based on user's skills and interests
        if profile.background_info.get('coding_skills'):
            opportunities.extend([
                {
                    'title': 'Open Source Contributor',
                    'description': 'Contribute to open source projects that benefit the community',
                    'category': 'technology',
                    'estimated_impact': 'high',
                    'time_commitment': 'flexible'
                },
                {
                    'title': 'Tech Mentor',
                    'description': 'Mentor others learning to code and develop blockchain skills',
                    'category': 'education',
                    'estimated_impact': 'high',
                    'time_commitment': 'moderate'
                }
            ])
        
        if profile.background_info.get('criminal_justice_experience'):
            opportunities.extend([
                {
                    'title': 'Rehabilitation Advocate',
                    'description': 'Help others navigate the rehabilitation process',
                    'category': 'social_services',
                    'estimated_impact': 'very_high',
                    'time_commitment': 'moderate'
                },
                {
                    'title': 'Policy Advisor',
                    'description': 'Advise on criminal justice reform policies',
                    'category': 'government',
                    'estimated_impact': 'very_high',
                    'time_commitment': 'high'
                }
            ])
        
        # General opportunities
        opportunities.extend([
            {
                'title': 'Community Organizer',
                'description': 'Organize community events and initiatives',
                'category': 'community',
                'estimated_impact': 'high',
                'time_commitment': 'moderate'
            },
            {
                'title': 'Financial Literacy Teacher',
                'description': 'Teach financial literacy to underserved communities',
                'category': 'education',
                'estimated_impact': 'high',
                'time_commitment': 'moderate'
            }
        ])
        
        return opportunities[:5]  # Limit to 5 opportunities
    
    def _generate_growth_chart_data(self, profile: RehabilitationProfile) -> Dict[str, Any]:
        """Generate data for growth chart visualization"""
        # This would typically come from historical data
        # For now, generate mock data
        months = 12
        categories = list(GrowthCategory)
        
        chart_data = {
            'labels': [f'Month {i+1}' for i in range(months)],
            'datasets': []
        }
        
        for category in categories:
            # Generate mock growth data
            values = [profile.growth_categories.get(category, 0) * (i + 1) / months for i in range(months)]
            
            chart_data['datasets'].append({
                'label': category.value.replace('_', ' ').title(),
                'data': values,
                'borderColor': self._get_category_color(category),
                'backgroundColor': self._get_category_color(category, alpha=0.1)
            })
        
        return chart_data
    
    def _generate_stage_progression_chart(self, profile: RehabilitationProfile) -> Dict[str, Any]:
        """Generate data for stage progression chart"""
        stages = list(RehabilitationStage)
        current_stage_index = stages.index(profile.current_stage)
        
        return {
            'labels': [stage.value.replace('_', ' ').title() for stage in stages],
            'datasets': [{
                'label': 'Progress',
                'data': [100 if i < current_stage_index else (profile.stage_progress * 100 if i == current_stage_index else 0) for i in range(len(stages))],
                'backgroundColor': ['#4CAF50' if i < current_stage_index else ('#FFC107' if i == current_stage_index else '#E0E0E0') for i in range(len(stages))]
            }]
        }
    
    def _generate_category_breakdown_chart(self, profile: RehabilitationProfile) -> Dict[str, Any]:
        """Generate data for category breakdown chart"""
        categories = list(GrowthCategory)
        values = [profile.growth_categories.get(category, 0) for category in categories]
        colors = [self._get_category_color(category) for category in categories]
        
        return {
            'labels': [category.value.replace('_', ' ').title() for category in categories],
            'datasets': [{
                'data': values,
                'backgroundColor': colors
            }]
        }
    
    def _get_category_color(self, category: GrowthCategory, alpha: float = 1.0) -> str:
        """Get color for a growth category"""
        colors = {
            GrowthCategory.SELF_IMPROVEMENT: '#2196F3',
            GrowthCategory.COMMUNITY_SERVICE: '#4CAF50',
            GrowthCategory.KNOWLEDGE_SHARING: '#FF9800',
            GrowthCategory.MENTORSHIP: '#9C27B0',
            GrowthCategory.INNOVATION: '#00BCD4',
            GrowthCategory.SOCIAL_IMPACT: '#F44336',
            GrowthCategory.FINANCIAL_LITERACY: '#795548',
            GrowthCategory.EMOTIONAL_INTELLIGENCE: '#607D8B'
        }
        
        base_color = colors.get(category, '#757575')
        if alpha < 1.0:
            # Convert hex to rgba
            hex_color = base_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})'
        
        return base_color
    
    def submit_project_for_validation(self, user_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a project for validation"""
        if not self.rehabilitation_tracker or user_id not in self.rehabilitation_tracker.rehabilitation_profiles:
            return {'error': 'Rehabilitation profile not found'}
        
        # Add project to rehabilitation profile
        project = self.rehabilitation_tracker.add_project(user_id, project_data)
        
        # Validate the project
        validation = self.project_validator.validate_project(project_data, 'system_validator')
        
        # Update project with validation results
        project.impact_score = validation.impact_score
        project.innovation_score = validation.innovation_score
        project.verified = validation.validation_status.value == 'approved'
        project.points_earned = validation.points_earned
        project.coins_earned = validation.coins_earned
        
        return {
            'project_id': project.project_id,
            'validation_status': validation.validation_status.value,
            'validation_score': validation.validation_score,
            'points_earned': validation.points_earned,
            'coins_earned': {tier.value: amount for tier, amount in validation.coins_earned.items()},
            'recommendations': validation.recommendations
        }
    
    def get_project_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get project opportunities tailored to the user"""
        if not self.rehabilitation_tracker or user_id not in self.rehabilitation_tracker.rehabilitation_profiles:
            return []
        
        profile = self.rehabilitation_tracker.rehabilitation_profiles[user_id]
        opportunities = []
        
        # Based on user's background and interests
        if profile.background_info.get('coding_skills'):
            opportunities.extend([
                {
                    'title': 'Blockchain Education Platform',
                    'description': 'Create an educational platform for blockchain and crypto literacy',
                    'category': 'education',
                    'target_beneficiaries': 1000,
                    'estimated_duration': 90,
                    'difficulty': 'medium',
                    'potential_impact': 'high'
                },
                {
                    'title': 'Criminal Justice Reform App',
                    'description': 'Develop an app to help people navigate the criminal justice system',
                    'category': 'criminal_justice',
                    'target_beneficiaries': 5000,
                    'estimated_duration': 180,
                    'difficulty': 'high',
                    'potential_impact': 'very_high'
                }
            ])
        
        if profile.background_info.get('financial_challenges'):
            opportunities.extend([
                {
                    'title': 'Financial Literacy for Ex-Offenders',
                    'description': 'Create financial education resources specifically for people with criminal records',
                    'category': 'finance',
                    'target_beneficiaries': 2000,
                    'estimated_duration': 120,
                    'difficulty': 'medium',
                    'potential_impact': 'high'
                }
            ])
        
        # General opportunities
        opportunities.extend([
            {
                'title': 'Community Resource Directory',
                'description': 'Build a directory of resources for people in rehabilitation',
                'category': 'social_services',
                'target_beneficiaries': 10000,
                'estimated_duration': 60,
                'difficulty': 'low',
                'potential_impact': 'medium'
            },
            {
                'title': 'Mental Health Support Network',
                'description': 'Create a peer support network for mental health and wellness',
                'category': 'mental_health',
                'target_beneficiaries': 3000,
                'estimated_duration': 150,
                'difficulty': 'medium',
                'potential_impact': 'high'
            }
        ])
        
        return opportunities
