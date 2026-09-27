"""
WSGI Entrypoint for Production Cloud Deployments (Render, Railway, Fly.io, Heroku, Docker).
Dispatches incoming requests:
- Root "/" -> Main AI Audit Application (Officer Portal)
- "/reference" -> Company Reference Portal
- "/api/reference" -> Reference REST API
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

# Ensure required directories exist
(BASE_DIR / "main_audit_app" / "uploads").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "reports").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "database" / "storage").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "reference_portal" / "reference_documents").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "demo_files" / "sample_bids").mkdir(parents=True, exist_ok=True)

# Run seed generator if reference data does not exist
try:
    from database.seed_data import seed_reference_data, generate_sample_officer_bids
    seed_reference_data()
    generate_sample_officer_bids()
except Exception as e:
    print(f"[WSGI Startup] Seed data check warning: {e}")

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from main_audit_app.app import create_audit_app
from reference_portal.app import create_reference_app

audit_app = create_audit_app()
ref_app = create_reference_app()

# Route /reference and /api/reference to reference_portal, and root / to audit_app
app = DispatcherMiddleware(audit_app, {
    "/reference": ref_app,
    "/api/reference": ref_app
})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    from werkzeug.serving import run_simple
    print(f"Running production WSGI server on port {port}...")
    run_simple("0.0.0.0", port, app, use_reloader=False)
