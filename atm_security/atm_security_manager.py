"""
ATM Security Manager
===================

Comprehensive security management system that integrates all ATM security components:
- AI-powered camera system
- Behavior detection
- Safety switch system
- Card edge sensors
- Emergency protocols

Features:
- Unified security monitoring
- Real-time threat assessment
- Automated response protocols
- Law enforcement integration
- Comprehensive logging and reporting
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
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .atm_camera_system import ATMCameraSystem, CameraConfig, DetectionStatus
from .behavior_detector import BehaviorDetector, BehaviorType, BehaviorAnalysis
from .safety_switch import SafetySwitch, SafetyLevel, SafetyTrigger
from .card_edge_sensor import CardEdgeSensor, ThreatLevel, EMFieldMap

class SecurityStatus(Enum):
    """Overall security status"""
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH_ALERT = "high_alert"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ResponseAction(Enum):
    """Security response actions"""
    MONITOR = "monitor"
    ALERT_SECURITY = "alert_security"
    ACTIVATE_CAMERAS = "activate_cameras"
    ENABLE_FACIAL_RECOGNITION = "enable_facial_recognition"
    CONTACT_LAW_ENFORCEMENT = "contact_law_enforcement"
    EVACUATE_AREA = "evacuate_area"
    LOCKDOWN_ATM = "lockdown_atm"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

@dataclass
class SecurityAssessment:
    """Comprehensive security assessment"""
    timestamp: float
    overall_status: SecurityStatus
    threat_score: float  # 0-1
    active_threats: List[str]
    recommended_actions: List[ResponseAction]
    confidence: float
    source_systems: List[str]
    requires_immediate_response: bool

@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    timestamp: float
    event_type: str
    severity: str
    description: str
    source_system: str
    response_taken: List[ResponseAction]
    resolved: bool
    metadata: Dict[str, Any] = None

class ATMSecurityManager:
    """
    Comprehensive ATM security management system
    
    Integrates all security components and provides unified monitoring,
    threat assessment, and response coordination.
    """
    
    def __init__(self, atm_id: str = "ATM_001"):
        self.atm_id = atm_id
        self.logger = logging.getLogger(__name__)
        
        # Initialize security components
        self.camera_system = ATMCameraSystem()
        self.behavior_detector = BehaviorDetector()
        self.safety_switch = SafetySwitch()
        self.card_edge_sensor = CardEdgeSensor()
        
        # Security state
        self.current_status = SecurityStatus.NORMAL
        self.security_history = deque(maxlen=1000)
        self.active_events: Dict[str, SecurityEvent] = {}
        self.event_counter = 0
        
        # Response protocols
        self.response_protocols = self._initialize_response_protocols()
        self.emergency_contacts = self._initialize_emergency_contacts()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Callbacks
        self.security_callbacks: List[Callable] = []
        self.emergency_callbacks: List[Callable] = []
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Setup component integration
        self._setup_component_integration()
        
        # Start monitoring
        self.start_monitoring()
    
    def _initialize_response_protocols(self) -> Dict[SecurityStatus, List[ResponseAction]]:
        """Initialize response protocols for different security levels"""
        return {
            SecurityStatus.NORMAL: [ResponseAction.MONITOR],
            SecurityStatus.ELEVATED: [
                ResponseAction.MONITOR,
                ResponseAction.ALERT_SECURITY
            ],
            SecurityStatus.HIGH_ALERT: [
                ResponseAction.MONITOR,
                ResponseAction.ALERT_SECURITY,
                ResponseAction.ACTIVATE_CAMERAS,
                ResponseAction.ENABLE_FACIAL_RECOGNITION
            ],
            SecurityStatus.CRITICAL: [
                ResponseAction.MONITOR,
                ResponseAction.ALERT_SECURITY,
                ResponseAction.ACTIVATE_CAMERAS,
                ResponseAction.ENABLE_FACIAL_RECOGNITION,
                ResponseAction.CONTACT_LAW_ENFORCEMENT,
                ResponseAction.LOCKDOWN_ATM
            ],
            SecurityStatus.EMERGENCY: [
                ResponseAction.MONITOR,
                ResponseAction.ALERT_SECURITY,
                ResponseAction.ACTIVATE_CAMERAS,
                ResponseAction.ENABLE_FACIAL_RECOGNITION,
                ResponseAction.CONTACT_LAW_ENFORCEMENT,
                ResponseAction.EVACUATE_AREA,
                ResponseAction.EMERGENCY_SHUTDOWN
            ]
        }
    
    def _initialize_emergency_contacts(self) -> Dict[str, str]:
        """Initialize emergency contact information"""
        return {
            'security_team': '+1-555-SECURITY',
            'law_enforcement': '911',
            'atm_operator': '+1-555-ATM-HELP',
            'technical_support': '+1-555-TECH-SUPPORT'
        }
    
    def _setup_component_integration(self):
        """Setup integration between security components"""
        # Camera system callbacks
        self.camera_system.add_detection_callback(self._handle_camera_detection)
        self.camera_system.add_threat_callback(self._handle_camera_threat)
        self.camera_system.add_emergency_callback(self._handle_camera_emergency)
        
        # Behavior detector callbacks
        self.behavior_detector.add_behavior_callback(self._handle_behavior_detection)
        self.behavior_detector.add_threat_callback(self._handle_behavior_threat)
        self.behavior_detector.add_emergency_callback(self._handle_behavior_emergency)
        
        # Safety switch callbacks
        self.safety_switch.add_safety_callback(self._handle_safety_assessment)
        self.safety_switch.add_recognition_callback(self._handle_facial_recognition)
        self.safety_switch.add_emergency_callback(self._handle_safety_emergency)
        
        # Card edge sensor callbacks
        self.card_edge_sensor.add_signal_callback(self._handle_em_signal)
        self.card_edge_sensor.add_threat_callback(self._handle_em_threat)
        self.card_edge_sensor.add_analysis_callback(self._handle_em_analysis)
        
        self.logger.info("Component integration setup complete")
    
    def start_monitoring(self):
        """Start comprehensive security monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Start component monitoring
        self.camera_system.start_processing()
        self.behavior_detector.start_analysis()
        self.safety_switch.start_monitoring()
        self.card_edge_sensor.start_scanning()
        
        self.logger.info("ATM security monitoring started")
    
    def stop_monitoring(self):
        """Stop security monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.stop_monitoring.set()
        
        # Stop component monitoring
        self.camera_system.stop_processing()
        self.behavior_detector.stop_analysis()
        self.safety_switch.stop_monitoring()
        self.card_edge_sensor.stop_scanning()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("ATM security monitoring stopped")
    
    def _monitoring_loop(self):
        """Main security monitoring loop"""
        while not self.stop_monitoring.is_set():
            try:
                # Perform comprehensive security assessment
                assessment = self._perform_security_assessment()
                if assessment:
                    self._handle_security_assessment(assessment)
                
                time.sleep(1.0)  # Assess every second
                
            except Exception as e:
                self.logger.error(f"Error in security monitoring loop: {e}")
                time.sleep(1.0)
    
    def _perform_security_assessment(self) -> Optional[SecurityAssessment]:
        """Perform comprehensive security assessment"""
        # Gather data from all components
        camera_status = self.camera_system.get_current_status()
        behavior_status = self.behavior_detector.get_current_behavior_status()
        safety_status = self.safety_switch.get_current_safety_status()
        sensor_status = self.card_edge_sensor.get_current_status()
        
        # Calculate overall threat score
        threat_score = self._calculate_overall_threat_score(
            camera_status, behavior_status, safety_status, sensor_status
        )
        
        # Determine security status
        security_status = self._determine_security_status(threat_score)
        
        # Identify active threats
        active_threats = self._identify_active_threats(
            camera_status, behavior_status, safety_status, sensor_status
        )
        
        # Generate recommended actions
        recommended_actions = self.response_protocols.get(security_status, [])
        
        # Calculate confidence
        confidence = self._calculate_assessment_confidence(
            camera_status, behavior_status, safety_status, sensor_status
        )
        
        # Determine source systems
        source_systems = self._identify_source_systems(
            camera_status, behavior_status, safety_status, sensor_status
        )
        
        # Check if immediate response is required
        requires_immediate_response = security_status in [
            SecurityStatus.CRITICAL, SecurityStatus.EMERGENCY
        ]
        
        assessment = SecurityAssessment(
            timestamp=time.time(),
            overall_status=security_status,
            threat_score=threat_score,
            active_threats=active_threats,
            recommended_actions=recommended_actions,
            confidence=confidence,
            source_systems=source_systems,
            requires_immediate_response=requires_immediate_response
        )
        
        return assessment
    
    def _calculate_overall_threat_score(self, camera_status: Dict, behavior_status: Dict,
                                      safety_status: Dict, sensor_status: Dict) -> float:
        """Calculate overall threat score from all components"""
        threat_scores = []
        
        # Camera system threat
        if camera_status.get('detection_status') in ['threat_detected', 'emergency']:
            threat_scores.append(0.8)
        elif camera_status.get('detection_status') == 'suspicious_activity':
            threat_scores.append(0.5)
        elif camera_status.get('detection_status') == 'multiple_people':
            threat_scores.append(0.3)
        else:
            threat_scores.append(0.1)
        
        # Behavior detector threat
        behavior_threat = behavior_status.get('threat_level', 0.0)
        threat_scores.append(behavior_threat)
        
        # Safety switch threat
        if safety_status.get('emergency_protocols_active'):
            threat_scores.append(0.9)
        elif safety_status.get('facial_recognition_active'):
            threat_scores.append(0.6)
        else:
            threat_scores.append(0.1)
        
        # Card edge sensor threat
        if sensor_status.get('field_maps_count', 0) > 0:
            # This would be based on actual field map analysis
            threat_scores.append(0.2)
        else:
            threat_scores.append(0.1)
        
        return np.mean(threat_scores) if threat_scores else 0.0
    
    def _determine_security_status(self, threat_score: float) -> SecurityStatus:
        """Determine security status based on threat score"""
        if threat_score >= 0.9:
            return SecurityStatus.EMERGENCY
        elif threat_score >= 0.7:
            return SecurityStatus.CRITICAL
        elif threat_score >= 0.5:
            return SecurityStatus.HIGH_ALERT
        elif threat_score >= 0.3:
            return SecurityStatus.ELEVATED
        else:
            return SecurityStatus.NORMAL
    
    def _identify_active_threats(self, camera_status: Dict, behavior_status: Dict,
                               safety_status: Dict, sensor_status: Dict) -> List[str]:
        """Identify active threats from all components"""
        threats = []
        
        # Camera threats
        detection_status = camera_status.get('detection_status', 'normal')
        if detection_status == 'emergency':
            threats.append('Emergency situation detected by cameras')
        elif detection_status == 'threat_detected':
            threats.append('Threat detected by camera system')
        elif detection_status == 'suspicious_activity':
            threats.append('Suspicious activity detected by cameras')
        elif detection_status == 'multiple_people':
            threats.append('Multiple people detected at ATM')
        
        # Behavior threats
        behavior_type = behavior_status.get('behavior_type', 'normal')
        if behavior_type in ['threatening', 'emergency']:
            threats.append(f'Threatening behavior detected: {behavior_type}')
        elif behavior_type == 'frantic':
            threats.append('Frantic behavior detected')
        elif behavior_type == 'aggressive':
            threats.append('Aggressive behavior detected')
        
        # Safety switch threats
        if safety_status.get('emergency_protocols_active'):
            threats.append('Emergency protocols activated')
        elif safety_status.get('facial_recognition_active'):
            threats.append('Facial recognition system activated')
        
        # Sensor threats
        if sensor_status.get('field_maps_count', 0) > 0:
            threats.append('Electromagnetic anomalies detected')
        
        return threats
    
    def _calculate_assessment_confidence(self, camera_status: Dict, behavior_status: Dict,
                                       safety_status: Dict, sensor_status: Dict) -> float:
        """Calculate confidence in security assessment"""
        confidences = []
        
        # Camera confidence
        camera_confidence = 0.8 if camera_status.get('processing_active') else 0.0
        confidences.append(camera_confidence)
        
        # Behavior confidence
        behavior_confidence = behavior_status.get('confidence', 0.0)
        confidences.append(behavior_confidence)
        
        # Safety confidence
        safety_confidence = 0.9 if safety_status.get('monitoring_active') else 0.0
        confidences.append(safety_confidence)
        
        # Sensor confidence
        sensor_confidence = 0.7 if sensor_status.get('is_scanning') else 0.0
        confidences.append(sensor_confidence)
        
        return np.mean(confidences) if confidences else 0.0
    
    def _identify_source_systems(self, camera_status: Dict, behavior_status: Dict,
                               safety_status: Dict, sensor_status: Dict) -> List[str]:
        """Identify which systems are contributing to the assessment"""
        sources = []
        
        if camera_status.get('processing_active'):
            sources.append('camera_system')
        
        if behavior_status.get('confidence', 0) > 0.5:
            sources.append('behavior_detector')
        
        if safety_status.get('monitoring_active'):
            sources.append('safety_switch')
        
        if sensor_status.get('is_scanning'):
            sources.append('card_edge_sensor')
        
        return sources
    
    def _handle_security_assessment(self, assessment: SecurityAssessment):
        """Handle security assessment results"""
        # Update current status
        self.current_status = assessment.overall_status
        
        # Store in history
        self.security_history.append(assessment)
        
        # Log assessment
        self.logger.info(f"Security assessment: {assessment.overall_status.value} "
                        f"(threat score: {assessment.threat_score:.2f}, "
                        f"confidence: {assessment.confidence:.2f})")
        
        # Execute recommended actions
        self._execute_response_actions(assessment.recommended_actions)
        
        # Create security event if status changed
        if len(self.security_history) > 1:
            prev_assessment = self.security_history[-2]
            if prev_assessment.overall_status != assessment.overall_status:
                self._create_security_event(assessment)
        
        # Trigger callbacks
        for callback in self.security_callbacks:
            try:
                callback(assessment)
            except Exception as e:
                self.logger.error(f"Error in security callback: {e}")
        
        # Handle emergency situations
        if assessment.requires_immediate_response:
            self._handle_emergency_situation(assessment)
    
    def _execute_response_actions(self, actions: List[ResponseAction]):
        """Execute recommended response actions"""
        for action in actions:
            try:
                self._execute_single_action(action)
            except Exception as e:
                self.logger.error(f"Error executing action {action.value}: {e}")
    
    def _execute_single_action(self, action: ResponseAction):
        """Execute a single response action"""
        if action == ResponseAction.MONITOR:
            self.logger.debug("Continuing monitoring")
        
        elif action == ResponseAction.ALERT_SECURITY:
            self._alert_security_team()
        
        elif action == ResponseAction.ACTIVATE_CAMERAS:
            self._activate_cameras()
        
        elif action == ResponseAction.ENABLE_FACIAL_RECOGNITION:
            self._enable_facial_recognition()
        
        elif action == ResponseAction.CONTACT_LAW_ENFORCEMENT:
            self._contact_law_enforcement()
        
        elif action == ResponseAction.EVACUATE_AREA:
            self._evacuate_area()
        
        elif action == ResponseAction.LOCKDOWN_ATM:
            self._lockdown_atm()
        
        elif action == ResponseAction.EMERGENCY_SHUTDOWN:
            self._emergency_shutdown()
    
    def _alert_security_team(self):
        """Alert security team"""
        self.logger.warning("ALERT: Security team notified")
        # In a real implementation, this would send actual alerts
    
    def _activate_cameras(self):
        """Activate all cameras"""
        self.logger.info("Activating all cameras")
        # Cameras are already active, but this could trigger additional recording
    
    def _enable_facial_recognition(self):
        """Enable facial recognition system"""
        self.logger.info("Enabling facial recognition system")
        # This would be handled by the safety switch system
    
    def _contact_law_enforcement(self):
        """Contact law enforcement"""
        self.logger.critical("CONTACTING LAW ENFORCEMENT")
        # In a real implementation, this would make actual contact
    
    def _evacuate_area(self):
        """Initiate area evacuation"""
        self.logger.critical("INITIATING AREA EVACUATION")
        # In a real implementation, this would trigger evacuation protocols
    
    def _lockdown_atm(self):
        """Lockdown the ATM"""
        self.logger.critical("ATM LOCKDOWN INITIATED")
        # In a real implementation, this would disable ATM functions
    
    def _emergency_shutdown(self):
        """Emergency shutdown of all systems"""
        self.logger.critical("EMERGENCY SHUTDOWN INITIATED")
        # In a real implementation, this would shut down all systems safely
    
    def _create_security_event(self, assessment: SecurityAssessment):
        """Create a security event record"""
        event_id = f"EVENT_{self.event_counter:06d}"
        self.event_counter += 1
        
        event = SecurityEvent(
            event_id=event_id,
            timestamp=assessment.timestamp,
            event_type=f"status_change_to_{assessment.overall_status.value}",
            severity=assessment.overall_status.value,
            description=f"Security status changed to {assessment.overall_status.value}",
            source_system="security_manager",
            response_taken=assessment.recommended_actions,
            resolved=False,
            metadata={
                'threat_score': assessment.threat_score,
                'confidence': assessment.confidence,
                'active_threats': assessment.active_threats,
                'source_systems': assessment.source_systems
            }
        )
        
        self.active_events[event_id] = event
        self.logger.info(f"Security event created: {event_id}")
    
    def _handle_emergency_situation(self, assessment: SecurityAssessment):
        """Handle emergency situations"""
        self.logger.critical(f"EMERGENCY SITUATION: {assessment.overall_status.value}")
        
        # Trigger emergency callbacks
        for callback in self.emergency_callbacks:
            try:
                callback(assessment)
            except Exception as e:
                self.logger.error(f"Error in emergency callback: {e}")
    
    # Component event handlers
    def _handle_camera_detection(self, detection):
        """Handle camera detection events"""
        self.logger.debug(f"Camera detection: {detection.person_id}")
    
    def _handle_camera_threat(self, status, crowd_analysis):
        """Handle camera threat events"""
        self.logger.warning(f"Camera threat detected: {status.value}")
    
    def _handle_camera_emergency(self, status, crowd_analysis):
        """Handle camera emergency events"""
        self.logger.critical(f"Camera emergency: {status.value}")
    
    def _handle_behavior_detection(self, analysis: BehaviorAnalysis):
        """Handle behavior detection events"""
        self.logger.debug(f"Behavior detected: {analysis.behavior_type.value}")
    
    def _handle_behavior_threat(self, analysis: BehaviorAnalysis):
        """Handle behavior threat events"""
        self.logger.warning(f"Behavior threat: {analysis.behavior_type.value}")
    
    def _handle_behavior_emergency(self, analysis: BehaviorAnalysis):
        """Handle behavior emergency events"""
        self.logger.critical(f"Behavior emergency: {analysis.behavior_type.value}")
    
    def _handle_safety_assessment(self, assessment):
        """Handle safety assessment events"""
        self.logger.debug(f"Safety assessment: {assessment.safety_level.value}")
    
    def _handle_facial_recognition(self, result):
        """Handle facial recognition events"""
        self.logger.info(f"Facial recognition: {'Match' if result.match_found else 'No match'}")
    
    def _handle_safety_emergency(self, data):
        """Handle safety emergency events"""
        self.logger.critical("Safety emergency detected")
    
    def _handle_em_signal(self, reading):
        """Handle EM signal events"""
        self.logger.debug(f"EM signal: {reading.signal_type.value}")
    
    def _handle_em_threat(self, field_map: EMFieldMap):
        """Handle EM threat events"""
        self.logger.warning(f"EM threat: {field_map.threat_level.value}")
    
    def _handle_em_analysis(self, field_map: EMFieldMap, analysis):
        """Handle EM analysis events"""
        self.logger.debug("EM analysis completed")
    
    def add_security_callback(self, callback: Callable):
        """Add callback for security events"""
        self.security_callbacks.append(callback)
    
    def add_emergency_callback(self, callback: Callable):
        """Add callback for emergency events"""
        self.emergency_callbacks.append(callback)
    
    def get_current_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            'atm_id': self.atm_id,
            'current_status': self.current_status.value,
            'is_monitoring': self.is_monitoring,
            'active_events': len(self.active_events),
            'security_history_size': len(self.security_history),
            'component_status': {
                'camera_system': self.camera_system.get_current_status(),
                'behavior_detector': self.behavior_detector.get_current_behavior_status(),
                'safety_switch': self.safety_switch.get_current_safety_status(),
                'card_edge_sensor': self.card_edge_sensor.get_current_status()
            }
        }
    
    def get_security_history(self, duration_seconds: int = 3600) -> List[SecurityAssessment]:
        """Get security assessment history"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        return [assessment for assessment in self.security_history 
                if assessment.timestamp >= cutoff_time]
    
    def export_security_report(self, filepath: str):
        """Export comprehensive security report"""
        data = {
            'atm_id': self.atm_id,
            'export_timestamp': time.time(),
            'current_status': self.current_status.value,
            'security_assessments': [
                {
                    'timestamp': assessment.timestamp,
                    'overall_status': assessment.overall_status.value,
                    'threat_score': assessment.threat_score,
                    'active_threats': assessment.active_threats,
                    'recommended_actions': [action.value for action in assessment.recommended_actions],
                    'confidence': assessment.confidence,
                    'source_systems': assessment.source_systems,
                    'requires_immediate_response': assessment.requires_immediate_response
                }
                for assessment in self.security_history
            ],
            'active_events': [
                {
                    'event_id': event.event_id,
                    'timestamp': event.timestamp,
                    'event_type': event.event_type,
                    'severity': event.severity,
                    'description': event.description,
                    'source_system': event.source_system,
                    'response_taken': [action.value for action in event.response_taken],
                    'resolved': event.resolved,
                    'metadata': event.metadata
                }
                for event in self.active_events.values()
            ],
            'component_data': {
                'camera_system': self.camera_system.get_current_status(),
                'behavior_detector': self.behavior_detector.get_current_behavior_status(),
                'safety_switch': self.safety_switch.get_current_safety_status(),
                'card_edge_sensor': self.card_edge_sensor.get_current_status()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Security report exported to {filepath}")
    
    def shutdown(self):
        """Shutdown the security manager and all components"""
        self.logger.info("Shutting down ATM security manager")
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Shutdown components
        self.camera_system.stop_processing()
        self.behavior_detector.stop_analysis()
        self.safety_switch.stop_monitoring()
        self.card_edge_sensor.stop_scanning()
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        self.logger.info("ATM security manager shutdown complete")
