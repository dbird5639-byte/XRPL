"""
Core Health Scoring System
=========================

This module contains the core algorithms and data models for the XRP Health Score platform.
It implements a multi-dimensional scoring system that evaluates users across various
categories including financial health, community engagement, blockchain activity,
and social responsibility.
"""

from .health_scorer import HealthScorer, HealthScore
from .citizen_coin import CitizenCoinSystem, CoinTier
from .scoring_categories import ScoringCategory, CategoryWeight
from .data_models import UserProfile, ActivityRecord, ScoreHistory

__all__ = [
    'HealthScorer',
    'HealthScore', 
    'CitizenCoinSystem',
    'CoinTier',
    'ScoringCategory',
    'CategoryWeight',
    'UserProfile',
    'ActivityRecord',
    'ScoreHistory'
]
