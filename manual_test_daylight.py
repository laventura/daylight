#!/usr/bin/env python3
"""
Manual test script for the daylight CLI.
This script performs a series of manual tests using the daylight CLI.
"""

import subprocess
import os
import sys

def run_test(description, command):
    """Run a test command and display the results."""
    print(f"\n{'=' * 80}")
    print(f"TEST: {description}")
    print(f"COMMAND: {' '.join(command)}")
    print('-' * 80)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR (exit code {e.returncode}):")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run a series of manual tests."""
    tests = [
        # Basic tests
        ("Default behavior (today, current location)", ["python", "daylight.py"]),
        ("Verbose output", ["python", "daylight.py", "--verbose"]),
        ("JSON output", ["python", "daylight.py", "--json"]),
        ("Brief output", ["python", "daylight.py", "--brief"]),
        
        # Date options
        ("Tomorrow", ["python", "daylight.py", "--tomorrow"]),
        ("Yesterday", ["python", "daylight.py", "--yesterday"]),
        ("Day after tomorrow", ["python", "daylight.py", "--day-after"]),
        ("Specific date (summer solstice)", ["python", "daylight.py", "--date", "2025-06-21"]),
        ("Specific date (winter solstice)", ["python", "daylight.py", "--date", "2025-12-21"]),
        
        # Location options
        ("Location: London", ["python", "daylight.py", "--location", "London"]),
        ("Location: Tokyo", ["python", "daylight.py", "--location", "Tokyo"]),
        ("Location: Sydney", ["python", "daylight.py", "--location", "Sydney, Australia"]),
        ("Location: New York", ["python", "daylight.py", "--location", "New York"]),
        ("Location: Nairobi", ["python", "daylight.py", "--location", "Nairobi, Kenya"]),
        ("Location: Reykjavik", ["python", "daylight.py", "--location", "Reykjavik, Iceland"]),
        
        # Combinations
        ("Tokyo, tomorrow, verbose", ["python", "daylight.py", "--location", "Tokyo", "--tomorrow", "--verbose"]),
        ("London, winter solstice, JSON", ["python", "daylight.py", "--location", "London", "--date", "2025-12-21", "--json"]),
        
        # Edge cases
        ("Far north: Svalbard in summer", ["python", "daylight.py", "--location", "Svalbard", "--date", "2025-06-21"]),
        ("Far north: Svalbard in winter", ["python", "daylight.py", "--location", "Svalbard", "--date", "2025-12-21"]),
        ("Southern hemisphere: Melbourne in summer", ["python", "daylight.py", "--location", "Melbourne, Australia", "--date", "2025-12-21"]),
        ("Southern hemisphere: Melbourne in winter", ["python", "daylight.py", "--location", "Melbourne, Australia", "--date", "2025-06-21"]),
        ("Near date line: Fiji", ["python", "daylight.py", "--location", "Fiji"]),
        
        # Different output formats for the same query
        ("Mountain View (default)", ["python", "daylight.py", "--location", "Mountain View, CA"]),
        ("Mountain View (verbose)", ["python", "daylight.py", "--location", "Mountain View, CA", "--verbose"]),
        ("Mountain View (JSON)", ["python", "daylight.py", "--location", "Mountain View, CA", "--json"]),
        ("Mountain View (brief)", ["python", "daylight.py", "--location", "Mountain View, CA", "--brief"]),
    ]
    
    success_count = 0
    failure_count = 0
    
    for description, command in tests:
        if run_test(description, command):
            success_count += 1
        else:
            failure_count += 1
    
    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {success_count} tests passed, {failure_count} tests failed")
    print(f"{'=' * 80}")
    
    return 0 if failure_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())