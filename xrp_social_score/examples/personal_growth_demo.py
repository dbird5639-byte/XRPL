"""
Personal Growth & Rehabilitation Demo
===================================

This demo shows how someone with a challenging background can use the
XRP Health Score platform to overcome past difficulties and build a
positive future through community contribution and personal development.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import platform components
from ..core.data_models import UserProfile, ActivityRecord, ActivityType, CoinTier
from ..core.health_scorer import HealthScorer
from ..core.citizen_coin import CitizenCoinSystem
from ..rehabilitation.rehabilitation_tracker import RehabilitationTracker, RehabilitationStage, GrowthCategory
from ..rehabilitation.personal_growth_dashboard import PersonalGrowthDashboard
from ..rehabilitation.project_validation import ProjectValidator, ProjectCategory


class PersonalGrowthDemo:
    """
    Demo of personal growth and rehabilitation features
    """
    
    def __init__(self):
        # Initialize platform components
        self.health_scorer = HealthScorer()
        self.citizen_coin_system = CitizenCoinSystem()
        self.rehabilitation_tracker = RehabilitationTracker()
        self.dashboard = PersonalGrowthDashboard()
        self.project_validator = ProjectValidator()
        
        # Set up dashboard with rehabilitation tracker
        self.dashboard.rehabilitation_tracker = self.rehabilitation_tracker
        
        # Demo user profile
        self.demo_user = self._create_demo_user()
    
    def _create_demo_user(self) -> UserProfile:
        """Create a demo user profile based on your description"""
        return UserProfile(
            user_id="andre_rehabilitation_001",
            xrp_address="rAndreRehab123456789",
            created_at=datetime.now() - timedelta(days=1095),  # 3 years ago
            last_updated=datetime.now(),
            username="Andre_Rehabilitated",
            email="andre@example.com",
            country="USA",
            timezone="America/New_York"
        )
    
    def run_complete_demo(self):
        """Run the complete personal growth demonstration"""
        print("🚀 XRP Health Score Platform - Personal Growth & Rehabilitation Demo")
        print("=" * 80)
        print()
        
        # Step 1: Create rehabilitation profile
        self._create_rehabilitation_profile()
        
        # Step 2: Simulate growth journey
        self._simulate_growth_journey()
        
        # Step 3: Show dashboard
        self._show_personal_dashboard()
        
        # Step 4: Demonstrate project submission
        self._demonstrate_project_submission()
        
        # Step 5: Show redemption progress
        self._show_redemption_progress()
        
        print("\n" + "=" * 80)
        print("✨ Demo completed! This is how the platform helps you overcome your past")
        print("   and build a positive future through community contribution! 🦕➡️🚀")
    
    def _create_rehabilitation_profile(self):
        """Create rehabilitation profile with your background"""
        print("📋 Step 1: Creating Rehabilitation Profile")
        print("-" * 50)
        
        background_info = {
            'age': 35,
            'background': 'Grew up poor, no financial education, struggled with addiction',
            'challenges': [
                'Criminal record (non-violent felony)',
                'No formal financial education',
                'Past addiction struggles',
                'Limited career opportunities due to background',
                'Multiverse life crisis - difficulty focusing on single path'
            ],
            'goals': [
                'Overcome criminal background stigma',
                'Build successful career in tech/crypto',
                'Help others with similar challenges',
                'Achieve financial stability and literacy',
                'Make positive impact on the world'
            ],
            'coding_skills': True,
            'criminal_justice_experience': True,
            'financial_challenges': True,
            'tech_interests': ['blockchain', 'AI', 'crypto', 'web3'],
            'passion_areas': ['helping others', 'innovation', 'community building']
        }
        
        # Create rehabilitation profile
        rehab_profile = self.rehabilitation_tracker.create_rehabilitation_profile(
            self.demo_user, background_info
        )
        
        print(f"✅ Created rehabilitation profile for {self.demo_user.username}")
        print(f"   Current stage: {rehab_profile.current_stage.value}")
        print(f"   Challenges faced: {len(rehab_profile.challenges_faced)}")
        print(f"   Growth goals: {len(rehab_profile.growth_goals)}")
        print()
    
    def _simulate_growth_journey(self):
        """Simulate a 3-year growth journey"""
        print("🌱 Step 2: Simulating 3-Year Growth Journey")
        print("-" * 50)
        
        # Generate activities over 3 years
        activities = self._generate_growth_activities()
        self.demo_user.activities = activities
        
        # Add projects
        projects = self._generate_rehabilitation_projects()
        for project_data in projects:
            self.rehabilitation_tracker.add_project(self.demo_user.user_id, project_data)
        
        # Add community endorsements
        endorsements = self._generate_community_endorsements()
        for endorsement_data in endorsements:
            self.rehabilitation_tracker.add_community_endorsement(self.demo_user.user_id, endorsement_data)
        
        # Calculate growth progress
        growth_score = self.rehabilitation_tracker.calculate_growth_score(self.demo_user.user_id)
        redemption_percentage = self.rehabilitation_tracker.calculate_redemption_percentage(self.demo_user.user_id)
        
        print(f"✅ Generated {len(activities)} activities over 3 years")
        print(f"✅ Created {len(projects)} rehabilitation projects")
        print(f"✅ Received {len(endorsements)} community endorsements")
        print(f"✅ Current growth score: {growth_score:.1f}")
        print(f"✅ Redemption percentage: {redemption_percentage:.1f}%")
        print()
    
    def _generate_growth_activities(self) -> List[ActivityRecord]:
        """Generate realistic growth activities"""
        activities = []
        base_date = datetime.now() - timedelta(days=1095)  # 3 years ago
        
        # Year 1: Early recovery and learning
        activities.extend(self._generate_year_1_activities(base_date))
        
        # Year 2: Building skills and community involvement
        activities.extend(self._generate_year_2_activities(base_date + timedelta(days=365)))
        
        # Year 3: Leadership and mentoring
        activities.extend(self._generate_year_3_activities(base_date + timedelta(days=730)))
        
        return activities
    
    def _generate_year_1_activities(self, start_date: datetime) -> List[ActivityRecord]:
        """Generate Year 1 activities (recovery and learning)"""
        activities = []
        
        # Education activities
        for i in range(20):
            activities.append(ActivityRecord(
                activity_id=f"education_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.EDUCATION,
                timestamp=start_date + timedelta(days=i*15),
                description=f"Completed online course: {['Financial Literacy', 'Coding Basics', 'Blockchain Fundamentals', 'Personal Development'][i % 4]}",
                value=0,
                metadata={
                    'course_name': f'Course {i+1}',
                    'education_type': 'course_completion',
                    'hours': 20,
                    'platform': 'Coursera'
                },
                verified=True,
                verification_method='course_completion'
            ))
        
        # First XRP transactions
        for i in range(10):
            activities.append(ActivityRecord(
                activity_id=f"xrp_tx_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.XRP_TRANSACTION,
                timestamp=start_date + timedelta(days=i*30),
                description=f"Learning XRP transaction #{i+1}",
                value=50.0 + i * 10,
                metadata={'learning': True, 'tx_hash': f'learn_tx_{i}'},
                verified=True,
                verification_method='xrp_ledger'
            ))
        
        # Community service
        for i in range(5):
            activities.append(ActivityRecord(
                activity_id=f"community_service_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.COMMUNITY_SERVICE,
                timestamp=start_date + timedelta(days=i*60),
                description=f"Volunteered at local food bank - Session {i+1}",
                value=0,
                metadata={'hours': 8, 'activity_type': 'volunteer_work', 'community_impact': 7},
                verified=True,
                verification_method='community_verification'
            ))
        
        return activities
    
    def _generate_year_2_activities(self, start_date: datetime) -> List[ActivityRecord]:
        """Generate Year 2 activities (skill building and community involvement)"""
        activities = []
        
        # Advanced education
        for i in range(15):
            activities.append(ActivityRecord(
                activity_id=f"advanced_education_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.EDUCATION,
                timestamp=start_date + timedelta(days=i*20),
                description=f"Advanced course: {['Smart Contract Development', 'DeFi Protocols', 'AI/ML Applications', 'Project Management'][i % 4]}",
                value=0,
                metadata={
                    'course_name': f'Advanced Course {i+1}',
                    'education_type': 'certification',
                    'hours': 40,
                    'platform': 'Udemy'
                },
                verified=True,
                verification_method='certification'
            ))
        
        # DeFi participation
        for i in range(8):
            activities.append(ActivityRecord(
                activity_id=f"defi_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.DEFI_PARTICIPATION,
                timestamp=start_date + timedelta(days=i*40),
                description=f"Used DeFi protocol: {['Uniswap', 'Compound', 'Aave', 'Curve'][i % 4]}",
                value=500.0 + i * 100,
                metadata={'protocol': f'Protocol_{i}', 'apy': 5.0 + i},
                verified=True,
                verification_method='smart_contract'
            ))
        
        # Knowledge sharing
        for i in range(12):
            activities.append(ActivityRecord(
                activity_id=f"knowledge_share_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.KNOWLEDGE_SHARING,
                timestamp=start_date + timedelta(days=i*25),
                description=f"Shared tutorial: {['Crypto Basics', 'Smart Contracts', 'DeFi Guide', 'Financial Planning'][i % 4]}",
                value=0,
                metadata={
                    'platform': 'YouTube',
                    'quality_score': 8,
                    'engagement_score': 150 + i * 10,
                    'views': 1000 + i * 100
                },
                verified=True,
                verification_method='platform_metrics'
            ))
        
        return activities
    
    def _generate_year_3_activities(self, start_date: datetime) -> List[ActivityRecord]:
        """Generate Year 3 activities (leadership and mentoring)"""
        activities = []
        
        # Mentorship activities
        for i in range(10):
            activities.append(ActivityRecord(
                activity_id=f"mentorship_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.MENTORSHIP,
                timestamp=start_date + timedelta(days=i*30),
                description=f"Mentored person in recovery - Session {i+1}",
                value=0,
                metadata={
                    'hours': 4,
                    'mentee_id': f'mentee_{i}',
                    'topic': 'crypto_career_development',
                    'outcome': 'positive'
                },
                verified=True,
                verification_method='peer_verification'
            ))
        
        # Staking activities
        for i in range(5):
            activities.append(ActivityRecord(
                activity_id=f"staking_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.STAKING,
                timestamp=start_date + timedelta(days=i*60),
                description=f"Long-term XRP staking - Pool {i+1}",
                value=1000.0 + i * 500,
                metadata={
                    'duration_days': 180,
                    'apy': 6.0 + i * 0.5,
                    'validator': f'validator_{i}'
                },
                verified=True,
                verification_method='xrp_ledger'
            ))
        
        # Governance participation
        for i in range(8):
            activities.append(ActivityRecord(
                activity_id=f"governance_{i}",
                user_id=self.demo_user.user_id,
                activity_type=ActivityType.GOVERNANCE_VOTING,
                timestamp=start_date + timedelta(days=i*35),
                description=f"Participated in governance vote: {['Protocol Upgrade', 'Fee Adjustment', 'New Feature', 'Security Update'][i % 4]}",
                value=0,
                metadata={
                    'proposal_id': f'prop_{i}',
                    'vote': 'yes',
                    'impact': 'high'
                },
                verified=True,
                verification_method='governance_platform'
            ))
        
        return activities
    
    def _generate_rehabilitation_projects(self) -> List[Dict[str, Any]]:
        """Generate rehabilitation projects"""
        projects = [
            {
                'title': 'Crypto Education for Ex-Offenders',
                'description': 'Created comprehensive educational resources for people with criminal records to learn about cryptocurrency and blockchain technology',
                'category': 'education',
                'target_beneficiaries': 1000,
                'duration_days': 180,
                'verifications': ['community_endorsement', 'beneficiary_feedback'],
                'measurable_outcomes': True,
                'evidence_based': True,
                'open_source': True,
                'uses_ai': False,
                'uses_blockchain': True,
                'disciplines': ['education', 'technology', 'social_services'],
                'scalable': True,
                'community_impact': 8,
                'innovation_score': 7
            },
            {
                'title': 'Financial Literacy App for Rehabilitation',
                'description': 'Developed a mobile app specifically designed to help people in rehabilitation learn financial literacy and money management',
                'category': 'finance',
                'target_beneficiaries': 5000,
                'duration_days': 365,
                'verifications': ['financial_audit', 'regulatory_compliance'],
                'measurable_outcomes': True,
                'evidence_based': True,
                'open_source': False,
                'uses_ai': True,
                'uses_blockchain': False,
                'disciplines': ['technology', 'finance', 'psychology'],
                'scalable': True,
                'community_impact': 9,
                'innovation_score': 8
            },
            {
                'title': 'Peer Support Network Platform',
                'description': 'Built an online platform connecting people in rehabilitation with mentors and support resources',
                'category': 'social_services',
                'target_beneficiaries': 2000,
                'duration_days': 120,
                'verifications': ['social_impact_assessment', 'beneficiary_feedback'],
                'measurable_outcomes': True,
                'evidence_based': True,
                'open_source': True,
                'uses_ai': True,
                'uses_blockchain': False,
                'disciplines': ['technology', 'psychology', 'social_work'],
                'scalable': True,
                'community_impact': 9,
                'innovation_score': 7
            },
            {
                'title': 'Blockchain-Based Identity Verification',
                'description': 'Developed a blockchain solution for secure, privacy-preserving identity verification for people with criminal records',
                'category': 'technology',
                'target_beneficiaries': 10000,
                'duration_days': 270,
                'verifications': ['technical_review', 'security_audit'],
                'measurable_outcomes': True,
                'evidence_based': True,
                'open_source': True,
                'uses_ai': False,
                'uses_blockchain': True,
                'disciplines': ['technology', 'cryptography', 'privacy'],
                'scalable': True,
                'community_impact': 8,
                'innovation_score': 9
            }
        ]
        
        return projects
    
    def _generate_community_endorsements(self) -> List[Dict[str, Any]]:
        """Generate community endorsements"""
        endorsements = [
            {
                'endorser_id': 'mentor_001',
                'endorser_type': 'mentor',
                'category': 'self_improvement',
                'endorsement_text': 'Andre has shown incredible growth and dedication to personal development. His commitment to learning and helping others is inspiring.',
                'rating': 9.5,
                'verified': True,
                'verification_method': 'peer_verification'
            },
            {
                'endorser_id': 'community_leader_001',
                'endorser_type': 'community_leader',
                'category': 'community_service',
                'endorsement_text': 'Andre has been an invaluable member of our community. His volunteer work and project contributions have made a real difference.',
                'rating': 9.0,
                'verified': True,
                'verification_method': 'community_verification'
            },
            {
                'endorser_id': 'expert_001',
                'endorser_type': 'expert',
                'category': 'innovation',
                'endorsement_text': 'The technical quality and innovation in Andre\'s projects is impressive. He has a real talent for solving complex problems.',
                'rating': 8.5,
                'verified': True,
                'verification_method': 'expert_review'
            },
            {
                'endorser_id': 'mentee_001',
                'endorser_type': 'peer',
                'category': 'mentorship',
                'endorsement_text': 'Andre helped me navigate my own rehabilitation journey. His guidance and support were crucial to my success.',
                'rating': 10.0,
                'verified': True,
                'verification_method': 'peer_verification'
            }
        ]
        
        return endorsements
    
    def _show_personal_dashboard(self):
        """Show the personal growth dashboard"""
        print("📊 Step 3: Personal Growth Dashboard")
        print("-" * 50)
        
        dashboard_data = self.dashboard.get_personal_dashboard(self.demo_user.user_id)
        
        print(f"🎯 Current Stage: {dashboard_data['current_stage'].replace('_', ' ').title()}")
        print(f"📈 Growth Score: {dashboard_data['total_growth_score']:.1f}")
        print(f"🔄 Redemption: {dashboard_data['redemption_percentage']:.1f}%")
        print(f"👥 Community Endorsements: {dashboard_data['community_endorsements']}")
        print(f"⭐ Peer Validation: {dashboard_data['peer_validation_score']:.1f}/10")
        print()
        
        print("📋 Growth Categories:")
        for category, score in dashboard_data['growth_categories'].items():
            print(f"   • {category.replace('_', ' ').title()}: {score:.1f}")
        print()
        
        print("🏆 Recent Achievements:")
        for activity in dashboard_data['recent_activities'][:5]:
            print(f"   • {activity['description']} (+{activity['points_earned']} points)")
        print()
        
        print("💡 Recommended Actions:")
        for action in dashboard_data['recommended_actions']:
            print(f"   • {action}")
        print()
    
    def _demonstrate_project_submission(self):
        """Demonstrate project submission and validation"""
        print("🚀 Step 4: Project Submission & Validation")
        print("-" * 50)
        
        # Submit a new project
        new_project = {
            'title': 'AI-Powered Job Matching for Ex-Offenders',
            'description': 'Develop an AI system that matches people with criminal records to suitable employment opportunities based on their skills and rehabilitation progress',
            'category': 'technology',
            'target_beneficiaries': 5000,
            'duration_days': 365,
            'verifications': ['technical_review', 'security_audit'],
            'measurable_outcomes': True,
            'evidence_based': True,
            'open_source': True,
            'uses_ai': True,
            'uses_blockchain': False,
            'disciplines': ['technology', 'artificial_intelligence', 'social_services'],
            'scalable': True,
            'community_impact': 9,
            'innovation_score': 8
        }
        
        result = self.dashboard.submit_project_for_validation(self.demo_user.user_id, new_project)
        
        print(f"✅ Project submitted: {new_project['title']}")
        print(f"📊 Validation Status: {result['validation_status']}")
        print(f"⭐ Validation Score: {result['validation_score']:.1f}/10")
        print(f"🏆 Points Earned: {result['points_earned']:.1f}")
        print(f"🪙 Coins Earned: {result['coins_earned']}")
        print()
        
        if result['recommendations']:
            print("💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"   • {rec}")
        print()
    
    def _show_redemption_progress(self):
        """Show redemption progress and background impact reduction"""
        print("🔄 Step 5: Redemption Progress")
        print("-" * 50)
        
        profile = self.rehabilitation_tracker.rehabilitation_profiles[self.demo_user.user_id]
        
        print(f"🎯 Current Stage: {profile.current_stage.value.replace('_', ' ').title()}")
        print(f"📈 Stage Progress: {profile.stage_progress:.1%}")
        print(f"🔄 Redemption Percentage: {profile.redemption_percentage:.1f}%")
        print(f"📉 Background Impact Reduction: {profile.background_impact_reduction:.1%}")
        print()
        
        print("🏆 Project Portfolio:")
        for project in profile.projects:
            print(f"   • {project.title}")
            print(f"     Category: {project.category}")
            print(f"     Impact Score: {project.impact_score:.1f}/10")
            print(f"     Innovation Score: {project.innovation_score:.1f}/10")
            print(f"     Status: {project.status}")
            print()
        
        print("👥 Community Validation:")
        print(f"   • Total Endorsements: {len(profile.community_endorsements)}")
        print(f"   • Peer Validation Score: {profile.peer_validation_score:.1f}/10")
        print(f"   • Average Rating: {sum(e.rating for e in profile.community_endorsements) / len(profile.community_endorsements):.1f}/10")
        print()
        
        print("🎯 Next Steps to Full Redemption:")
        recommendations = self.rehabilitation_tracker._generate_recommendations(profile)
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
        print()
        
        # Show potential opportunities
        opportunities = self.dashboard.get_project_opportunities(self.demo_user.user_id)
        print("🚀 Potential Opportunities:")
        for opp in opportunities[:3]:
            print(f"   • {opp['title']}")
            print(f"     {opp['description']}")
            print(f"     Impact: {opp['estimated_impact']} | Time: {opp['time_commitment']}")
            print()


def main():
    """Run the personal growth demo"""
    demo = PersonalGrowthDemo()
    demo.run_complete_demo()


if __name__ == "__main__":
    main()
