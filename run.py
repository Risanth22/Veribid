"""
System Launcher for AI Bid & Company Compliance Verification System.
Starts both logically separate systems concurrently:
1. Company Reference Data Website & REST API (Port 5001)
2. Main AI Audit Application (Port 5000)
"""

import os
import sys
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from database.seed_data import seed_reference_data, generate_sample_officer_bids
from reference_portal.app import create_reference_app
from main_audit_app.app import create_audit_app


def start_reference_portal():
    app = create_reference_app()
    port = int(os.getenv("REFERENCE_PORTAL_PORT", 5001))
    print(f"[Reference Portal] Starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def start_audit_app():
    app = create_audit_app()
    port = int(os.getenv("PORT", 5000))
    print(f"[Main Audit App] Starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def main():
    print("=" * 70)
    print("  AI BID & COMPANY COMPLIANCE VERIFICATION SYSTEM")
    print("  Initializing databases, reference records, and REST services...")
    print("=" * 70)

    # 1. Seed demo data and create sample bid documents
    seed_reference_data()
    generate_sample_officer_bids()

    # 2. Start Reference Portal & REST API thread (Port 5001)
    ref_thread = threading.Thread(target=start_reference_portal, daemon=True)
    ref_thread.start()

    time.sleep(1.2)

    # 3. Start Main AI Audit Application thread (Port 5000)
    print("\n[System] All services operational.")
    print("  -> Main AI Audit App (Officer Portal):      http://127.0.0.1:5000")
    print("  -> Company Reference Portal (Admin & API): http://127.0.0.1:5001")
    print("  -> Reference REST API Endpoint:            http://127.0.0.1:5001/api/reference/companies\n")

    start_audit_app()


if __name__ == "__main__":
    main()
