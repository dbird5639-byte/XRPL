#!/usr/bin/env python3
"""
XRP Health Score Platform Demo Runner
====================================

This script runs a comprehensive demo of the XRP Health Score platform,
showcasing all features including health scoring, citizen coins, achievements,
and blockchain integration.
"""

import sys
import os
from pathlib import Path

# Add the platform directory to Python path
platform_dir = Path(__file__).parent
sys.path.insert(0, str(platform_dir))

from examples.demo_platform import XRPHealthScoreDemo


def main():
    """Run the XRP Health Score Platform demo"""
    print("🚀 Starting XRP Health Score Platform Demo...")
    print("=" * 60)
    
    try:
        # Initialize and run the demo
        demo = XRPHealthScoreDemo()
        demo.run_demo()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Explore the API endpoints in api/rest_api.py")
        print("2. Check out the gamification features in gamification/")
        print("3. Review the blockchain integration in blockchain/")
        print("4. Customize the scoring algorithms in core/scoring_categories.py")
        print("\nReady to revolutionize social scoring! 🦕➡️🚀")
        
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
