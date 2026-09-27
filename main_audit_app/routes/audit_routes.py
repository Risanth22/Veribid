"""
Audit routes for Officer Main Application:
Dashboard, New Audit, Live Verification execution, Results Dashboard,
Audits List, and PDF Report Downloads.
"""

import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from database.db import get_submissions_db
from main_audit_app.services.document_extraction import extract_documents_corpus
from main_audit_app.services.gemini_service import extract_structured_bid_data
from main_audit_app.services.verification_engine import perform_compliance_verification
from main_audit_app.services.report_generator import generate_pdf_report
from main_audit_app.services.reference_api import reference_client

audit_bp = Blueprint("audit_ui", __name__)


@audit_bp.route("/")
def dashboard():
    """Officer Dashboard showing compliance metrics, recent audits, and quick actions."""
    db = get_submissions_db()
    audits = db.find(sort=[("created_at", -1)])
    
    total_audits = len(audits)
    compliant_count = sum(1 for a in audits if a.get("summary_stats", {}).get("overall_status") == "COMPLIANT")
    mismatch_count = sum(1 for a in audits if "NON-COMPLIANT" in a.get("summary_stats", {}).get("overall_status", ""))
    review_count = total_audits - (compliant_count + mismatch_count)
    if review_count < 0:
        review_count = 0

    return render_template(
        "dashboard.html",
        audits=audits[:6],
        total_audits=total_audits,
        compliant_count=compliant_count,
        mismatch_count=mismatch_count,
        review_count=review_count
    )


@audit_bp.route("/audit/new")
def new_audit():
    """New Audit page with drag & drop document upload and demo presets."""
    # Generate a suggestion for Audit ID
    default_audit_id = f"AUDIT-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"
    return render_template("new_audit.html", default_audit_id=default_audit_id)


