#!/usr/bin/env python3
"""
Test script to verify bootstrap execution with maximum logging
This script tests the bootstrap functionality in a controlled environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_bootstrap_test():
    """Run bootstrap tests with different configurations"""
    
    print("🧪 BOOTSTRAP TESTING SUITE")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    tests = [
        {
            "name": "Dry Run - Basic",
            "command": ["python3", "scripts/bootstrap_roles_users.py", "--dry-run"],
            "expected_exit": 0
        },
        {
            "name": "Dry Run - Verbose",
            "command": ["python3", "scripts/bootstrap_roles_users.py", "--dry-run", "--verbose"],
            "expected_exit": 0
        },
        {
            "name": "Dry Run - Production Environment",
            "command": ["python3", "scripts/bootstrap_roles_users.py", "--dry-run", "--environment", "production"],
            "expected_exit": 0
        },
        {
            "name": "Dry Run - Custom Log File",
            "command": ["python3", "scripts/bootstrap_roles_users.py", "--dry-run", "--verbose", "--log-file", "custom_test.log"],
            "expected_exit": 0
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n🔍 Running test: {test['name']}")
        print(f"📝 Command: {' '.join(test['command'])}")
        
        try:
            result = subprocess.run(
                test['command'],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            success = result.returncode == test['expected_exit']
            
            print(f"✅ Exit code: {result.returncode} (expected: {test['expected_exit']})")
            print(f"📊 Status: {'PASS' if success else 'FAIL'}")
            
            if result.stdout:
                print(f"📋 Output lines: {len(result.stdout.splitlines())}")
            
            if result.stderr:
                print(f"⚠️ Error output: {result.stderr[:200]}...")
            
            results.append({
                "name": test['name'],
                "success": success,
                "exit_code": result.returncode,
                "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
                "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0
            })
            
        except subprocess.TimeoutExpired:
            print(f"❌ Test timed out after 60 seconds")
            results.append({
                "name": test['name'],
                "success": False,
                "exit_code": -1,
                "stdout_lines": 0,
                "stderr_lines": 0
            })
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append({
                "name": test['name'],
                "success": False,
                "exit_code": -2,
                "stdout_lines": 0,
                "stderr_lines": 0
            })
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} - {result['name']} (exit: {result['exit_code']})")
    
    # Check log files
    print("\n📄 LOG FILES CREATED:")
    log_files = [
        "bootstrap_debug.log",
        "test_bootstrap.log", 
        "custom_test.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"📄 {log_file}: {size:,} bytes")
        else:
            print(f"📄 {log_file}: Not found")
    
    return passed == total

if __name__ == "__main__":
    success = run_bootstrap_test()
    sys.exit(0 if success else 1)

