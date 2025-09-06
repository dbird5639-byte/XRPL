#!/usr/bin/env python3
"""
Setup script for Safety and Defense Software development environment.
This script initializes the project structure and sets up the development environment.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def print_status(message):
    """Print a status message with formatting."""
    print(f"[INFO] {message}")

def print_error(message):
    """Print an error message with formatting."""
    print(f"[ERROR] {message}")

def print_success(message):
    """Print a success message with formatting."""
    print(f"[SUCCESS] {message}")

def check_python_version():
    """Check if Python version meets requirements."""
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_virtual_environment():
    """Create a virtual environment for the project."""
    venv_path = Path("venv")
    if venv_path.exists():
        print_status("Virtual environment already exists")
        return True
    
    try:
        print_status("Creating virtual environment...")
        venv.create("venv", with_pip=True)
        print_success("Virtual environment created successfully")
        return True
    except Exception as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install project dependencies."""
    try:
        print_status("Installing dependencies...")
        
        # Determine the pip command based on OS
        if os.name == 'nt':  # Windows
            pip_cmd = "venv\\Scripts\\pip"
        else:  # Unix/Linux/Mac
            pip_cmd = "venv/bin/pip"
        
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error during dependency installation: {e}")
        return False

def create_directories():
    """Create additional project directories if they don't exist."""
    directories = [
        "src/core/authentication",
        "src/core/encryption",
        "src/core/monitoring",
        "src/core/threat_detection",
        "src/api",
        "src/database",
        "src/services",
        "src/utils",
        "tests/unit",
        "tests/integration",
        "tests/security",
        "tests/performance",
        "deployment/docker",
        "deployment/kubernetes",
        "deployment/terraform",
        "deployment/scripts",
        "research/threat_analysis",
        "research/vulnerability_research",
        "research/compliance_research",
        "research/papers",
        "data/raw",
        "data/processed",
        "data/models",
        "data/backups",
        "scripts/setup",
        "scripts/maintenance",
        "scripts/monitoring",
        "scripts/security",
        "security/protocols",
        "security/tools",
        "security/policies",
        "security/incident_response",
        "compliance/audit_reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory.startswith("src/") or directory.startswith("tests/"):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()

def create_initial_files():
    """Create initial Python files for the project structure."""
    files_to_create = [
        ("src/core/__init__.py", "# Core security and defense functionality"),
        ("src/api/__init__.py", "# API endpoints and interfaces"),
        ("src/database/__init__.py", "# Database models and connections"),
        ("src/services/__init__.py", "# Business logic services"),
        ("src/utils/__init__.py", "# Utility functions and helpers"),
        ("tests/__init__.py", "# Test suite initialization"),
        ("tests/unit/__init__.py", "# Unit tests"),
        ("tests/integration/__init__.py", "# Integration tests"),
        ("tests/security/__init__.py", "# Security tests"),
        ("tests/performance/__init__.py", "# Performance tests")
    ]
    
    for file_path, content in files_to_create:
        file_obj = Path(file_path)
        if not file_obj.exists():
            file_obj.write_text(content)

def main():
    """Main setup function."""
    print("=" * 60)
    print("Safety and Defense Software - Environment Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Create project directories
    print_status("Creating project directory structure...")
    create_directories()
    create_initial_files()
    print_success("Project structure created")
    
    # Install dependencies
    if not install_dependencies():
        print_error("Setup incomplete due to dependency installation failure")
        print_status("You can manually install dependencies using:")
        if os.name == 'nt':  # Windows
            print("    venv\\Scripts\\pip install -r requirements.txt")
        else:  # Unix/Linux/Mac
            print("    venv/bin/pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print_success("Environment setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
    print("2. Review the documentation in the docs/ directory")
    print("3. Check security protocols in docs/SECURITY_PROTOCOLS.md")
    print("4. Review compliance requirements in compliance/")
    print("5. Start development in the src/ directory")
    print("=" * 60)

if __name__ == "__main__":
    main()
