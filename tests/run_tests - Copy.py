"""
SalesSight 360 — Master Test Runner
Discovers and executes all unit and integration tests across tests/,
prints a formatted summary, and exits with appropriate status code.
"""

import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
TESTS_DIR = os.path.join(BASE_DIR, "tests")

def main():
    print("=" * 70)
    print(" SALESSIGHT 360 — AUTOMATED TEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=TESTS_DIR, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f" TESTS RUN: {result.testsRun}")
    print(f" SUCCESSES: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" FAILURES : {len(result.failures)}")
    print(f" ERRORS   : {len(result.errors)}")
    print("=" * 70)

    if result.wasSuccessful():
        print("[OVERALL STATUS] ALL TESTS PASSED SUCCESSFULLY! (100% PASS RATE)")
        sys.exit(0)
    else:
        print("[OVERALL STATUS] TEST SUITE FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
