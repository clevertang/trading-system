#!/usr/bin/env python3
"""
Test runner script for the trading system.
Provides convenient interface for running different test suites.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False


def main():
    parser = argparse.ArgumentParser(description="Trading System Test Runner")
    parser.add_argument(
        "suite", 
        nargs="?",
        choices=["unit", "integration", "e2e", "all", "coverage", "fast"],
        default="all",
        help="Test suite to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--pattern", "-k",
        help="Run tests matching pattern"
    )
    parser.add_argument(
        "--file", "-f",
        help="Run specific test file"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML test report"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        base_cmd.extend(["-vvv", "-s"])
    else:
        base_cmd.append("-v")
    
    # Add parallel execution
    if args.parallel:
        base_cmd.extend(["-n", "auto"])
    
    # Add pattern matching
    if args.pattern:
        base_cmd.extend(["-k", args.pattern])
    
    # Add HTML report generation
    if args.report:
        base_cmd.extend([
            "--html=reports/test-report.html", 
            "--self-contained-html"
        ])
        # Create reports directory
        Path("reports").mkdir(exist_ok=True)
    
    success = True
    
    if args.file:
        # Run specific file
        cmd = base_cmd + [args.file]
        success = run_command(cmd, f"Test file: {args.file}")
        
    elif args.suite == "unit":
        # Unit tests only
        cmd = base_cmd + ["tests/unit/", "-m", "not slow"]
        success = run_command(cmd, "Unit Tests")
        
    elif args.suite == "integration":
        # Integration tests (unit + e2e, excluding network tests)
        cmd = base_cmd + ["tests/unit/", "tests/e2e/", "-m", "not network"]
        success = run_command(cmd, "Integration Tests")
        
    elif args.suite == "e2e":
        # End-to-end tests only
        cmd = base_cmd + ["tests/e2e/"]
        success = run_command(cmd, "End-to-End Tests")
        
    elif args.suite == "coverage":
        # Tests with coverage
        cmd = base_cmd + [
            "--cov=trading",
            "--cov-report=html",
            "--cov-report=term-missing",
            "tests/"
        ]
        success = run_command(cmd, "Tests with Coverage")
        if success:
            print(f"\n📊 Coverage report generated in htmlcov/index.html")
        
    elif args.suite == "fast":
        # Fast test subset
        cmd = base_cmd + ["tests/unit/", "-m", "not slow", "-n", "auto"]
        success = run_command(cmd, "Fast Test Suite")
        
    else:  # args.suite == "all"
        # Run all test suites
        test_suites = [
            (["tests/unit/", "-m", "not slow"], "Unit Tests"),
            (["tests/e2e/", "-m", "not network"], "E2E Tests (no network)"),
        ]
        
        for suite_args, description in test_suites:
            cmd = base_cmd + suite_args
            suite_success = run_command(cmd, description)
            success = success and suite_success
            
            if not suite_success:
                print(f"\n⚠️  {description} failed, continuing with other suites...")
    
    # Final summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Check output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()