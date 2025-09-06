"""
Project Validation System for Rehabilitation
==========================================

This module validates and scores rehabilitation projects to ensure they
contribute meaningfully to community impact and personal growth.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import re

from ..core.data_models import CoinTier


class ProjectCategory(Enum):
    """Categories of rehabilitation projects"""
    GOVERNMENT = "government"
    COMMUNITY = "community"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    TECHNOLOGY = "technology"
    ENVIRONMENT = "environment"
    SOCIAL_SERVICES = "social_services"
    CRIMINAL_JUSTICE = "criminal_justice"
    MENTAL_HEALTH = "mental_health"


class ValidationStatus(Enum):
    """Project validation status"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass
class ValidationCriteria:
    """Criteria for project validation"""
    category: ProjectCategory
    min_impact_score: float
    min_innovation_score: float
    required_verification: List[str]
    bonus_factors: List[str]
    max_duration_days: int


@dataclass
class ProjectValidation:
    """Project validation result"""
    project_id: str
    validation_status: ValidationStatus
    validation_score: float
    impact_score: float
    innovation_score: float
    feasibility_score: float
    community_benefit_score: float
    
    # Detailed scoring
    technical_quality: float
    documentation_quality: float
    scalability_potential: float
    sustainability: float
    
    # Validation details
    validator_id: str
    validation_notes: str
    requirements_met: List[str]
    requirements_missing: List[str]
    recommendations: List[str]
    
    # Rewards
    points_earned: float
    coins_earned: Dict[CoinTier, int]
    
    validated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'project_id': self.project_id,
            'validation_status': self.validation_status.value,
            'validation_score': self.validation_score,
            'impact_score': self.impact_score,
            'innovation_score': self.innovation_score,
            'feasibility_score': self.feasibility_score,
            'community_benefit_score': self.community_benefit_score,
            'technical_quality': self.technical_quality,
            'documentation_quality': self.documentation_quality,
            'scalability_potential': self.scalability_potential,
            'sustainability': self.sustainability,
            'validator_id': self.validator_id,
            'validation_notes': self.validation_notes,
            'requirements_met': self.requirements_met,
            'requirements_missing': self.requirements_missing,
            'recommendations': self.recommendations,
            'points_earned': self.points_earned,
            'coins_earned': {tier.value: amount for tier, amount in self.coins_earned.items()},
            'validated_at': self.validated_at.isoformat()
        }


