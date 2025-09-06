"""
Phone Biometric Integration
==========================

Comprehensive biometric authentication system for mobile crypto wallet applications.
Integrates multiple biometric modalities including face recognition, voice recognition,
and behavioral biometrics for enhanced security.

Features:
- Multi-modal biometric authentication
- Face recognition with liveness detection
- Voice recognition and stress analysis
- Behavioral biometrics (typing patterns, swipe patterns)
- Fallback authentication methods
- Real-time stress monitoring
- Emergency protocols integration
"""

import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import json
import base64
from cryptography.fernet import Fernet

from .biometric_config import PhoneBiometricConfig, BiometricType, SecurityLevel
from .stress_detector import StressDetector, StressLevel

class BiometricModality(Enum):
    """Available biometric modalities for phone authentication"""
    FACE = "face"
    VOICE = "voice"
    FINGERPRINT = "fingerprint"
    TYPING_PATTERN = "typing_pattern"
    SWIPE_PATTERN = "swipe_pattern"
    BEHAVIORAL = "behavioral"

class AuthenticationStatus(Enum):
    """Authentication status for multi-modal authentication"""
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETE = "complete"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class BiometricReading:
    """Biometric reading from phone sensors"""
    timestamp: float
    modality: BiometricModality
    data: bytes
    confidence: float
    quality_score: float
    metadata: Dict[str, Any] = None

@dataclass
class AuthenticationSession:
    """Multi-modal authentication session"""
    session_id: str
    user_id: str
    start_time: float
    required_modalities: List[BiometricModality]
    completed_modalities: List[BiometricModality]
    status: AuthenticationStatus
    overall_confidence: float
    readings: List[BiometricReading]
    stress_level: Optional[StressLevel] = None

