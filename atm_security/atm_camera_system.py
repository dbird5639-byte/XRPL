"""
ATM Camera System
================

AI-powered camera system for crypto ATMs with advanced computer vision capabilities:
- Multi-person detection and tracking
- Real-time face recognition
- Crowd density analysis
- Movement pattern monitoring
- Threat assessment

Features:
- High-resolution multi-camera setup
- Real-time processing pipeline
- Edge computing optimization
- Privacy-preserving analytics
- Emergency response integration
"""

import time
import logging
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import json
from collections import deque
import math

class CameraPosition(Enum):
    """Camera positions in ATM setup"""
    FRONT_MAIN = "front_main"
    FRONT_OVERHEAD = "front_overhead"
    SIDE_LEFT = "side_left"
    SIDE_RIGHT = "side_right"
    REAR_SECURITY = "rear_security"
    CARD_READER = "card_reader"

class DetectionStatus(Enum):
    """Detection status for different scenarios"""
    NORMAL = "normal"
    MULTIPLE_PEOPLE = "multiple_people"
    CROWD_DETECTED = "crowd_detected"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    THREAT_DETECTED = "threat_detected"
    EMERGENCY = "emergency"

@dataclass
class PersonDetection:
    """Individual person detection result"""
    person_id: int
    face_bbox: Tuple[int, int, int, int]  # x, y, width, height
    face_confidence: float
    body_bbox: Optional[Tuple[int, int, int, int]]
    body_confidence: float
    face_landmarks: List[Tuple[int, int]]
    age_estimate: Optional[int]
    gender_estimate: Optional[str]
    emotion_scores: Dict[str, float]
    pose_angles: Dict[str, float]
    timestamp: float
    camera_id: str

@dataclass
class CrowdAnalysis:
    """Crowd density and behavior analysis"""
    person_count: int
    density_score: float  # 0.0 to 1.0
    crowd_formation: str  # "scattered", "grouped", "line", "circle"
    movement_velocity: float
    movement_direction: Tuple[float, float]
    threat_level: float  # 0.0 to 1.0
    timestamp: float

@dataclass
class CameraConfig:
    """Configuration for ATM camera system"""
    # Camera settings
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    exposure_mode: str = "auto"
    white_balance: str = "auto"
    
    # Detection settings
    face_detection_confidence: float = 0.7
    body_detection_confidence: float = 0.6
    tracking_max_disappeared: int = 30
    tracking_max_distance: int = 50
    
    # Analysis settings
    emotion_analysis_enabled: bool = True
    age_gender_estimation_enabled: bool = True
    pose_estimation_enabled: bool = True
    crowd_analysis_enabled: bool = True
    
    # Security settings
    max_persons_normal: int = 2
    crowd_threshold: int = 4
    threat_analysis_enabled: bool = True
    
    # Performance settings
    processing_interval: float = 0.1  # seconds
    max_detection_history: int = 100
    enable_edge_processing: bool = True

