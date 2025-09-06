"""
Card Edge Electromagnetic Sensor System
======================================

Advanced electromagnetic sensor system that detects and analyzes electromagnetic
signals around the edges of crypto cards. Uses AI to map out and render statistical
analysis based images of the electromagnetic field patterns.

Features:
- Multi-frequency EM field detection
- Real-time signal analysis
- AI-powered pattern recognition
- Statistical visualization rendering
- Threat detection through EM signatures
- Card authentication via EM fingerprinting
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
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import cv2

class EMSignalType(Enum):
    """Types of electromagnetic signals detected"""
    MAGNETIC_FIELD = "magnetic_field"
    ELECTRIC_FIELD = "electric_field"
    RADIO_FREQUENCY = "radio_frequency"
    INFRARED = "infrared"
    THERMAL = "thermal"
    UNKNOWN = "unknown"

class SignalStrength(Enum):
    """Signal strength classifications"""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class ThreatLevel(Enum):
    """Threat level based on EM analysis"""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"

@dataclass
class EMSignalReading:
    """Individual EM signal reading"""
    timestamp: float
    signal_type: EMSignalType
    frequency: float  # Hz
    amplitude: float  # V or T
    phase: float  # radians
    position: Tuple[float, float]  # x, y coordinates around card edge
    strength: SignalStrength
    quality: float  # 0-1 signal quality
    metadata: Dict[str, Any] = None

@dataclass
class EMFieldMap:
    """Electromagnetic field map around card"""
    timestamp: float
    signal_readings: List[EMSignalReading]
    field_strength_map: np.ndarray  # 2D array of field strengths
    frequency_spectrum: Dict[float, float]  # frequency -> amplitude
    anomaly_detected: bool
    threat_level: ThreatLevel
    confidence: float

@dataclass
class StatisticalAnalysis:
    """Statistical analysis of EM signals"""
    mean_amplitude: float
    std_amplitude: float
    frequency_dominance: float
    spatial_correlation: float
    temporal_stability: float
    anomaly_score: float
    pattern_complexity: float

class CardEdgeSensor:
    """
    Advanced electromagnetic sensor system for crypto card analysis
    
    Detects and analyzes electromagnetic signals around card edges
    using multiple sensor arrays and AI-powered analysis.
    """
    
    def __init__(self, sensor_resolution: int = 64, 
                 frequency_range: Tuple[float, float] = (1e3, 1e9)):
        self.sensor_resolution = sensor_resolution
        self.frequency_range = frequency_range
        self.logger = logging.getLogger(__name__)
        
        # Sensor configuration
        self.sensor_positions = self._generate_sensor_positions()
        self.active_sensors = set()
        
        # Data storage
        self.signal_history = deque(maxlen=10000)
        self.field_maps = deque(maxlen=100)
        self.statistical_analyses = deque(maxlen=1000)
        
        # Processing state
        self.is_scanning = False
        self.scanning_thread = None
        self.stop_scanning = threading.Event()
        
        # AI analysis
        self.pattern_analyzer = MockPatternAnalyzer()
        self.threat_detector = MockThreatDetector()
        self.visualization_engine = MockVisualizationEngine()
        
        # Callbacks
        self.signal_callbacks: List[Callable] = []
        self.threat_callbacks: List[Callable] = []
        self.analysis_callbacks: List[Callable] = []
        
        # Card detection
        self.card_detected = False
        self.card_position = None
        self.card_orientation = 0.0
        
        self.logger.info("Card edge sensor system initialized")
    
    def _generate_sensor_positions(self) -> List[Tuple[float, float]]:
        """Generate sensor positions around card edge"""
        positions = []
        
        # Card dimensions (standard credit card size: 85.6mm x 53.98mm)
        card_width = 85.6
        card_height = 53.98
        sensor_spacing = 2.0  # mm
        
        # Top edge
        for x in np.arange(0, card_width, sensor_spacing):
            positions.append((x, card_height + 1))
        
        # Bottom edge
        for x in np.arange(0, card_width, sensor_spacing):
            positions.append((x, -1))
        
        # Left edge
        for y in np.arange(0, card_height, sensor_spacing):
            positions.append((-1, y))
        
        # Right edge
        for y in np.arange(0, card_height, sensor_spacing):
            positions.append((card_width + 1, y))
        
        return positions
    
    def start_scanning(self):
        """Start EM signal scanning"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.stop_scanning.clear()
        self.scanning_thread = threading.Thread(target=self._scanning_loop, daemon=True)
        self.scanning_thread.start()
        self.logger.info("EM signal scanning started")
    
    def stop_scanning(self):
        """Stop EM signal scanning"""
        if not self.is_scanning:
            return
        
        self.is_scanning = False
        self.stop_scanning.set()
        if self.scanning_thread:
            self.scanning_thread.join(timeout=5)
        self.logger.info("EM signal scanning stopped")
    
    def _scanning_loop(self):
        """Main scanning loop"""
        while not self.stop_scanning.is_set():
            try:
                # Scan all active sensors
                for sensor_pos in self.active_sensors:
                    self._scan_sensor_position(sensor_pos)
                
                # Perform analysis if we have enough data
                if len(self.signal_history) >= 100:
                    self._perform_analysis()
                
                time.sleep(0.01)  # 100Hz scanning rate
                
            except Exception as e:
                self.logger.error(f"Error in scanning loop: {e}")
                time.sleep(0.01)
    
    def _scan_sensor_position(self, position: Tuple[float, float]):
        """Scan a specific sensor position for EM signals"""
        # In a real implementation, this would interface with actual EM sensors
        # For simulation, we'll generate mock signal data
        
        current_time = time.time()
        
        # Simulate different types of EM signals
        signal_types = [EMSignalType.MAGNETIC_FIELD, EMSignalType.ELECTRIC_FIELD, 
                       EMSignalType.RADIO_FREQUENCY, EMSignalType.INFRARED]
        
        for signal_type in signal_types:
            # Generate mock signal reading
            reading = self._generate_mock_signal_reading(position, signal_type, current_time)
            if reading:
                self.signal_history.append(reading)
                
                # Trigger callbacks
                for callback in self.signal_callbacks:
                    try:
                        callback(reading)
                    except Exception as e:
                        self.logger.error(f"Error in signal callback: {e}")
    
    def _generate_mock_signal_reading(self, position: Tuple[float, float], 
                                    signal_type: EMSignalType, 
                                    timestamp: float) -> Optional[EMSignalReading]:
        """Generate mock EM signal reading"""
        try:
            # Generate frequency based on signal type
            if signal_type == EMSignalType.MAGNETIC_FIELD:
                frequency = np.random.uniform(1e3, 1e6)  # 1kHz to 1MHz
                base_amplitude = np.random.uniform(1e-9, 1e-6)  # Tesla
            elif signal_type == EMSignalType.ELECTRIC_FIELD:
                frequency = np.random.uniform(1e3, 1e7)  # 1kHz to 10MHz
                base_amplitude = np.random.uniform(1e-3, 1e-1)  # V/m
            elif signal_type == EMSignalType.RADIO_FREQUENCY:
                frequency = np.random.uniform(1e6, 1e9)  # 1MHz to 1GHz
                base_amplitude = np.random.uniform(1e-6, 1e-3)  # V/m
            elif signal_type == EMSignalType.INFRARED:
                frequency = np.random.uniform(1e12, 1e14)  # THz range
                base_amplitude = np.random.uniform(1e-6, 1e-4)  # W/m²
            else:
                frequency = np.random.uniform(1e3, 1e9)
                base_amplitude = np.random.uniform(1e-6, 1e-3)
            
            # Add position-based variation
            x, y = position
            position_factor = 1.0 + 0.1 * np.sin(x * 0.1) * np.cos(y * 0.1)
            amplitude = base_amplitude * position_factor
            
            # Add some noise
            noise = np.random.normal(0, 0.1 * amplitude)
            amplitude += noise
            
            # Determine signal strength
            if amplitude < 1e-8:
                strength = SignalStrength.VERY_WEAK
            elif amplitude < 1e-6:
                strength = SignalStrength.WEAK
            elif amplitude < 1e-4:
                strength = SignalStrength.MODERATE
            elif amplitude < 1e-2:
                strength = SignalStrength.STRONG
            else:
                strength = SignalStrength.VERY_STRONG
            
            # Calculate quality (simulate sensor quality)
            quality = np.random.uniform(0.7, 0.95)
            
            # Generate phase
            phase = np.random.uniform(0, 2 * np.pi)
            
            reading = EMSignalReading(
                timestamp=timestamp,
                signal_type=signal_type,
                frequency=frequency,
                amplitude=amplitude,
                phase=phase,
                position=position,
                strength=strength,
                quality=quality,
                metadata={'sensor_id': f"sensor_{hash(position) % 1000}"}
            )
            
            return reading
            
        except Exception as e:
            self.logger.error(f"Error generating mock signal reading: {e}")
            return None
    
    def _perform_analysis(self):
        """Perform comprehensive EM signal analysis"""
        if len(self.signal_history) < 50:
            return
        
        # Get recent signals (last 5 seconds)
        current_time = time.time()
        recent_signals = [
            s for s in self.signal_history 
            if current_time - s.timestamp <= 5.0
        ]
        
        if not recent_signals:
            return
        
        # Create field map
        field_map = self._create_field_map(recent_signals)
        if field_map:
            self.field_maps.append(field_map)
            
            # Perform statistical analysis
            statistical_analysis = self._perform_statistical_analysis(recent_signals)
            if statistical_analysis:
                self.statistical_analyses.append(statistical_analysis)
                
                # Trigger analysis callbacks
                for callback in self.analysis_callbacks:
                    try:
                        callback(field_map, statistical_analysis)
                    except Exception as e:
                        self.logger.error(f"Error in analysis callback: {e}")
    
    def _create_field_map(self, signals: List[EMSignalReading]) -> Optional[EMFieldMap]:
        """Create electromagnetic field map from signals"""
        if not signals:
            return None
        
        # Group signals by type
        signals_by_type = {}
        for signal in signals:
            signal_type = signal.signal_type
            if signal_type not in signals_by_type:
                signals_by_type[signal_type] = []
            signals_by_type[signal_type].append(signal)
        
        # Create field strength map for each signal type
        field_strength_maps = {}
        for signal_type, type_signals in signals_by_type.items():
            field_map = self._create_2d_field_map(type_signals)
            if field_map is not None:
                field_strength_maps[signal_type] = field_map
        
        # Combine all field maps
        combined_field_map = self._combine_field_maps(field_strength_maps)
        
        # Analyze frequency spectrum
        frequency_spectrum = self._analyze_frequency_spectrum(signals)
        
        # Detect anomalies
        anomaly_detected = self._detect_anomalies(combined_field_map, frequency_spectrum)
        
        # Determine threat level
        threat_level = self._assess_threat_level(combined_field_map, anomaly_detected)
        
        # Calculate confidence
        confidence = self._calculate_field_map_confidence(signals, combined_field_map)
        
        field_map = EMFieldMap(
            timestamp=time.time(),
            signal_readings=signals,
            field_strength_map=combined_field_map,
            frequency_spectrum=frequency_spectrum,
            anomaly_detected=anomaly_detected,
            threat_level=threat_level,
            confidence=confidence
        )
        
        return field_map
    
    def _create_2d_field_map(self, signals: List[EMSignalReading]) -> Optional[np.ndarray]:
        """Create 2D field strength map from signals"""
        if not signals:
            return None
        
        # Create grid
        x_coords = [s.position[0] for s in signals]
        y_coords = [s.position[1] for s in signals]
        
        if not x_coords or not y_coords:
            return None
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Add padding
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1
        
        x_min -= x_padding
        x_max += x_padding
        y_min -= y_padding
        y_max += y_padding
        
        # Create grid
        x_grid = np.linspace(x_min, x_max, self.sensor_resolution)
        y_grid = np.linspace(y_min, y_max, self.sensor_resolution)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # Interpolate field strength
        field_strength = np.zeros_like(X)
        
        for signal in signals:
            x, y = signal.position
            amplitude = signal.amplitude
            
            # Find closest grid points
            x_idx = np.argmin(np.abs(x_grid - x))
            y_idx = np.argmin(np.abs(y_grid - y))
            
            # Add signal contribution with Gaussian spread
            sigma = 2.0  # Spread parameter
            for i in range(max(0, y_idx - 3), min(self.sensor_resolution, y_idx + 4)):
                for j in range(max(0, x_idx - 3), min(self.sensor_resolution, x_idx + 4)):
                    distance = np.sqrt((X[i, j] - x)**2 + (Y[i, j] - y)**2)
                    weight = np.exp(-(distance**2) / (2 * sigma**2))
                    field_strength[i, j] += amplitude * weight
        
        return field_strength
    
    def _combine_field_maps(self, field_maps: Dict[EMSignalType, np.ndarray]) -> np.ndarray:
        """Combine multiple field maps into a single map"""
        if not field_maps:
            return np.zeros((self.sensor_resolution, self.sensor_resolution))
        
        # Normalize each field map
        normalized_maps = {}
        for signal_type, field_map in field_maps.items():
            if field_map is not None and field_map.size > 0:
                normalized_maps[signal_type] = field_map / np.max(np.abs(field_map))
        
        # Combine with weighted average
        weights = {
            EMSignalType.MAGNETIC_FIELD: 0.3,
            EMSignalType.ELECTRIC_FIELD: 0.3,
            EMSignalType.RADIO_FREQUENCY: 0.2,
            EMSignalType.INFRARED: 0.2
        }
        
        combined_map = np.zeros((self.sensor_resolution, self.sensor_resolution))
        total_weight = 0.0
        
        for signal_type, field_map in normalized_maps.items():
            weight = weights.get(signal_type, 0.1)
            combined_map += field_map * weight
            total_weight += weight
        
        if total_weight > 0:
            combined_map /= total_weight
        
        return combined_map
    
    def _analyze_frequency_spectrum(self, signals: List[EMSignalReading]) -> Dict[float, float]:
        """Analyze frequency spectrum of signals"""
        frequency_spectrum = {}
        
        for signal in signals:
            freq = signal.frequency
            amplitude = signal.amplitude
            
            if freq in frequency_spectrum:
                frequency_spectrum[freq] = max(frequency_spectrum[freq], amplitude)
            else:
                frequency_spectrum[freq] = amplitude
        
        return frequency_spectrum
    
    def _detect_anomalies(self, field_map: np.ndarray, 
                         frequency_spectrum: Dict[float, float]) -> bool:
        """Detect anomalies in EM field patterns"""
        if field_map.size == 0:
            return False
        
        # Check for unusual field strength patterns
        field_std = np.std(field_map)
        field_mean = np.mean(field_map)
        
        # Anomaly if standard deviation is too high
        if field_std > 3 * field_mean:
            return True
        
        # Check for unusual frequency components
        if frequency_spectrum:
            frequencies = list(frequency_spectrum.keys())
            amplitudes = list(frequency_spectrum.values())
            
            # Anomaly if there are very high frequency components
            high_freq_threshold = 1e8  # 100 MHz
            high_freq_amplitudes = [amp for freq, amp in frequency_spectrum.items() 
                                  if freq > high_freq_threshold]
            
            if high_freq_amplitudes and max(high_freq_amplitudes) > np.mean(amplitudes) * 2:
                return True
        
        return False
    
    def _assess_threat_level(self, field_map: np.ndarray, anomaly_detected: bool) -> ThreatLevel:
        """Assess threat level based on field analysis"""
        if anomaly_detected:
            return ThreatLevel.CRITICAL
        
        if field_map.size == 0:
            return ThreatLevel.NORMAL
        
        # Calculate field strength metrics
        max_strength = np.max(np.abs(field_map))
        mean_strength = np.mean(np.abs(field_map))
        std_strength = np.std(field_map)
        
        # Assess based on field characteristics
        if max_strength > mean_strength * 5 and std_strength > mean_strength * 2:
            return ThreatLevel.HIGH_RISK
        elif max_strength > mean_strength * 3 or std_strength > mean_strength * 1.5:
            return ThreatLevel.SUSPICIOUS
        else:
            return ThreatLevel.NORMAL
    
    def _calculate_field_map_confidence(self, signals: List[EMSignalReading], 
                                      field_map: np.ndarray) -> float:
        """Calculate confidence in field map analysis"""
        if not signals or field_map.size == 0:
            return 0.0
        
        # Base confidence on number of signals and their quality
        signal_count = len(signals)
        avg_quality = np.mean([s.quality for s in signals])
        
        # Normalize signal count (more signals = higher confidence)
        count_confidence = min(1.0, signal_count / 100.0)
        
        # Overall confidence
        confidence = (count_confidence * 0.6 + avg_quality * 0.4)
        return min(1.0, confidence)
    
    def _perform_statistical_analysis(self, signals: List[EMSignalReading]) -> Optional[StatisticalAnalysis]:
        """Perform statistical analysis of EM signals"""
        if not signals:
            return None
        
        amplitudes = [s.amplitude for s in signals]
        frequencies = [s.frequency for s in signals]
        
        # Basic statistics
        mean_amplitude = np.mean(amplitudes)
        std_amplitude = np.std(amplitudes)
        
        # Frequency analysis
        freq_hist, freq_bins = np.histogram(frequencies, bins=20)
        dominant_freq_idx = np.argmax(freq_hist)
        frequency_dominance = freq_hist[dominant_freq_idx] / len(frequencies)
        
        # Spatial correlation
        positions = [s.position for s in signals]
        if len(positions) > 1:
            x_coords = [p[0] for p in positions]
            y_coords = [p[1] for p in positions]
            spatial_correlation = np.corrcoef(x_coords, y_coords)[0, 1]
            spatial_correlation = abs(spatial_correlation) if not np.isnan(spatial_correlation) else 0.0
        else:
            spatial_correlation = 0.0
        
        # Temporal stability
        timestamps = [s.timestamp for s in signals]
        if len(timestamps) > 1:
            time_diffs = np.diff(timestamps)
            temporal_stability = 1.0 / (1.0 + np.std(time_diffs)) if len(time_diffs) > 0 else 0.0
        else:
            temporal_stability = 0.0
        
        # Anomaly score
        anomaly_score = self._calculate_anomaly_score(amplitudes, frequencies)
        
        # Pattern complexity
        pattern_complexity = self._calculate_pattern_complexity(amplitudes, frequencies)
        
        analysis = StatisticalAnalysis(
            mean_amplitude=mean_amplitude,
            std_amplitude=std_amplitude,
            frequency_dominance=frequency_dominance,
            spatial_correlation=spatial_correlation,
            temporal_stability=temporal_stability,
            anomaly_score=anomaly_score,
            pattern_complexity=pattern_complexity
        )
        
        return analysis
    
    def _calculate_anomaly_score(self, amplitudes: List[float], 
                               frequencies: List[float]) -> float:
        """Calculate anomaly score for signals"""
        if len(amplitudes) < 3:
            return 0.0
        
        # Calculate z-scores for amplitudes
        amp_mean = np.mean(amplitudes)
        amp_std = np.std(amplitudes)
        
        if amp_std == 0:
            return 0.0
        
        z_scores = [abs((amp - amp_mean) / amp_std) for amp in amplitudes]
        anomaly_score = np.mean(z_scores)
        
        # Normalize to 0-1 range
        return min(1.0, anomaly_score / 3.0)  # 3-sigma rule
    
    def _calculate_pattern_complexity(self, amplitudes: List[float], 
                                    frequencies: List[float]) -> float:
        """Calculate pattern complexity of signals"""
        if len(amplitudes) < 3:
            return 0.0
        
        # Calculate entropy of amplitude distribution
        amp_hist, _ = np.histogram(amplitudes, bins=10)
        amp_probs = amp_hist / np.sum(amp_hist)
        amp_probs = amp_probs[amp_probs > 0]  # Remove zero probabilities
        
        entropy = -np.sum(amp_probs * np.log2(amp_probs))
        
        # Normalize entropy (max entropy for 10 bins is log2(10) ≈ 3.32)
        normalized_entropy = entropy / np.log2(10)
        
        return min(1.0, normalized_entropy)
    
    def render_statistical_image(self, field_map: EMFieldMap, 
                               output_path: str) -> bool:
        """Render statistical analysis as an image"""
        try:
            # Create figure
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Electromagnetic Field Analysis', fontsize=16)
            
            # Field strength map
            ax1 = axes[0, 0]
            im1 = ax1.imshow(field_map.field_strength_map, cmap='viridis', 
                           interpolation='bilinear', origin='lower')
            ax1.set_title('Field Strength Map')
            ax1.set_xlabel('X Position (mm)')
            ax1.set_ylabel('Y Position (mm)')
            plt.colorbar(im1, ax=ax1, label='Field Strength')
            
            # Frequency spectrum
            ax2 = axes[0, 1]
            if field_map.frequency_spectrum:
                frequencies = list(field_map.frequency_spectrum.keys())
                amplitudes = list(field_map.frequency_spectrum.values())
                ax2.semilogy(frequencies, amplitudes, 'b-', linewidth=2)
                ax2.set_title('Frequency Spectrum')
                ax2.set_xlabel('Frequency (Hz)')
                ax2.set_ylabel('Amplitude')
                ax2.grid(True, alpha=0.3)
            
            # Signal distribution
            ax3 = axes[1, 0]
            signal_types = [s.signal_type.value for s in field_map.signal_readings]
            type_counts = {}
            for signal_type in signal_types:
                type_counts[signal_type] = type_counts.get(signal_type, 0) + 1
            
            if type_counts:
                ax3.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
                ax3.set_title('Signal Type Distribution')
            
            # Threat assessment
            ax4 = axes[1, 1]
            threat_colors = {
                'normal': 'green',
                'suspicious': 'yellow',
                'high_risk': 'orange',
                'critical': 'red'
            }
            
            threat_level = field_map.threat_level.value
            color = threat_colors.get(threat_level, 'gray')
            
            ax4.text(0.5, 0.7, f'Threat Level: {threat_level.upper()}', 
                    ha='center', va='center', fontsize=14, weight='bold', color=color)
            ax4.text(0.5, 0.5, f'Anomaly Detected: {"Yes" if field_map.anomaly_detected else "No"}', 
                    ha='center', va='center', fontsize=12)
            ax4.text(0.5, 0.3, f'Confidence: {field_map.confidence:.2f}', 
                    ha='center', va='center', fontsize=12)
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
            ax4.axis('off')
            ax4.set_title('Threat Assessment')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Statistical analysis image saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rendering statistical image: {e}")
            return False
    
    def activate_sensor(self, position: Tuple[float, float]):
        """Activate a specific sensor position"""
        self.active_sensors.add(position)
        self.logger.debug(f"Sensor activated at position {position}")
    
    def deactivate_sensor(self, position: Tuple[float, float]):
        """Deactivate a specific sensor position"""
        self.active_sensors.discard(position)
        self.logger.debug(f"Sensor deactivated at position {position}")
    
    def activate_all_sensors(self):
        """Activate all available sensors"""
        self.active_sensors = set(self.sensor_positions)
        self.logger.info("All sensors activated")
    
    def deactivate_all_sensors(self):
        """Deactivate all sensors"""
        self.active_sensors.clear()
        self.logger.info("All sensors deactivated")
    
    def add_signal_callback(self, callback: Callable):
        """Add callback for signal detection events"""
        self.signal_callbacks.append(callback)
    
    def add_threat_callback(self, callback: Callable):
        """Add callback for threat detection events"""
        self.threat_callbacks.append(callback)
    
    def add_analysis_callback(self, callback: Callable):
        """Add callback for analysis events"""
        self.analysis_callbacks.append(callback)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current sensor system status"""
        return {
            'is_scanning': self.is_scanning,
            'active_sensors': len(self.active_sensors),
            'total_sensors': len(self.sensor_positions),
            'signal_history_size': len(self.signal_history),
            'field_maps_count': len(self.field_maps),
            'statistical_analyses_count': len(self.statistical_analyses),
            'card_detected': self.card_detected
        }
    
    def export_sensor_data(self, filepath: str):
        """Export sensor data to JSON file"""
        data = {
            'export_timestamp': time.time(),
            'sensor_configuration': {
                'resolution': self.sensor_resolution,
                'frequency_range': self.frequency_range,
                'sensor_positions': self.sensor_positions,
                'active_sensors': list(self.active_sensors)
            },
            'field_maps': [
                {
                    'timestamp': field_map.timestamp,
                    'anomaly_detected': field_map.anomaly_detected,
                    'threat_level': field_map.threat_level.value,
                    'confidence': field_map.confidence,
                    'frequency_spectrum': field_map.frequency_spectrum,
                    'signal_count': len(field_map.signal_readings)
                }
                for field_map in self.field_maps
            ],
            'statistical_analyses': [
                {
                    'mean_amplitude': analysis.mean_amplitude,
                    'std_amplitude': analysis.std_amplitude,
                    'frequency_dominance': analysis.frequency_dominance,
                    'spatial_correlation': analysis.spatial_correlation,
                    'temporal_stability': analysis.temporal_stability,
                    'anomaly_score': analysis.anomaly_score,
                    'pattern_complexity': analysis.pattern_complexity
                }
                for analysis in self.statistical_analyses
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Sensor data exported to {filepath}")


# Mock AI Analysis Classes
class MockPatternAnalyzer:
    def analyze_patterns(self, field_map):
        # Mock pattern analysis
        return {'pattern_type': 'complex', 'confidence': 0.8}

class MockThreatDetector:
    def detect_threats(self, field_map):
        # Mock threat detection
        return {'threat_level': 'low', 'confidence': 0.7}

class MockVisualizationEngine:
    def render_visualization(self, data):
        # Mock visualization
        return True
