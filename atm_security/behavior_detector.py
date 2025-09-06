"""
Behavior Detection System
========================

Advanced AI-powered behavior detection system for ATM security that analyzes:
- Frantic movement patterns
- Gesture recognition
- Stress indicators
- Threat assessment
- Emergency situation detection

Features:
- Real-time movement analysis
- Pattern recognition algorithms
- Multi-modal behavior assessment
- Threat level classification
- Emergency response triggers
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
import math

class BehaviorType(Enum):
    """Types of detected behaviors"""
    NORMAL = "normal"
    FRANTIC = "frantic"
    AGGRESSIVE = "aggressive"
    SUSPICIOUS = "suspicious"
    THREATENING = "threatening"
    EMERGENCY = "emergency"

class MovementPattern(Enum):
    """Movement pattern classifications"""
    STATIONARY = "stationary"
    WALKING = "walking"
    RUNNING = "running"
    FRANTIC = "frantic"
    AGGRESSIVE = "aggressive"
    RETREATING = "retreating"

class GestureType(Enum):
    """Gesture recognition types"""
    WAVING = "waving"
    POINTING = "pointing"
    THREATENING = "threatening"
    PLEADING = "pleading"
    HIDING = "hiding"
    UNKNOWN = "unknown"

@dataclass
class MovementAnalysis:
    """Analysis of movement patterns"""
    velocity: float  # pixels per second
    acceleration: float  # pixels per second squared
    direction_change_rate: float  # radians per second
    jerkiness: float  # movement irregularity (0-1)
    pattern: MovementPattern
    confidence: float
    timestamp: float

@dataclass
class GestureAnalysis:
    """Analysis of detected gestures"""
    gesture_type: GestureType
    confidence: float
    duration: float  # seconds
    intensity: float  # 0-1
    bounding_box: Tuple[int, int, int, int]
    timestamp: float

@dataclass
class BehaviorAnalysis:
    """Comprehensive behavior analysis result"""
    timestamp: float
    behavior_type: BehaviorType
    threat_level: float  # 0-1
    movement_analysis: Optional[MovementAnalysis]
    gesture_analysis: List[GestureAnalysis]
    stress_indicators: Dict[str, float]
    confidence: float
    requires_attention: bool
    recommended_action: str

class BehaviorDetector:
    """
    Advanced behavior detection system for ATM security
    
    Analyzes movement patterns, gestures, and behavioral indicators
    to detect threatening or emergency situations.
    """
    
    def __init__(self, analysis_interval: float = 0.1):
        self.analysis_interval = analysis_interval
        self.logger = logging.getLogger(__name__)
        
        # Analysis state
        self.movement_history = deque(maxlen=100)
        self.gesture_history = deque(maxlen=50)
        self.behavior_history = deque(maxlen=100)
        
        # Processing state
        self.is_analyzing = False
        self.analysis_thread = None
        self.stop_analysis = threading.Event()
        
        # Callbacks
        self.behavior_callbacks: List[Callable] = []
        self.threat_callbacks: List[Callable] = []
        self.emergency_callbacks: List[Callable] = []
        
        # Analysis parameters
        self.movement_thresholds = {
            'frantic_velocity': 100,  # pixels per second
            'frantic_acceleration': 50,  # pixels per second squared
            'frantic_jerkiness': 0.7,  # 0-1 scale
            'aggressive_velocity': 80,
            'aggressive_acceleration': 40,
            'suspicious_direction_changes': 2.0  # radians per second
        }
        
        # Gesture recognition parameters
        self.gesture_thresholds = {
            'min_confidence': 0.6,
            'min_duration': 0.5,  # seconds
            'max_duration': 10.0  # seconds
        }
        
        # Start analysis
        self.start_analysis()
    
    def start_analysis(self):
        """Start behavior analysis"""
        if self.is_analyzing:
            return
        
        self.is_analyzing = True
        self.stop_analysis.clear()
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        self.logger.info("Behavior analysis started")
    
    def stop_analysis(self):
        """Stop behavior analysis"""
        if not self.is_analyzing:
            return
        
        self.is_analyzing = False
        self.stop_analysis.set()
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
        self.logger.info("Behavior analysis stopped")
    
    def _analysis_loop(self):
        """Main analysis loop"""
        while not self.stop_analysis.is_set():
            try:
                # Analyze recent movement data
                if len(self.movement_history) >= 5:
                    behavior_analysis = self._analyze_behavior()
                    if behavior_analysis:
                        self._handle_behavior_detection(behavior_analysis)
                
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                self.logger.error(f"Error in behavior analysis loop: {e}")
                time.sleep(self.analysis_interval)
    
    def add_movement_data(self, person_id: int, position: Tuple[float, float], 
                         timestamp: float = None):
        """
        Add movement data for analysis
        
        Args:
            person_id: Unique identifier for the person
            position: (x, y) position coordinates
            timestamp: Timestamp of the movement (uses current time if None)
        """
        if timestamp is None:
            timestamp = time.time()
        
        movement_data = {
            'person_id': person_id,
            'position': position,
            'timestamp': timestamp
        }
        
        self.movement_history.append(movement_data)
    
    def add_gesture_data(self, person_id: int, gesture_type: GestureType, 
                        confidence: float, bounding_box: Tuple[int, int, int, int],
                        timestamp: float = None):
        """
        Add gesture data for analysis
        
        Args:
            person_id: Unique identifier for the person
            gesture_type: Type of gesture detected
            confidence: Confidence score (0-1)
            bounding_box: Bounding box of the gesture
            timestamp: Timestamp of the gesture
        """
        if timestamp is None:
            timestamp = time.time()
        
        gesture_data = {
            'person_id': person_id,
            'gesture_type': gesture_type,
            'confidence': confidence,
            'bounding_box': bounding_box,
            'timestamp': timestamp
        }
        
        self.gesture_history.append(gesture_data)
    
    def _analyze_behavior(self) -> Optional[BehaviorAnalysis]:
        """Analyze behavior from recent data"""
        if not self.movement_history:
            return None
        
        # Analyze movement patterns
        movement_analysis = self._analyze_movement_patterns()
        
        # Analyze gestures
        gesture_analysis = self._analyze_gestures()
        
        # Calculate stress indicators
        stress_indicators = self._calculate_stress_indicators(movement_analysis, gesture_analysis)
        
        # Determine behavior type and threat level
        behavior_type, threat_level = self._classify_behavior(
            movement_analysis, gesture_analysis, stress_indicators
        )
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(movement_analysis, gesture_analysis)
        
        # Determine if attention is required
        requires_attention = self._requires_attention(behavior_type, threat_level)
        
        # Generate recommended action
        recommended_action = self._generate_recommendation(behavior_type, threat_level)
        
        analysis = BehaviorAnalysis(
            timestamp=time.time(),
            behavior_type=behavior_type,
            threat_level=threat_level,
            movement_analysis=movement_analysis,
            gesture_analysis=gesture_analysis,
            stress_indicators=stress_indicators,
            confidence=confidence,
            requires_attention=requires_attention,
            recommended_action=recommended_action
        )
        
        self.behavior_history.append(analysis)
        return analysis
    
    def _analyze_movement_patterns(self) -> Optional[MovementAnalysis]:
        """Analyze movement patterns from recent data"""
        if len(self.movement_history) < 3:
            return None
        
        # Get recent movements (last 2 seconds)
        current_time = time.time()
        recent_movements = [
            m for m in self.movement_history 
            if current_time - m['timestamp'] <= 2.0
        ]
        
        if len(recent_movements) < 3:
            return None
        
        # Calculate velocity
        velocities = []
        for i in range(1, len(recent_movements)):
            prev = recent_movements[i-1]
            curr = recent_movements[i]
            
            dt = curr['timestamp'] - prev['timestamp']
            if dt > 0:
                dx = curr['position'][0] - prev['position'][0]
                dy = curr['position'][1] - prev['position'][1]
                distance = math.sqrt(dx**2 + dy**2)
                velocity = distance / dt
                velocities.append(velocity)
        
        if not velocities:
            return None
        
        avg_velocity = np.mean(velocities)
        
        # Calculate acceleration
        accelerations = []
        for i in range(1, len(velocities)):
            dt = recent_movements[i+1]['timestamp'] - recent_movements[i]['timestamp']
            if dt > 0:
                acceleration = (velocities[i] - velocities[i-1]) / dt
                accelerations.append(acceleration)
        
        avg_acceleration = np.mean(accelerations) if accelerations else 0.0
        
        # Calculate direction change rate
        direction_changes = []
        for i in range(1, len(recent_movements)):
            prev = recent_movements[i-1]
            curr = recent_movements[i]
            next_mov = recent_movements[i+1] if i+1 < len(recent_movements) else curr
            
            # Calculate direction vectors
            dir1 = (curr['position'][0] - prev['position'][0], 
                   curr['position'][1] - prev['position'][1])
            dir2 = (next_mov['position'][0] - curr['position'][0], 
                   next_mov['position'][1] - curr['position'][1])
            
            # Calculate angle between directions
            if np.linalg.norm(dir1) > 0 and np.linalg.norm(dir2) > 0:
                cos_angle = np.dot(dir1, dir2) / (np.linalg.norm(dir1) * np.linalg.norm(dir2))
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                angle = math.acos(cos_angle)
                direction_changes.append(angle)
        
        direction_change_rate = np.mean(direction_changes) if direction_changes else 0.0
        
        # Calculate jerkiness (irregularity of movement)
        jerkiness = self._calculate_jerkiness(velocities)
        
        # Classify movement pattern
        pattern = self._classify_movement_pattern(avg_velocity, avg_acceleration, jerkiness)
        
        # Calculate confidence
        confidence = min(1.0, len(recent_movements) / 10.0)  # More data = higher confidence
        
        return MovementAnalysis(
            velocity=avg_velocity,
            acceleration=avg_acceleration,
            direction_change_rate=direction_change_rate,
            jerkiness=jerkiness,
            pattern=pattern,
            confidence=confidence,
            timestamp=current_time
        )
    
    def _calculate_jerkiness(self, velocities: List[float]) -> float:
        """Calculate jerkiness (irregularity) of movement"""
        if len(velocities) < 3:
            return 0.0
        
        # Calculate velocity changes
        velocity_changes = []
        for i in range(1, len(velocities)):
            velocity_changes.append(abs(velocities[i] - velocities[i-1]))
        
        # Jerkiness is the standard deviation of velocity changes
        jerkiness = np.std(velocity_changes) if velocity_changes else 0.0
        
        # Normalize to 0-1 scale
        max_expected_jerkiness = 50.0  # Adjust based on expected movement
        return min(1.0, jerkiness / max_expected_jerkiness)
    
    def _classify_movement_pattern(self, velocity: float, acceleration: float, 
                                 jerkiness: float) -> MovementPattern:
        """Classify movement pattern based on metrics"""
        if velocity < 5:
            return MovementPattern.STATIONARY
        elif velocity < 20:
            return MovementPattern.WALKING
        elif velocity < 50:
            return MovementPattern.RUNNING
        elif jerkiness > self.movement_thresholds['frantic_jerkiness']:
            return MovementPattern.FRANTIC
        elif velocity > self.movement_thresholds['aggressive_velocity']:
            return MovementPattern.AGGRESSIVE
        else:
            return MovementPattern.WALKING
    
    def _analyze_gestures(self) -> List[GestureAnalysis]:
        """Analyze gestures from recent data"""
        if not self.gesture_history:
            return []
        
        # Get recent gestures (last 5 seconds)
        current_time = time.time()
        recent_gestures = [
            g for g in self.gesture_history 
            if current_time - g['timestamp'] <= 5.0
        ]
        
        gesture_analyses = []
        for gesture_data in recent_gestures:
            if gesture_data['confidence'] >= self.gesture_thresholds['min_confidence']:
                # Calculate gesture duration (simplified)
                duration = 1.0  # Assume 1 second duration for simulation
                
                # Calculate intensity based on confidence and type
                intensity = gesture_data['confidence']
                if gesture_data['gesture_type'] in [GestureType.THREATENING, GestureType.AGGRESSIVE]:
                    intensity *= 1.2  # Boost intensity for threatening gestures
                
                analysis = GestureAnalysis(
                    gesture_type=gesture_data['gesture_type'],
                    confidence=gesture_data['confidence'],
                    duration=duration,
                    intensity=min(1.0, intensity),
                    bounding_box=gesture_data['bounding_box'],
                    timestamp=gesture_data['timestamp']
                )
                
                gesture_analyses.append(analysis)
        
        return gesture_analyses
    
    def _calculate_stress_indicators(self, movement_analysis: Optional[MovementAnalysis], 
                                   gesture_analysis: List[GestureAnalysis]) -> Dict[str, float]:
        """Calculate stress indicators from movement and gesture data"""
        indicators = {
            'movement_stress': 0.0,
            'gesture_stress': 0.0,
            'overall_stress': 0.0
        }
        
        # Movement-based stress
        if movement_analysis:
            if movement_analysis.pattern == MovementPattern.FRANTIC:
                indicators['movement_stress'] = 0.9
            elif movement_analysis.pattern == MovementPattern.AGGRESSIVE:
                indicators['movement_stress'] = 0.7
            elif movement_analysis.jerkiness > 0.5:
                indicators['movement_stress'] = 0.5
            else:
                indicators['movement_stress'] = 0.1
        
        # Gesture-based stress
        if gesture_analysis:
            threatening_gestures = [g for g in gesture_analysis 
                                  if g.gesture_type in [GestureType.THREATENING, GestureType.AGGRESSIVE]]
            
            if threatening_gestures:
                max_intensity = max(g.intensity for g in threatening_gestures)
                indicators['gesture_stress'] = max_intensity
            else:
                indicators['gesture_stress'] = 0.1
        else:
            indicators['gesture_stress'] = 0.0
        
        # Overall stress (weighted average)
        indicators['overall_stress'] = (
            indicators['movement_stress'] * 0.6 + 
            indicators['gesture_stress'] * 0.4
        )
        
        return indicators
    
    def _classify_behavior(self, movement_analysis: Optional[MovementAnalysis], 
                          gesture_analysis: List[GestureAnalysis], 
                          stress_indicators: Dict[str, float]) -> Tuple[BehaviorType, float]:
        """Classify behavior type and calculate threat level"""
        threat_level = 0.0
        behavior_type = BehaviorType.NORMAL
        
        # Movement-based threat assessment
        if movement_analysis:
            if movement_analysis.pattern == MovementPattern.FRANTIC:
                threat_level += 0.4
                behavior_type = BehaviorType.FRANTIC
            elif movement_analysis.pattern == MovementPattern.AGGRESSIVE:
                threat_level += 0.3
                behavior_type = BehaviorType.AGGRESSIVE
            elif movement_analysis.velocity > self.movement_thresholds['frantic_velocity']:
                threat_level += 0.2
                behavior_type = BehaviorType.SUSPICIOUS
        
        # Gesture-based threat assessment
        if gesture_analysis:
            threatening_gestures = [g for g in gesture_analysis 
                                  if g.gesture_type in [GestureType.THREATENING, GestureType.AGGRESSIVE]]
            
            if threatening_gestures:
                threat_level += 0.3
                if behavior_type == BehaviorType.NORMAL:
                    behavior_type = BehaviorType.AGGRESSIVE
                elif behavior_type == BehaviorType.SUSPICIOUS:
                    behavior_type = BehaviorType.THREATENING
        
        # Stress-based threat assessment
        overall_stress = stress_indicators.get('overall_stress', 0.0)
        if overall_stress > 0.8:
            threat_level += 0.2
            if behavior_type in [BehaviorType.NORMAL, BehaviorType.SUSPICIOUS]:
                behavior_type = BehaviorType.FRANTIC
        elif overall_stress > 0.6:
            threat_level += 0.1
            if behavior_type == BehaviorType.NORMAL:
                behavior_type = BehaviorType.SUSPICIOUS
        
        # Determine final behavior type
        if threat_level > 0.8:
            behavior_type = BehaviorType.EMERGENCY
        elif threat_level > 0.6:
            behavior_type = BehaviorType.THREATENING
        elif threat_level > 0.3:
            behavior_type = BehaviorType.SUSPICIOUS
        
        return behavior_type, min(1.0, threat_level)
    
    def _calculate_confidence(self, movement_analysis: Optional[MovementAnalysis], 
                            gesture_analysis: List[GestureAnalysis]) -> float:
        """Calculate overall confidence in the behavior analysis"""
        confidence_factors = []
        
        if movement_analysis:
            confidence_factors.append(movement_analysis.confidence)
        
        if gesture_analysis:
            gesture_confidences = [g.confidence for g in gesture_analysis]
            confidence_factors.append(np.mean(gesture_confidences))
        
        if not confidence_factors:
            return 0.0
        
        return np.mean(confidence_factors)
    
    def _requires_attention(self, behavior_type: BehaviorType, threat_level: float) -> bool:
        """Determine if the behavior requires immediate attention"""
        return (behavior_type in [BehaviorType.THREATENING, BehaviorType.EMERGENCY] or 
                threat_level > 0.6)
    
    def _generate_recommendation(self, behavior_type: BehaviorType, threat_level: float) -> str:
        """Generate recommended action based on behavior analysis"""
        if behavior_type == BehaviorType.EMERGENCY or threat_level > 0.8:
            return "IMMEDIATE: Activate emergency protocols, contact law enforcement"
        elif behavior_type == BehaviorType.THREATENING or threat_level > 0.6:
            return "URGENT: Increase security monitoring, prepare emergency response"
        elif behavior_type == BehaviorType.AGGRESSIVE or threat_level > 0.4:
            return "CAUTION: Monitor closely, consider security intervention"
        elif behavior_type == BehaviorType.SUSPICIOUS or threat_level > 0.2:
            return "ALERT: Watch for escalation, maintain awareness"
        else:
            return "NORMAL: Continue standard monitoring"
    
    def _handle_behavior_detection(self, analysis: BehaviorAnalysis):
        """Handle behavior detection events"""
        self.logger.info(f"Behavior detected: {analysis.behavior_type.value} "
                        f"(threat level: {analysis.threat_level:.2f})")
        
        # Trigger callbacks
        for callback in self.behavior_callbacks:
            try:
                callback(analysis)
            except Exception as e:
                self.logger.error(f"Error in behavior callback: {e}")
        
        # Handle high-threat situations
        if analysis.requires_attention:
            for callback in self.threat_callbacks:
                try:
                    callback(analysis)
                except Exception as e:
                    self.logger.error(f"Error in threat callback: {e}")
        
        # Handle emergency situations
        if analysis.behavior_type == BehaviorType.EMERGENCY:
            for callback in self.emergency_callbacks:
                try:
                    callback(analysis)
                except Exception as e:
                    self.logger.error(f"Error in emergency callback: {e}")
    
    def add_behavior_callback(self, callback: Callable):
        """Add callback for behavior detection events"""
        self.behavior_callbacks.append(callback)
    
    def add_threat_callback(self, callback: Callable):
        """Add callback for threat detection events"""
        self.threat_callbacks.append(callback)
    
    def add_emergency_callback(self, callback: Callable):
        """Add callback for emergency events"""
        self.emergency_callbacks.append(callback)
    
    def get_current_behavior_status(self) -> Dict[str, Any]:
        """Get current behavior analysis status"""
        if not self.behavior_history:
            return {
                'behavior_type': BehaviorType.NORMAL.value,
                'threat_level': 0.0,
                'requires_attention': False,
                'confidence': 0.0
            }
        
        latest_analysis = self.behavior_history[-1]
        return {
            'behavior_type': latest_analysis.behavior_type.value,
            'threat_level': latest_analysis.threat_level,
            'requires_attention': latest_analysis.requires_attention,
            'confidence': latest_analysis.confidence,
            'recommended_action': latest_analysis.recommended_action,
            'stress_indicators': latest_analysis.stress_indicators
        }
    
    def get_behavior_history(self, duration_seconds: int = 300) -> List[BehaviorAnalysis]:
        """Get behavior analysis history for the specified duration"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        return [analysis for analysis in self.behavior_history 
                if analysis.timestamp >= cutoff_time]
    
    def export_behavior_data(self, filepath: str):
        """Export behavior analysis data to JSON file"""
        data = {
            'export_timestamp': time.time(),
            'behavior_analyses': [
                {
                    'timestamp': analysis.timestamp,
                    'behavior_type': analysis.behavior_type.value,
                    'threat_level': analysis.threat_level,
                    'confidence': analysis.confidence,
                    'requires_attention': analysis.requires_attention,
                    'recommended_action': analysis.recommended_action,
                    'stress_indicators': analysis.stress_indicators,
                    'movement_analysis': {
                        'velocity': analysis.movement_analysis.velocity if analysis.movement_analysis else None,
                        'acceleration': analysis.movement_analysis.acceleration if analysis.movement_analysis else None,
                        'pattern': analysis.movement_analysis.pattern.value if analysis.movement_analysis else None,
                        'jerkiness': analysis.movement_analysis.jerkiness if analysis.movement_analysis else None
                    } if analysis.movement_analysis else None,
                    'gesture_analysis': [
                        {
                            'gesture_type': gesture.gesture_type.value,
                            'confidence': gesture.confidence,
                            'intensity': gesture.intensity,
                            'duration': gesture.duration
                        }
                        for gesture in analysis.gesture_analysis
                    ]
                }
                for analysis in self.behavior_history
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Behavior data exported to {filepath}")
