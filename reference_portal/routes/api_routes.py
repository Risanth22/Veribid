"""
REST API routes for the Company Reference Portal.
These endpoints are consumed by the Main Audit Application to retrieve trusted reference data.
"""

from flask import Blueprint, jsonify, request, send_from_directory, current_app
from pathlib import Path
from database.db import get_reference_db

api_bp = Blueprint("reference_api", __name__, url_prefix="/api/reference")


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "Company Reference Data API", "version": "1.0.0"})


@api_bp.route("/companies", methods=["GET"])
def list_companies():
    """Retrieve all trusted reference companies with optional search query."""
    q = request.args.get("q", "").strip()
    db = get_reference_db()
    if q:
        query = {
            "$or": [
                {"company_name": {"$regex": q, "$options": "i"}},
                {"gstin": {"$regex": q, "$options": "i"}},
                {"cin": {"$regex": q, "$options": "i"}},
                {"company_id": {"$regex": q, "$options": "i"}}
            ]
        }
        # If fallback JsonCollection without $or support, search in memory
        all_companies = db.find()
        filtered = [
            c for c in all_companies
            if q.lower() in str(c.get("company_name", "")).lower()
            or q.lower() in str(c.get("gstin", "")).lower()
            or q.lower() in str(c.get("cin", "")).lower()
            or q.lower() in str(c.get("company_id", "")).lower()
        ]
        return jsonify({"success": True, "count": len(filtered), "data": filtered})
    
    companies = db.find()
    return jsonify({"success": True, "count": len(companies), "data": companies})


@api_bp.route("/company/id/<company_id>", methods=["GET"])
@api_bp.route("/company/<company_identifier>", methods=["GET"])
def get_company(company_identifier=None, company_id=None):
    """
    Retrieve reference data by company_id, company_name, GSTIN, or CIN.
    Prioritizes unique identifiers (GSTIN, CIN, ID) then company name.
    """
    identifier = company_id or company_identifier
    if not identifier:
        return jsonify({"success": False, "error": "Company identifier required"}), 400

    db = get_reference_db()
    
    # 1. Exact match on company_id
    comp = db.find_one({"company_id": identifier})
    if comp:
        return jsonify({"success": True, "source": "company_id", "data": comp})

    # 2. Exact match on GSTIN
    comp = db.find_one({"gstin": identifier.upper()})
    if comp:
        return jsonify({"success": True, "source": "gstin", "data": comp})

    # 3. Exact match on CIN
    comp = db.find_one({"cin": identifier.upper()})
    if comp:
        return jsonify({"success": True, "source": "cin", "data": comp})

    # 4. Search by company_name (case insensitive)
    all_companies = db.find()
    clean_id = identifier.lower().replace("pvt", "").replace("ltd", "").replace(".", "").strip()
    
    for c in all_companies:
        c_name = c.get("company_name", "").lower().replace("pvt", "").replace("ltd", "").replace(".", "").strip()
        if c_name == clean_id or clean_id in c_name or c_name in clean_id:
            return jsonify({"success": True, "source": "company_name", "data": c})

    return jsonify({
        "success": False,
        "error": f"Reference company not found for identifier '{identifier}' — manual review required."
    }), 404


@api_bp.route("/company/<company_id>/certificates", methods=["GET"])
def get_company_certificates(company_id):
    """Retrieve trusted reference certificates for a company."""
    db = get_reference_db()
    comp = db.find_one({"company_id": company_id}) or db.find_one({"company_name": company_id})
    if not comp:
        return jsonify({"success": False, "error": "Company not found"}), 404

    return jsonify({
        "success": True,
        "company_id": comp.get("company_id"),
        "company_name": comp.get("company_name"),
        "certificates": comp.get("certificates", [])
    })


@api_bp.route("/company/<company_id>/documents", methods=["GET"])
def get_company_documents(company_id):
    """Retrieve trusted reference documents list for a company."""
    db = get_reference_db()
    comp = db.find_one({"company_id": company_id}) or db.find_one({"company_name": company_id})
    if not comp:
        return jsonify({"success": False, "error": "Company not found"}), 404

    return jsonify({
        "success": True,
        "company_id": comp.get("company_id"),
        "company_name": comp.get("company_name"),
        "documents": comp.get("documents", [])
    })


@api_bp.route("/document/<filename>", methods=["GET"])
def download_reference_document(filename):
    """Download/view a stored reference certificate or file."""
    ref_dir = Path(current_app.config["REFERENCE_DOCS_DIR"])
    target_file = ref_dir / filename
    if not target_file.exists():
        return jsonify({"success": False, "error": "File not found"}), 404
    return send_from_directory(str(ref_dir), filename)


@api_bp.route("/company", methods=["POST"])
def create_company():
    """Create a new trusted company record."""
    data = request.get_json() or {}
    if not data.get("company_name"):
        return jsonify({"success": False, "error": "Company name is required"}), 400

    db = get_reference_db()
    
    # Generate ID if missing
    if not data.get("company_id"):
        count = db.count_documents() + 1
        data["company_id"] = f"COMP-{count:03d}"

    # Default fields
    data.setdefault("status", "APPROVED")
    data.setdefault("products", [])
    data.setdefault("certificates", [])
    data.setdefault("documents", [])

    db.insert_one(data)
    return jsonify({"success": True, "message": "Company created successfully", "data": data}), 201


@api_bp.route("/company/<company_id>", methods=["PUT"])
def update_company(company_id):
    """Update an existing trusted company record."""
    data = request.get_json() or {}
    db = get_reference_db()
    existing = db.find_one({"company_id": company_id})
    if not existing:
        return jsonify({"success": False, "error": "Company not found"}), 404

    db.update_one({"company_id": company_id}, {"$set": data})
    updated = db.find_one({"company_id": company_id})
    return jsonify({"success": True, "message": "Company updated successfully", "data": updated})
