#!/usr/bin/env python3
"""
Personal Growth & Rehabilitation Demo Runner
==========================================

This script demonstrates how the XRP Health Score platform can help
someone overcome past challenges and build a positive future through
community contribution and personal development.
"""

import sys
import os
from pathlib import Path

# Add the platform directory to Python path
platform_dir = Path(__file__).parent
sys.path.insert(0, str(platform_dir))

from examples.personal_growth_demo import PersonalGrowthDemo


def main():
    """Run the personal growth and rehabilitation demo"""
    print("🌱 Starting Personal Growth & Rehabilitation Demo...")
    print("=" * 70)
    print()
    print("This demo shows how the XRP Health Score platform can help")
    print("someone overcome past challenges and build a positive future")
    print("through community contribution and personal development.")
    print()
    
    try:
        # Initialize and run the demo
        demo = PersonalGrowthDemo()
        demo.run_complete_demo()
        
        print("\n" + "=" * 70)
        print("✅ Personal Growth Demo completed successfully!")
        print()
        print("Key Takeaways:")
        print("• The platform recognizes and rewards personal growth")
        print("• Past challenges can be overcome through positive action")
        print("• Community contribution leads to redemption and recognition")
        print("• Technology skills can be leveraged for social good")
        print("• The system provides a clear path to rehabilitation")
        print()
        print("Ready to start your own growth journey? 🚀")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that all modules are properly imported")
        print("3. Verify the platform structure is intact")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
