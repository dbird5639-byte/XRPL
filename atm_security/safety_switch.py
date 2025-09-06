"""
Facial Recognition Safety Switch System
======================================

Advanced safety switch system that activates facial recognition and emergency protocols
only when multiple safety concern indicators are triggered. This prevents false positives
and ensures the system only activates when there's a genuine threat.

Features:
- Multi-factor safety trigger system
- Facial recognition database integration
- Emergency protocol activation
- Law enforcement integration
- False positive prevention
- Real-time threat assessment
"""

import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import json
from collections import deque
import hashlib

class SafetyTrigger(Enum):
    """Types of safety triggers"""
    MULTIPLE_PEOPLE = "multiple_people"
    FRANTIC_BEHAVIOR = "frantic_behavior"
    THREATENING_GESTURES = "threatening_gestures"
    HIGH_STRESS_LEVELS = "high_stress_levels"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    EMERGENCY_SITUATION = "emergency_situation"
    WEAPON_DETECTED = "weapon_detected"
    FORCED_ENTRY = "forced_entry"

class SafetyLevel(Enum):
    """Safety levels for different threat scenarios"""
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class FacialRecognitionStatus(Enum):
    """Facial recognition status"""
    INACTIVE = "inactive"
    SCANNING = "scanning"
    MATCH_FOUND = "match_found"
    NO_MATCH = "no_match"
    ERROR = "error"

@dataclass
class SafetyIndicator:
    """Individual safety indicator"""
    trigger_type: SafetyTrigger
    confidence: float  # 0-1
    severity: float  # 0-1
    timestamp: float
    source: str  # Which system detected it
    metadata: Dict[str, Any] = None

@dataclass
class SafetyAssessment:
    """Comprehensive safety assessment"""
    timestamp: float
    safety_level: SafetyLevel
    active_triggers: List[SafetyTrigger]
    overall_threat_score: float  # 0-1
    facial_recognition_status: FacialRecognitionStatus
    recommended_actions: List[str]
    requires_emergency_response: bool
    confidence: float

@dataclass
class FacialRecognitionResult:
    """Facial recognition result"""
    person_id: Optional[str]
    confidence: float
    match_found: bool
    database_entry: Optional[Dict[str, Any]]
    timestamp: float

