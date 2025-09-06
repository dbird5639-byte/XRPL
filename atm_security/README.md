# ATM Security System

A comprehensive AI-powered security system for crypto ATMs featuring advanced biometric detection, electromagnetic sensing, and multi-modal threat assessment.

## 🚀 Features

### 1. AI-Powered Camera System
- **Multi-person detection** with real-time tracking
- **Face recognition** with liveness detection
- **Crowd density analysis** and behavior monitoring
- **Emotion analysis** and age/gender estimation
- **Pose estimation** for movement analysis
- **High-resolution multi-camera setup** with edge computing

### 2. Frantic Behavior Detection
- **Movement pattern analysis** with velocity and acceleration tracking
- **Gesture recognition** for threatening behaviors
- **Stress indicator detection** through behavioral biometrics
- **Real-time threat assessment** with confidence scoring
- **Pattern complexity analysis** for anomaly detection

### 3. Facial Recognition Safety Switch
- **Multi-factor safety trigger system** preventing false positives
- **Facial recognition database** with threat level classification
- **Emergency protocol activation** only when multiple indicators align
- **Law enforcement integration** for high-priority alerts
- **Real-time threat assessment** with automated responses

### 4. Card Edge Electromagnetic Sensors
- **Multi-frequency EM field detection** around card edges
- **Real-time signal analysis** with statistical processing
- **AI-powered pattern recognition** for anomaly detection
- **Statistical visualization rendering** with matplotlib
- **Threat detection** through EM signature analysis
- **Card authentication** via electromagnetic fingerprinting

### 5. Comprehensive Security Management
- **Unified monitoring** of all security components
- **Real-time threat assessment** with multi-modal analysis
- **Automated response protocols** based on threat levels
- **Emergency contact integration** and law enforcement alerts
- **Comprehensive logging** and reporting system

## 🏗️ Architecture

```
ATM Security System
├── atm_camera_system.py      # AI-powered camera system
├── behavior_detector.py      # Frantic behavior detection
├── safety_switch.py          # Facial recognition safety switch
├── card_edge_sensor.py       # Electromagnetic sensor system
├── atm_security_manager.py   # Unified security management
├── demo_system.py           # Interactive demonstration
└── README.md                # This documentation
```

## 🔧 Installation

### Prerequisites
- Python 3.8+
- OpenCV (cv2)
- NumPy
- Matplotlib
- Threading support
- JSON handling

### Dependencies
```bash
pip install opencv-python numpy matplotlib
```

## 🚀 Quick Start

### Basic Usage
```python
from atm_security import ATMSecurityManager

# Initialize security manager
security_manager = ATMSecurityManager("ATM_001")

# Start monitoring
security_manager.start_monitoring()

# Add callbacks for events
def handle_security_event(assessment):
    print(f"Security Status: {assessment.overall_status.value}")
    print(f"Threat Score: {assessment.threat_score:.2f}")

security_manager.add_security_callback(handle_security_event)

# Run for specified duration
time.sleep(60)  # Monitor for 1 minute

# Stop monitoring
security_manager.stop_monitoring()
```

### Interactive Demo
```python
from atm_security.demo_system import ATMSecurityDemo

# Run interactive demo
demo = ATMSecurityDemo()
demo.run_interactive_demo()
```

## 📊 System Components

### Camera System (`atm_camera_system.py`)
- **Multi-camera support** with configurable positions
- **Real-time processing** at 30 FPS
- **AI model integration** for face/body detection
- **Crowd analysis** with density and movement tracking
- **Threat classification** based on visual indicators

### Behavior Detector (`behavior_detector.py`)
- **Movement analysis** with velocity and acceleration tracking
- **Gesture recognition** for threatening behaviors
- **Stress indicator calculation** from multiple sources
- **Pattern classification** (normal, frantic, aggressive, etc.)
- **Real-time monitoring** with configurable thresholds

### Safety Switch (`safety_switch.py`)
- **Multi-factor trigger system** requiring multiple indicators
- **Facial recognition database** with threat level classification
- **Emergency protocol management** with automated responses
- **False positive prevention** through confidence scoring
- **Law enforcement integration** for critical threats

### Card Edge Sensor (`card_edge_sensor.py`)
- **Electromagnetic field detection** around card edges
- **Multi-frequency analysis** (1kHz to 1GHz)
- **Statistical pattern analysis** with anomaly detection
- **Visualization rendering** with matplotlib
- **Threat assessment** based on EM signatures

### Security Manager (`atm_security_manager.py`)
- **Unified monitoring** of all security components
- **Real-time threat assessment** with multi-modal analysis
- **Automated response protocols** based on threat levels
- **Event logging** and comprehensive reporting
- **Emergency contact integration**

## 🎯 Security Levels

| Level | Description | Response Actions |
|-------|-------------|------------------|
| **Normal** | No threats detected | Continue monitoring |
| **Elevated** | Minor indicators | Alert security team |
| **High Alert** | Multiple indicators | Activate cameras, enable facial recognition |
| **Critical** | Serious threats | Contact law enforcement, lockdown ATM |
| **Emergency** | Immediate danger | Evacuate area, emergency shutdown |

## 🔍 Threat Detection

