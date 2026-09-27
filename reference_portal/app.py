"""
Company Reference Data Website & API Server.
Maintained by authorized administrators to store trusted reference company information,
reference certificates, product specs, and provide the REST API for Main Audit Application.
"""

import os
import sys
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

def create_reference_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "reference_portal" / "templates"),
        static_folder=str(BASE_DIR / "reference_portal" / "static")
    )
    
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "ref-portal-secret-key-2026")
    app.config["REFERENCE_DOCS_DIR"] = str(BASE_DIR / "reference_portal" / "reference_documents")
    Path(app.config["REFERENCE_DOCS_DIR"]).mkdir(parents=True, exist_ok=True)

    from reference_portal.routes.portal_routes import portal_bp
    from reference_portal.routes.api_routes import api_bp

    app.register_blueprint(portal_bp)
    app.register_blueprint(api_bp)

    return app


if __name__ == "__main__":
    app = create_reference_app()
    port = int(os.getenv("REFERENCE_PORTAL_PORT", 5001))
    print(f"[Reference Portal] Running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