class ATMCameraSystem:
    """
    Advanced AI-powered camera system for crypto ATMs
    
    Provides real-time multi-person detection, face recognition,
    and behavioral analysis for enhanced security.
    """
    
    def __init__(self, config: CameraConfig = None):
        self.config = config or CameraConfig()
        self.logger = logging.getLogger(__name__)
        
        # Camera management
        self.cameras: Dict[str, Any] = {}
        self.camera_positions = list(CameraPosition)
        
        # Detection state
        self.detection_history = deque(maxlen=self.config.max_detection_history)
        self.active_detections: Dict[int, PersonDetection] = {}
        self.person_counter = 0
        
        # Analysis state
        self.crowd_analysis = None
        self.current_status = DetectionStatus.NORMAL
        
        # Processing pipeline
        self.is_processing = False
        self.processing_thread = None
        self.stop_processing = threading.Event()
        
        # Callbacks
        self.detection_callbacks: List[Callable] = []
        self.threat_callbacks: List[Callable] = []
        self.emergency_callbacks: List[Callable] = []
        
        # AI models (simulated)
        self.face_detector = None
        self.body_detector = None
        self.emotion_analyzer = None
        self.age_gender_estimator = None
        self.pose_estimator = None
        
        # Initialize AI models
        self._initialize_ai_models()
        
        # Start processing
        self.start_processing()
    
    def _initialize_ai_models(self):
        """Initialize AI models for computer vision tasks"""
        # In a real implementation, this would load actual AI models
        # For simulation, we'll create mock models
        
        self.face_detector = MockFaceDetector()
        self.body_detector = MockBodyDetector()
        self.emotion_analyzer = MockEmotionAnalyzer()
        self.age_gender_estimator = MockAgeGenderEstimator()
        self.pose_estimator = MockPoseEstimator()
        
        self.logger.info("AI models initialized for ATM camera system")
    
    def add_camera(self, camera_id: str, position: CameraPosition, 
                   camera_source: Any = None) -> bool:
        """
        Add a camera to the system
        
        Args:
            camera_id: Unique identifier for the camera
            position: Physical position of the camera
            camera_source: Camera source (cv2.VideoCapture, IP stream, etc.)
        
        Returns:
            Success status
        """
        try:
            # In a real implementation, this would initialize actual cameras
            # For simulation, we'll create mock camera objects
            
            camera_info = {
                'id': camera_id,
                'position': position,
                'source': camera_source,
                'is_active': True,
                'last_frame': None,
                'frame_count': 0
            }
            
            self.cameras[camera_id] = camera_info
            self.logger.info(f"Camera {camera_id} added at position {position.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add camera {camera_id}: {e}")
            return False
    
    def start_processing(self):
        """Start the camera processing pipeline"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.stop_processing.clear()
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        self.logger.info("Camera processing started")
    
    def stop_processing(self):
        """Stop the camera processing pipeline"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        self.stop_processing.set()
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        self.logger.info("Camera processing stopped")
    
    def _processing_loop(self):
        """Main processing loop for camera analysis"""
        while not self.stop_processing.is_set():
            try:
                # Process all active cameras
                for camera_id, camera_info in self.cameras.items():
                    if camera_info['is_active']:
                        self._process_camera(camera_id, camera_info)
                
                # Perform crowd analysis
                if self.config.crowd_analysis_enabled:
                    self._analyze_crowd()
                
                # Update detection status
                self._update_detection_status()
                
                time.sleep(self.config.processing_interval)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(self.config.processing_interval)
    
    def _process_camera(self, camera_id: str, camera_info: Dict[str, Any]):
        """Process a single camera feed"""
        # In a real implementation, this would capture actual frames
        # For simulation, we'll generate mock frame data
        
        frame = self._generate_mock_frame(camera_id)
        if frame is None:
            return
        
        # Detect faces
        face_detections = self.face_detector.detect_faces(frame)
        
        # Detect bodies
        body_detections = self.body_detector.detect_bodies(frame)
        
        # Process each detection
        for face_det in face_detections:
            person_detection = self._create_person_detection(
                camera_id, face_det, body_detections, frame
            )
            
            if person_detection:
                self._update_person_tracking(person_detection)
        
        # Update camera info
        camera_info['last_frame'] = frame
        camera_info['frame_count'] += 1
    
    def _generate_mock_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Generate mock frame data for simulation"""
        # In a real implementation, this would capture actual camera frames
        # For simulation, we'll create random frame data
        
        height, width = self.config.resolution[1], self.config.resolution[0]
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        
        # Add some variation to simulate real camera data
        noise = np.random.normal(0, 10, frame.shape).astype(np.uint8)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return frame
    
    def _create_person_detection(self, camera_id: str, face_det: Dict[str, Any], 
                               body_detections: List[Dict[str, Any]], 
                               frame: np.ndarray) -> Optional[PersonDetection]:
        """Create a person detection from face and body detections"""
        try:
            # Generate unique person ID
            person_id = self.person_counter
            self.person_counter += 1
            
            # Extract face information
            face_bbox = face_det.get('bbox', (0, 0, 100, 100))
            face_confidence = face_det.get('confidence', 0.8)
            face_landmarks = face_det.get('landmarks', [])
            
            # Find matching body detection
            body_bbox = None
            body_confidence = 0.0
            if body_detections:
                # Simple matching based on proximity
                body_bbox = body_detections[0].get('bbox', None)
                body_confidence = body_detections[0].get('confidence', 0.0)
            
            # Analyze emotions
            emotion_scores = {}
            if self.config.emotion_analysis_enabled:
                emotion_scores = self.emotion_analyzer.analyze_emotions(frame, face_bbox)
            
            # Estimate age and gender
            age_estimate = None
            gender_estimate = None
            if self.config.age_gender_estimation_enabled:
                age_estimate = self.age_gender_estimator.estimate_age(frame, face_bbox)
                gender_estimate = self.age_gender_estimator.estimate_gender(frame, face_bbox)
            
            # Estimate pose
            pose_angles = {}
            if self.config.pose_estimation_enabled:
                pose_angles = self.pose_estimator.estimate_pose(frame, body_bbox or face_bbox)
            
            detection = PersonDetection(
                person_id=person_id,
                face_bbox=face_bbox,
                face_confidence=face_confidence,
                body_bbox=body_bbox,
                body_confidence=body_confidence,
                face_landmarks=face_landmarks,
                age_estimate=age_estimate,
                gender_estimate=gender_estimate,
                emotion_scores=emotion_scores,
                pose_angles=pose_angles,
                timestamp=time.time(),
                camera_id=camera_id
            )
            
            return detection
            
        except Exception as e:
            self.logger.error(f"Error creating person detection: {e}")
            return None
    
    def _update_person_tracking(self, detection: PersonDetection):
        """Update person tracking with new detection"""
        person_id = detection.person_id
        
        # Store detection
        self.active_detections[person_id] = detection
        self.detection_history.append(detection)
        
        # Trigger callbacks
        for callback in self.detection_callbacks:
            try:
                callback(detection)
            except Exception as e:
                self.logger.error(f"Error in detection callback: {e}")
    
    def _analyze_crowd(self):
        """Analyze crowd density and behavior"""
        if not self.active_detections:
            self.crowd_analysis = None
            return
        
        # Calculate crowd metrics
        person_count = len(self.active_detections)
        density_score = min(1.0, person_count / self.config.crowd_threshold)
        
        # Analyze crowd formation
        crowd_formation = self._analyze_crowd_formation()
        
        # Calculate movement patterns
        movement_velocity, movement_direction = self._analyze_movement_patterns()
        
        # Assess threat level
        threat_level = self._assess_threat_level(person_count, density_score, movement_velocity)
        
        self.crowd_analysis = CrowdAnalysis(
            person_count=person_count,
            density_score=density_score,
            crowd_formation=crowd_formation,
            movement_velocity=movement_velocity,
            movement_direction=movement_direction,
            threat_level=threat_level,
            timestamp=time.time()
        )
    
    def _analyze_crowd_formation(self) -> str:
        """Analyze how people are positioned relative to each other"""
        if len(self.active_detections) < 2:
            return "scattered"
        
        # Simple formation analysis based on positions
        positions = []
        for detection in self.active_detections.values():
            if detection.body_bbox:
                x, y, w, h = detection.body_bbox
                center_x = x + w // 2
                center_y = y + h // 2
                positions.append((center_x, center_y))
        
        if len(positions) < 2:
            return "scattered"
        
        # Analyze spatial distribution
        positions = np.array(positions)
        x_coords = positions[:, 0]
        y_coords = positions[:, 1]
        
        # Check if people are in a line (low y variance)
        y_variance = np.var(y_coords)
        if y_variance < 1000:  # Threshold for line formation
            return "line"
        
        # Check if people are grouped (low overall variance)
        overall_variance = np.var(positions)
        if overall_variance < 5000:  # Threshold for grouped formation
            return "grouped"
        
        return "scattered"
    
    def _analyze_movement_patterns(self) -> Tuple[float, Tuple[float, float]]:
        """Analyze movement patterns of detected people"""
        if len(self.detection_history) < 2:
            return 0.0, (0.0, 0.0)
        
        # Get recent detections
        recent_detections = list(self.detection_history)[-10:]  # Last 10 detections
        
        if len(recent_detections) < 2:
            return 0.0, (0.0, 0.0)
        
        # Calculate movement vectors
        movements = []
        for i in range(1, len(recent_detections)):
            prev_det = recent_detections[i-1]
            curr_det = recent_detections[i]
            
            if prev_det.body_bbox and curr_det.body_bbox:
                prev_x = prev_det.body_bbox[0] + prev_det.body_bbox[2] // 2
                prev_y = prev_det.body_bbox[1] + prev_det.body_bbox[3] // 2
                curr_x = curr_det.body_bbox[0] + curr_det.body_bbox[2] // 2
                curr_y = curr_det.body_bbox[1] + curr_det.body_bbox[3] // 2
                
                dx = curr_x - prev_x
                dy = curr_y - prev_y
                movements.append((dx, dy))
        
        if not movements:
            return 0.0, (0.0, 0.0)
        
        # Calculate average velocity and direction
        movements = np.array(movements)
        velocities = np.sqrt(movements[:, 0]**2 + movements[:, 1]**2)
        avg_velocity = np.mean(velocities)
        
        # Calculate average direction
        avg_dx = np.mean(movements[:, 0])
        avg_dy = np.mean(movements[:, 1])
        direction = (avg_dx, avg_dy)
        
        return avg_velocity, direction
    
    def _assess_threat_level(self, person_count: int, density_score: float, 
                           movement_velocity: float) -> float:
        """Assess overall threat level based on various factors"""
        threat_score = 0.0
        
        # Person count threat
        if person_count > self.config.max_persons_normal:
            threat_score += 0.3
        
        # Density threat
        if density_score > 0.7:
            threat_score += 0.2
        
        # Movement threat (frantic movement)
        if movement_velocity > 50:  # Threshold for frantic movement
            threat_score += 0.3
        
        # Emotion-based threat (if available)
        for detection in self.active_detections.values():
            if 'anger' in detection.emotion_scores and detection.emotion_scores['anger'] > 0.7:
                threat_score += 0.1
            if 'fear' in detection.emotion_scores and detection.emotion_scores['fear'] > 0.7:
                threat_score += 0.1
        
        return min(1.0, threat_score)
    
    def _update_detection_status(self):
        """Update overall detection status based on current analysis"""
        if not self.crowd_analysis:
            self.current_status = DetectionStatus.NORMAL
            return
        
        person_count = self.crowd_analysis.person_count
        threat_level = self.crowd_analysis.threat_level
        
        if threat_level > 0.8:
            self.current_status = DetectionStatus.EMERGENCY
        elif threat_level > 0.6:
            self.current_status = DetectionStatus.THREAT_DETECTED
        elif person_count > self.config.crowd_threshold:
            self.current_status = DetectionStatus.CROWD_DETECTED
        elif person_count > self.config.max_persons_normal:
            self.current_status = DetectionStatus.MULTIPLE_PEOPLE
        else:
            self.current_status = DetectionStatus.NORMAL
        
        # Trigger callbacks for status changes
        if self.current_status in [DetectionStatus.THREAT_DETECTED, DetectionStatus.EMERGENCY]:
            for callback in self.threat_callbacks:
                try:
                    callback(self.current_status, self.crowd_analysis)
                except Exception as e:
                    self.logger.error(f"Error in threat callback: {e}")
    
    def add_detection_callback(self, callback: Callable):
        """Add callback for person detection events"""
        self.detection_callbacks.append(callback)
    
    def add_threat_callback(self, callback: Callable):
        """Add callback for threat detection events"""
        self.threat_callbacks.append(callback)
    
    def add_emergency_callback(self, callback: Callable):
        """Add callback for emergency events"""
        self.emergency_callbacks.append(callback)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'detection_status': self.current_status.value,
            'active_detections': len(self.active_detections),
            'crowd_analysis': {
                'person_count': self.crowd_analysis.person_count if self.crowd_analysis else 0,
                'density_score': self.crowd_analysis.density_score if self.crowd_analysis else 0.0,
                'threat_level': self.crowd_analysis.threat_level if self.crowd_analysis else 0.0,
                'crowd_formation': self.crowd_analysis.crowd_formation if self.crowd_analysis else "unknown"
            },
            'cameras_active': len([c for c in self.cameras.values() if c['is_active']]),
            'processing_active': self.is_processing
        }
    
    def get_detection_history(self, duration_seconds: int = 300) -> List[PersonDetection]:
        """Get detection history for the specified duration"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        return [detection for detection in self.detection_history 
                if detection.timestamp >= cutoff_time]
    
    def export_detection_data(self, filepath: str):
        """Export detection data to JSON file"""
        data = {
            'export_timestamp': time.time(),
            'current_status': self.current_status.value,
            'crowd_analysis': {
                'person_count': self.crowd_analysis.person_count if self.crowd_analysis else 0,
                'density_score': self.crowd_analysis.density_score if self.crowd_analysis else 0.0,
                'threat_level': self.crowd_analysis.threat_level if self.crowd_analysis else 0.0,
                'crowd_formation': self.crowd_analysis.crowd_formation if self.crowd_analysis else "unknown",
                'movement_velocity': self.crowd_analysis.movement_velocity if self.crowd_analysis else 0.0,
                'movement_direction': self.crowd_analysis.movement_direction if self.crowd_analysis else [0.0, 0.0],
                'timestamp': self.crowd_analysis.timestamp if self.crowd_analysis else 0.0
            },
            'detections': [
                {
                    'person_id': detection.person_id,
                    'face_bbox': detection.face_bbox,
                    'face_confidence': detection.face_confidence,
                    'body_bbox': detection.body_bbox,
                    'body_confidence': detection.body_confidence,
                    'age_estimate': detection.age_estimate,
                    'gender_estimate': detection.gender_estimate,
                    'emotion_scores': detection.emotion_scores,
                    'pose_angles': detection.pose_angles,
                    'timestamp': detection.timestamp,
                    'camera_id': detection.camera_id
                }
                for detection in self.detection_history
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Detection data exported to {filepath}")


# Mock AI Model Classes for Simulation
class MockFaceDetector:
    def detect_faces(self, frame):
        # Simulate face detection
        num_faces = np.random.randint(0, 3)  # 0-2 faces
        detections = []
        for i in range(num_faces):
            x = np.random.randint(0, frame.shape[1] - 100)
            y = np.random.randint(0, frame.shape[0] - 100)
            w = np.random.randint(50, 150)
            h = np.random.randint(50, 150)
            
            detections.append({
                'bbox': (x, y, w, h),
                'confidence': np.random.uniform(0.7, 0.95),
                'landmarks': [(x + w//2, y + h//2) for _ in range(5)]
            })
        return detections

class MockBodyDetector:
    def detect_bodies(self, frame):
        # Simulate body detection
        num_bodies = np.random.randint(0, 2)  # 0-1 bodies
        detections = []
        for i in range(num_bodies):
            x = np.random.randint(0, frame.shape[1] - 200)
            y = np.random.randint(0, frame.shape[0] - 300)
            w = np.random.randint(100, 200)
            h = np.random.randint(200, 400)
            
            detections.append({
                'bbox': (x, y, w, h),
                'confidence': np.random.uniform(0.6, 0.9)
            })
        return detections

class MockEmotionAnalyzer:
    def analyze_emotions(self, frame, face_bbox):
        # Simulate emotion analysis
        emotions = ['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise', 'neutral']
        scores = np.random.dirichlet(np.ones(len(emotions)))
        return dict(zip(emotions, scores))

class MockAgeGenderEstimator:
    def estimate_age(self, frame, face_bbox):
        return np.random.randint(18, 80)
    
    def estimate_gender(self, frame, face_bbox):
        return np.random.choice(['male', 'female'])

class MockPoseEstimator:
    def estimate_pose(self, frame, bbox):
        # Simulate pose estimation
        angles = ['head_yaw', 'head_pitch', 'head_roll', 'shoulder_angle', 'elbow_angle']
        return {angle: np.random.uniform(-180, 180) for angle in angles}
