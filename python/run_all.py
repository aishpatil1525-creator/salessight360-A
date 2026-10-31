"""
SalesSight 360 — Master Orchestration Script
Runs data generation, ETL cleaning, schema verification, data validation,
and test suite sequentially.
"""

import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_step(step_name, script_path):
    print("\n" + "=" * 70)
    print(f" >>> RUNNING: {step_name}")
    print("=" * 70)
    result = subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n[ERROR] Step '{step_name}' failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    print(f"[SUCCESS] Finished: {step_name}")

def main():
    print("*" * 70)
    print("  SALESSIGHT 360 — END-TO-END PIPELINE ORCHESTRATION")
    print("*" * 70)

    # Step 1: Generate Data
    run_step("Generate Synthetic Datasets", os.path.join(BASE_DIR, "python", "generate_sample_data.py"))

    # Step 2: ETL Pipeline
    run_step("Execute ETL & Build SQLite Warehouse", os.path.join(BASE_DIR, "python", "etl_pipeline.py"))

    # Step 3: Validate Data Quality
    run_step("Run Data Quality & Integrity Checks", os.path.join(BASE_DIR, "python", "validate_data.py"))

    # Step 4: Unit & Integration Tests (if available)
    test_runner = os.path.join(BASE_DIR, "tests", "run_tests.py")
    if os.path.exists(test_runner):
        run_step("Execute Automated Tests", test_runner)

    # Step 5: Executive Analytical Reports
    reports_script = os.path.join(BASE_DIR, "python", "generate_reports.py")
    if os.path.exists(reports_script):
        run_step("Generate Executive Analytical Reports", reports_script)

    print("\n" + "*" * 70)
    print("  ALL PIPELINE STAGES COMPLETED SUCCESSFULLY")
    print("*" * 70)

if __name__ == "__main__":
    main()
