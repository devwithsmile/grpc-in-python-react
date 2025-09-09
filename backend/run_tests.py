#!/usr/bin/env python3
"""
Test runner script for the Library Service.
"""

import sys
import os
import subprocess
import argparse

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run Library Service tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--validation", action="store_true", help="Run validation tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-cov", action="store_true", help="Disable coverage reporting")
    
    args = parser.parse_args()
    
    # Change to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Build pytest command
    pytest_cmd = "python -m pytest"
    
    if args.unit:
        pytest_cmd += " tests/unit/"
    elif args.integration:
        pytest_cmd += " tests/integration/"
    elif args.validation:
        pytest_cmd += " -m validation"
    else:
        pytest_cmd += " tests/"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if not args.no_cov and args.coverage:
        pytest_cmd += " --cov=app --cov-report=html --cov-report=term-missing"
    
    # Run tests
    success = run_command(pytest_cmd, "Running tests")
    
    if success:
        print(f"\n{'='*60}")
        print("✅ All tests passed!")
        print(f"{'='*60}")
        
        if args.coverage and not args.no_cov:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n{'='*60}")
        print("❌ Tests failed!")
        print(f"{'='*60}")
        sys.exit(1)

if __name__ == "__main__":
    main()
