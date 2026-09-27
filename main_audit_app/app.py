"""
Main AI Audit Application Server.
Used by Compliance Officers to upload bid documents, run AI extraction,
execute field-by-field verification via Reference REST API, view dashboard,
and generate audit reports.
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


def create_audit_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "main_audit_app" / "templates"),
        static_folder=str(BASE_DIR / "main_audit_app" / "static")
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "compliance-audit-secret-2026")
    app.config["UPLOAD_DIR"] = str(BASE_DIR / "main_audit_app" / "uploads")
    app.config["REPORTS_DIR"] = str(BASE_DIR / "reports")
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32MB upload limit

    Path(app.config["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["REPORTS_DIR"]).mkdir(parents=True, exist_ok=True)

    from main_audit_app.routes.audit_routes import audit_bp
    app.register_blueprint(audit_bp)

    return app


if __name__ == "__main__":
    app = create_audit_app()
    port = int(os.getenv("PORT", 5000))
    print(f"[Main Audit App] Running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
