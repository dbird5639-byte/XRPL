"""
ATM Security System
==================

Advanced AI-powered security system for crypto ATMs featuring:

1. Multi-Person Detection Camera System
   - Real-time face detection and tracking
   - Multiple person presence monitoring
   - Crowd density analysis

2. Frantic Behavior Detection
   - Movement pattern analysis
   - Gesture recognition
   - Stress indicator detection
   - Threat assessment algorithms

3. Facial Recognition Safety Switch
   - Multi-factor safety trigger system
   - Emergency protocol activation
   - Law enforcement integration

4. Card Edge Electromagnetic Sensor
   - EM field detection around card edges
   - AI-powered signal analysis
   - Statistical visualization rendering

Author: AI Assistant
Version: 1.0.0
"""

from .atm_camera_system import ATMCameraSystem, CameraConfig
from .behavior_detector import BehaviorDetector, BehaviorAnalysis
from .safety_switch import SafetySwitch, SafetyTrigger
from .card_edge_sensor import CardEdgeSensor, EMSignalAnalysis
from .atm_security_manager import ATMSecurityManager

__version__ = "1.0.0"
__all__ = [
    "ATMCameraSystem",
    "CameraConfig",
    "BehaviorDetector", 
    "BehaviorAnalysis",
    "SafetySwitch",
    "SafetyTrigger",
    "CardEdgeSensor",
    "EMSignalAnalysis",
    "ATMSecurityManager"
]
