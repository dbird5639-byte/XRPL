"""
Stress Detection System
======================

Advanced stress detection system that monitors multiple biometric indicators
to detect signs of physical coercion or duress when using crypto wallets.

This system analyzes:
- Heart rate variability
- Blood pressure patterns
- Voice stress indicators
- Eye movement patterns
- Behavioral biometrics
- Environmental factors
"""

import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import threading
from collections import deque
import json

from .biometric_config import StressThresholds, SecurityLevel, BiometricType

class StressLevel(Enum):
    """Stress level classifications"""
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class BiometricReading:
    """Individual biometric reading with metadata"""
    timestamp: float
    biometric_type: BiometricType
    value: float
    confidence: float
    device_id: str
    location: Optional[Tuple[float, float]] = None

@dataclass
class StressAnalysis:
    """Comprehensive stress analysis result"""
    timestamp: float
    overall_stress_level: StressLevel
    stress_score: float  # 0.0 to 1.0
    individual_indicators: Dict[BiometricType, float]
    confidence: float
    risk_assessment: str
    recommended_action: str
    requires_immediate_attention: bool

class StressDetector:
    """
    Advanced stress detection system for crypto wallet security
    
    Monitors multiple biometric indicators in real-time to detect
    signs of physical coercion or duress.
    """
    
    def __init__(self, config: StressThresholds, monitoring_interval: float = 1.0):
        self.config = config
        self.monitoring_interval = monitoring_interval
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.biometric_history = deque(maxlen=1000)  # Keep last 1000 readings
        self.stress_history = deque(maxlen=100)      # Keep last 100 stress analyses
        
        # Baseline measurements (user's normal state)
        self.baseline_measurements = {}
        self.baseline_established = False
        self.baseline_samples_needed = 30
        self.baseline_samples_collected = 0
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Alert thresholds
        self.alert_thresholds = {
            StressLevel.ELEVATED: 0.3,
            StressLevel.HIGH: 0.6,
            StressLevel.CRITICAL: 0.8,
            StressLevel.EMERGENCY: 0.9
        }
        
        # Callbacks for stress detection events
        self.stress_callbacks = []
        self.emergency_callbacks = []
    
    def add_stress_callback(self, callback):
        """Add callback function for stress detection events"""
        self.stress_callbacks.append(callback)
    
    def add_emergency_callback(self, callback):
        """Add callback function for emergency situations"""
        self.emergency_callbacks.append(callback)
    
    def start_monitoring(self):
        """Start continuous stress monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Stress monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous stress monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Stress monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.is_set():
            try:
                # Collect biometric data from available sensors
                self._collect_biometric_data()
                
                # Analyze stress levels
                if len(self.biometric_history) >= 5:  # Need minimum data points
                    stress_analysis = self.analyze_stress()
                    if stress_analysis:
                        self._handle_stress_detection(stress_analysis)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_biometric_data(self):
        """Collect biometric data from available sensors"""
        # In a real implementation, this would interface with actual sensors
        # For now, we'll simulate data collection
        
        current_time = time.time()
        
        # Simulate heart rate monitoring
        if self._has_sensor(BiometricType.HEART_RATE):
            heart_rate = self._simulate_heart_rate_reading()
            reading = BiometricReading(
                timestamp=current_time,
                biometric_type=BiometricType.HEART_RATE,
                value=heart_rate,
                confidence=0.95,
                device_id="heart_rate_sensor_001"
            )
            self.biometric_history.append(reading)
        
        # Simulate blood pressure monitoring
        if self._has_sensor(BiometricType.BLOOD_PRESSURE):
            systolic, diastolic = self._simulate_blood_pressure_reading()
            reading = BiometricReading(
                timestamp=current_time,
                biometric_type=BiometricType.BLOOD_PRESSURE,
                value=systolic,  # Store systolic as primary value
                confidence=0.90,
                device_id="blood_pressure_sensor_001"
            )
            reading.metadata = {"diastolic": diastolic}
            self.biometric_history.append(reading)
        
        # Simulate voice stress analysis
        if self._has_sensor(BiometricType.VOICE):
            voice_stress = self._simulate_voice_stress_reading()
            reading = BiometricReading(
                timestamp=current_time,
                biometric_type=BiometricType.VOICE,
                value=voice_stress,
                confidence=0.85,
                device_id="voice_analyzer_001"
            )
            self.biometric_history.append(reading)
    
    def _has_sensor(self, biometric_type: BiometricType) -> bool:
        """Check if a specific biometric sensor is available"""
        # In a real implementation, this would check actual hardware
        return True  # Simulate all sensors available
    
    def _simulate_heart_rate_reading(self) -> float:
        """Simulate heart rate reading with some variability"""
        base_rate = 75
        if self.baseline_established:
            base_rate = self.baseline_measurements.get('heart_rate', 75)
        
        # Add some random variation
        variation = np.random.normal(0, 5)
        return max(40, min(200, base_rate + variation))
    
    def _simulate_blood_pressure_reading(self) -> Tuple[float, float]:
        """Simulate blood pressure reading"""
        systolic_base = 120
        diastolic_base = 80
        
        if self.baseline_established:
            systolic_base = self.baseline_measurements.get('systolic', 120)
            diastolic_base = self.baseline_measurements.get('diastolic', 80)
        
        systolic = max(80, min(200, systolic_base + np.random.normal(0, 10))
        diastolic = max(50, min(120, diastolic_base + np.random.normal(0, 5))
        
        return systolic, diastolic
    
    def _simulate_voice_stress_reading(self) -> float:
        """Simulate voice stress analysis (0.0 = normal, 1.0 = high stress)"""
        base_stress = 0.1
        if self.baseline_established:
            base_stress = self.baseline_measurements.get('voice_stress', 0.1)
        
        return max(0.0, min(1.0, base_stress + np.random.normal(0, 0.05)))
    
    def add_biometric_reading(self, reading: BiometricReading):
        """Add a biometric reading from external sensors"""
        self.biometric_history.append(reading)
        
        # Update baseline if needed
        if not self.baseline_established:
            self._update_baseline(reading)
    
    def _update_baseline(self, reading: BiometricReading):
        """Update baseline measurements for normal state"""
        biometric_type = reading.biometric_type
        
        if biometric_type not in self.baseline_measurements:
            self.baseline_measurements[biometric_type] = []
        
        self.baseline_measurements[biometric_type].append(reading.value)
        self.baseline_samples_collected += 1
        
        # Check if we have enough samples to establish baseline
        if self.baseline_samples_collected >= self.baseline_samples_needed:
            self._establish_baseline()
    
    def _establish_baseline(self):
        """Establish baseline measurements from collected samples"""
        for biometric_type, values in self.baseline_measurements.items():
            if values:
                self.baseline_measurements[biometric_type] = np.mean(values)
        
        self.baseline_established = True
        self.logger.info("Baseline measurements established")
    
    def analyze_stress(self) -> Optional[StressAnalysis]:
        """Analyze current stress levels from recent biometric data"""
        if not self.biometric_history:
            return None
        
        # Get recent readings (last 30 seconds)
        current_time = time.time()
        recent_readings = [
            r for r in self.biometric_history 
            if current_time - r.timestamp <= 30
        ]
        
        if not recent_readings:
            return None
        
        # Analyze individual indicators
        individual_indicators = {}
        stress_scores = []
        
        for biometric_type in BiometricType:
            type_readings = [r for r in recent_readings if r.biometric_type == biometric_type]
            if type_readings:
                indicator_score = self._analyze_biometric_indicator(biometric_type, type_readings)
                individual_indicators[biometric_type] = indicator_score
                stress_scores.append(indicator_score)
        
        if not stress_scores:
            return None
        
        # Calculate overall stress score
        overall_stress_score = np.mean(stress_scores)
        
        # Determine stress level
        stress_level = self._classify_stress_level(overall_stress_score)
        
        # Calculate confidence based on number of indicators and data quality
        confidence = min(1.0, len(stress_scores) / 3.0)  # Normalize by expected indicators
        
        # Generate risk assessment and recommendations
        risk_assessment, recommended_action = self._generate_assessment(stress_level, overall_stress_score)
        
        stress_analysis = StressAnalysis(
            timestamp=current_time,
            overall_stress_level=stress_level,
            stress_score=overall_stress_score,
            individual_indicators=individual_indicators,
            confidence=confidence,
            risk_assessment=risk_assessment,
            recommended_action=recommended_action,
            requires_immediate_attention=stress_level in [StressLevel.CRITICAL, StressLevel.EMERGENCY]
        )
        
        self.stress_history.append(stress_analysis)
        return stress_analysis
    
    def _analyze_biometric_indicator(self, biometric_type: BiometricType, readings: List[BiometricReading]) -> float:
        """Analyze a specific biometric indicator and return stress score (0.0-1.0)"""
        if not readings:
            return 0.0
        
        values = [r.value for r in readings]
        avg_value = np.mean(values)
        
        if biometric_type == BiometricType.HEART_RATE:
            return self._analyze_heart_rate_stress(avg_value)
        elif biometric_type == BiometricType.BLOOD_PRESSURE:
            return self._analyze_blood_pressure_stress(avg_value)
        elif biometric_type == BiometricType.VOICE:
            return self._analyze_voice_stress(avg_value)
        elif biometric_type == BiometricType.STRESS_LEVEL:
            return avg_value  # Direct stress level reading
        else:
            return 0.0  # Unknown indicator
    
    def _analyze_heart_rate_stress(self, heart_rate: float) -> float:
        """Analyze heart rate for stress indicators"""
        if heart_rate <= self.config.heart_rate_normal_max:
            return 0.0
        elif heart_rate <= self.config.heart_rate_stress_min:
            # Elevated but not clearly stressed
            return 0.3
        elif heart_rate <= self.config.heart_rate_stress_max:
            # Stressed range
            normalized = (heart_rate - self.config.heart_rate_stress_min) / \
                       (self.config.heart_rate_stress_max - self.config.heart_rate_stress_min)
            return 0.3 + (normalized * 0.4)  # 0.3 to 0.7
        else:
            # Very high heart rate
            return 1.0
    
    def _analyze_blood_pressure_stress(self, systolic: float) -> float:
        """Analyze blood pressure for stress indicators"""
        if systolic <= self.config.systolic_normal_max:
            return 0.0
        elif systolic <= self.config.systolic_stress_min:
            # Elevated but not clearly stressed
            return 0.3
        else:
            # High blood pressure
            normalized = (systolic - self.config.systolic_stress_min) / 60  # Assume max of 180
            return min(1.0, 0.3 + (normalized * 0.7))
    
    def _analyze_voice_stress(self, voice_stress: float) -> float:
        """Analyze voice stress indicators"""
        if voice_stress <= self.config.voice_tremor_threshold:
            return 0.0
        else:
            normalized = (voice_stress - self.config.voice_tremor_threshold) / \
                       (1.0 - self.config.voice_tremor_threshold)
            return min(1.0, normalized)
    
    def _classify_stress_level(self, stress_score: float) -> StressLevel:
        """Classify stress level based on overall score"""
        if stress_score >= self.alert_thresholds[StressLevel.EMERGENCY]:
            return StressLevel.EMERGENCY
        elif stress_score >= self.alert_thresholds[StressLevel.CRITICAL]:
            return StressLevel.CRITICAL
        elif stress_score >= self.alert_thresholds[StressLevel.HIGH]:
            return StressLevel.HIGH
        elif stress_score >= self.alert_thresholds[StressLevel.ELEVATED]:
            return StressLevel.ELEVATED
        else:
            return StressLevel.NORMAL
    
    def _generate_assessment(self, stress_level: StressLevel, stress_score: float) -> Tuple[str, str]:
        """Generate risk assessment and recommended action"""
        if stress_level == StressLevel.EMERGENCY:
            return (
                "CRITICAL: Extreme stress detected. Possible physical coercion or medical emergency.",
                "IMMEDIATE: Activate emergency protocols, contact authorities, disable wallet access"
            )
        elif stress_level == StressLevel.CRITICAL:
            return (
                "HIGH RISK: Severe stress indicators detected. Potential threat situation.",
                "URGENT: Verify user safety, consider emergency protocols, increase security monitoring"
            )
        elif stress_level == StressLevel.HIGH:
            return (
                "MODERATE RISK: Elevated stress levels detected. Monitor closely.",
                "CAUTION: Verify user identity, check for unusual behavior, consider additional authentication"
            )
        elif stress_level == StressLevel.ELEVATED:
            return (
                "LOW RISK: Slightly elevated stress levels. Normal variation possible.",
                "MONITOR: Continue normal operation, watch for escalation"
            )
        else:
            return (
                "NORMAL: Stress levels within normal range.",
                "CONTINUE: Normal operation, maintain standard security protocols"
            )
    
    def _handle_stress_detection(self, stress_analysis: StressAnalysis):
        """Handle stress detection events"""
        self.logger.info(f"Stress detected: {stress_analysis.overall_stress_level.value} "
                        f"(score: {stress_analysis.stress_score:.2f})")
        
        # Trigger callbacks
        for callback in self.stress_callbacks:
            try:
                callback(stress_analysis)
            except Exception as e:
                self.logger.error(f"Error in stress callback: {e}")
        
        # Handle emergency situations
        if stress_analysis.requires_immediate_attention:
            for callback in self.emergency_callbacks:
                try:
                    callback(stress_analysis)
                except Exception as e:
                    self.logger.error(f"Error in emergency callback: {e}")
    
    def get_current_stress_level(self) -> Optional[StressLevel]:
        """Get the most recent stress level"""
        if self.stress_history:
            return self.stress_history[-1].overall_stress_level
        return None
    
    def get_stress_history(self, duration_seconds: int = 300) -> List[StressAnalysis]:
        """Get stress analysis history for the specified duration"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        return [analysis for analysis in self.stress_history 
                if analysis.timestamp >= cutoff_time]
    
    def export_stress_data(self, filepath: str):
        """Export stress analysis data to JSON file"""
        data = {
            'stress_analyses': [
                {
                    'timestamp': analysis.timestamp,
                    'stress_level': analysis.overall_stress_level.value,
                    'stress_score': analysis.stress_score,
                    'confidence': analysis.confidence,
                    'risk_assessment': analysis.risk_assessment,
                    'recommended_action': analysis.recommended_action,
                    'individual_indicators': {
                        indicator.value: score 
                        for indicator, score in analysis.individual_indicators.items()
                    }
                }
                for analysis in self.stress_history
            ],
            'baseline_measurements': {
                indicator.value: value 
                for indicator, value in self.baseline_measurements.items()
            },
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Stress data exported to {filepath}")
    
    def reset_baseline(self):
        """Reset baseline measurements and re-establish them"""
        self.baseline_measurements = {}
        self.baseline_established = False
        self.baseline_samples_collected = 0
        self.logger.info("Baseline measurements reset")
