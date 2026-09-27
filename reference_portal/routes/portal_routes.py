"""
Portal Admin UI routes for managing trusted reference company data,
certificates, products, and documents.
"""

import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from database.db import get_reference_db

portal_bp = Blueprint("portal_ui", __name__)


@portal_bp.route("/")
def index():
    return redirect(url_for("portal_ui.companies_list"))


@portal_bp.route("/companies")
def companies_list():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    db = get_reference_db()
    
    companies = db.find()
    if q:
        q_lower = q.lower()
        companies = [
            c for c in companies
            if q_lower in str(c.get("company_name", "")).lower()
            or q_lower in str(c.get("gstin", "")).lower()
            or q_lower in str(c.get("cin", "")).lower()
            or q_lower in str(c.get("company_id", "")).lower()
        ]
    if status_filter:
        companies = [c for c in companies if c.get("status") == status_filter]
        
    return render_template("companies.html", companies=companies, search_query=q, status_filter=status_filter)


@portal_bp.route("/companies/new", methods=["GET", "POST"])
def company_create():
    db = get_reference_db()
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        gstin = request.form.get("gstin", "").strip().upper()
        cin = request.form.get("cin", "").strip().upper()
        reg_no = request.form.get("registration_number", "").strip()
        status = request.form.get("status", "APPROVED")
        email = request.form.get("contact_email", "").strip()
        phone = request.form.get("contact_phone", "").strip()
        address = request.form.get("address", "").strip()
        exp_years = int(request.form.get("experience_years", 0) or 0)
        
        # Products
        product_names = request.form.getlist("product_name[]")
        product_specs = request.form.getlist("product_spec[]")
        products = []
        for name, spec in zip(product_names, product_specs):
            if name.strip():
                products.append({"name": name.strip(), "specs": spec.strip()})

        # Certificates
        cert_names = request.form.getlist("cert_name[]")
        cert_numbers = request.form.getlist("cert_number[]")
        cert_valid_untils = request.form.getlist("cert_valid_until[]")
        certificates = []
        for cname, cnum, cvalid in zip(cert_names, cert_numbers, cert_valid_untils):
            if cname.strip():
                certificates.append({
                    "name": cname.strip(),
                    "certificate_number": cnum.strip(),
                    "valid_until": cvalid.strip(),
                    "status": "ACTIVE"
                })

        count = db.count_documents() + 1
        company_id = f"COMP-{count:03d}"
        
        new_comp = {
            "company_id": company_id,
            "company_name": company_name,
            "gstin": gstin,
            "cin": cin,
            "registration_number": reg_no,
            "status": status,
            "contact_email": email,
            "contact_phone": phone,
            "address": address,
            "experience_years": exp_years,
            "products": products,
            "certificates": certificates,
            "documents": []
        }
        
        db.insert_one(new_comp)
        flash(f"Company '{company_name}' ({company_id}) added successfully!", "success")
        return redirect(url_for("portal_ui.company_detail", company_id=company_id))

    return render_template("company_form.html", company=None, is_edit=False)


@portal_bp.route("/companies/<company_id>")
def company_detail(company_id):
    db = get_reference_db()
    comp = db.find_one({"company_id": company_id})
    if not comp:
        flash(f"Company {company_id} not found.", "danger")
        return redirect(url_for("portal_ui.companies_list"))
    return render_template("company_detail.html", company=comp)


@portal_bp.route("/companies/<company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id):
    db = get_reference_db()
    comp = db.find_one({"company_id": company_id})
    if not comp:
        flash(f"Company {company_id} not found.", "danger")
        return redirect(url_for("portal_ui.companies_list"))

    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        gstin = request.form.get("gstin", "").strip().upper()
        cin = request.form.get("cin", "").strip().upper()
        reg_no = request.form.get("registration_number", "").strip()
        status = request.form.get("status", "APPROVED")
        email = request.form.get("contact_email", "").strip()
        phone = request.form.get("contact_phone", "").strip()
        address = request.form.get("address", "").strip()
        exp_years = int(request.form.get("experience_years", 0) or 0)

        # Products
        product_names = request.form.getlist("product_name[]")
        product_specs = request.form.getlist("product_spec[]")
        products = []
        for name, spec in zip(product_names, product_specs):
            if name.strip():
                products.append({"name": name.strip(), "specs": spec.strip()})

        # Certificates
        cert_names = request.form.getlist("cert_name[]")
        cert_numbers = request.form.getlist("cert_number[]")
        cert_valid_untils = request.form.getlist("cert_valid_until[]")
        certificates = []
        for cname, cnum, cvalid in zip(cert_names, cert_numbers, cert_valid_untils):
            if cname.strip():
                certificates.append({
                    "name": cname.strip(),
                    "certificate_number": cnum.strip(),
                    "valid_until": cvalid.strip(),
                    "status": "ACTIVE"
                })

        update_data = {
            "company_name": company_name,
            "gstin": gstin,
            "cin": cin,
            "registration_number": reg_no,
            "status": status,
            "contact_email": email,
            "contact_phone": phone,
            "address": address,
            "experience_years": exp_years,
            "products": products,
            "certificates": certificates
        }

        db.update_one({"company_id": company_id}, {"$set": update_data})
        flash(f"Company '{company_name}' updated successfully!", "success")
        return redirect(url_for("portal_ui.company_detail", company_id=company_id))

    return render_template("company_form.html", company=comp, is_edit=True)


@portal_bp.route("/companies/<company_id>/upload_doc", methods=["POST"])
def upload_reference_document(company_id):
    db = get_reference_db()
    comp = db.find_one({"company_id": company_id})
    if not comp:
        flash("Company not found", "danger")
        return redirect(url_for("portal_ui.companies_list"))

    file = request.files.get("document_file")
    doc_type = request.form.get("document_type", "Reference Document").strip()
    
    if file and file.filename:
        filename = secure_filename(f"{company_id}_{file.filename}")
        save_path = Path(current_app.config["REFERENCE_DOCS_DIR"]) / filename
        file.save(str(save_path))

        docs = comp.get("documents", [])
        docs.append({
            "name": doc_type or file.filename,
            "reference_file": filename,
            "verified": True
        })
        db.update_one({"company_id": company_id}, {"$set": {"documents": docs}})
        flash(f"Document '{filename}' uploaded to reference repository!", "success")

    return redirect(url_for("portal_ui.company_detail", company_id=company_id))


@portal_bp.route("/companies/<company_id>/status", methods=["POST"])
def update_status(company_id):
    db = get_reference_db()
    new_status = request.form.get("status", "APPROVED")
    db.update_one({"company_id": company_id}, {"$set": {"status": new_status}})
    flash(f"Company status updated to {new_status}", "info")
    return redirect(url_for("portal_ui.company_detail", company_id=company_id))


@portal_bp.route("/api-docs")
def api_docs():
    return render_template("api_docs.html")