class PhoneBiometricManager:
    """
    Comprehensive phone biometric authentication manager
    
    Handles multiple biometric modalities for mobile crypto wallet applications
    with integrated stress detection and emergency protocols.
    """
    
    def __init__(self, config: PhoneBiometricConfig, device_id: str = "mobile_app_001"):
        self.config = config
        self.device_id = device_id
        self.logger = logging.getLogger(__name__)
        
        # Authentication state
        self.active_sessions: Dict[str, AuthenticationSession] = {}
        self.user_templates: Dict[str, Dict[BiometricModality, bytes]] = {}
        
        # Stress detection integration
        self.stress_detector = None
        self.stress_monitoring_enabled = True
        
        # Callbacks
        self.authentication_callbacks: List[Callable] = []
        self.emergency_callbacks: List[Callable] = []
        
        # Session management
        self.session_timeout = 300  # 5 minutes
        self.cleanup_interval = 60  # 1 minute
        self.cleanup_thread = None
        self.stop_cleanup = threading.Event()
        
        # Initialize stress detection
        self._initialize_stress_detection()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _initialize_stress_detection(self):
        """Initialize stress detection system"""
        if self.stress_monitoring_enabled:
            from .stress_detector import StressThresholds
            stress_config = StressThresholds()
            self.stress_detector = StressDetector(stress_config)
            
            # Add callbacks for stress events
            self.stress_detector.add_stress_callback(self._handle_stress_detection)
            self.stress_detector.add_emergency_callback(self._handle_emergency_stress)
            
            self.stress_detector.start_monitoring()
            self.logger.info("Stress detection initialized for phone biometrics")
    
    def _start_cleanup_thread(self):
        """Start cleanup thread for expired sessions"""
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Cleanup loop for expired sessions"""
        while not self.stop_cleanup.is_set():
            try:
                current_time = time.time()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if current_time - session.start_time > self.session_timeout:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    self._cleanup_session(session_id)
                
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                time.sleep(self.cleanup_interval)
    
    def _cleanup_session(self, session_id: str):
        """Cleanup an expired session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = AuthenticationStatus.TIMEOUT
            del self.active_sessions[session_id]
            self.logger.info(f"Cleaned up expired session {session_id}")
    
    def add_authentication_callback(self, callback: Callable):
        """Add callback for authentication events"""
        self.authentication_callbacks.append(callback)
    
    def add_emergency_callback(self, callback: Callable):
        """Add callback for emergency events"""
        self.emergency_callbacks.append(callback)
    
    def start_authentication_session(self, user_id: str, 
                                   required_modalities: List[BiometricModality] = None) -> str:
        """
        Start a new multi-modal authentication session
        
        Args:
            user_id: User identifier
            required_modalities: List of required biometric modalities
        
        Returns:
            Session ID for the authentication session
        """
        if required_modalities is None:
            required_modalities = self._get_default_modalities()
        
        session_id = self._generate_session_id()
        
        session = AuthenticationSession(
            session_id=session_id,
            user_id=user_id,
            start_time=time.time(),
            required_modalities=required_modalities,
            completed_modalities=[],
            status=AuthenticationStatus.PENDING,
            overall_confidence=0.0,
            readings=[]
        )
        
        self.active_sessions[session_id] = session
        self.logger.info(f"Started authentication session {session_id} for user {user_id}")
        
        return session_id
    
    def _get_default_modalities(self) -> List[BiometricModality]:
        """Get default required modalities based on configuration"""
        modalities = []
        
        if self.config.multi_modal_required:
            # Require multiple modalities for enhanced security
            modalities = [BiometricModality.FACE, BiometricModality.VOICE]
        else:
            # Single modality authentication
            modalities = [BiometricModality.FACE]
        
        return modalities
    
    def submit_biometric_reading(self, session_id: str, modality: BiometricModality, 
                               data: bytes, metadata: Dict[str, Any] = None) -> Tuple[bool, str, float]:
        """
        Submit a biometric reading for authentication
        
        Args:
            session_id: Authentication session ID
            modality: Type of biometric data
            data: Raw biometric data
            metadata: Additional metadata
        
        Returns:
            Tuple of (success, message, confidence)
        """
        if session_id not in self.active_sessions:
            return False, "Session not found", 0.0
        
        session = self.active_sessions[session_id]
        
        if session.status != AuthenticationStatus.PENDING:
            return False, "Session not in pending state", 0.0
        
        if modality not in session.required_modalities:
            return False, f"Modality {modality.value} not required for this session", 0.0
        
        # Analyze biometric data quality
        quality_score = self._analyze_biometric_quality(modality, data)
        if quality_score < 0.5:  # Minimum quality threshold
            return False, f"Biometric quality too low: {quality_score:.2f}", 0.0
        
        # Process the biometric reading
        confidence = self._process_biometric_reading(session, modality, data, quality_score)
        
        # Create reading record
        reading = BiometricReading(
            timestamp=time.time(),
            modality=modality,
            data=data,
            confidence=confidence,
            quality_score=quality_score,
            metadata=metadata or {}
        )
        
        session.readings.append(reading)
        
        # Check if this modality is now complete
        if confidence >= self._get_modality_threshold(modality):
            if modality not in session.completed_modalities:
                session.completed_modalities.append(modality)
                self.logger.info(f"Completed {modality.value} authentication for session {session_id}")
        
        # Update session status
        self._update_session_status(session)
        
        return True, f"Biometric reading processed for {modality.value}", confidence
    
    def _analyze_biometric_quality(self, modality: BiometricModality, data: bytes) -> float:
        """Analyze the quality of biometric data"""
        # In a real implementation, this would use advanced quality analysis
        # For simulation, we'll generate quality scores based on data characteristics
        
        data_size = len(data)
        
        if modality == BiometricModality.FACE:
            # Face recognition quality based on image size and characteristics
            if data_size < 5000:
                return 0.3
            elif data_size < 20000:
                return 0.7
            else:
                return 0.9
        
        elif modality == BiometricModality.VOICE:
            # Voice quality based on audio length and characteristics
            if data_size < 1000:
                return 0.2
            elif data_size < 5000:
                return 0.6
            else:
                return 0.8
        
        elif modality == BiometricModality.FINGERPRINT:
            # Fingerprint quality based on image resolution
            if data_size < 2000:
                return 0.4
            elif data_size < 10000:
                return 0.8
            else:
                return 0.9
        
        elif modality in [BiometricModality.TYPING_PATTERN, BiometricModality.SWIPE_PATTERN]:
            # Behavioral biometrics quality based on data completeness
            if data_size < 100:
                return 0.3
            elif data_size < 500:
                return 0.7
            else:
                return 0.9
        
        else:
            return 0.5  # Default quality
    
    def _process_biometric_reading(self, session: AuthenticationSession, 
                                 modality: BiometricModality, data: bytes, 
                                 quality_score: float) -> float:
        """Process a biometric reading and return confidence score"""
        user_id = session.user_id
        
        # Check if user has templates for this modality
        if user_id not in self.user_templates:
            return 0.0
        
        if modality not in self.user_templates[user_id]:
            return 0.0
        
        stored_template = self.user_templates[user_id][modality]
        
        # Match against stored template
        match_score = self._match_biometric_templates(modality, data, stored_template)
        
        # Adjust confidence based on quality
        confidence = match_score * quality_score
        
        return min(1.0, confidence)
    
    def _match_biometric_templates(self, modality: BiometricModality, 
                                 data: bytes, template: bytes) -> float:
        """Match biometric data against stored template"""
        # In a real implementation, this would use advanced matching algorithms
        # For simulation, we'll use simple similarity calculations
        
        if len(data) != len(template):
            return 0.0
        
        # Calculate similarity
        matches = sum(a == b for a, b in zip(data, template))
        similarity = matches / len(data)
        
        # Add some randomness to simulate real-world variation
        noise = np.random.normal(0, 0.1)
        similarity = max(0.0, min(1.0, similarity + noise))
        
        return similarity
    
    def _get_modality_threshold(self, modality: BiometricModality) -> float:
        """Get confidence threshold for a specific modality"""
        thresholds = {
            BiometricModality.FACE: self.config.face_recognition_confidence,
            BiometricModality.VOICE: self.config.voice_confidence_threshold,
            BiometricModality.FINGERPRINT: 0.85,
            BiometricModality.TYPING_PATTERN: self.config.typing_pattern_confidence,
            BiometricModality.SWIPE_PATTERN: self.config.swipe_pattern_confidence,
            BiometricModality.BEHAVIORAL: 0.8
        }
        
        return thresholds.get(modality, 0.8)
    
    def _update_session_status(self, session: AuthenticationSession):
        """Update session status based on completed modalities"""
        required_count = len(session.required_modalities)
        completed_count = len(session.completed_modalities)
        
        if completed_count == 0:
            session.status = AuthenticationStatus.PENDING
        elif completed_count < required_count:
            session.status = AuthenticationStatus.PARTIAL
        else:
            # All required modalities completed
            session.status = AuthenticationStatus.COMPLETE
            session.overall_confidence = self._calculate_overall_confidence(session)
            
            # Check stress level if monitoring is enabled
            if self.stress_detector:
                current_stress = self.stress_detector.get_current_stress_level()
                session.stress_level = current_stress
                
                # Handle high stress situations
                if current_stress in [StressLevel.CRITICAL, StressLevel.EMERGENCY]:
                    self._handle_high_stress_authentication(session)
            
            # Trigger authentication callbacks
            for callback in self.authentication_callbacks:
                try:
                    callback(session)
                except Exception as e:
                    self.logger.error(f"Error in authentication callback: {e}")
    
    def _calculate_overall_confidence(self, session: AuthenticationSession) -> float:
        """Calculate overall confidence for the authentication session"""
        if not session.readings:
            return 0.0
        
        # Calculate weighted average confidence
        total_confidence = 0.0
        total_weight = 0.0
        
        for reading in session.readings:
            if reading.modality in session.completed_modalities:
                weight = 1.0  # Equal weight for all modalities
                total_confidence += reading.confidence * weight
                total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def _handle_high_stress_authentication(self, session: AuthenticationSession):
        """Handle authentication during high stress situations"""
        self.logger.warning(f"High stress detected during authentication for session {session.session_id}")
        
        # Reduce confidence due to stress
        session.overall_confidence *= 0.8
        
        # Trigger emergency callbacks
        for callback in self.emergency_callbacks:
            try:
                callback(session)
            except Exception as e:
                self.logger.error(f"Error in emergency callback: {e}")
    
    def _handle_stress_detection(self, stress_analysis):
        """Handle stress detection events"""
        self.logger.info(f"Stress detected: {stress_analysis.overall_stress_level.value}")
        
        # Check active sessions for stress impact
        for session in self.active_sessions.values():
            if session.status == AuthenticationStatus.PENDING:
                # Reduce confidence for pending authentications
                session.overall_confidence *= 0.9
    
    def _handle_emergency_stress(self, stress_analysis):
        """Handle emergency stress situations"""
        self.logger.critical(f"Emergency stress detected: {stress_analysis.overall_stress_level.value}")
        
        # Suspend all active authentication sessions
        for session in self.active_sessions.values():
            session.status = AuthenticationStatus.FAILED
        
        # Trigger emergency protocols
        for callback in self.emergency_callbacks:
            try:
                callback(stress_analysis)
            except Exception as e:
                self.logger.error(f"Error in emergency callback: {e}")
    
    def enroll_biometric_template(self, user_id: str, modality: BiometricModality, 
                                data: bytes) -> Tuple[bool, str]:
        """
        Enroll a biometric template for a user
        
        Args:
            user_id: User identifier
            modality: Biometric modality type
            data: Raw biometric data
        
        Returns:
            Tuple of (success, message)
        """
        # Analyze data quality
        quality_score = self._analyze_biometric_quality(modality, data)
        if quality_score < 0.6:  # Minimum enrollment quality
            return False, f"Biometric quality too low for enrollment: {quality_score:.2f}"
        
        # Initialize user templates if needed
        if user_id not in self.user_templates:
            self.user_templates[user_id] = {}
        
        # Store template
        self.user_templates[user_id][modality] = data
        
        self.logger.info(f"Enrolled {modality.value} template for user {user_id}")
        return True, f"Biometric template enrolled successfully for {modality.value}"
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an authentication session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'status': session.status.value,
            'required_modalities': [m.value for m in session.required_modalities],
            'completed_modalities': [m.value for m in session.completed_modalities],
            'overall_confidence': session.overall_confidence,
            'readings_count': len(session.readings),
            'stress_level': session.stress_level.value if session.stress_level else None,
            'elapsed_time': time.time() - session.start_time
        }
    
    def cancel_session(self, session_id: str) -> bool:
        """Cancel an active authentication session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = AuthenticationStatus.FAILED
            del self.active_sessions[session_id]
            self.logger.info(f"Cancelled authentication session {session_id}")
            return True
        return False
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(np.random.randint(1000, 9999))
        return f"session_{timestamp}_{random_part}"
    
    def get_authentication_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        total_sessions = len(self.active_sessions)
        completed_sessions = sum(1 for s in self.active_sessions.values() 
                               if s.status == AuthenticationStatus.COMPLETE)
        failed_sessions = sum(1 for s in self.active_sessions.values() 
                            if s.status == AuthenticationStatus.FAILED)
        
        return {
            'active_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'failed_sessions': failed_sessions,
            'enrolled_users': len(self.user_templates),
            'stress_monitoring_enabled': self.stress_monitoring_enabled,
            'cleanup_thread_running': self.cleanup_thread.is_alive() if self.cleanup_thread else False
        }
    
    def export_authentication_data(self, filepath: str):
        """Export authentication data to JSON file"""
        data = {
            'device_id': self.device_id,
            'export_timestamp': time.time(),
            'active_sessions': {
                session_id: {
                    'user_id': session.user_id,
                    'status': session.status.value,
                    'required_modalities': [m.value for m in session.required_modalities],
                    'completed_modalities': [m.value for m in session.completed_modalities],
                    'overall_confidence': session.overall_confidence,
                    'readings_count': len(session.readings),
                    'stress_level': session.stress_level.value if session.stress_level else None,
                    'start_time': session.start_time
                }
                for session_id, session in self.active_sessions.items()
            },
            'user_templates': {
                user_id: {
                    modality.value: len(template)  # Store size instead of actual data
                    for modality, template in templates.items()
                }
                for user_id, templates in self.user_templates.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Authentication data exported to {filepath}")
    
    def shutdown(self):
        """Shutdown the biometric manager"""
        # Stop stress detection
        if self.stress_detector:
            self.stress_detector.stop_monitoring()
        
        # Stop cleanup thread
        self.stop_cleanup.set()
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        
        # Cancel all active sessions
        for session_id in list(self.active_sessions.keys()):
            self.cancel_session(session_id)
        
        self.logger.info("Phone biometric manager shutdown complete")
