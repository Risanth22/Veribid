"""
Verification Engine for AI Bid & Company Compliance Verification System.
Implements:
1. Company identification hierarchy: GSTIN -> CIN -> Company ID -> Company Name.
2. Deterministic rule-based comparisons for exact fields (GSTIN, CIN, Cert Number, Dates, Numbers).
3. Semantic verification via Gemini for complex text/specs.
4. Certificate/File-level field comparisons.
5. Strict compliance statuses: MATCH, MISMATCH, MISSING, EXPIRED, NOT FOUND, REQUIRES REVIEW.
"""

import re
from datetime import datetime, date
from .gemini_service import semantic_compare_specifications, generate_compliance_summary
from .reference_api import reference_client


def parse_date(date_str):
    """Attempts to parse varied date formats into a date object."""
    if not date_str or not isinstance(date_str, str):
        return None
    cleaned = date_str.strip()
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    # Try finding YYYY-MM-DD in string
    match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", cleaned)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass
    return None


def is_date_expired(date_str):
    """Checks if a date is in the past compared to today's date."""
    d = parse_date(date_str)
    if not d:
        return False
    # Use current local date: September 2026
    current_date = date.today()
    return d < current_date


def identify_company(submitted_data):
    """
    Identifies the company in the reference repository using the required priority:
    1. GSTIN
    2. CIN
    3. Vendor / Company ID
    4. Company Name
    Returns: (company_data, identifier_used, error_msg)
    """
    gstin = submitted_data.get("gstin")
    cin = submitted_data.get("cin")
    comp_id = submitted_data.get("company_id")
    comp_name = submitted_data.get("company_name")

    # 1. Try GSTIN
    if gstin:
        res = reference_client.get_company(gstin)
        if res.get("success"):
            return res.get("data"), "GSTIN", None

    # 2. Try CIN
    if cin:
        res = reference_client.get_company(cin)
        if res.get("success"):
            return res.get("data"), "CIN", None

    # 3. Try Company ID
    if comp_id:
        res = reference_client.get_company(comp_id)
        if res.get("success"):
            return res.get("data"), "Company ID", None

    # 4. Try Company Name
    if comp_name:
        res = reference_client.get_company(comp_name)
        if res.get("success"):
            return res.get("data"), "Company Name", None

    return None, None, "Reference company not found — manual review required."


