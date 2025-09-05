#!/usr/bin/env python3
"""
XRPL Ecosystem Setup Script
Installs dependencies and configures the environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install Python dependencies"""
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/training",
        "data/market",
        "models",
        "logs",
        "config",
        "frontend/build",
        "frontend/src",
        "contracts/ethereum",
        "contracts/solana",
        "contracts/polygon"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def create_env_file():
    """Create environment configuration file"""
    env_content = """# XRPL Ecosystem Environment Configuration

# Environment
ENVIRONMENT=development

# XRPL Configuration
XRPL_MAINNET_URL=wss://xrplcluster.com
XRPL_TESTNET_URL=wss://s.altnet.rippletest.net:51233
XRPL_DEVNET_URL=wss://s.devnet.rippletest.net:51233

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/xrpl_ecosystem
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017/xrpl_ecosystem

# API Configuration
API_PORT=8000
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# External API Keys (replace with your actual keys)
ETHEREUM_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
SOLANA_RPC=https://api.mainnet-beta.solana.com
POLYGON_RPC=https://polygon-rpc.com

# AI Trading Configuration
AI_MODEL_PATH=models/
AI_TRAINING_DATA_PATH=data/training/
AI_CONFIDENCE_THRESHOLD=0.7
AI_MAX_POSITION_SIZE=0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/xrpl_ecosystem.log
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env configuration file")
    else:
        print("ℹ️  .env file already exists")
    
    return True

def setup_database():
    """Setup database connections (placeholder)"""
    print("ℹ️  Database setup requires manual configuration")
    print("   - Install PostgreSQL, Redis, and MongoDB")
    print("   - Update .env file with database credentials")
    print("   - Create database: xrpl_ecosystem")
    return True

def setup_blockchain():
    """Setup blockchain connections (placeholder)"""
    print("ℹ️  Blockchain setup requires manual configuration")
    print("   - Get API keys from Infura, Alchemy, etc.")
    print("   - Update .env file with RPC endpoints")
    print("   - Deploy bridge contracts if needed")
    return True

def run_tests():
    """Run basic tests"""
    print("🧪 Running basic tests...")
    
    # Test imports
    try:
        import xrpl
        print("✅ XRPL library imported successfully")
    except ImportError:
        print("❌ XRPL library import failed")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError:
        print("❌ Pandas import failed")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError:
        print("❌ NumPy import failed")
        return False
    
    print("✅ All basic tests passed")
    return True

def main():
    """Main setup function"""
    print("🚀 XRPL Ecosystem Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("❌ Failed to create environment file")
        sys.exit(1)
    
    # Setup database (placeholder)
    setup_database()
    
    # Setup blockchain (placeholder)
    setup_blockchain()
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed")
        sys.exit(1)
    
    print("\n🎉 XRPL Ecosystem setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Update .env file with your configuration")
    print("   2. Setup databases (PostgreSQL, Redis, MongoDB)")
    print("   3. Configure blockchain RPC endpoints")
    print("   4. Run: python main.py")
    print("   5. Check examples: python examples/basic_usage.py")
    
    print("\n📚 Documentation:")
    print("   - README.md: Project overview and setup")
    print("   - config.py: Configuration options")
    print("   - examples/: Usage examples")

if __name__ == "__main__":
    main()
