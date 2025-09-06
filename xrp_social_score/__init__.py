"""
XRP Health Score Platform
========================

A revolutionary health scoring system built on the XRP Ledger that goes far beyond
traditional credit scoring. This platform integrates blockchain technology, community
incentives, and gamification to create a comprehensive social scoring system.

Key Features:
- Multi-dimensional health scoring algorithm
- Citizen Coin tokenization with tiered rewards
- XRP Ledger integration for all blockchain activities
- Web3 features: staking, farming, airdrops, mining
- Community-driven governance and challenges
- Real-time scoring and analytics
- Cross-platform API and SDK

Modules:
- core: Core scoring algorithms and data models
- blockchain: XRP Ledger integration and smart contracts
- gamification: Achievement system and community features
- api: REST API and SDK for integrations
- dashboard: Web interface for users
- analytics: Advanced analytics and reporting
"""

__version__ = "1.0.0"
__author__ = "XRP Health Platform Team"

from .core.health_scorer import HealthScorer
from .core.citizen_coin import CitizenCoinSystem
from .blockchain.xrp_integration import XRPLedgerIntegration
from .gamification.achievement_system import AchievementSystem

__all__ = [
    'HealthScorer',
    'CitizenCoinSystem', 
    'XRPLedgerIntegration',
    'AchievementSystem'
]