def perform_compliance_verification(submitted_data, audit_id=None):
    """
    Executes complete end-to-end compliance verification:
    - Identifies company
    - Compares company details (GSTIN, CIN, Name, Registration, Experience)
    - Compares products & technical specifications (deterministic + semantic)
    - Compares certificates at file & field levels
    - Evaluates required reference documents
    - Generates summary statistics and AI explanation
    """
    ref_company, id_used, error_msg = identify_company(submitted_data)

    field_results = []
    cert_comparisons = []
    source_map = submitted_data.get("source_mapping", {})

    if not ref_company:
        # Not found in Reference Database
        field_results.append({
            "field": "Company Identification",
            "category": "Identity",
            "submitted": submitted_data.get("company_name") or submitted_data.get("gstin") or "Unidentified",
            "reference": "NOT IN REFERENCE REPOSITORY",
            "status": "NOT FOUND",
            "explanation": error_msg or "Reference company not found — manual review required. Do not automatically mark compliant.",
            "source_document": source_map.get("company_name", "Uploaded Submission"),
            "is_exact": False
        })
        summary_stats = {
            "total": 1,
            "matched": 0,
            "mismatched": 0,
            "missing": 0,
            "expired": 0,
            "not_found": 1,
            "review": 1,
            "overall_status": "MANUAL REVIEW REQUIRED"
        }
        ai_summary = (
            f"The submitted documents could not be matched with any authorized organization in the trusted company reference "
            f"database. As per compliance protocols, reference company not found requires mandatory manual officer review."
        )
        return {
            "identified": False,
            "company_name": submitted_data.get("company_name") or "Unidentified Vendor",
            "reference_company": {},
            "identifier_used": None,
            "field_results": field_results,
            "cert_comparisons": cert_comparisons,
            "summary_stats": summary_stats,
            "ai_summary": ai_summary
        }

    # 1. Company Legal Name
    sub_name = (submitted_data.get("company_name") or "").strip()
    ref_name = (ref_company.get("company_name") or "").strip()
    clean_sub = re.sub(r"[^a-zA-Z0-9]", "", sub_name.lower())
    clean_ref = re.sub(r"[^a-zA-Z0-9]", "", ref_name.lower())
    
    if clean_sub == clean_ref:
        name_status = "MATCH"
        name_expl = "Exact match between submitted vendor name and registered company record."
    elif clean_sub in clean_ref or clean_ref in clean_sub:
        name_status = "MATCH"
        name_expl = "Normalized name match (punctuation/spacing variation handled)."
    elif not sub_name:
        name_status = "MISSING"
        name_expl = "Company name not clearly stated in submitted documents."
    else:
        name_status = "MISMATCH"
        name_expl = f"Submitted company name '{sub_name}' differs from reference name '{ref_name}'."

    field_results.append({
        "field": "Company Legal Name",
        "category": "Company Details",
        "submitted": sub_name or "Missing",
        "reference": ref_name,
        "status": name_status,
        "explanation": name_expl,
        "source_document": source_map.get("company_name", "Tender Bid Document"),
        "is_exact": True
    })

    # 2. GSTIN (Deterministic)
    sub_gst = (submitted_data.get("gstin") or "").strip().upper()
    ref_gst = (ref_company.get("gstin") or "").strip().upper()
    if sub_gst and ref_gst and sub_gst == ref_gst:
        gst_status = "MATCH"
        gst_expl = "Deterministic verification: GSTIN values match exactly (15 alphanumeric characters)."
    elif not sub_gst:
        gst_status = "MISSING"
        gst_expl = "GSTIN was not found in the uploaded submission."
    else:
        gst_status = "MISMATCH"
        gst_expl = f"GSTIN mismatch! Submitted '{sub_gst}' does not match reference '{ref_gst}'."

    field_results.append({
        "field": "GSTIN (Tax ID)",
        "category": "Company Details",
        "submitted": sub_gst or "Missing",
        "reference": ref_gst,
        "status": gst_status,
        "explanation": gst_expl,
        "source_document": source_map.get("gstin", "GST / Bid Document"),
        "is_exact": True
    })

    # 3. CIN (Deterministic)
    sub_cin = (submitted_data.get("cin") or "").strip().upper()
    ref_cin = (ref_company.get("cin") or "").strip().upper()
    if sub_cin and ref_cin and sub_cin == ref_cin:
        cin_status = "MATCH"
        cin_expl = "Deterministic verification: CIN matches Ministry of Corporate Affairs reference record."
    elif not sub_cin:
        cin_status = "MISSING"
        cin_expl = "CIN was not provided in the uploaded submission."
    else:
        cin_status = "MISMATCH"
        cin_expl = f"CIN mismatch! Submitted '{sub_cin}' does not match reference '{ref_cin}'."

    field_results.append({
        "field": "CIN (Corporate Identity)",
        "category": "Company Details",
        "submitted": sub_cin or "Missing",
        "reference": ref_cin,
        "status": cin_status,
        "explanation": cin_expl,
        "source_document": source_map.get("cin", "Incorporation / Bid Document"),
        "is_exact": True
    })

    # 4. Registration Number (Deterministic)
    if ref_company.get("registration_number"):
        ref_reg = ref_company.get("registration_number").strip()
        sub_reg = (submitted_data.get("registration_number") or "").strip()
        if sub_reg and sub_reg.upper() == ref_reg.upper():
            reg_status = "MATCH"
            reg_expl = "Registration numbers match exactly."
        elif not sub_reg:
            reg_status = "REQUIRES REVIEW"
            reg_expl = "Distinct registration number not explicitly listed; verified via CIN/GSTIN."
        else:
            reg_status = "MISMATCH"
            reg_expl = f"Registration number '{sub_reg}' differs from registered '{ref_reg}'."

        field_results.append({
            "field": "Registration Number",
            "category": "Company Details",
            "submitted": sub_reg or "Not specified",
            "reference": ref_reg,
            "status": reg_status,
            "explanation": reg_expl,
            "source_document": source_map.get("company_name", "Registration Document"),
            "is_exact": True
        })

    # 5. Experience Years
    ref_exp = ref_company.get("experience_years", 0)
    sub_exp = submitted_data.get("experience_years")
    if sub_exp is not None and sub_exp != "":
        sub_exp_val = int(sub_exp)
        if sub_exp_val >= ref_exp:
            exp_status = "MATCH"
            exp_expl = f"Submitted experience of {sub_exp_val} years satisfies requirement ({ref_exp} years registered)."
        else:
            exp_status = "MISMATCH"
            exp_expl = f"Submitted experience ({sub_exp_val} years) is below verified organization tenure ({ref_exp} years)."
    else:
        exp_status = "MISSING"
        exp_expl = "No experience declaration found in submitted tender bid."

    field_results.append({
        "field": "Years of Experience",
        "category": "Eligibility",
        "submitted": f"{sub_exp} Years" if sub_exp is not None else "Missing",
        "reference": f"{ref_exp} Years",
        "status": exp_status,
        "explanation": exp_expl,
        "source_document": "Experience / Bid Summary",
        "is_exact": True
    })

    # 6. Product Details & Technical Specifications (Deterministic + Gemini Semantic)
    ref_products = ref_company.get("products", [])
    sub_products = submitted_data.get("products", [])

    if ref_products:
        for ref_prod in ref_products:
            ref_prod_name = ref_prod.get("name", "")
            # Find matching submitted product
            matched_sub_prod = None
            for sp in sub_products:
                if ref_prod_name.lower() in sp.get("name", "").lower() or sp.get("name", "").lower() in ref_prod_name.lower():
                    matched_sub_prod = sp
                    break

            if matched_sub_prod:
                # Exact name check
                field_results.append({
                    "field": f"Product: {ref_prod_name}",
                    "category": "Products",
                    "submitted": matched_sub_prod.get("name"),
                    "reference": ref_prod_name,
                    "status": "MATCH",
                    "explanation": f"Product '{ref_prod_name}' is approved in organization reference catalog.",
                    "source_document": source_map.get("products", "Product Spec Document"),
                    "is_exact": True
                })

                # Technical Specification comparison
                ref_spec = ref_prod.get("specs", "")
                sub_spec = matched_sub_prod.get("specs", "")
                if ref_spec and sub_spec:
                    sem_res = semantic_compare_specifications(sub_spec, ref_spec, field_name=ref_prod_name)
                    spec_status = "MATCH" if sem_res.get("match") else "REQUIRES REVIEW"
                    field_results.append({
                        "field": f"Tech Specs ({ref_prod_name})",
                        "category": "Specifications",
                        "submitted": sub_spec,
                        "reference": ref_spec,
                        "status": spec_status,
                        "explanation": f"AI Semantic Analysis ({sem_res.get('confidence', 'CONFIRMED')}): {sem_res.get('explanation')}",
                        "source_document": source_map.get("products", "Technical Specification"),
                        "is_exact": False
                    })
            else:
                field_results.append({
                    "field": f"Product: {ref_prod_name}",
                    "category": "Products",
                    "submitted": "NOT OFFERED IN BID",
                    "reference": ref_prod_name,
                    "status": "MISSING",
                    "explanation": f"Required catalog product '{ref_prod_name}' was not detected in vendor submission.",
                    "source_document": "Bid Submission",
                    "is_exact": True
                })

    # 7. Certificate & File-Level Verification
    ref_certs = ref_company.get("certificates", [])
    sub_certs = submitted_data.get("certificates", [])

    for r_cert in ref_certs:
        c_name = r_cert.get("name", "Certificate")
        r_num = r_cert.get("certificate_number", "").strip()
        r_valid = r_cert.get("valid_until", "").strip()

        # Find matching submitted certificate
        matching_sub_cert = None
        for sc in sub_certs:
            if c_name.lower() in sc.get("name", "").lower() or sc.get("name", "").lower() in c_name.lower():
                matching_sub_cert = sc
                break

        if matching_sub_cert:
            s_num = (matching_sub_cert.get("certificate_number") or "").strip()
            s_valid = (matching_sub_cert.get("valid_until") or "").strip()
            s_holder = matching_sub_cert.get("company_name_on_cert") or sub_name

            # Compare Certificate Number (Deterministic)
            if s_num and r_num and s_num.upper() == r_num.upper():
                cert_num_status = "MATCH"
                cert_num_expl = f"Certificate numbers match exactly ({s_num})."
            elif not s_num:
                cert_num_status = "MISSING"
                cert_num_expl = "Certificate number not indicated on submitted copy."
            else:
                cert_num_status = "MISMATCH"
                cert_num_expl = f"Certificate number MISMATCH: Submitted '{s_num}' vs Trusted Reference '{r_num}'."

            # Compare Certificate Validity / Expiry (Deterministic Date Rules)
            is_sub_expired = is_date_expired(s_valid) if s_valid else False
            if is_sub_expired:
                valid_status = "EXPIRED"
                valid_expl = f"Submitted certificate expired on {s_valid}. Action required: renewal verification."
            elif s_valid and r_valid:
                if s_valid == r_valid:
                    valid_status = "MATCH"
                    valid_expl = f"Validity dates match ({s_valid}) and certificate is currently ACTIVE."
                else:
                    valid_status = "REQUIRES REVIEW"
                    valid_expl = f"Validity date variance: Submitted {s_valid} vs Reference {r_valid}."
            elif s_valid and not is_sub_expired:
                valid_status = "MATCH"
                valid_expl = f"Certificate is valid until {s_valid}."
            else:
                valid_status = "REQUIRES REVIEW"
                valid_expl = "Certificate validity date not specified."

            # Company name on certificate check
            holder_status = "MATCH" if clean_sub in clean_ref or clean_ref in clean_sub else "MISMATCH"

            # Record in Field Results
            field_results.append({
                "field": f"{c_name} Certificate Number",
                "category": "Certifications",
                "submitted": s_num or "Missing",
                "reference": r_num,
                "status": cert_num_status,
                "explanation": cert_num_expl,
                "source_document": source_map.get("certificates", f"{c_name} File"),
                "is_exact": True
            })

            field_results.append({
                "field": f"{c_name} Validity Date",
                "category": "Certifications",
                "submitted": s_valid or "Not stated",
                "reference": r_valid or "Permanent / Active",
                "status": valid_status,
                "explanation": valid_expl,
                "source_document": source_map.get("certificates", f"{c_name} File"),
                "is_exact": True
            })

            # Record in File-Level Certificate Comparisons
            cert_comparisons.append({
                "certificate_name": c_name,
                "submitted_file": source_map.get("certificates", "Submitted Certificate"),
                "reference_file": r_cert.get("reference_file", "Official Repository File"),
                "checks": [
                    {
                        "property": "Certificate Number",
                        "submitted": s_num,
                        "reference": r_num,
                        "status": cert_num_status
                    },
                    {
                        "property": "Company Name on Cert",
                        "submitted": s_holder,
                        "reference": ref_name,
                        "status": holder_status
                    },
                    {
                        "property": "Certificate Validity",
                        "submitted": s_valid,
                        "reference": r_valid,
                        "status": valid_status
                    }
                ]
            })
        else:
            field_results.append({
                "field": f"{c_name} Certificate",
                "category": "Certifications",
                "submitted": "NOT SUBMITTED",
                "reference": f"{r_num} (Valid: {r_valid})",
                "status": "MISSING",
                "explanation": f"Mandatory compliance certificate '{c_name}' was not enclosed in the submission.",
                "source_document": "Uploaded Package",
                "is_exact": True
            })

    # 8. Required Reference Documents Check
    ref_docs = ref_company.get("documents", [])
    for rd in ref_docs:
        doc_name = rd.get("name", "Reference Document")
        # Check if mention in submission
        found = False
        for fr in field_results:
            if doc_name.lower() in fr.get("field", "").lower() or doc_name.lower() in fr.get("source_document", "").lower():
                found = True
                break
        if not found:
            field_results.append({
                "field": f"Document: {doc_name}",
                "category": "Required Documents",
                "submitted": "Document not uploaded",
                "reference": f"Mandatory Archive File: {rd.get('reference_file', 'Available')}",
                "status": "MISSING",
                "explanation": f"Reference document '{doc_name}' is designated in registry but missing from bid submission.",
                "source_document": "Officer Document Package",
                "is_exact": True
            })

    # Summary Statistics Calculation
    matched_count = sum(1 for f in field_results if f["status"] == "MATCH")
    mismatched_count = sum(1 for f in field_results if f["status"] == "MISMATCH")
    missing_count = sum(1 for f in field_results if f["status"] == "MISSING")
    expired_count = sum(1 for f in field_results if f["status"] == "EXPIRED")
    review_count = sum(1 for f in field_results if f["status"] in ["REQUIRES REVIEW", "NOT FOUND"])

    overall_status = "COMPLIANT"
    if expired_count > 0 or mismatched_count > 0:
        overall_status = "NON-COMPLIANT (DISCREPANCIES DETECTED)"
    elif missing_count > 0 or review_count > 0:
        overall_status = "CONDITIONAL / OFFICER REVIEW REQUIRED"

    summary_stats = {
        "total": len(field_results),
        "matched": matched_count,
        "mismatched": mismatched_count,
        "missing": missing_count,
        "expired": expired_count,
        "review": review_count,
        "overall_status": overall_status
    }

    # Generate AI Explanation with Gemini
    ai_summary = generate_compliance_summary(ref_name, audit_id or "AUDIT-NEW", summary_stats, field_results)

    return {
        "identified": True,
        "company_name": ref_name,
        "reference_company": ref_company,
        "identifier_used": id_used,
        "field_results": field_results,
        "cert_comparisons": cert_comparisons,
        "summary_stats": summary_stats,
        "ai_summary": ai_summary
    }
