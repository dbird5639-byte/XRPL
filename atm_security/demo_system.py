"""
ATM Security System Demo
========================

Comprehensive demonstration of the ATM security system including:
- AI-powered camera system with multi-person detection
- Frantic behavior detection algorithms
- Facial recognition safety switch
- Card edge electromagnetic sensors
- Statistical analysis and image rendering

This demo simulates real-world scenarios and demonstrates the system's
capabilities in detecting and responding to various security threats.
"""

import time
import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import json
import os
from datetime import datetime

from .atm_security_manager import ATMSecurityManager, SecurityStatus, ResponseAction
from .atm_camera_system import CameraPosition, DetectionStatus
from .behavior_detector import BehaviorType, MovementPattern
from .safety_switch import SafetyTrigger, SafetyLevel
from .card_edge_sensor import EMSignalType, ThreatLevel

class ATMSecurityDemo:
    """
    Comprehensive demo of the ATM security system
    
    Simulates various security scenarios and demonstrates the system's
    ability to detect, analyze, and respond to threats.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Initialize security manager
        self.security_manager = ATMSecurityManager("DEMO_ATM_001")
        
        # Demo state
        self.demo_scenarios = self._initialize_demo_scenarios()
        self.current_scenario = None
        self.demo_running = False
        
        # Setup callbacks
        self._setup_demo_callbacks()
        
        self.logger.info("ATM Security Demo initialized")
    
    def setup_logging(self):
        """Setup logging for the demo"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('atm_security_demo.log')
            ]
        )
    
    def _initialize_demo_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Initialize demo scenarios"""
        return {
            'normal_operation': {
                'name': 'Normal Operation',
                'description': 'Single person using ATM normally',
                'duration': 30,
                'triggers': []
            },
            'multiple_people': {
                'name': 'Multiple People Detected',
                'description': 'Multiple people approach the ATM',
                'duration': 45,
                'triggers': ['multiple_people']
            },
            'frantic_behavior': {
                'name': 'Frantic Behavior',
                'description': 'Person exhibits frantic, suspicious behavior',
                'duration': 60,
                'triggers': ['frantic_behavior', 'high_stress']
            },
            'threatening_gestures': {
                'name': 'Threatening Gestures',
                'description': 'Person makes threatening gestures',
                'duration': 45,
                'triggers': ['threatening_gestures', 'aggressive_behavior']
            },
            'weapon_detected': {
                'name': 'Weapon Detected',
                'description': 'Weapon detected in vicinity',
                'duration': 30,
                'triggers': ['weapon_detected', 'emergency_situation']
            },
            'card_em_anomaly': {
                'name': 'Card EM Anomaly',
                'description': 'Unusual electromagnetic signals from card',
                'duration': 40,
                'triggers': ['em_anomaly', 'suspicious_card']
            },
            'emergency_situation': {
                'name': 'Emergency Situation',
                'description': 'Multiple threat indicators trigger emergency protocols',
                'duration': 60,
                'triggers': ['multiple_threats', 'emergency_protocols']
            }
        }
    
    def _setup_demo_callbacks(self):
        """Setup demo callbacks for monitoring system responses"""
        self.security_manager.add_security_callback(self._handle_security_event)
        self.security_manager.add_emergency_callback(self._handle_emergency_event)
    
    def _handle_security_event(self, assessment):
        """Handle security assessment events"""
        self.logger.info(f"🔍 Security Event: {assessment.overall_status.value} "
                        f"(Threat Score: {assessment.threat_score:.2f})")
        
        if assessment.active_threats:
            self.logger.warning(f"⚠️  Active Threats: {', '.join(assessment.active_threats)}")
        
        if assessment.recommended_actions:
            actions = [action.value for action in assessment.recommended_actions]
            self.logger.info(f"📋 Recommended Actions: {', '.join(actions)}")
    
    def _handle_emergency_event(self, assessment):
        """Handle emergency events"""
        self.logger.critical(f"🚨 EMERGENCY: {assessment.overall_status.value}")
        self.logger.critical(f"🚨 Threat Score: {assessment.threat_score:.2f}")
        self.logger.critical(f"🚨 Active Threats: {', '.join(assessment.active_threats)}")
    
    def run_demo(self, scenario_name: str = None):
        """Run the security demo"""
        if scenario_name:
            if scenario_name not in self.demo_scenarios:
                self.logger.error(f"Unknown scenario: {scenario_name}")
                return
            scenarios = [scenario_name]
        else:
            scenarios = list(self.demo_scenarios.keys())
        
        self.logger.info("🚀 Starting ATM Security System Demo")
        self.logger.info("=" * 60)
        
        for scenario_name in scenarios:
            self._run_scenario(scenario_name)
            time.sleep(2)  # Brief pause between scenarios
        
        self.logger.info("✅ Demo completed successfully")
        self._generate_demo_report()
    
    def _run_scenario(self, scenario_name: str):
        """Run a specific demo scenario"""
        scenario = self.demo_scenarios[scenario_name]
        self.current_scenario = scenario_name
        
        self.logger.info(f"\n🎬 Running Scenario: {scenario['name']}")
        self.logger.info(f"📝 Description: {scenario['description']}")
        self.logger.info(f"⏱️  Duration: {scenario['duration']} seconds")
        self.logger.info("-" * 40)
        
        # Simulate the scenario
        self._simulate_scenario(scenario)
        
        # Wait for scenario duration
        time.sleep(scenario['duration'])
        
        # Cleanup scenario
        self._cleanup_scenario()
        
        self.logger.info(f"✅ Scenario '{scenario['name']}' completed")
    
    def _simulate_scenario(self, scenario: Dict[str, Any]):
        """Simulate a specific scenario"""
        triggers = scenario.get('triggers', [])
        
        for trigger in triggers:
            self._simulate_trigger(trigger)
            time.sleep(1)  # Brief delay between triggers
    
    def _simulate_trigger(self, trigger: str):
        """Simulate a specific trigger"""
        if trigger == 'multiple_people':
            self._simulate_multiple_people()
        elif trigger == 'frantic_behavior':
            self._simulate_frantic_behavior()
        elif trigger == 'threatening_gestures':
            self._simulate_threatening_gestures()
        elif trigger == 'weapon_detected':
            self._simulate_weapon_detection()
        elif trigger == 'em_anomaly':
            self._simulate_em_anomaly()
        elif trigger == 'high_stress':
            self._simulate_high_stress()
        elif trigger == 'aggressive_behavior':
            self._simulate_aggressive_behavior()
        elif trigger == 'suspicious_card':
            self._simulate_suspicious_card()
        elif trigger == 'multiple_threats':
            self._simulate_multiple_threats()
        elif trigger == 'emergency_protocols':
            self._simulate_emergency_protocols()
    
    def _simulate_multiple_people(self):
        """Simulate multiple people detection"""
        self.logger.info("👥 Simulating multiple people detection...")
        
        # Add multiple people to camera system
        for i in range(3):
            person_id = f"person_{i+1}"
            position = (100 + i * 50, 200 + i * 30)
            self.security_manager.behavior_detector.add_movement_data(
                person_id, position, time.time()
            )
        
        # Trigger camera system detection
        self.security_manager.camera_system.add_detection_callback(
            lambda detection: self.logger.info(f"👤 Person detected: {detection.person_id}")
        )
    
    def _simulate_frantic_behavior(self):
        """Simulate frantic behavior"""
        self.logger.info("🏃 Simulating frantic behavior...")
        
        # Add frantic movement data
        person_id = "frantic_person"
        base_position = (200, 300)
        
        for i in range(20):
            # Simulate erratic movement
            x_offset = np.random.normal(0, 20)
            y_offset = np.random.normal(0, 20)
            position = (base_position[0] + x_offset, base_position[1] + y_offset)
            
            self.security_manager.behavior_detector.add_movement_data(
                person_id, position, time.time() + i * 0.1
            )
        
        # Add threatening gesture
        self.security_manager.behavior_detector.add_gesture_data(
            person_id, "threatening", 0.8, (150, 250, 100, 100), time.time()
        )
    
    def _simulate_threatening_gestures(self):
        """Simulate threatening gestures"""
        self.logger.info("👊 Simulating threatening gestures...")
        
        person_id = "threatening_person"
        
        # Add multiple threatening gestures
        gestures = ["pointing", "threatening", "aggressive"]
        for gesture in gestures:
            self.security_manager.behavior_detector.add_gesture_data(
                person_id, gesture, 0.9, (200, 300, 80, 80), time.time()
            )
    
    def _simulate_weapon_detection(self):
        """Simulate weapon detection"""
        self.logger.info("🔫 Simulating weapon detection...")
        
        # Add weapon detection to safety switch
        self.security_manager.safety_switch.add_safety_indicator(
            SafetyTrigger.WEAPON_DETECTED, 0.95, 0.9, "weapon_detector", 
            {'weapon_type': 'firearm', 'confidence': 0.95}
        )
    
    def _simulate_em_anomaly(self):
        """Simulate electromagnetic anomaly"""
        self.logger.info("⚡ Simulating EM anomaly...")
        
        # Activate card edge sensors
        self.security_manager.card_edge_sensor.activate_all_sensors()
        
        # Simulate unusual EM signals
        for i in range(10):
            position = (50 + i * 10, 30)
            self.security_manager.card_edge_sensor._scan_sensor_position(position)
    
    def _simulate_high_stress(self):
        """Simulate high stress levels"""
        self.logger.info("😰 Simulating high stress levels...")
        
        # Add stress indicators to safety switch
        self.security_manager.safety_switch.add_safety_indicator(
            SafetyTrigger.HIGH_STRESS_LEVELS, 0.8, 0.7, "stress_detector",
            {'heart_rate': 120, 'blood_pressure': '140/90'}
        )
    
    def _simulate_aggressive_behavior(self):
        """Simulate aggressive behavior"""
        self.logger.info("😠 Simulating aggressive behavior...")
        
        person_id = "aggressive_person"
        
        # Add aggressive movement patterns
        for i in range(15):
            x = 200 + np.random.normal(0, 15)
            y = 300 + np.random.normal(0, 15)
            self.security_manager.behavior_detector.add_movement_data(
                person_id, (x, y), time.time() + i * 0.1
            )
    
    def _simulate_suspicious_card(self):
        """Simulate suspicious card activity"""
        self.logger.info("💳 Simulating suspicious card activity...")
        
        # Add suspicious card indicators
        self.security_manager.safety_switch.add_safety_indicator(
            SafetyTrigger.SUSPICIOUS_ACTIVITY, 0.7, 0.6, "card_reader",
            {'card_type': 'suspicious', 'anomaly_detected': True}
        )
    
    def _simulate_multiple_threats(self):
        """Simulate multiple simultaneous threats"""
        self.logger.info("🚨 Simulating multiple threats...")
        
        # Combine multiple threat indicators
        self._simulate_multiple_people()
        time.sleep(1)
        self._simulate_frantic_behavior()
        time.sleep(1)
        self._simulate_threatening_gestures()
        time.sleep(1)
        self._simulate_high_stress()
    
    def _simulate_emergency_protocols(self):
        """Simulate emergency protocol activation"""
        self.logger.info("🚨 Simulating emergency protocols...")
        
        # Add emergency indicators
        self.security_manager.safety_switch.add_safety_indicator(
            SafetyTrigger.EMERGENCY_SITUATION, 0.95, 0.9, "emergency_detector",
            {'situation': 'critical', 'immediate_response_required': True}
        )
    
    def _cleanup_scenario(self):
        """Cleanup after scenario completion"""
        # Clear active indicators
        self.security_manager.safety_switch.reset_safety_system()
        
        # Deactivate sensors
        self.security_manager.card_edge_sensor.deactivate_all_sensors()
        
        # Clear movement data
        self.security_manager.behavior_detector.movement_history.clear()
        self.security_manager.behavior_detector.gesture_history.clear()
    
    def _generate_demo_report(self):
        """Generate comprehensive demo report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"atm_security_demo_report_{timestamp}.json"
        
        # Get security history
        security_history = self.security_manager.get_security_history()
        
        # Generate report
        report = {
            'demo_info': {
                'timestamp': timestamp,
                'scenarios_run': list(self.demo_scenarios.keys()),
                'total_duration': sum(scenario['duration'] for scenario in self.demo_scenarios.values())
            },
            'security_summary': {
                'total_assessments': len(security_history),
                'status_distribution': self._calculate_status_distribution(security_history),
                'threat_score_average': np.mean([a.threat_score for a in security_history]) if security_history else 0,
                'confidence_average': np.mean([a.confidence for a in security_history]) if security_history else 0
            },
            'security_assessments': [
                {
                    'timestamp': assessment.timestamp,
                    'status': assessment.overall_status.value,
                    'threat_score': assessment.threat_score,
                    'active_threats': assessment.active_threats,
                    'confidence': assessment.confidence
                }
                for assessment in security_history
            ]
        }
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📊 Demo report saved to: {report_path}")
        self._print_demo_summary(report)
    
    def _calculate_status_distribution(self, security_history) -> Dict[str, int]:
        """Calculate distribution of security statuses"""
        distribution = {}
        for assessment in security_history:
            status = assessment.overall_status.value
            distribution[status] = distribution.get(status, 0) + 1
        return distribution
    
    def _print_demo_summary(self, report: Dict[str, Any]):
        """Print demo summary to console"""
        print("\n" + "=" * 60)
        print("🎯 ATM SECURITY SYSTEM DEMO SUMMARY")
        print("=" * 60)
        
        summary = report['security_summary']
        print(f"📊 Total Security Assessments: {summary['total_assessments']}")
        print(f"📈 Average Threat Score: {summary['threat_score_average']:.3f}")
        print(f"🎯 Average Confidence: {summary['confidence_average']:.3f}")
        
        print("\n📋 Status Distribution:")
        for status, count in summary['status_distribution'].items():
            print(f"   {status}: {count}")
        
        print("\n✅ Demo completed successfully!")
        print("=" * 60)
    
    def run_interactive_demo(self):
        """Run interactive demo with user input"""
        print("\n🎮 ATM Security System Interactive Demo")
        print("=" * 50)
        
        while True:
            print("\nAvailable scenarios:")
            for i, (name, scenario) in enumerate(self.demo_scenarios.items(), 1):
                print(f"{i}. {scenario['name']} - {scenario['description']}")
            
            print("0. Run all scenarios")
            print("q. Quit")
            
            choice = input("\nSelect scenario (number): ").strip()
            
            if choice.lower() == 'q':
                break
            elif choice == '0':
                self.run_demo()
            else:
                try:
                    scenario_index = int(choice) - 1
                    scenario_names = list(self.demo_scenarios.keys())
                    if 0 <= scenario_index < len(scenario_names):
                        self.run_demo(scenario_names[scenario_index])
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
    
    def shutdown(self):
        """Shutdown the demo system"""
        self.logger.info("Shutting down ATM Security Demo")
        self.security_manager.shutdown()


def main():
    """Main demo function"""
    demo = ATMSecurityDemo()
    
    try:
        # Run interactive demo
        demo.run_interactive_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    finally:
        demo.shutdown()


if __name__ == "__main__":
    main()
