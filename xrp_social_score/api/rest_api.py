"""
REST API for XRP Health Score Platform
=====================================

This module provides comprehensive REST API endpoints for the health score platform,
enabling third-party integrations and mobile/web applications.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging

from ..core.health_scorer import HealthScorer
from ..core.citizen_coin import CitizenCoinSystem
from ..blockchain.xrp_integration import XRPLedgerIntegration
from ..gamification.achievement_system import AchievementSystem
from ..core.data_models import UserProfile, ActivityRecord, ActivityType, CoinTier


class HealthScoreAPI:
    """
    REST API server for the XRP Health Score Platform
    """
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize core systems
        self.health_scorer = HealthScorer()
        self.citizen_coin_system = CitizenCoinSystem()
        self.xrp_integration = XRPLedgerIntegration()
        self.achievement_system = AchievementSystem()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all API routes"""
        
        # Health and status endpoints
        self.app.route('/health', methods=['GET'])(self.health_check)
        self.app.route('/status', methods=['GET'])(self.status)
        
        # User management endpoints
        self.app.route('/users', methods=['POST'])(self.create_user)
        self.app.route('/users/<user_id>', methods=['GET'])(self.get_user)
        self.app.route('/users/<user_id>', methods=['PUT'])(self.update_user)
        self.app.route('/users/<user_id>/profile', methods=['GET'])(self.get_user_profile)
        
        # Health score endpoints
        self.app.route('/users/<user_id>/health-score', methods=['GET'])(self.get_health_score)
        self.app.route('/users/<user_id>/health-score/history', methods=['GET'])(self.get_health_score_history)
        self.app.route('/users/<user_id>/health-score/compare', methods=['POST'])(self.compare_health_scores)
        
        # Activity endpoints
        self.app.route('/users/<user_id>/activities', methods=['GET'])(self.get_user_activities)
        self.app.route('/users/<user_id>/activities', methods=['POST'])(self.add_activity)
        self.app.route('/users/<user_id>/activities/<activity_id>', methods=['GET'])(self.get_activity)
        self.app.route('/users/<user_id>/activities/<activity_id>', methods=['PUT'])(self.update_activity)
        
        # Citizen Coin endpoints
        self.app.route('/users/<user_id>/citizen-coins', methods=['GET'])(self.get_citizen_coins)
        self.app.route('/users/<user_id>/citizen-coins/transfer', methods=['POST'])(self.transfer_citizen_coins)
        self.app.route('/users/<user_id>/citizen-coins/convert', methods=['POST'])(self.convert_citizen_coins)
        self.app.route('/users/<user_id>/citizen-coins/history', methods=['GET'])(self.get_coin_history)
        
        # Blockchain integration endpoints
        self.app.route('/users/<user_id>/xrp/transactions', methods=['GET'])(self.get_xrp_transactions)
        self.app.route('/users/<user_id>/xrp/staking', methods=['GET'])(self.get_xrp_staking)
        self.app.route('/users/<user_id>/xrp/sync', methods=['POST'])(self.sync_xrp_activities)
        
        # Achievement endpoints
        self.app.route('/users/<user_id>/achievements', methods=['GET'])(self.get_user_achievements)
        self.app.route('/users/<user_id>/achievements/<achievement_id>', methods=['GET'])(self.get_achievement)
        self.app.route('/users/<user_id>/achievements/recommendations', methods=['GET'])(self.get_achievement_recommendations)
        
        # Community endpoints
        self.app.route('/community/leaderboard', methods=['GET'])(self.get_leaderboard)
        self.app.route('/community/challenges', methods=['GET'])(self.get_community_challenges)
        self.app.route('/community/challenges/<challenge_id>/join', methods=['POST'])(self.join_challenge)
        
        # Analytics endpoints
        self.app.route('/analytics/global-stats', methods=['GET'])(self.get_global_stats)
        self.app.route('/analytics/category-breakdown', methods=['GET'])(self.get_category_breakdown)
        self.app.route('/analytics/trends', methods=['GET'])(self.get_trends)
        
        # Web3 endpoints
        self.app.route('/web3/airdrops', methods=['GET'])(self.get_airdrops)
        self.app.route('/web3/airdrops/<airdrop_id>/claim', methods=['POST'])(self.claim_airdrop)
        self.app.route('/web3/farming', methods=['GET'])(self.get_farming_opportunities)
        self.app.route('/web3/mining', methods=['GET'])(self.get_mining_pools)
        self.app.route('/web3/nfts', methods=['GET'])(self.get_nft_collections)
    
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
    
    def status(self):
        """Detailed status endpoint"""
        return jsonify({
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "health_scorer": "operational",
                "citizen_coin_system": "operational",
                "xrp_integration": "operational",
                "achievement_system": "operational"
            },
            "database": "connected",
            "blockchain": "connected"
        })
    
    def create_user(self):
        """Create a new user"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['user_id', 'xrp_address', 'username', 'email']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Create user profile
            user_profile = UserProfile(
                user_id=data['user_id'],
                xrp_address=data['xrp_address'],
                created_at=datetime.now(),
                last_updated=datetime.now(),
                username=data['username'],
                email=data['email'],
                country=data.get('country'),
                timezone=data.get('timezone')
            )
            
            # In a real implementation, save to database
            # self.database.save_user(user_profile)
            
            return jsonify({
                "message": "User created successfully",
                "user_id": user_profile.user_id,
                "created_at": user_profile.created_at.isoformat()
            }), 201
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_user(self, user_id: str):
        """Get user information"""
        try:
            # In a real implementation, fetch from database
            # user_profile = self.database.get_user(user_id)
            
            # Mock user data for demonstration
            user_profile = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            return jsonify(user_profile.to_dict())
            
        except Exception as e:
            self.logger.error(f"Error getting user: {e}")
            return jsonify({"error": "User not found"}), 404
    
    def update_user(self, user_id: str):
        """Update user information"""
        try:
            data = request.get_json()
            
            # In a real implementation, update user in database
            # user_profile = self.database.get_user(user_id)
            # Update fields from data
            # self.database.save_user(user_profile)
            
            return jsonify({"message": "User updated successfully"})
            
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_user_profile(self, user_id: str):
        """Get detailed user profile"""
        try:
            # In a real implementation, fetch from database
            user_profile = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            return jsonify(user_profile.to_dict())
            
        except Exception as e:
            self.logger.error(f"Error getting user profile: {e}")
            return jsonify({"error": "User profile not found"}), 404
    
    def get_health_score(self, user_id: str):
        """Get user's current health score"""
        try:
            # In a real implementation, fetch user profile from database
            user_profile = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            # Calculate health score
            health_score = self.health_scorer.calculate_health_score(user_profile)
            
            return jsonify(health_score.to_dict())
            
        except Exception as e:
            self.logger.error(f"Error getting health score: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_health_score_history(self, user_id: str):
        """Get user's health score history"""
        try:
            # In a real implementation, fetch user profile from database
            user_profile = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            # Get score history
            days = request.args.get('days', 30, type=int)
            history = self.health_scorer.get_score_history(user_profile, days)
            
            return jsonify([score.to_dict() for score in history])
            
        except Exception as e:
            self.logger.error(f"Error getting health score history: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def compare_health_scores(self, user_id: str):
        """Compare user's health score with community"""
        try:
            data = request.get_json()
            community_user_ids = data.get('community_user_ids', [])
            
            # In a real implementation, fetch user profiles from database
            user_profile = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            # Calculate user's health score
            user_health_score = self.health_scorer.calculate_health_score(user_profile)
            
            # Calculate community scores (mock data)
            community_scores = []
            for community_user_id in community_user_ids:
                community_profile = UserProfile(
                    user_id=community_user_id,
                    xrp_address=f"rMockAddress{community_user_id}",
                    created_at=datetime.now() - timedelta(days=30),
                    last_updated=datetime.now(),
                    username=f"user_{community_user_id}",
                    email=f"user{community_user_id}@example.com"
                )
                community_score = self.health_scorer.calculate_health_score(community_profile)
                community_scores.append(community_score)
            
            # Compare scores
            comparison = self.health_scorer.compare_with_community(user_health_score, community_scores)
            
            return jsonify(comparison)
            
        except Exception as e:
            self.logger.error(f"Error comparing health scores: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_user_activities(self, user_id: str):
        """Get user's activities"""
        try:
            # Query parameters
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            activity_type = request.args.get('type')
            
            # In a real implementation, fetch from database
            activities = []  # Mock data
            
            return jsonify({
                "activities": [activity.to_dict() for activity in activities],
                "total": len(activities),
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            self.logger.error(f"Error getting user activities: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def add_activity(self, user_id: str):
        """Add a new activity for a user"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['activity_type', 'description', 'value']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Create activity record
            activity = ActivityRecord(
                activity_id=f"activity_{datetime.now().timestamp()}",
                user_id=user_id,
                activity_type=ActivityType(data['activity_type']),
                timestamp=datetime.now(),
                description=data['description'],
                value=data['value'],
                metadata=data.get('metadata', {}),
                verified=data.get('verified', False),
                verification_method=data.get('verification_method')
            )
            
            # In a real implementation, save to database
            # self.database.save_activity(activity)
            
            # Update achievement progress
            unlocked_achievements = self.achievement_system.update_achievement_progress(user_id, activity)
            
            return jsonify({
                "message": "Activity added successfully",
                "activity_id": activity.activity_id,
                "unlocked_achievements": [achievement.achievement_id for achievement in unlocked_achievements]
            }), 201
            
        except Exception as e:
            self.logger.error(f"Error adding activity: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_citizen_coins(self, user_id: str):
        """Get user's citizen coin holdings"""
        try:
            # In a real implementation, fetch user profile from database
            user_profile = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            # Get coin summary
            coin_summary = self.citizen_coin_system.get_user_coin_summary(user_profile)
            
            return jsonify(coin_summary)
            
        except Exception as e:
            self.logger.error(f"Error getting citizen coins: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def transfer_citizen_coins(self, user_id: str):
        """Transfer citizen coins between users"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['to_user_id', 'amount', 'coin_tier']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # In a real implementation, fetch user profiles from database
            from_user = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            to_user = UserProfile(
                user_id=data['to_user_id'],
                xrp_address="rMockAddress987654321",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="recipient_user",
                email="recipient@example.com"
            )
            
            # Execute transfer
            coin_tier = CoinTier(data['coin_tier'])
            success = self.citizen_coin_system.execute_transfer(
                from_user, to_user, data['amount'], coin_tier
            )
            
            if success:
                return jsonify({"message": "Transfer successful"})
            else:
                return jsonify({"error": "Transfer failed"}), 400
            
        except Exception as e:
            self.logger.error(f"Error transferring citizen coins: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_xrp_transactions(self, user_id: str):
        """Get user's XRP transaction history"""
        try:
            # In a real implementation, fetch user profile from database
            user_profile = UserProfile(
                user_id=user_id,
                xrp_address="rMockAddress123456789",
                created_at=datetime.now() - timedelta(days=30),
                last_updated=datetime.now(),
                username="demo_user",
                email="demo@example.com"
            )
            
            # Get XRP transactions
            transactions = await self.xrp_integration.get_transaction_history(user_profile.xrp_address)
            
            return jsonify([{
                "tx_hash": tx.tx_hash,
                "from_address": tx.from_address,
                "to_address": tx.to_address,
                "amount": tx.amount,
                "timestamp": tx.timestamp.isoformat(),
                "fee": tx.fee
            } for tx in transactions])
            
        except Exception as e:
            self.logger.error(f"Error getting XRP transactions: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_user_achievements(self, user_id: str):
        """Get user's achievements"""
        try:
            achievements = self.achievement_system.get_user_achievements(user_id)
            stats = self.achievement_system.get_achievement_stats(user_id)
            
            return jsonify({
                "achievements": [achievement.to_dict() for achievement in achievements.values()],
                "stats": stats
            })
            
        except Exception as e:
            self.logger.error(f"Error getting user achievements: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_leaderboard(self):
        """Get community leaderboard"""
        try:
            # In a real implementation, fetch from database
            leaderboard = [
                {"user_id": "user1", "username": "crypto_whale", "score": 950.5},
                {"user_id": "user2", "username": "defi_master", "score": 920.3},
                {"user_id": "user3", "username": "community_hero", "score": 890.7}
            ]
            
            return jsonify({"leaderboard": leaderboard})
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_global_stats(self):
        """Get global platform statistics"""
        try:
            stats = {
                "total_users": 10000,
                "total_activities": 500000,
                "total_citizen_coins": 1000000000,
                "average_health_score": 750.5,
                "active_achievements": 50,
                "community_challenges": 12
            }
            
            return jsonify(stats)
            
        except Exception as e:
            self.logger.error(f"Error getting global stats: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the API server"""
        self.app.run(host=host, port=port, debug=debug)


# Example usage
if __name__ == "__main__":
    api = HealthScoreAPI()
    api.run(debug=True)
