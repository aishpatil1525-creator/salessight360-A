"""
SalesSight 360 — Automated Screenshot Capture Script
Launches the Streamlit analytics dashboard locally in headless mode,
navigates through all 5 analytics pages using Playwright, and captures
crisp 1600x1000 screenshots stored in screenshots/.
"""

import os
import sys
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

PORT = 8501
URL = f"http://127.0.0.1:{PORT}"

def wait_for_server(url=URL, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print(f"[SUCCESS] Streamlit server is active at {url}")
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def capture_all():
    print("=" * 65)
    print(" SALESSIGHT 360 — AUTOMATED DASHBOARD SCREENSHOT CAPTURE")
    print("=" * 65)

    # 1. Launch Streamlit server
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(BASE_DIR, "dashboard", "app.py"),
        f"--server.port={PORT}",
        "--server.address=127.0.0.1",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    print(f"Launching Streamlit background process on port {PORT}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        if not wait_for_server():
            raise RuntimeError("Streamlit server failed to start within timeout.")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1050}, device_scale_factor=1)
            page = context.new_page()

            # Page 1: Executive Overview
            print("Capturing Page 1: Executive Overview...")
            page.goto(URL, wait_until="networkidle")
            time.sleep(4)
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "executive_overview.png"), full_page=False)
            print("-> Saved screenshots/executive_overview.png")

            # Page 2: Funnel & Conversion
            print("Capturing Page 2: Funnel & Conversion...")
            page.locator("text=Funnel & Conversion").click()
            time.sleep(3)
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "funnel_conversion.png"), full_page=False)
            print("-> Saved screenshots/funnel_conversion.png")

            # Page 3: Forecast & Variance
            print("Capturing Page 3: Forecast & Variance...")
            page.locator("text=Forecast & Variance").click()
            time.sleep(3)
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "forecast_variance.png"), full_page=False)
            print("-> Saved screenshots/forecast_variance.png")

            # Page 4: Rep Performance
            print("Capturing Page 4: Rep Performance...")
            page.locator("text=Rep Performance").click()
            time.sleep(3)
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "rep_performance.png"), full_page=False)
            print("-> Saved screenshots/rep_performance.png")

            # Page 5: Data Quality & Methodology
            print("Capturing Page 5: Data Quality...")
            page.locator("text=Data Quality & Methodology").click()
            time.sleep(3)
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "data_quality.png"), full_page=False)
            print("-> Saved screenshots/data_quality.png")

            # Return to Executive Overview for Filtered View
            print("Capturing Filtered View...")
            page.locator("text=Executive Overview").click()
            time.sleep(2)
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "filtered_view.png"), full_page=False)
            print("-> Saved screenshots/filtered_view.png")

            browser.close()

    finally:
        print("Terminating Streamlit process...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Streamlit process terminated.")

    print("\n[SUCCESS] All 6 dashboard screenshots captured successfully.")

if __name__ == "__main__":
    capture_all()