class ProjectValidator:
    """
    Validates and scores rehabilitation projects for community impact
    """
    
    def __init__(self):
        self.validation_criteria = self._initialize_validation_criteria()
        self.validators = {}  # validator_id -> validator_info
        self.validation_history = {}  # project_id -> validation_history
    
    def _initialize_validation_criteria(self) -> Dict[ProjectCategory, ValidationCriteria]:
        """Initialize validation criteria for each project category"""
        return {
            ProjectCategory.GOVERNMENT: ValidationCriteria(
                category=ProjectCategory.GOVERNMENT,
                min_impact_score=7.0,
                min_innovation_score=6.0,
                required_verification=["government_approval", "legal_compliance"],
                bonus_factors=["transparency", "citizen_engagement", "measurable_outcomes"],
                max_duration_days=365
            ),
            ProjectCategory.COMMUNITY: ValidationCriteria(
                category=ProjectCategory.COMMUNITY,
                min_impact_score=6.0,
                min_innovation_score=5.0,
                required_verification=["community_endorsement", "beneficiary_feedback"],
                bonus_factors=["volunteer_participation", "local_support", "sustainability"],
                max_duration_days=180
            ),
            ProjectCategory.HEALTHCARE: ValidationCriteria(
                category=ProjectCategory.HEALTHCARE,
                min_impact_score=8.0,
                min_innovation_score=7.0,
                required_verification=["medical_approval", "safety_compliance"],
                bonus_factors=["evidence_based", "accessibility", "cost_effectiveness"],
                max_duration_days=730
            ),
            ProjectCategory.FINANCE: ValidationCriteria(
                category=ProjectCategory.FINANCE,
                min_impact_score=7.0,
                min_innovation_score=8.0,
                required_verification=["financial_audit", "regulatory_compliance"],
                bonus_factors=["transparency", "security", "user_friendliness"],
                max_duration_days=365
            ),
            ProjectCategory.EDUCATION: ValidationCriteria(
                category=ProjectCategory.EDUCATION,
                min_impact_score=6.0,
                min_innovation_score=6.0,
                required_verification=["educational_approval", "learning_outcomes"],
                bonus_factors=["accessibility", "engagement", "measurable_learning"],
                max_duration_days=180
            ),
            ProjectCategory.TECHNOLOGY: ValidationCriteria(
                category=ProjectCategory.TECHNOLOGY,
                min_impact_score=7.0,
                min_innovation_score=8.0,
                required_verification=["technical_review", "security_audit"],
                bonus_factors=["open_source", "documentation", "scalability"],
                max_duration_days=365
            ),
            ProjectCategory.ENVIRONMENT: ValidationCriteria(
                category=ProjectCategory.ENVIRONMENT,
                min_impact_score=6.0,
                min_innovation_score=6.0,
                required_verification=["environmental_impact_assessment"],
                bonus_factors=["carbon_reduction", "sustainability", "measurable_impact"],
                max_duration_days=365
            ),
            ProjectCategory.SOCIAL_SERVICES: ValidationCriteria(
                category=ProjectCategory.SOCIAL_SERVICES,
                min_impact_score=6.0,
                min_innovation_score=5.0,
                required_verification=["social_impact_assessment", "beneficiary_feedback"],
                bonus_factors=["inclusivity", "accessibility", "long_term_support"],
                max_duration_days=180
            ),
            ProjectCategory.CRIMINAL_JUSTICE: ValidationCriteria(
                category=ProjectCategory.CRIMINAL_JUSTICE,
                min_impact_score=8.0,
                min_innovation_score=7.0,
                required_verification=["legal_approval", "ethical_review"],
                bonus_factors=["rehabilitation_focus", "community_safety", "evidence_based"],
                max_duration_days=365
            ),
            ProjectCategory.MENTAL_HEALTH: ValidationCriteria(
                category=ProjectCategory.MENTAL_HEALTH,
                min_impact_score=7.0,
                min_innovation_score=6.0,
                required_verification=["mental_health_approval", "safety_protocols"],
                bonus_factors=["evidence_based", "accessibility", "stigma_reduction"],
                max_duration_days=365
            )
        }
    
    def validate_project(self, project_data: Dict[str, Any], 
                        validator_id: str) -> ProjectValidation:
        """Validate a rehabilitation project"""
        
        # Extract project information
        project_id = project_data['project_id']
        category = ProjectCategory(project_data['category'])
        criteria = self.validation_criteria[category]
        
        # Calculate individual scores
        impact_score = self._calculate_impact_score(project_data, category)
        innovation_score = self._calculate_innovation_score(project_data, category)
        feasibility_score = self._calculate_feasibility_score(project_data, category)
        community_benefit_score = self._calculate_community_benefit_score(project_data, category)
        
        # Calculate detailed scores
        technical_quality = self._assess_technical_quality(project_data)
        documentation_quality = self._assess_documentation_quality(project_data)
        scalability_potential = self._assess_scalability(project_data)
        sustainability = self._assess_sustainability(project_data)
        
        # Check requirements
        requirements_met, requirements_missing = self._check_requirements(project_data, criteria)
        
        # Calculate overall validation score
        validation_score = self._calculate_validation_score(
            impact_score, innovation_score, feasibility_score, community_benefit_score,
            technical_quality, documentation_quality, scalability_potential, sustainability
        )
        
        # Determine validation status
        validation_status = self._determine_validation_status(
            validation_score, impact_score, innovation_score, requirements_met, criteria
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            project_data, impact_score, innovation_score, feasibility_score,
            requirements_missing, technical_quality, documentation_quality
        )
        
        # Calculate rewards
        points_earned, coins_earned = self._calculate_rewards(
            validation_score, impact_score, innovation_score, category
        )
        
        # Create validation result
        validation = ProjectValidation(
            project_id=project_id,
            validation_status=validation_status,
            validation_score=validation_score,
            impact_score=impact_score,
            innovation_score=innovation_score,
            feasibility_score=feasibility_score,
            community_benefit_score=community_benefit_score,
            technical_quality=technical_quality,
            documentation_quality=documentation_quality,
            scalability_potential=scalability_potential,
            sustainability=sustainability,
            validator_id=validator_id,
            validation_notes=self._generate_validation_notes(project_data, validation_score),
            requirements_met=requirements_met,
            requirements_missing=requirements_missing,
            recommendations=recommendations,
            points_earned=points_earned,
            coins_earned=coins_earned,
            validated_at=datetime.now()
        )
        
        # Store validation history
        if project_id not in self.validation_history:
            self.validation_history[project_id] = []
        self.validation_history[project_id].append(validation)
        
        return validation
    
    def _calculate_impact_score(self, project_data: Dict[str, Any], 
                              category: ProjectCategory) -> float:
        """Calculate impact score for a project"""
        base_score = 0.0
        
        # Beneficiary count impact
        target_beneficiaries = project_data.get('target_beneficiaries', 0)
        if target_beneficiaries > 0:
            # Logarithmic scaling for beneficiary count
            import math
            base_score += min(5.0, math.log10(target_beneficiaries + 1) * 2)
        
        # Duration impact
        duration_days = project_data.get('duration_days', 0)
        if duration_days > 0:
            base_score += min(3.0, duration_days / 30.0)  # Up to 3 points for long-term projects
        
        # Category-specific impact factors
        category_multipliers = {
            ProjectCategory.HEALTHCARE: 1.5,
            ProjectCategory.CRIMINAL_JUSTICE: 1.4,
            ProjectCategory.EDUCATION: 1.3,
            ProjectCategory.SOCIAL_SERVICES: 1.2,
            ProjectCategory.ENVIRONMENT: 1.2,
            ProjectCategory.COMMUNITY: 1.1,
            ProjectCategory.GOVERNMENT: 1.0,
            ProjectCategory.FINANCE: 1.0,
            ProjectCategory.TECHNOLOGY: 0.9,
            ProjectCategory.MENTAL_HEALTH: 1.3
        }
        
        base_score *= category_multipliers.get(category, 1.0)
        
        # Bonus for measurable outcomes
        if project_data.get('measurable_outcomes'):
            base_score += 2.0
        
        # Bonus for evidence-based approach
        if project_data.get('evidence_based'):
            base_score += 1.5
        
        return min(10.0, base_score)
    
    def _calculate_innovation_score(self, project_data: Dict[str, Any], 
                                 category: ProjectCategory) -> float:
        """Calculate innovation score for a project"""
        base_score = 0.0
        
        # Novelty assessment
        novelty = project_data.get('novelty_level', 'low')
        novelty_scores = {'low': 1.0, 'medium': 3.0, 'high': 5.0, 'revolutionary': 7.0}
        base_score += novelty_scores.get(novelty, 1.0)
        
        # Technology integration
        if project_data.get('uses_ai'):
            base_score += 2.0
        if project_data.get('uses_blockchain'):
            base_score += 1.5
        if project_data.get('uses_iot'):
            base_score += 1.0
        
        # Open source contribution
        if project_data.get('open_source'):
            base_score += 1.5
        
        # Cross-disciplinary approach
        disciplines = project_data.get('disciplines', [])
        if len(disciplines) > 1:
            base_score += min(2.0, len(disciplines) * 0.5)
        
        # Scalability potential
        if project_data.get('scalable'):
            base_score += 1.0
        
        return min(10.0, base_score)
    
    def _calculate_feasibility_score(self, project_data: Dict[str, Any], 
                                   category: ProjectCategory) -> float:
        """Calculate feasibility score for a project"""
        base_score = 5.0  # Start with neutral score
        
        # Resource availability
        resources = project_data.get('resources', {})
        if resources.get('funding_secured'):
            base_score += 1.0
        if resources.get('team_assembled'):
            base_score += 1.0
        if resources.get('partnerships_established'):
            base_score += 1.0
        
        # Timeline realism
        duration_days = project_data.get('duration_days', 0)
        complexity = project_data.get('complexity', 'medium')
        complexity_days = {'low': 30, 'medium': 90, 'high': 180, 'very_high': 365}
        expected_duration = complexity_days.get(complexity, 90)
        
        if duration_days <= expected_duration * 1.2:  # Within 20% of expected
            base_score += 1.0
        elif duration_days > expected_duration * 2:  # More than double expected
            base_score -= 1.0
        
        # Risk assessment
        risks = project_data.get('risks', [])
        if len(risks) == 0:
            base_score += 1.0
        elif len(risks) > 5:
            base_score -= 1.0
        
        # Mitigation plans
        if project_data.get('risk_mitigation_plans'):
            base_score += 1.0
        
        return min(10.0, max(0.0, base_score))
    
    def _calculate_community_benefit_score(self, project_data: Dict[str, Any], 
                                        category: ProjectCategory) -> float:
        """Calculate community benefit score for a project"""
        base_score = 0.0
        
        # Direct community impact
        if project_data.get('direct_community_impact'):
            base_score += 3.0
        
        # Inclusivity
        if project_data.get('inclusive_design'):
            base_score += 2.0
        
        # Accessibility
        if project_data.get('accessible'):
            base_score += 1.5
        
        # Local engagement
        if project_data.get('local_community_involvement'):
            base_score += 2.0
        
        # Long-term benefits
        if project_data.get('long_term_sustainability'):
            base_score += 1.5
        
        # Social justice focus
        if project_data.get('social_justice_focus'):
            base_score += 2.0
        
        return min(10.0, base_score)
    
    def _assess_technical_quality(self, project_data: Dict[str, Any]) -> float:
        """Assess technical quality of the project"""
        score = 0.0
        
        # Code quality indicators
        if project_data.get('code_reviewed'):
            score += 2.0
        if project_data.get('tests_written'):
            score += 2.0
        if project_data.get('documentation_complete'):
            score += 1.5
        
        # Architecture quality
        if project_data.get('well_architected'):
            score += 2.0
        if project_data.get('follows_best_practices'):
            score += 1.5
        
        # Security considerations
        if project_data.get('security_audited'):
            score += 2.0
        if project_data.get('privacy_protected'):
            score += 1.0
        
        return min(10.0, score)
    
    def _assess_documentation_quality(self, project_data: Dict[str, Any]) -> float:
        """Assess documentation quality of the project"""
        score = 0.0
        
        # Documentation completeness
        if project_data.get('readme_complete'):
            score += 2.0
        if project_data.get('api_documented'):
            score += 2.0
        if project_data.get('user_guide_available'):
            score += 1.5
        
        # Code documentation
        if project_data.get('code_commented'):
            score += 1.5
        if project_data.get('architecture_documented'):
            score += 1.0
        
        # Accessibility documentation
        if project_data.get('accessibility_documented'):
            score += 1.0
        
        return min(10.0, score)
    
    def _assess_scalability(self, project_data: Dict[str, Any]) -> float:
        """Assess scalability potential of the project"""
        score = 0.0
        
        # Scalability design
        if project_data.get('scalable_architecture'):
            score += 3.0
        if project_data.get('cloud_ready'):
            score += 2.0
        if project_data.get('microservices_design'):
            score += 2.0
        
        # Performance considerations
        if project_data.get('performance_optimized'):
            score += 2.0
        if project_data.get('load_tested'):
            score += 1.0
        
        return min(10.0, score)
    
    def _assess_sustainability(self, project_data: Dict[str, Any]) -> float:
        """Assess sustainability of the project"""
        score = 0.0
        
        # Environmental sustainability
        if project_data.get('environmentally_friendly'):
            score += 2.0
        if project_data.get('carbon_neutral'):
            score += 1.5
        
        # Economic sustainability
        if project_data.get('sustainable_funding_model'):
            score += 2.0
        if project_data.get('cost_effective'):
            score += 1.5
        
        # Social sustainability
        if project_data.get('community_owned'):
            score += 2.0
        if project_data.get('long_term_viable'):
            score += 1.5
        
        return min(10.0, score)
    
    def _check_requirements(self, project_data: Dict[str, Any], 
                          criteria: ValidationCriteria) -> Tuple[List[str], List[str]]:
        """Check if project meets validation requirements"""
        requirements_met = []
        requirements_missing = []
        
        # Check verification requirements
        verifications = project_data.get('verifications', [])
        for required_verification in criteria.required_verification:
            if required_verification in verifications:
                requirements_met.append(f"verification_{required_verification}")
            else:
                requirements_missing.append(f"verification_{required_verification}")
        
        # Check bonus factors
        for bonus_factor in criteria.bonus_factors:
            if project_data.get(bonus_factor):
                requirements_met.append(f"bonus_{bonus_factor}")
        
        return requirements_met, requirements_missing
    
    def _calculate_validation_score(self, impact_score: float, innovation_score: float,
                                 feasibility_score: float, community_benefit_score: float,
                                 technical_quality: float, documentation_quality: float,
                                 scalability_potential: float, sustainability: float) -> float:
        """Calculate overall validation score"""
        # Weighted average of all scores
        weights = {
            'impact': 0.25,
            'innovation': 0.20,
            'feasibility': 0.15,
            'community_benefit': 0.15,
            'technical_quality': 0.10,
            'documentation_quality': 0.05,
            'scalability': 0.05,
            'sustainability': 0.05
        }
        
        total_score = (
            impact_score * weights['impact'] +
            innovation_score * weights['innovation'] +
            feasibility_score * weights['feasibility'] +
            community_benefit_score * weights['community_benefit'] +
            technical_quality * weights['technical_quality'] +
            documentation_quality * weights['documentation_quality'] +
            scalability_potential * weights['scalability'] +
            sustainability * weights['sustainability']
        )
        
        return min(10.0, total_score)
    
    def _determine_validation_status(self, validation_score: float, impact_score: float,
                                   innovation_score: float, requirements_met: List[str],
                                   criteria: ValidationCriteria) -> ValidationStatus:
        """Determine validation status based on scores and requirements"""
        
        # Check minimum score requirements
        if (validation_score >= 7.0 and 
            impact_score >= criteria.min_impact_score and
            innovation_score >= criteria.min_innovation_score and
            len(requirements_met) >= len(criteria.required_verification)):
            return ValidationStatus.APPROVED
        
        # Check if needs revision
        elif (validation_score >= 5.0 and 
              impact_score >= criteria.min_impact_score * 0.7 and
              innovation_score >= criteria.min_innovation_score * 0.7):
            return ValidationStatus.NEEDS_REVISION
        
        # Otherwise reject
        else:
            return ValidationStatus.REJECTED
    
    def _generate_recommendations(self, project_data: Dict[str, Any], 
                                impact_score: float, innovation_score: float,
                                feasibility_score: float, requirements_missing: List[str],
                                technical_quality: float, documentation_quality: float) -> List[str]:
        """Generate recommendations for project improvement"""
        recommendations = []
        
        # Impact recommendations
        if impact_score < 6.0:
            recommendations.append("Increase the scope of beneficiaries or measurable impact")
            recommendations.append("Add specific, measurable outcomes to your project")
        
        # Innovation recommendations
        if innovation_score < 6.0:
            recommendations.append("Consider incorporating new technologies or approaches")
            recommendations.append("Look for ways to make your project more unique or novel")
        
        # Feasibility recommendations
        if feasibility_score < 6.0:
            recommendations.append("Ensure you have adequate resources and realistic timelines")
            recommendations.append("Develop comprehensive risk mitigation plans")
        
        # Technical quality recommendations
        if technical_quality < 6.0:
            recommendations.append("Improve code quality through reviews and testing")
            recommendations.append("Follow industry best practices and standards")
        
        # Documentation recommendations
        if documentation_quality < 6.0:
            recommendations.append("Enhance project documentation and user guides")
            recommendations.append("Provide clear API documentation and examples")
        
        # Requirements recommendations
        for missing in requirements_missing:
            if missing.startswith("verification_"):
                verification_type = missing.replace("verification_", "")
                recommendations.append(f"Obtain {verification_type.replace('_', ' ')} verification")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _calculate_rewards(self, validation_score: float, impact_score: float,
                         innovation_score: float, category: ProjectCategory) -> Tuple[float, Dict[CoinTier, int]]:
        """Calculate rewards for validated project"""
        
        # Base points from validation score
        base_points = validation_score * 10
        
        # Impact bonus
        impact_bonus = impact_score * 2
        
        # Innovation bonus
        innovation_bonus = innovation_score * 1.5
        
        # Category multiplier
        category_multipliers = {
            ProjectCategory.CRIMINAL_JUSTICE: 1.5,
            ProjectCategory.HEALTHCARE: 1.4,
            ProjectCategory.EDUCATION: 1.3,
            ProjectCategory.SOCIAL_SERVICES: 1.2,
            ProjectCategory.ENVIRONMENT: 1.2,
            ProjectCategory.COMMUNITY: 1.1,
            ProjectCategory.GOVERNMENT: 1.0,
            ProjectCategory.FINANCE: 1.0,
            ProjectCategory.TECHNOLOGY: 0.9,
            ProjectCategory.MENTAL_HEALTH: 1.3
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        total_points = (base_points + impact_bonus + innovation_bonus) * multiplier
        
        # Convert points to coins
        coins_earned = {
            CoinTier.COPPER: int(total_points),
            CoinTier.SILVER: int(total_points / 100),
            CoinTier.GOLD: int(total_points / 10000),
            CoinTier.PLATINUM: int(total_points / 1000000),
            CoinTier.DIAMOND: int(total_points / 100000000)
        }
        
        return total_points, coins_earned
    
    def _generate_validation_notes(self, project_data: Dict[str, Any], 
                                 validation_score: float) -> str:
        """Generate validation notes for the project"""
        notes = []
        
        if validation_score >= 8.0:
            notes.append("Excellent project with high impact potential and strong innovation.")
        elif validation_score >= 6.0:
            notes.append("Good project with solid potential, some areas for improvement.")
        elif validation_score >= 4.0:
            notes.append("Project shows promise but needs significant improvements.")
        else:
            notes.append("Project requires major revisions before approval.")
        
        # Add specific feedback
        if project_data.get('target_beneficiaries', 0) > 1000:
            notes.append("Strong potential for widespread impact.")
        
        if project_data.get('uses_ai') or project_data.get('uses_blockchain'):
            notes.append("Innovative use of cutting-edge technologies.")
        
        if project_data.get('open_source'):
            notes.append("Open source approach promotes community collaboration.")
        
        return " ".join(notes)
    
    def get_validation_summary(self, project_id: str) -> Dict[str, Any]:
        """Get validation summary for a project"""
        if project_id not in self.validation_history:
            return {}
        
        validations = self.validation_history[project_id]
        latest_validation = validations[-1]
        
        return {
            'project_id': project_id,
            'validation_count': len(validations),
            'latest_validation': latest_validation.to_dict(),
            'validation_trend': self._calculate_validation_trend(validations),
            'overall_status': latest_validation.validation_status.value
        }
    
    def _calculate_validation_trend(self, validations: List[ProjectValidation]) -> str:
        """Calculate validation trend over time"""
        if len(validations) < 2:
            return "stable"
        
        scores = [v.validation_score for v in validations]
        if scores[-1] > scores[-2]:
            return "improving"
        elif scores[-1] < scores[-2]:
            return "declining"
        else:
            return "stable"