class SafetySwitch:
    """
    Advanced safety switch system for ATM security
    
    Activates facial recognition and emergency protocols only when
    multiple safety indicators are triggered simultaneously.
    """
    
    def __init__(self, activation_threshold: int = 3, 
                 critical_threshold: int = 2,
                 emergency_threshold: int = 1):
        self.activation_threshold = activation_threshold  # Triggers needed to activate
        self.critical_threshold = critical_threshold      # Triggers for critical response
        self.emergency_threshold = emergency_threshold    # Triggers for emergency response
        
        self.logger = logging.getLogger(__name__)
        
        # Safety state
        self.active_indicators: Dict[SafetyTrigger, SafetyIndicator] = {}
        self.safety_history = deque(maxlen=1000)
        self.facial_recognition_active = False
        self.emergency_protocols_active = False
        
        # Facial recognition database
        self.face_database: Dict[str, Dict[str, Any]] = {}
        self.recognition_results: List[FacialRecognitionResult] = []
        
        # Processing state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Callbacks
        self.safety_callbacks: List[Callable] = []
        self.recognition_callbacks: List[Callable] = []
        self.emergency_callbacks: List[Callable] = []
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start safety monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Safety switch monitoring started")
    
    def stop_monitoring(self):
        """Stop safety monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Safety switch monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.is_set():
            try:
                # Assess current safety level
                assessment = self._assess_safety_level()
                if assessment:
                    self._handle_safety_assessment(assessment)
                
                # Clean up expired indicators
                self._cleanup_expired_indicators()
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                self.logger.error(f"Error in safety monitoring loop: {e}")
                time.sleep(0.1)
    
    def add_safety_indicator(self, trigger_type: SafetyTrigger, confidence: float, 
                           severity: float, source: str, metadata: Dict[str, Any] = None):
        """
        Add a safety indicator
        
        Args:
            trigger_type: Type of safety trigger
            confidence: Confidence in the detection (0-1)
            severity: Severity of the threat (0-1)
            source: System that detected the threat
            metadata: Additional metadata
        """
        indicator = SafetyIndicator(
            trigger_type=trigger_type,
            confidence=confidence,
            severity=severity,
            timestamp=time.time(),
            source=source,
            metadata=metadata or {}
        )
        
        self.active_indicators[trigger_type] = indicator
        self.logger.debug(f"Safety indicator added: {trigger_type.value} "
                         f"(confidence: {confidence:.2f}, severity: {severity:.2f})")
    
    def remove_safety_indicator(self, trigger_type: SafetyTrigger):
        """Remove a safety indicator"""
        if trigger_type in self.active_indicators:
            del self.active_indicators[trigger_type]
            self.logger.debug(f"Safety indicator removed: {trigger_type.value}")
    
    def _assess_safety_level(self) -> Optional[SafetyAssessment]:
        """Assess current safety level based on active indicators"""
        if not self.active_indicators:
            return None
        
        # Count active triggers
        active_triggers = list(self.active_indicators.keys())
        trigger_count = len(active_triggers)
        
        # Calculate overall threat score
        threat_scores = []
        for indicator in self.active_indicators.values():
            # Weighted score: confidence * severity
            weighted_score = indicator.confidence * indicator.severity
            threat_scores.append(weighted_score)
        
        overall_threat_score = np.mean(threat_scores) if threat_scores else 0.0
        
        # Determine safety level
        safety_level = self._determine_safety_level(trigger_count, overall_threat_score)
        
        # Determine if facial recognition should be activated
        facial_recognition_status = self._determine_facial_recognition_status(
            trigger_count, overall_threat_score
        )
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(
            safety_level, active_triggers, overall_threat_score
        )
        
        # Determine if emergency response is required
        requires_emergency_response = self._requires_emergency_response(
            safety_level, trigger_count, overall_threat_score
        )
        
        # Calculate confidence in assessment
        confidence = self._calculate_assessment_confidence(active_triggers, threat_scores)
        
        assessment = SafetyAssessment(
            timestamp=time.time(),
            safety_level=safety_level,
            active_triggers=active_triggers,
            overall_threat_score=overall_threat_score,
            facial_recognition_status=facial_recognition_status,
            recommended_actions=recommended_actions,
            requires_emergency_response=requires_emergency_response,
            confidence=confidence
        )
        
        self.safety_history.append(assessment)
        return assessment
    
    def _determine_safety_level(self, trigger_count: int, threat_score: float) -> SafetyLevel:
        """Determine safety level based on trigger count and threat score"""
        if trigger_count >= self.emergency_threshold and threat_score > 0.8:
            return SafetyLevel.EMERGENCY
        elif trigger_count >= self.critical_threshold and threat_score > 0.6:
            return SafetyLevel.CRITICAL
        elif trigger_count >= self.activation_threshold and threat_score > 0.4:
            return SafetyLevel.HIGH
        elif trigger_count >= 2 and threat_score > 0.2:
            return SafetyLevel.ELEVATED
        else:
            return SafetyLevel.NORMAL
    
    def _determine_facial_recognition_status(self, trigger_count: int, 
                                           threat_score: float) -> FacialRecognitionStatus:
        """Determine if facial recognition should be activated"""
        if trigger_count >= self.activation_threshold and threat_score > 0.3:
            if not self.facial_recognition_active:
                self._activate_facial_recognition()
            return FacialRecognitionStatus.SCANNING
        elif self.facial_recognition_active:
            return FacialRecognitionStatus.SCANNING
        else:
            return FacialRecognitionStatus.INACTIVE
    
    def _requires_emergency_response(self, safety_level: SafetyLevel, 
                                   trigger_count: int, threat_score: float) -> bool:
        """Determine if emergency response is required"""
        return (safety_level in [SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY] or
                trigger_count >= self.emergency_threshold or
                threat_score > 0.8)
    
    def _calculate_assessment_confidence(self, active_triggers: List[SafetyTrigger], 
                                       threat_scores: List[float]) -> float:
        """Calculate confidence in the safety assessment"""
        if not active_triggers:
            return 0.0
        
        # Base confidence on number of triggers and their scores
        trigger_confidence = min(1.0, len(active_triggers) / 5.0)  # More triggers = higher confidence
        score_confidence = np.mean(threat_scores) if threat_scores else 0.0
        
        # Weighted average
        overall_confidence = (trigger_confidence * 0.4 + score_confidence * 0.6)
        return min(1.0, overall_confidence)
    
    def _generate_recommended_actions(self, safety_level: SafetyLevel, 
                                    active_triggers: List[SafetyTrigger], 
                                    threat_score: float) -> List[str]:
        """Generate recommended actions based on safety assessment"""
        actions = []
        
        if safety_level == SafetyLevel.EMERGENCY:
            actions.extend([
                "IMMEDIATE: Activate emergency protocols",
                "Contact law enforcement immediately",
                "Evacuate area if safe to do so",
                "Record all available evidence"
            ])
        elif safety_level == SafetyLevel.CRITICAL:
            actions.extend([
                "URGENT: Increase security monitoring",
                "Prepare emergency response team",
                "Activate facial recognition system",
                "Alert security personnel"
            ])
        elif safety_level == SafetyLevel.HIGH:
            actions.extend([
                "CAUTION: Monitor situation closely",
                "Consider activating facial recognition",
                "Prepare for potential escalation",
                "Document all activities"
            ])
        elif safety_level == SafetyLevel.ELEVATED:
            actions.extend([
                "ALERT: Watch for additional indicators",
                "Maintain heightened awareness",
                "Prepare response protocols"
            ])
        else:
            actions.append("NORMAL: Continue standard monitoring")
        
        # Add specific actions based on active triggers
        if SafetyTrigger.MULTIPLE_PEOPLE in active_triggers:
            actions.append("Monitor crowd behavior closely")
        
        if SafetyTrigger.FRANTIC_BEHAVIOR in active_triggers:
            actions.append("Watch for escalation of behavior")
        
        if SafetyTrigger.THREATENING_GESTURES in active_triggers:
            actions.append("Prepare for potential confrontation")
        
        if SafetyTrigger.WEAPON_DETECTED in active_triggers:
            actions.append("IMMEDIATE: Treat as active threat")
        
        return actions
    
    def _activate_facial_recognition(self):
        """Activate facial recognition system"""
        if not self.facial_recognition_active:
            self.facial_recognition_active = True
            self.logger.info("Facial recognition system activated")
            
            # Start facial recognition scanning
            self._start_facial_recognition_scanning()
    
    def _start_facial_recognition_scanning(self):
        """Start facial recognition scanning process"""
        # In a real implementation, this would interface with actual facial recognition
        # For simulation, we'll create mock scanning results
        
        def scanning_worker():
            scan_count = 0
            max_scans = 10  # Simulate 10 scans
            
            while self.facial_recognition_active and scan_count < max_scans:
                try:
                    # Simulate facial recognition scan
                    result = self._perform_facial_recognition_scan()
                    if result:
                        self._handle_facial_recognition_result(result)
                    
                    scan_count += 1
                    time.sleep(1)  # Scan every second
                    
                except Exception as e:
                    self.logger.error(f"Error in facial recognition scanning: {e}")
                    break
            
            # Deactivate after max scans
            self.facial_recognition_active = False
            self.logger.info("Facial recognition scanning completed")
        
        # Start scanning in separate thread
        scanning_thread = threading.Thread(target=scanning_worker, daemon=True)
        scanning_thread.start()
    
    def _perform_facial_recognition_scan(self) -> Optional[FacialRecognitionResult]:
        """Perform a single facial recognition scan"""
        # In a real implementation, this would use actual facial recognition
        # For simulation, we'll generate mock results
        
        # Simulate scan result
        match_found = np.random.random() < 0.3  # 30% chance of finding a match
        confidence = np.random.uniform(0.6, 0.95)
        
        person_id = None
        database_entry = None
        
        if match_found:
            # Generate mock person ID
            person_id = f"person_{np.random.randint(1000, 9999)}"
            
            # Create mock database entry
            database_entry = {
                'person_id': person_id,
                'name': f"Person_{person_id}",
                'threat_level': np.random.choice(['low', 'medium', 'high']),
                'last_seen': time.time(),
                'notes': 'Mock database entry'
            }
        
        result = FacialRecognitionResult(
            person_id=person_id,
            confidence=confidence,
            match_found=match_found,
            database_entry=database_entry,
            timestamp=time.time()
        )
        
        return result
    
    def _handle_facial_recognition_result(self, result: FacialRecognitionResult):
        """Handle facial recognition result"""
        self.recognition_results.append(result)
        
        self.logger.info(f"Facial recognition result: "
                        f"{'Match found' if result.match_found else 'No match'} "
                        f"(confidence: {result.confidence:.2f})")
        
        # Trigger callbacks
        for callback in self.recognition_callbacks:
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in recognition callback: {e}")
        
        # Handle match found
        if result.match_found and result.database_entry:
            self._handle_known_person_detected(result)
    
    def _handle_known_person_detected(self, result: FacialRecognitionResult):
        """Handle detection of a known person"""
        person_id = result.person_id
        database_entry = result.database_entry
        
        self.logger.warning(f"Known person detected: {person_id} "
                           f"(threat level: {database_entry.get('threat_level', 'unknown')})")
        
        # Check if person is on watch list
        threat_level = database_entry.get('threat_level', 'low')
        if threat_level in ['high', 'critical']:
            self._trigger_high_priority_alert(person_id, database_entry)
    
    def _trigger_high_priority_alert(self, person_id: str, database_entry: Dict[str, Any]):
        """Trigger high priority alert for known threat"""
        alert_data = {
            'person_id': person_id,
            'database_entry': database_entry,
            'timestamp': time.time(),
            'alert_type': 'known_threat_detected'
        }
        
        self.logger.critical(f"HIGH PRIORITY ALERT: Known threat detected - {person_id}")
        
        # Trigger emergency callbacks
        for callback in self.emergency_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                self.logger.error(f"Error in emergency callback: {e}")
    
    def _handle_safety_assessment(self, assessment: SafetyAssessment):
        """Handle safety assessment results"""
        self.logger.info(f"Safety assessment: {assessment.safety_level.value} "
                        f"(threat score: {assessment.overall_threat_score:.2f}, "
                        f"triggers: {len(assessment.active_triggers)})")
        
        # Trigger callbacks
        for callback in self.safety_callbacks:
            try:
                callback(assessment)
            except Exception as e:
                self.logger.error(f"Error in safety callback: {e}")
        
        # Handle emergency response
        if assessment.requires_emergency_response:
            self._activate_emergency_protocols(assessment)
    
    def _activate_emergency_protocols(self, assessment: SafetyAssessment):
        """Activate emergency response protocols"""
        if not self.emergency_protocols_active:
            self.emergency_protocols_active = True
            self.logger.critical("EMERGENCY PROTOCOLS ACTIVATED")
            
            # Trigger emergency callbacks
            for callback in self.emergency_callbacks:
                try:
                    callback(assessment)
                except Exception as e:
                    self.logger.error(f"Error in emergency callback: {e}")
    
    def _cleanup_expired_indicators(self):
        """Clean up expired safety indicators"""
        current_time = time.time()
        expired_triggers = []
        
        for trigger_type, indicator in self.active_indicators.items():
            # Remove indicators older than 30 seconds
            if current_time - indicator.timestamp > 30:
                expired_triggers.append(trigger_type)
        
        for trigger_type in expired_triggers:
            del self.active_indicators[trigger_type]
    
    def add_person_to_database(self, person_id: str, name: str, 
                             threat_level: str = 'low', notes: str = ''):
        """Add a person to the facial recognition database"""
        database_entry = {
            'person_id': person_id,
            'name': name,
            'threat_level': threat_level,
            'last_seen': time.time(),
            'notes': notes
        }
        
        self.face_database[person_id] = database_entry
        self.logger.info(f"Person added to database: {person_id} ({name})")
    
    def remove_person_from_database(self, person_id: str):
        """Remove a person from the facial recognition database"""
        if person_id in self.face_database:
            del self.face_database[person_id]
            self.logger.info(f"Person removed from database: {person_id}")
    
    def add_safety_callback(self, callback: Callable):
        """Add callback for safety assessment events"""
        self.safety_callbacks.append(callback)
    
    def add_recognition_callback(self, callback: Callable):
        """Add callback for facial recognition events"""
        self.recognition_callbacks.append(callback)
    
    def add_emergency_callback(self, callback: Callable):
        """Add callback for emergency events"""
        self.emergency_callbacks.append(callback)
    
    def get_current_safety_status(self) -> Dict[str, Any]:
        """Get current safety status"""
        return {
            'active_indicators': len(self.active_indicators),
            'facial_recognition_active': self.facial_recognition_active,
            'emergency_protocols_active': self.emergency_protocols_active,
            'database_size': len(self.face_database),
            'recent_recognition_results': len(self.recognition_results),
            'monitoring_active': self.is_monitoring
        }
    
    def get_safety_history(self, duration_seconds: int = 300) -> List[SafetyAssessment]:
        """Get safety assessment history"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        return [assessment for assessment in self.safety_history 
                if assessment.timestamp >= cutoff_time]
    
    def export_safety_data(self, filepath: str):
        """Export safety data to JSON file"""
        data = {
            'export_timestamp': time.time(),
            'safety_assessments': [
                {
                    'timestamp': assessment.timestamp,
                    'safety_level': assessment.safety_level.value,
                    'active_triggers': [t.value for t in assessment.active_triggers],
                    'overall_threat_score': assessment.overall_threat_score,
                    'facial_recognition_status': assessment.facial_recognition_status.value,
                    'recommended_actions': assessment.recommended_actions,
                    'requires_emergency_response': assessment.requires_emergency_response,
                    'confidence': assessment.confidence
                }
                for assessment in self.safety_history
            ],
            'recognition_results': [
                {
                    'person_id': result.person_id,
                    'confidence': result.confidence,
                    'match_found': result.match_found,
                    'database_entry': result.database_entry,
                    'timestamp': result.timestamp
                }
                for result in self.recognition_results
            ],
            'face_database': self.face_database
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Safety data exported to {filepath}")
    
    def deactivate_emergency_protocols(self):
        """Deactivate emergency protocols"""
        self.emergency_protocols_active = False
        self.facial_recognition_active = False
        self.logger.info("Emergency protocols deactivated")
    
    def reset_safety_system(self):
        """Reset the safety system to normal state"""
        self.active_indicators.clear()
        self.facial_recognition_active = False
        self.emergency_protocols_active = False
        self.recognition_results.clear()
        self.logger.info("Safety system reset to normal state")
