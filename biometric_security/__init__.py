"""
Biometric Security System for Crypto Wallets
============================================

A comprehensive biometric security system designed to protect crypto wallet users
from physical coercion and theft through:

1. Stress Detection System - Monitors biometric indicators for signs of duress
2. Fingerprint Authentication - Secure biometric locks for physical cards
3. Phone App Integration - Mobile biometric security features
4. Emergency Protocols - Automated responses to detected threats
5. Multi-factor Security - Layered protection mechanisms

This system is designed to work across:
- Physical crypto cards with embedded fingerprint sensors
- Mobile applications with biometric capabilities
- Hardware security modules (HSMs)
- Emergency contact and law enforcement integration

Author: AI Assistant
Version: 1.0.0
"""

from .stress_detector import StressDetector, StressThresholds
from .fingerprint_auth import FingerprintAuthenticator
from .phone_biometric import PhoneBiometricManager
from .security_monitor import SecurityMonitor
from .emergency_protocols import EmergencyProtocols
from .biometric_config import BiometricConfig

__version__ = "1.0.0"
__all__ = [
    "StressDetector",
    "StressThresholds", 
    "FingerprintAuthenticator",
    "PhoneBiometricManager",
    "SecurityMonitor",
    "EmergencyProtocols",
    "BiometricConfig"
]
