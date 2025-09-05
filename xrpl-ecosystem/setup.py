#!/usr/bin/env python3
"""
XRPL Ecosystem Setup Script
Automated setup and configuration for the XRPL ecosystem
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description or command} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {description or command}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")

def check_node_version():
    """Check if Node.js version is compatible"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Node.js {version} found")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ Node.js 16 or higher is required")
    print("Please install Node.js from https://nodejs.org/")
    return False

def setup_python_environment():
    """Setup Python environment and dependencies"""
    print("\n=== Setting up Python Environment ===")
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        run_command("python -m venv venv", "Creating virtual environment")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install Python dependencies
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies")

def setup_node_environment():
    """Setup Node.js environment and dependencies"""
    print("\n=== Setting up Node.js Environment ===")
    
    # Install root dependencies
    run_command("npm install", "Installing root Node.js dependencies")
    
    # Setup frontend applications
    frontend_dirs = ["frontend/web-interface", "frontend/xaman-wallet", "frontend/ai-ide"]
    for frontend_dir in frontend_dirs:
        if Path(frontend_dir).exists():
            print(f"Setting up {frontend_dir}...")
            run_command(f"cd {frontend_dir} && npm install", f"Installing dependencies for {frontend_dir}")
    
    # Setup smart contracts
    smart_contracts_dir = "smart-contracts"
    if Path(smart_contracts_dir).exists():
        print("Setting up smart contracts...")
        run_command(f"cd {smart_contracts_dir} && npm install", "Installing smart contract dependencies")

def create_directories():
    """Create necessary directories"""
    print("\n=== Creating Directories ===")
    
    directories = [
        "logs",
        "data",
        "cache",
        "temp",
        "backups",
        "docs/api",
        "docs/guides",
        "docs/architecture",
        "tools/scripts",
        "tools/testing",
        "tools/deployment",
        "examples/basic-usage",
        "examples/advanced"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_configuration():
    """Setup configuration files"""
    print("\n=== Setting up Configuration ===")
    
    # Copy example config if config doesn't exist
    config_file = Path("config.env")
    example_config = Path("config.example.env")
    
    if not config_file.exists() and example_config.exists():
        shutil.copy(example_config, config_file)
        print("✓ Created config.env from example")
        print("⚠️  Please edit config.env with your actual configuration values")
    
    # Create .gitignore if it doesn't exist
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        gitignore_content = """# Environment files
.env
config.env
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
temp/
cache/
*.tmp
"""
        gitignore_file.write_text(gitignore_content)
        print("✓ Created .gitignore file")

def setup_database():
    """Setup database (optional)"""
    print("\n=== Database Setup ===")
    print("Database setup is optional for development")
    print("For production, please configure PostgreSQL and Redis")
    print("Update config.env with your database URLs")

def run_tests():
    """Run basic tests to verify setup"""
    print("\n=== Running Tests ===")
    
    # Test Python imports
    test_script = """
import sys
sys.path.insert(0, '.')

try:
    from core.xrpl_client import XRPLClient
    from core.dex_engine import DEXTradingEngine
    from core.bridge_engine import CrossChainBridge
    from core.security import FortKnoxSecurity
    print("✓ All core modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
"""
    
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        python_cmd = "venv/bin/python"
    
    run_command(f"{python_cmd} -c \"{test_script}\"", "Testing Python imports")

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    print("\n=== Creating Startup Scripts ===")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting XRPL Ecosystem...
call venv\\Scripts\\activate
python main.py
pause
"""
    Path("start.bat").write_text(windows_script)
    print("✓ Created start.bat for Windows")
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting XRPL Ecosystem..."
source venv/bin/activate
python main.py
"""
    unix_script_path = Path("start.sh")
    unix_script_path.write_text(unix_script)
    unix_script_path.chmod(0o755)
    print("✓ Created start.sh for Unix/Linux/MacOS")

def main():
    """Main setup function"""
    print("🚀 XRPL Ecosystem Setup")
    print("=" * 50)
    
    # Check prerequisites
    check_python_version()
    if not check_node_version():
        print("⚠️  Node.js setup will be skipped")
    
    # Setup steps
    create_directories()
    setup_configuration()
    setup_python_environment()
    
    if check_node_version():
        setup_node_environment()
    
    setup_database()
    create_startup_scripts()
    run_tests()
    
    print("\n" + "=" * 50)
    print("🎉 XRPL Ecosystem setup completed!")
    print("\nNext steps:")
    print("1. Edit config.env with your configuration")
    print("2. Run 'python main.py' to start the ecosystem")
    print("3. Or use start.bat (Windows) or start.sh (Unix)")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
