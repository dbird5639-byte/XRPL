"""
Biometric Security Configuration
===============================

Configuration settings for the biometric security system including
thresholds, timeouts, and security parameters.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class SecurityLevel(Enum):
    """Security levels for different threat scenarios"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class BiometricType(Enum):
    """Types of biometric authentication supported"""
    FINGERPRINT = "fingerprint"
    FACE = "face"
    VOICE = "voice"
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    STRESS_LEVEL = "stress_level"
    EYE_MOVEMENT = "eye_movement"

@dataclass
class StressThresholds:
    """Thresholds for stress detection across different biometric indicators"""
    # Heart rate thresholds (BPM)
    heart_rate_normal_min: int = 60
    heart_rate_normal_max: int = 100
    heart_rate_stress_min: int = 110
    heart_rate_stress_max: int = 180
    
    # Blood pressure thresholds (mmHg)
    systolic_normal_max: int = 120
    diastolic_normal_max: int = 80
    systolic_stress_min: int = 140
    diastolic_stress_min: int = 90
    
    # Stress hormone levels (cortisol - ng/mL)
    cortisol_normal_max: float = 20.0
    cortisol_stress_min: float = 30.0
    
    # Voice stress indicators
    voice_tremor_threshold: float = 0.15
    voice_pitch_variance_threshold: float = 0.25
    
    # Eye movement stress indicators
    pupil_dilation_threshold: float = 1.2
    blink_rate_stress_threshold: float = 25.0  # blinks per minute
    
    # Behavioral stress indicators
    typing_speed_variance_threshold: float = 0.3
    mouse_movement_jerkiness_threshold: float = 0.4

@dataclass
class FingerprintConfig:
    """Configuration for fingerprint authentication"""
    # Sensor settings
    sensor_resolution: int = 500  # DPI
    image_quality_threshold: float = 0.7
    template_size: int = 1024  # bytes
    
    # Matching thresholds
    false_acceptance_rate: float = 0.001  # 0.1%
    false_rejection_rate: float = 0.01    # 1%
    matching_threshold: float = 0.85
    
    # Security settings
    max_attempts: int = 3
    lockout_duration: int = 300  # seconds
    template_encryption: bool = True
    
    # Hardware requirements
    requires_liveness_detection: bool = True
    anti_spoofing_enabled: bool = True

@dataclass
class PhoneBiometricConfig:
    """Configuration for phone-based biometric authentication"""
    # Face recognition
    face_recognition_confidence: float = 0.9
    face_liveness_threshold: float = 0.8
    
    # Voice recognition
    voice_confidence_threshold: float = 0.85
    voice_phrase_length: int = 3  # words
    
    # Behavioral biometrics
    typing_pattern_confidence: float = 0.8
    swipe_pattern_confidence: float = 0.75
    
    # Security settings
    multi_modal_required: bool = True
    fallback_methods: List[BiometricType] = None
    
    def __post_init__(self):
        if self.fallback_methods is None:
            self.fallback_methods = [BiometricType.FINGERPRINT, BiometricType.VOICE]

@dataclass
class EmergencyProtocolsConfig:
    """Configuration for emergency response protocols"""
    # Contact settings
    emergency_contacts: List[str] = None
    law_enforcement_contact: str = ""
    security_team_contact: str = ""
    
    # Response delays
    immediate_response_delay: int = 0  # seconds
    emergency_contact_delay: int = 30  # seconds
    law_enforcement_delay: int = 120  # seconds
    
    # Data protection
    auto_wipe_sensitive_data: bool = True
    wipe_delay: int = 60  # seconds
    backup_encryption_key: str = ""
    
    # Location tracking
    enable_location_tracking: bool = True
    location_accuracy_threshold: float = 10.0  # meters
    
    def __post_init__(self):
        if self.emergency_contacts is None:
            self.emergency_contacts = []

@dataclass
class BiometricConfig:
    """Main configuration class for the biometric security system"""
    
    # Core settings
    security_level: SecurityLevel = SecurityLevel.HIGH
    enable_stress_detection: bool = True
    enable_fingerprint_auth: bool = True
    enable_phone_biometric: bool = True
    enable_emergency_protocols: bool = True
    
    # Thresholds and limits
    stress_thresholds: StressThresholds = None
    fingerprint_config: FingerprintConfig = None
    phone_biometric_config: PhoneBiometricConfig = None
    emergency_config: EmergencyProtocolsConfig = None
    
    # Monitoring settings
    continuous_monitoring: bool = True
    monitoring_interval: int = 5  # seconds
    data_retention_days: int = 30
    
    # Logging and alerts
    enable_detailed_logging: bool = True
    alert_on_stress_detection: bool = True
    alert_on_failed_attempts: bool = True
    
    # Hardware requirements
    minimum_hardware_version: str = "2.0"
    requires_secure_element: bool = True
    requires_tamper_detection: bool = True
    
    def __post_init__(self):
        if self.stress_thresholds is None:
            self.stress_thresholds = StressThresholds()
        if self.fingerprint_config is None:
            self.fingerprint_config = FingerprintConfig()
        if self.phone_biometric_config is None:
            self.phone_biometric_config = PhoneBiometricConfig()
        if self.emergency_config is None:
            self.emergency_config = EmergencyProtocolsConfig()
    
    def validate_config(self) -> List[str]:
        """Validate the configuration and return any errors"""
        errors = []
        
        # Validate stress thresholds
        if self.stress_thresholds.heart_rate_normal_max >= self.stress_thresholds.heart_rate_stress_min:
            errors.append("Heart rate normal max must be less than stress min")
        
        if self.stress_thresholds.systolic_normal_max >= self.stress_thresholds.systolic_stress_min:
            errors.append("Systolic normal max must be less than stress min")
        
        # Validate fingerprint config
        if self.fingerprint_config.false_acceptance_rate <= 0 or self.fingerprint_config.false_acceptance_rate >= 1:
            errors.append("False acceptance rate must be between 0 and 1")
        
        if self.fingerprint_config.matching_threshold <= 0 or self.fingerprint_config.matching_threshold >= 1:
            errors.append("Matching threshold must be between 0 and 1")
        
        # Validate emergency config
        if self.emergency_config.wipe_delay < 0:
            errors.append("Wipe delay cannot be negative")
        
        return errors
