"""
Dashboard for XRP Health Score Platform
=====================================

This module provides a modern web dashboard for users to track and improve
their health scores, manage citizen coins, and participate in community activities.
"""

from .web_dashboard import WebDashboard
from .mobile_app import MobileApp
from .analytics_dashboard import AnalyticsDashboard

__all__ = [
    'WebDashboard',
    'MobileApp',
    'AnalyticsDashboard'
]
