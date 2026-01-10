#!/usr/bin/env python3
"""
Master Test Runner - Runs all test suites for the project.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run_test(name: str, script: str) -> tuple:
    """Run a test script and return (passed, failed, total)."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # Parse results from output
    lines = result.stdout.split('\n')
    passed = 0
    failed = 0

    for line in lines:
        if line.startswith("Passed:"):
            try:
                passed = int(line.split(":")[1].strip())
            except:
                pass
        elif line.startswith("Failed:"):
            try:
                failed = int(line.split(":")[1].strip())
            except:
                pass

    return passed, failed, passed + failed, result.returncode == 0


def main():
    """Run all test suites."""
    print("=" * 60)
    print("QWEN-IMAGE-LAYERED - COMPLETE TEST SUITE")
    print("=" * 60)

    test_suites = [
        ("TDD Compliance Tests", "tests/run_tests.py"),
        ("AI Enhancement Skills Tests", "tests/run_new_tests.py"),
        ("Text Processing Skills Tests", "tests/run_text_tests.py"),
        ("Phase 3 Generation Tests", "tests/run_phase3_tests.py"),
        ("Pipeline Integration Tests", "tests/test_pipeline_integration.py"),
        ("Mock API Tests", "tests/test_mock_api.py"),
        ("Integration Tests", "tests/test_integration.py"),
        ("Error Handling Tests", "tests/test_error_handling.py"),
        ("Infrastructure Tests", "tests/test_infrastructure.py"),
        ("Health Check Tests", "tests/test_health_check.py"),
    ]

    total_passed = 0
    total_failed = 0
    total_tests = 0
    all_success = True
    suite_results = []

    for name, script in test_suites:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            passed, failed, total, success = run_test(name, str(script_path))
            total_passed += passed
            total_failed += failed
            total_tests += total
            all_success = all_success and success
            suite_results.append((name, passed, failed, success))
        else:
            print(f"\n[SKIP] {name} - Script not found: {script}")
            suite_results.append((name, 0, 0, False))

    # Final Summary
    print("\n" + "=" * 60)
    print("COMPLETE TEST SUMMARY")
    print("=" * 60)

    print("\n--- Suite Results ---")
    for name, passed, failed, success in suite_results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}: {passed} passed, {failed} failed")

    print(f"\n--- Totals ---")
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    print(f"Total Tests:  {total_tests}")

    if total_tests > 0:
        print(f"Overall Success Rate: {total_passed / total_tests * 100:.1f}%")

    print("\n" + "=" * 60)
    if all_success and total_failed == 0:
        print("ALL TEST SUITES PASSED")
        return 0
    else:
        print(f"SOME TESTS FAILED - {total_failed} failures")
        return 1


if __name__ == "__main__":
    sys.exit(main())
