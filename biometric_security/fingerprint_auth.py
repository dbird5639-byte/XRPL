"""
Fingerprint Authentication System
================================

Advanced fingerprint authentication system for physical crypto cards
with embedded fingerprint sensors. Includes anti-spoofing, liveness
detection, and secure template storage.

Features:
- High-resolution fingerprint capture
- Anti-spoofing protection
- Liveness detection
- Secure template encryption
- Multi-attempt protection
- Hardware security module integration
"""

import hashlib
import hmac
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import threading
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .biometric_config import FingerprintConfig, BiometricType

class AuthenticationResult(Enum):
    """Fingerprint authentication results"""
    SUCCESS = "success"
    FAILED = "failed"
    INSUFFICIENT_QUALITY = "insufficient_quality"
    SPOOF_DETECTED = "spoof_detected"
    LOCKED_OUT = "locked_out"
    SENSOR_ERROR = "sensor_error"
    TEMPLATE_NOT_FOUND = "template_not_found"

class FingerprintQuality(Enum):
    """Fingerprint image quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

@dataclass
class FingerprintTemplate:
    """Encrypted fingerprint template with metadata"""
    template_id: str
    encrypted_data: bytes
    quality_score: float
    created_timestamp: float
    last_used_timestamp: float
    usage_count: int
    device_id: str
    checksum: str

@dataclass
class AuthenticationAttempt:
    """Record of an authentication attempt"""
    timestamp: float
    result: AuthenticationResult
    quality_score: float
    confidence: float
    device_id: str
    location: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = None

class FingerprintAuthenticator:
    """
    Advanced fingerprint authentication system for crypto cards
    
    Provides secure fingerprint-based authentication with anti-spoofing
    protection and hardware security module integration.
    """
    
    def __init__(self, config: FingerprintConfig, device_id: str = "crypto_card_001"):
        self.config = config
        self.device_id = device_id
        self.logger = logging.getLogger(__name__)
        
        # Template storage
        self.templates: Dict[str, FingerprintTemplate] = {}
        self.encryption_key = None
        
        # Authentication state
        self.failed_attempts = 0
        self.last_attempt_time = 0
        self.is_locked = False
        self.lockout_until = 0
        
        # Authentication history
        self.attempt_history = []
        
        # Hardware simulation
        self.sensor_available = True
        self.sensor_calibrated = False
        
        # Anti-spoofing state
        self.spoof_detection_enabled = config.anti_spoofing_enabled
        self.liveness_detection_enabled = config.requires_liveness_detection
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Initialize hardware
        self._initialize_hardware()
    
    def _initialize_encryption(self):
        """Initialize encryption for template storage"""
        # In a real implementation, this would use a hardware security module
        # For simulation, we'll generate a key from device-specific data
        device_seed = f"{self.device_id}_{time.time()}".encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'crypto_card_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(device_seed))
        self.encryption_key = Fernet(key)
        self.logger.info("Encryption initialized for fingerprint templates")
    
    def _initialize_hardware(self):
        """Initialize fingerprint sensor hardware"""
        # Simulate hardware initialization
        self.sensor_available = True
        self.sensor_calibrated = True
        self.logger.info(f"Fingerprint sensor initialized on device {self.device_id}")
    
    def enroll_fingerprint(self, user_id: str, fingerprint_data: bytes, 
                          quality_threshold: float = None) -> Tuple[bool, str]:
        """
        Enroll a new fingerprint template for a user
        
        Args:
            user_id: Unique identifier for the user
            fingerprint_data: Raw fingerprint image data
            quality_threshold: Minimum quality score required (uses config default if None)
        
        Returns:
            Tuple of (success, message)
        """
        if quality_threshold is None:
            quality_threshold = self.config.image_quality_threshold
        
        # Check if user already has a template
        if user_id in self.templates:
            return False, "User already has a fingerprint template enrolled"
        
        # Analyze fingerprint quality
        quality_score = self._analyze_fingerprint_quality(fingerprint_data)
        if quality_score < quality_threshold:
            return False, f"Fingerprint quality insufficient: {quality_score:.2f} < {quality_threshold:.2f}"
        
        # Check for spoofing
        if self.spoof_detection_enabled:
            is_spoof = self._detect_spoofing(fingerprint_data)
            if is_spoof:
                return False, "Spoofing detected in fingerprint image"
        
        # Check liveness
        if self.liveness_detection_enabled:
            is_live = self._detect_liveness(fingerprint_data)
            if not is_live:
                return False, "Liveness detection failed - fingerprint may not be from live finger"
        
        # Create fingerprint template
        template_id = self._generate_template_id(user_id)
        template_data = self._extract_template(fingerprint_data)
        
        # Encrypt template
        encrypted_data = self.encryption_key.encrypt(template_data)
        
        # Create template object
        template = FingerprintTemplate(
            template_id=template_id,
            encrypted_data=encrypted_data,
            quality_score=quality_score,
            created_timestamp=time.time(),
            last_used_timestamp=0,
            usage_count=0,
            device_id=self.device_id,
            checksum=self._calculate_checksum(template_data)
        )
        
        # Store template
        self.templates[user_id] = template
        
        self.logger.info(f"Fingerprint enrolled for user {user_id} with quality {quality_score:.2f}")
        return True, f"Fingerprint enrolled successfully with quality score {quality_score:.2f}"
    
    def authenticate_fingerprint(self, user_id: str, fingerprint_data: bytes) -> Tuple[AuthenticationResult, float, str]:
        """
        Authenticate a user using their fingerprint
        
        Args:
            user_id: User identifier
            fingerprint_data: Raw fingerprint image data
        
        Returns:
            Tuple of (result, confidence, message)
        """
        # Check if device is locked
        if self.is_locked:
            if time.time() < self.lockout_until:
                return AuthenticationResult.LOCKED_OUT, 0.0, "Device is locked due to failed attempts"
            else:
                self._unlock_device()
        
        # Check if user has a template
        if user_id not in self.templates:
            self._record_attempt(AuthenticationResult.TEMPLATE_NOT_FOUND, 0.0, 0.0)
            return AuthenticationResult.TEMPLATE_NOT_FOUND, 0.0, "No fingerprint template found for user"
        
        # Check sensor availability
        if not self.sensor_available:
            self._record_attempt(AuthenticationResult.SENSOR_ERROR, 0.0, 0.0)
            return AuthenticationResult.SENSOR_ERROR, 0.0, "Fingerprint sensor not available"
        
        # Analyze fingerprint quality
        quality_score = self._analyze_fingerprint_quality(fingerprint_data)
        if quality_score < self.config.image_quality_threshold:
            self._record_attempt(AuthenticationResult.INSUFFICIENT_QUALITY, quality_score, 0.0)
            return AuthenticationResult.INSUFFICIENT_QUALITY, quality_score, f"Fingerprint quality too low: {quality_score:.2f}"
        
        # Check for spoofing
        if self.spoof_detection_enabled:
            is_spoof = self._detect_spoofing(fingerprint_data)
            if is_spoof:
                self._record_attempt(AuthenticationResult.SPOOF_DETECTED, quality_score, 0.0)
                return AuthenticationResult.SPOOF_DETECTED, 0.0, "Spoofing detected in fingerprint"
        
        # Check liveness
        if self.liveness_detection_enabled:
            is_live = self._detect_liveness(fingerprint_data)
            if not is_live:
                self._record_attempt(AuthenticationResult.SPOOF_DETECTED, quality_score, 0.0)
                return AuthenticationResult.SPOOF_DETECTED, 0.0, "Liveness detection failed"
        
        # Extract template from current fingerprint
        current_template = self._extract_template(fingerprint_data)
        
        # Get stored template
        stored_template = self.templates[user_id]
        stored_data = self.encryption_key.decrypt(stored_template.encrypted_data)
        
        # Verify template integrity
        if not self._verify_template_integrity(stored_template, stored_data):
            self._record_attempt(AuthenticationResult.SENSOR_ERROR, quality_score, 0.0)
            return AuthenticationResult.SENSOR_ERROR, 0.0, "Template integrity check failed"
        
        # Match templates
        match_score = self._match_templates(current_template, stored_data)
        confidence = match_score
        
        # Determine authentication result
        if match_score >= self.config.matching_threshold:
            # Successful authentication
            self._record_attempt(AuthenticationResult.SUCCESS, quality_score, confidence)
            self._update_template_usage(stored_template)
            self._reset_failed_attempts()
            
            return AuthenticationResult.SUCCESS, confidence, "Authentication successful"
        else:
            # Failed authentication
            self._record_attempt(AuthenticationResult.FAILED, quality_score, confidence)
            self._handle_failed_attempt()
            
            return AuthenticationResult.FAILED, confidence, f"Authentication failed: {match_score:.2f} < {self.config.matching_threshold:.2f}"
    
    def _analyze_fingerprint_quality(self, fingerprint_data: bytes) -> float:
        """Analyze the quality of a fingerprint image"""
        # In a real implementation, this would use advanced image processing
        # For simulation, we'll generate a quality score based on data characteristics
        
        # Simulate quality analysis based on data size and characteristics
        data_size = len(fingerprint_data)
        
        # Base quality from data size (simulating resolution)
        if data_size < 1000:
            base_quality = 0.3
        elif data_size < 5000:
            base_quality = 0.6
        elif data_size < 20000:
            base_quality = 0.8
        else:
            base_quality = 0.9
        
        # Add some randomness to simulate real-world variation
        noise = np.random.normal(0, 0.1)
        quality = max(0.0, min(1.0, base_quality + noise))
        
        return quality
    
    def _detect_spoofing(self, fingerprint_data: bytes) -> bool:
        """Detect if fingerprint data is from a spoofed source"""
        # In a real implementation, this would use advanced anti-spoofing algorithms
        # For simulation, we'll use a simple heuristic based on data characteristics
        
        # Simulate spoofing detection
        # Real spoofing detection would analyze:
        # - Texture patterns
        # - Reflection properties
        # - Electrical conductivity
        # - Temperature patterns
        # - Blood flow patterns
        
        # For simulation, use a small probability of detecting spoofing
        spoof_probability = 0.05  # 5% chance of detecting spoofing
        return np.random.random() < spoof_probability
    
    def _detect_liveness(self, fingerprint_data: bytes) -> bool:
        """Detect if fingerprint is from a live finger"""
        # In a real implementation, this would use liveness detection algorithms
        # For simulation, we'll use a high success rate
        
        # Real liveness detection would analyze:
        # - Pulse detection
        # - Blood flow patterns
        # - Temperature variations
        # - Electrical impedance
        # - Movement patterns
        
        # For simulation, use a high success rate
        liveness_probability = 0.95  # 95% chance of detecting live finger
        return np.random.random() < liveness_probability
    
    def _extract_template(self, fingerprint_data: bytes) -> bytes:
        """Extract fingerprint template from raw image data"""
        # In a real implementation, this would use advanced minutiae extraction
        # For simulation, we'll create a template based on data characteristics
        
        # Simulate template extraction
        template_size = min(self.config.template_size, len(fingerprint_data))
        template = fingerprint_data[:template_size]
        
        # Pad or truncate to exact size
        if len(template) < self.config.template_size:
            template += b'\x00' * (self.config.template_size - len(template))
        else:
            template = template[:self.config.template_size]
        
        return template
    
    def _match_templates(self, template1: bytes, template2: bytes) -> float:
        """Match two fingerprint templates and return similarity score"""
        # In a real implementation, this would use advanced matching algorithms
        # For simulation, we'll use a simple similarity calculation
        
        if len(template1) != len(template2):
            return 0.0
        
        # Calculate similarity using Hamming distance
        matches = sum(a == b for a, b in zip(template1, template2))
        similarity = matches / len(template1)
        
        # Add some randomness to simulate real-world variation
        noise = np.random.normal(0, 0.05)
        similarity = max(0.0, min(1.0, similarity + noise))
        
        return similarity
    
    def _generate_template_id(self, user_id: str) -> str:
        """Generate unique template ID for a user"""
        timestamp = str(int(time.time() * 1000))
        data = f"{user_id}_{timestamp}_{self.device_id}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate checksum for data integrity verification"""
        return hashlib.sha256(data).hexdigest()
    
    def _verify_template_integrity(self, template: FingerprintTemplate, data: bytes) -> bool:
        """Verify template integrity using checksum"""
        calculated_checksum = self._calculate_checksum(data)
        return calculated_checksum == template.checksum
    
    def _record_attempt(self, result: AuthenticationResult, quality_score: float, confidence: float):
        """Record an authentication attempt"""
        attempt = AuthenticationAttempt(
            timestamp=time.time(),
            result=result,
            quality_score=quality_score,
            confidence=confidence,
            device_id=self.device_id
        )
        
        self.attempt_history.append(attempt)
        self.last_attempt_time = attempt.timestamp
        
        # Keep only recent attempts (last 100)
        if len(self.attempt_history) > 100:
            self.attempt_history = self.attempt_history[-100:]
    
    def _handle_failed_attempt(self):
        """Handle a failed authentication attempt"""
        self.failed_attempts += 1
        
        if self.failed_attempts >= self.config.max_attempts:
            self._lock_device()
    
    def _lock_device(self):
        """Lock the device due to too many failed attempts"""
        self.is_locked = True
        self.lockout_until = time.time() + self.config.lockout_duration
        self.logger.warning(f"Device locked for {self.config.lockout_duration} seconds due to failed attempts")
    
    def _unlock_device(self):
        """Unlock the device after lockout period"""
        self.is_locked = False
        self.failed_attempts = 0
        self.logger.info("Device unlocked")
    
    def _reset_failed_attempts(self):
        """Reset failed attempt counter after successful authentication"""
        self.failed_attempts = 0
    
    def _update_template_usage(self, template: FingerprintTemplate):
        """Update template usage statistics"""
        template.last_used_timestamp = time.time()
        template.usage_count += 1
    
    def delete_template(self, user_id: str) -> bool:
        """Delete a user's fingerprint template"""
        if user_id in self.templates:
            del self.templates[user_id]
            self.logger.info(f"Fingerprint template deleted for user {user_id}")
            return True
        return False
    
    def get_template_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a user's fingerprint template"""
        if user_id not in self.templates:
            return None
        
        template = self.templates[user_id]
        return {
            'template_id': template.template_id,
            'quality_score': template.quality_score,
            'created_timestamp': template.created_timestamp,
            'last_used_timestamp': template.last_used_timestamp,
            'usage_count': template.usage_count,
            'device_id': template.device_id
        }
    
    def get_authentication_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        if not self.attempt_history:
            return {
                'total_attempts': 0,
                'successful_attempts': 0,
                'failed_attempts': 0,
                'success_rate': 0.0,
                'average_confidence': 0.0,
                'is_locked': self.is_locked,
                'lockout_remaining': max(0, self.lockout_until - time.time())
            }
        
        total_attempts = len(self.attempt_history)
        successful_attempts = sum(1 for a in self.attempt_history if a.result == AuthenticationResult.SUCCESS)
        failed_attempts = total_attempts - successful_attempts
        success_rate = successful_attempts / total_attempts if total_attempts > 0 else 0.0
        
        successful_confidences = [a.confidence for a in self.attempt_history if a.result == AuthenticationResult.SUCCESS]
        average_confidence = np.mean(successful_confidences) if successful_confidences else 0.0
        
        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': failed_attempts,
            'success_rate': success_rate,
            'average_confidence': average_confidence,
            'is_locked': self.is_locked,
            'lockout_remaining': max(0, self.lockout_until - time.time())
        }
    
    def export_authentication_log(self, filepath: str):
        """Export authentication attempt log to JSON file"""
        log_data = {
            'device_id': self.device_id,
            'export_timestamp': time.time(),
            'attempts': [
                {
                    'timestamp': attempt.timestamp,
                    'result': attempt.result.value,
                    'quality_score': attempt.quality_score,
                    'confidence': attempt.confidence,
                    'device_id': attempt.device_id,
                    'location': attempt.location,
                    'metadata': attempt.metadata
                }
                for attempt in self.attempt_history
            ],
            'templates': {
                user_id: {
                    'template_id': template.template_id,
                    'quality_score': template.quality_score,
                    'created_timestamp': template.created_timestamp,
                    'last_used_timestamp': template.last_used_timestamp,
                    'usage_count': template.usage_count
                }
                for user_id, template in self.templates.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.logger.info(f"Authentication log exported to {filepath}")
    
    def calibrate_sensor(self) -> bool:
        """Calibrate the fingerprint sensor"""
        # Simulate sensor calibration
        self.sensor_calibrated = True
        self.logger.info("Fingerprint sensor calibrated successfully")
        return True
    
    def test_sensor(self) -> Dict[str, Any]:
        """Test the fingerprint sensor functionality"""
        test_results = {
            'sensor_available': self.sensor_available,
            'sensor_calibrated': self.sensor_calibrated,
            'spoof_detection_enabled': self.spoof_detection_enabled,
            'liveness_detection_enabled': self.liveness_detection_enabled,
            'templates_enrolled': len(self.templates),
            'is_locked': self.is_locked,
            'failed_attempts': self.failed_attempts
        }
        
        return test_results