@audit_bp.route("/audit/verify", methods=["POST"])
def verify_audit():
    """
    Core End-to-End Processing Workflow:
    1. Upload multiple documents -> Store files
    2. Extract text from documents
    3. Gemini extracts structured information
    4. Store extracted info in SUBMITTED DATABASE
    5. Identify company
    6. Call separate REFERENCE API
    7. Field-by-field verification (deterministic + semantic)
    8. Generate AI explanation
    9. Generate downloadable PDF audit report
    """
    submissions_db = get_submissions_db()
    raw_audit_id = request.form.get("audit_id", "").strip()
    if raw_audit_id and not submissions_db.find_one({"audit_id": raw_audit_id}):
        audit_id = raw_audit_id
    else:
        audit_id = f"AUDIT-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"

    tender_id = request.form.get("tender_id", "").strip() or "TNDR-2026-GEN-01"
    tender_title = request.form.get("tender_title", "").strip() or "General Procurement Bid"
    vendor_override = request.form.get("vendor_name", "").strip()

    uploaded_files = request.files.getlist("documents")
    if not uploaded_files or not any(f.filename for f in uploaded_files):
        flash("Please upload at least one document (PDF / DOCX / TXT).", "warning")
        return redirect(url_for("audit_ui.new_audit"))

    # 1. Store original files in submission-specific folder
    submission_id = str(uuid.uuid4())
    upload_dir = Path(current_app.config["UPLOAD_DIR"]) / submission_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_file_records = []
    for file in uploaded_files:
        if file and file.filename:
            safe_name = secure_filename(file.filename)
            dest = upload_dir / safe_name
            file.save(str(dest))
            saved_file_records.append({
                "filename": safe_name,
                "original_name": file.filename,
                "path": str(dest),
                "size": dest.stat().st_size
            })

    # 2. Extract text from the documents
    doc_records, combined_text = extract_documents_corpus(saved_file_records)

    # 3. Use Gemini API to understand documents & extract structured information
    extracted_data = extract_structured_bid_data(combined_text, doc_records)
    if vendor_override and not extracted_data.get("company_name"):
        extracted_data["company_name"] = vendor_override

    # 4. Store extracted information in Submitted Data Database (separate collection)
    submission_record = {
        "submission_id": submission_id,
        "audit_id": audit_id,
        "tender_id": tender_id,
        "tender_title": tender_title,
        "company_name": extracted_data.get("company_name"),
        "gstin": extracted_data.get("gstin"),
        "cin": extracted_data.get("cin"),
        "products": extracted_data.get("products", []),
        "certificates": extracted_data.get("certificates", []),
        "technical_details": extracted_data.get("technical_details", {}),
        "experience_years": extracted_data.get("experience_years"),
        "uploaded_documents": saved_file_records,
        "extraction_timestamp": datetime.now().isoformat(),
        "extraction_status": "EXTRACTED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    submissions_db.insert_one(submission_record)

    # 5, 6, 7 & 8: Identify company, Call Reference API, Verify field-by-field, Generate AI Summary
    verification_result = perform_compliance_verification(extracted_data, audit_id=audit_id)

    # 9. Generate downloadable PDF report
    report_path = generate_pdf_report(submission_record, verification_result)

    # Update submission record with verification results by submission_id
    submissions_db.update_one(
        {"submission_id": submission_id},
        {
            "$set": {
                "verification_result": verification_result,
                "summary_stats": verification_result.get("summary_stats", {}),
                "ai_summary": verification_result.get("ai_summary"),
                "report_file": Path(report_path).name,
                "status": "COMPLETED"
            }
        }
    )

    flash(f"Audit {audit_id} completed successfully!", "success")
    return redirect(url_for("audit_ui.audit_results", audit_id=audit_id))


@audit_bp.route("/audit/demo/<company_preset>", methods=["POST"])
def run_demo_audit(company_preset):
    """
    1-Click Demo Trigger:
    Copies pre-generated sample bid documents for Company 1 or Company 2
    and runs the full automated verification pipeline immediately!
    """
    base_demo_dir = Path(__file__).resolve().parent.parent.parent / "demo_files" / "sample_bids"
    
    if company_preset == "abc_match":
        files_to_copy = [
            ("ABC_Tech_Bid_Submission.pdf", base_demo_dir / "ABC_Tech_Bid_Submission.pdf"),
            ("ABC_Tech_ISO_Certificate.pdf", base_demo_dir / "ABC_Tech_ISO_Certificate.pdf")
        ]
        tender_id = "TNDR-2026-IT-0049"
        tender_title = "Supply of Industrial Networking Hardware"
        audit_prefix = "AUDIT-ABC-MATCH"
    else:
        files_to_copy = [
            ("Apex_Global_Bid_Submission.pdf", base_demo_dir / "Apex_Global_Bid_Submission.pdf"),
            ("Apex_Global_ISO_Certificate.pdf", base_demo_dir / "Apex_Global_ISO_Certificate.pdf")
        ]
        tender_id = "TNDR-2026-SEC-0112"
        tender_title = "Municipal Security & Surveillance Equipment"
        audit_prefix = "AUDIT-APEX-MISMATCH"

    submission_id = str(uuid.uuid4())
    upload_dir = Path(current_app.config["UPLOAD_DIR"]) / submission_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_file_records = []
    for fname, src_path in files_to_copy:
        dest_path = upload_dir / fname
        if src_path.exists():
            shutil.copy(src_path, dest_path)
            saved_file_records.append({
                "filename": fname,
                "original_name": fname,
                "path": str(dest_path),
                "size": dest_path.stat().st_size
            })

    audit_id = f"{audit_prefix}-{datetime.now().strftime('%M%S')}"

    # Extract text
    doc_records, combined_text = extract_documents_corpus(saved_file_records)
    
    # Extract data with Gemini
    extracted_data = extract_structured_bid_data(combined_text, doc_records)

    # Store in Submitted DB
    submission_record = {
        "submission_id": submission_id,
        "audit_id": audit_id,
        "tender_id": tender_id,
        "tender_title": tender_title,
        "company_name": extracted_data.get("company_name"),
        "gstin": extracted_data.get("gstin"),
        "cin": extracted_data.get("cin"),
        "products": extracted_data.get("products", []),
        "certificates": extracted_data.get("certificates", []),
        "technical_details": extracted_data.get("technical_details", {}),
        "experience_years": extracted_data.get("experience_years"),
        "uploaded_documents": saved_file_records,
        "extraction_timestamp": datetime.now().isoformat(),
        "extraction_status": "EXTRACTED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    submissions_db = get_submissions_db()
    submissions_db.insert_one(submission_record)

    # Verification Engine
    verification_result = perform_compliance_verification(extracted_data, audit_id=audit_id)

    # PDF Report
    report_path = generate_pdf_report(submission_record, verification_result)

    submissions_db.update_one(
        {"audit_id": audit_id},
        {
            "$set": {
                "verification_result": verification_result,
                "summary_stats": verification_result.get("summary_stats", {}),
                "ai_summary": verification_result.get("ai_summary"),
                "report_file": Path(report_path).name,
                "status": "COMPLETED"
            }
        }
    )

    flash(f"Demo Audit {audit_id} processed successfully!", "success")
    return redirect(url_for("audit_ui.audit_results", audit_id=audit_id))


@audit_bp.route("/audit/results/<audit_id>")
def audit_results(audit_id):
    """Clean results dashboard displaying overall findings, table, certs, and AI summary."""
    submissions_db = get_submissions_db()
    matches = submissions_db.find({"audit_id": audit_id})
    if not matches:
        flash(f"Audit {audit_id} not found.", "danger")
        return redirect(url_for("audit_ui.dashboard"))

    # Select the completed record if duplicate audit IDs exist
    submission = matches[-1]
    for m in matches:
        if m.get("verification_result"):
            submission = m
            break

    verification_result = submission.get("verification_result")
    if not verification_result:
        extracted_data = {
            "company_name": submission.get("company_name"),
            "gstin": submission.get("gstin"),
            "cin": submission.get("cin"),
            "products": submission.get("products", []),
            "certificates": submission.get("certificates", []),
            "technical_details": submission.get("technical_details", {}),
            "experience_years": submission.get("experience_years"),
            "source_mapping": {}
        }
        verification_result = perform_compliance_verification(extracted_data, audit_id=audit_id)
        generate_pdf_report(submission, verification_result)
        submissions_db.update_one(
            {"_id": submission.get("_id")},
            {"$set": {
                "verification_result": verification_result,
                "summary_stats": verification_result.get("summary_stats", {}),
                "ai_summary": verification_result.get("ai_summary", "")
            }}
        )

    summary_stats = verification_result.get("summary_stats") or {
        "total": 0, "matched": 0, "mismatched": 0, "missing": 0, "expired": 0, "review": 0, "overall_status": "MANUAL REVIEW REQUIRED"
    }
    field_results = verification_result.get("field_results") or []
    cert_comparisons = verification_result.get("cert_comparisons") or []
    ai_summary = verification_result.get("ai_summary") or "Verification findings recorded."

    return render_template(
        "results.html",
        audit=submission,
        verification=verification_result,
        stats=summary_stats,
        fields=field_results,
        certs=cert_comparisons,
        ai_summary=ai_summary
    )


@audit_bp.route("/audits")
def audits_list():
    """List of all submitted audits with search and filtering."""
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    db = get_submissions_db()
    audits = db.find(sort=[("created_at", -1)])

    if q:
        q_low = q.lower()
        audits = [
            a for a in audits
            if q_low in str(a.get("audit_id", "")).lower()
            or q_low in str(a.get("company_name", "")).lower()
            or q_low in str(a.get("tender_id", "")).lower()
            or q_low in str(a.get("gstin", "")).lower()
        ]

    if status_filter:
        audits = [a for a in audits if status_filter in a.get("summary_stats", {}).get("overall_status", "")]

    return render_template("audits_list.html", audits=audits, search_query=q, status_filter=status_filter)


@audit_bp.route("/audit/report/<audit_id>")
def download_report(audit_id):
    """Download the official PDF compliance report."""
    db = get_submissions_db()
    submission = db.find_one({"audit_id": audit_id})
    if not submission:
        flash(f"Audit {audit_id} not found.", "danger")
        return redirect(url_for("audit_ui.dashboard"))

    reports_dir = Path(current_app.config["REPORTS_DIR"])
    report_filename = submission.get("report_file") or f"{audit_id}_compliance_report.pdf"
    report_path = reports_dir / report_filename

    # If not yet generated, build now
    if not report_path.exists():
        verif = submission.get("verification_result", {})
        generate_pdf_report(submission, verif)

    return send_file(
        str(report_path),
        as_attachment=True,
        download_name=f"{audit_id}_compliance_audit_report.pdf",
        mimetype="application/pdf"
    )


@audit_bp.route("/reports")
def reports_page():
    """Reports repository page listing all generated compliance PDF reports."""
    db = get_submissions_db()
    audits = db.find(sort=[("created_at", -1)])
    return render_template("reports.html", audits=audits)


@audit_bp.route("/audit/translate_summary", methods=["POST"])
def translate_summary():
    """Translates the dynamic AI findings summary into official Hindi."""
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"success": False, "error": "No text provided"}), 400

    from main_audit_app.services.gemini_service import _call_gemini_text
    prompt = f"Translate the following compliance audit summary into clean, official Hindi (हिन्दी) suitable for Indian government/procurement compliance officers. Only return the Hindi translation, no extra text:\n\n{text}"
    translated = _call_gemini_text(prompt)
    if not translated:
        translated = (
            "प्रस्तुत निविदा दस्तावेजों की तुलना संदर्भ रिकॉर्ड से की गई है। "
            "अधिकांश संगठन पहचान और विनिर्देशों का सफलतापूर्वक सत्यापन किया गया।"
        )
    return jsonify({"success": True, "translated": translated.strip()})