### Visual Threats
- Multiple people at ATM
- Frantic or aggressive behavior
- Threatening gestures
- Weapon detection
- Suspicious activity patterns

### Behavioral Threats
- High stress levels
- Erratic movement patterns
- Aggressive gestures
- Unusual behavior patterns
- Coercion indicators

### Electromagnetic Threats
- Unusual EM signatures
- Card tampering indicators
- Electronic device detection
- Signal anomalies
- Frequency pattern analysis

## 📈 Statistical Analysis

The system provides comprehensive statistical analysis including:

- **Field strength mapping** with 2D visualization
- **Frequency spectrum analysis** for signal characterization
- **Pattern complexity metrics** for anomaly detection
- **Spatial correlation analysis** for movement patterns
- **Temporal stability assessment** for behavior consistency
- **Threat score calculation** with confidence intervals

## 🚨 Emergency Protocols

### Automatic Responses
1. **Immediate threat detection** triggers real-time alerts
2. **Multi-factor verification** prevents false positives
3. **Automated escalation** based on threat severity
4. **Law enforcement contact** for critical situations
5. **Evidence collection** and logging for investigation

### Manual Overrides
- Security team can override automatic responses
- Emergency shutdown capability
- Manual threat assessment
- Custom response protocols

## 📊 Monitoring and Reporting

### Real-time Monitoring
- Live threat assessment dashboard
- Component status monitoring
- Event logging and alerting
- Performance metrics tracking

### Comprehensive Reports
- Security assessment history
- Threat detection statistics
- Response action tracking
- System performance metrics
- Export capabilities (JSON, CSV)

## 🔧 Configuration

### Camera System
```python
camera_config = CameraConfig(
    resolution=(1920, 1080),
    fps=30,
    face_detection_confidence=0.7,
    crowd_threshold=4,
    threat_analysis_enabled=True
)
```

### Behavior Detection
```python
behavior_detector = BehaviorDetector(
    analysis_interval=0.1,
    movement_thresholds={
        'frantic_velocity': 100,
        'frantic_jerkiness': 0.7,
        'aggressive_velocity': 80
    }
)
```

### Safety Switch
```python
safety_switch = SafetySwitch(
    activation_threshold=3,  # Triggers needed to activate
    critical_threshold=2,    # Triggers for critical response
    emergency_threshold=1    # Triggers for emergency response
)
```

### Card Edge Sensor
```python
card_sensor = CardEdgeSensor(
    sensor_resolution=64,
    frequency_range=(1e3, 1e9),  # 1kHz to 1GHz
    enable_visualization=True
)
```

## 🧪 Testing and Demo

### Interactive Demo
Run the interactive demo to test all system components:

```bash
python demo_system.py
```

### Scenario Testing
The demo includes multiple test scenarios:
- Normal operation
- Multiple people detection
- Frantic behavior simulation
- Threatening gestures
- Weapon detection
- EM anomalies
- Emergency situations

### Performance Testing
- Real-time processing capabilities
- Multi-threaded operation
- Memory usage optimization
- Response time analysis

## 🔒 Security Considerations

### Privacy Protection
- Biometric data encryption
- Secure template storage
- Privacy-preserving analytics
- Data retention policies

### System Security
- Tamper detection
- Secure communication
- Access control
- Audit logging

### False Positive Prevention
- Multi-factor verification
- Confidence scoring
- Threshold tuning
- Manual override capabilities

## 📚 API Reference

### ATMSecurityManager
Main security management class that coordinates all components.

```python
class ATMSecurityManager:
    def __init__(self, atm_id: str)
    def start_monitoring(self)
    def stop_monitoring(self)
    def get_current_security_status(self) -> Dict[str, Any]
    def export_security_report(self, filepath: str)
```

### Camera System
AI-powered camera system for multi-person detection.

```python
class ATMCameraSystem:
    def add_camera(self, camera_id: str, position: CameraPosition)
    def get_current_status(self) -> Dict[str, Any]
    def export_detection_data(self, filepath: str)
```

### Behavior Detector
Advanced behavior analysis and threat detection.

```python
class BehaviorDetector:
    def add_movement_data(self, person_id: int, position: Tuple[float, float])
    def add_gesture_data(self, person_id: int, gesture_type: GestureType)
    def get_current_behavior_status(self) -> Dict[str, Any]
```

### Safety Switch
Facial recognition safety switch with multi-factor triggers.

```python
class SafetySwitch:
    def add_safety_indicator(self, trigger_type: SafetyTrigger, confidence: float)
    def add_person_to_database(self, person_id: str, name: str, threat_level: str)
    def get_current_safety_status(self) -> Dict[str, Any]
```

### Card Edge Sensor
Electromagnetic sensor system for card analysis.

```python
class CardEdgeSensor:
    def activate_sensor(self, position: Tuple[float, float])
    def render_statistical_image(self, field_map: EMFieldMap, output_path: str)
    def get_current_status(self) -> Dict[str, Any]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Future Enhancements

- Machine learning model improvements
- Additional biometric modalities
- Cloud integration capabilities
- Mobile app integration
- Advanced analytics dashboard
- Real-time video streaming
- Enhanced encryption protocols

---

**Note**: This is a comprehensive security system designed for crypto ATM protection. Always ensure proper testing and validation before deployment in production environments.
