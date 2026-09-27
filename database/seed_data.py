"""
Seed Data Generator for AI Bid & Company Compliance Verification System.
Creates trusted reference companies in the Reference Database,
and generates realistic sample reference PDFs and officer bid documents
for Company 1 (Full Match) and Company 2 (Intentional Mismatch / Missing).
"""

import os
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from database.db import get_reference_db

BASE_DIR = Path(__file__).resolve().parent.parent
REF_DOCS_DIR = BASE_DIR / "reference_portal" / "reference_documents"
DEMO_BIDS_DIR = BASE_DIR / "demo_files" / "sample_bids"

REF_DOCS_DIR.mkdir(parents=True, exist_ok=True)
DEMO_BIDS_DIR.mkdir(parents=True, exist_ok=True)


def create_sample_pdf(filepath, title, header_info, body_paragraphs, table_data=None):
    """Generates a professional sample PDF document using ReportLab."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )
    
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Paragraph("OFFICIAL RECORD / VERIFIED REFERENCE DOCUMENT - SAMPLE DATA", subtitle_style))
    story.append(Spacer(1, 10))
    
    for h in header_info:
        story.append(Paragraph(f"<b>{h[0]}:</b> {h[1]}", body_style))
    story.append(Spacer(1, 12))
    
    for p in body_paragraphs:
        story.append(Paragraph(p, body_style))
        
    if table_data:
        story.append(Spacer(1, 10))
        t = Table(table_data, colWidths=[180, 320])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9.5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        
    doc.build(story)


def seed_reference_data():
    """Seeds the Reference Database with trusted records and generates sample PDFs."""
    ref_db = get_reference_db()
    
    # Generate Sample Reference Documents for Company 1
    create_sample_pdf(
        REF_DOCS_DIR / "abc_gst_certificate.pdf",
        "GOVERNMENT OF INDIA - CERTIFICATE OF GST REGISTRATION",
        [
            ("Registration Number (GSTIN)", "33ABCDE1234F1Z5"),
            ("Legal Name", "ABC Technologies Pvt Ltd"),
            ("Date of Validity", "01/04/2018 to Permanent"),
            ("State Jurisdiction", "Tamil Nadu, India")
        ],
        [
            "This is to certify that ABC Technologies Pvt Ltd is duly registered under the Central Goods and Services Tax Act.",
            "Principal place of business: Plot 42, Electronics City Phase 1, Chennai, Tamil Nadu 600001."
        ]
    )
    
    create_sample_pdf(
        REF_DOCS_DIR / "abc_iso_9001.pdf",
        "INTERNATIONAL STANDARDIZATION CERTIFICATION (ISO 9001:2015)",
        [
            ("Certificate Number", "ISO123456"),
            ("Certified Organization", "ABC Technologies Pvt Ltd"),
            ("Standard", "ISO 9001:2015 Quality Management Systems"),
            ("Issuing Body", "Global Quality Registrar (GQR)"),
            ("Issue Date", "16/08/2022"),
            ("Valid Until", "2027-08-15")
        ],
        [
            "Scope: Design, development, assembly, and testing of Industrial Routers, Enterprise Switches, and Embedded Communication Modules.",
            "Certified status: ACTIVE & FULLY COMPLIANT."
        ]
    )

    create_sample_pdf(
        REF_DOCS_DIR / "abc_tech_spec.pdf",
        "TRUSTED TECHNICAL SPECIFICATION - INDUSTRIAL ROUTER IR-500",
        [
            ("Company Name", "ABC Technologies Pvt Ltd"),
            ("Product Model", "Industrial Router IR-500"),
            ("Product Category", "Networking & Telecommunications"),
            ("Operating Temperature", "-10°C to 60°C"),
            ("Port Configuration", "5 Gigabit Ethernet Ports, 1 SFP Port"),
            ("Power Input", "9-36V DC Redundant Power Input")
        ],
        [
            "This specification is approved and maintained in the organization reference repository as standard benchmark."
        ]
    )

    # Generate Sample Reference Documents for Company 2
    create_sample_pdf(
        REF_DOCS_DIR / "apex_gst_certificate.pdf",
        "GOVERNMENT OF INDIA - CERTIFICATE OF GST REGISTRATION",
        [
            ("Registration Number (GSTIN)", "27AAACA9999P1Z3"),
            ("Legal Name", "Apex Global Solutions Ltd"),
            ("CIN", "L98765MH2015PLC654321"),
            ("State Jurisdiction", "Maharashtra, India")
        ],
        [
            "This is to certify that Apex Global Solutions Ltd is duly registered under the Goods and Services Tax Act."
        ]
    )

    create_sample_pdf(
        REF_DOCS_DIR / "apex_iso_9001.pdf",
        "INTERNATIONAL STANDARDIZATION CERTIFICATION (ISO 9001:2015)",
        [
            ("Certificate Number", "ISO-REF-88442"),
            ("Certified Organization", "Apex Global Solutions Ltd"),
            ("Valid Until", "2025-05-20"),
            ("Status", "ACTIVE")
        ],
        [
            "Verified Reference Record: Registered certificate number is ISO-REF-88442."
        ]
    )

    # Reference Database Records
    companies = [
        {
            "company_id": "COMP-001",
            "company_name": "ABC Technologies Pvt Ltd",
            "gstin": "33ABCDE1234F1Z5",
            "cin": "U12345TN2020PTC123456",
            "registration_number": "REG-TN-2020-0981",
            "contact_email": "tenders@abctechnologies.com",
            "contact_phone": "+91-44-28394012",
            "address": "Plot 42, Electronics City Phase 1, Chennai, Tamil Nadu 600001",
            "status": "APPROVED",
            "products": [
                {
                    "name": "Industrial Router",
                    "model": "IR-500",
                    "category": "Networking",
                    "specs": "Operating temperature from -10°C to 60°C, 5 Gigabit Ethernet Ports, 9-36V DC Redundant Power"
                },
                {
                    "name": "Network Switch",
                    "model": "NS-24G",
                    "category": "Networking",
                    "specs": "24 Port Managed Gigabit Switch, Layer 3 Routing"
                }
            ],
            "certificates": [
                {
                    "name": "ISO 9001",
                    "certificate_number": "ISO123456",
                    "issuing_body": "Global Quality Registrar (GQR)",
                    "issue_date": "2022-08-16",
                    "valid_until": "2027-08-15",
                    "reference_file": "abc_iso_9001.pdf",
                    "status": "ACTIVE"
                }
            ],
            "documents": [
                {
                    "name": "GST Certificate",
                    "reference_file": "abc_gst_certificate.pdf",
                    "verified": True
                },
                {
                    "name": "Technical Specification Sheet",
                    "reference_file": "abc_tech_spec.pdf",
                    "verified": True
                }
            ],
            "experience_years": 5,
            "eligibility_status": "COMPLIANT"
        },
        {
            "company_id": "COMP-002",
            "company_name": "Apex Global Solutions Ltd",
            "gstin": "27AAACA9999P1Z3",
            "cin": "L98765MH2015PLC654321",
            "registration_number": "REG-MH-2015-4412",
            "contact_email": "compliance@apexglobal.in",
            "contact_phone": "+91-22-67891234",
            "address": "1204 Nariman Point, Mumbai, Maharashtra 400021",
            "status": "APPROVED",
            "products": [
                {
                    "name": "Surveillance Camera",
                    "model": "SC-4K",
                    "category": "Security Hardware",
                    "specs": "4K Ultra-HD Weatherproof IP Camera with IR Night Vision up to 50m"
                }
            ],
            "certificates": [
                {
                    "name": "ISO 9001",
                    "certificate_number": "ISO-REF-88442",
                    "issuing_body": "TUV Certification Agency",
                    "issue_date": "2020-05-21",
                    "valid_until": "2025-05-20",
                    "reference_file": "apex_iso_9001.pdf",
                    "status": "ACTIVE"
                }
            ],
            "documents": [
                {
                    "name": "GST Certificate",
                    "reference_file": "apex_gst_certificate.pdf",
                    "verified": True
                }
            ],
            "experience_years": 8,
            "eligibility_status": "COMPLIANT"
        }
    ]

    for comp in companies:
        existing = ref_db.find_one({"company_id": comp["company_id"]})
        if existing:
            ref_db.update_one({"company_id": comp["company_id"]}, {"$set": comp})
        else:
            ref_db.insert_one(comp)
            
    print(f"[Seed] Reference database initialized with {len(companies)} trusted company profiles.")


def generate_sample_officer_bids():
    """
    Generates realistic bid tender submission PDF files for officers to upload during demo:
    - Set 1: ABC Technologies (MATCH on all fields)
    - Set 2: Apex Global Solutions (MISMATCH in ISO certificate, MISSING experience document)
    """
    # 1. ABC Technologies - Submitted Tender Bid & Credentials
    create_sample_pdf(
        DEMO_BIDS_DIR / "ABC_Tech_Bid_Submission.pdf",
        "TENDER SUBMISSION & COMPLIANCE BID",
        [
            ("Tender Reference", "TNDR-2026-IT-0049"),
            ("Vendor Legal Name", "ABC Technologies Pvt Ltd"),
            ("Goods & Services Tax (GSTIN)", "33ABCDE1234F1Z5"),
            ("Corporate Identity Number (CIN)", "U12345TN2020PTC123456"),
            ("Registration Number", "REG-TN-2020-0981"),
            ("Claimed Relevant Experience", "5 Years in Industrial Networking"),
            ("Primary Contact", "tenders@abctechnologies.com")
        ],
        [
            "We hereby submit our commercial and technical bid for Supply of Industrial Networking Hardware.",
            "Offered Product: Industrial Router IR-500.",
            "Technical Summary: Operating temperature from -10°C to 60°C with 5 Gigabit Ethernet Ports and dual 9-36V DC redundant power input.",
            "We declare that all information, certificates, and compliance declarations submitted herein are true and authentic."
        ],
        table_data=[
            ["Document Enclosed", "Document Ref / Number"],
            ["GST Registration Certificate", "33ABCDE1234F1Z5"],
            ["Certificate of Incorporation (CIN)", "U12345TN2020PTC123456"],
            ["Quality Certification", "ISO 9001:2015 (Cert No: ISO123456)"],
            ["Product Model Offered", "Industrial Router (IR-500)"]
        ]
    )
    
    create_sample_pdf(
        DEMO_BIDS_DIR / "ABC_Tech_ISO_Certificate.pdf",
        "QUALITY MANAGEMENT CERTIFICATE - ISO 9001:2015",
        [
            ("Holder Name", "ABC Technologies Pvt Ltd"),
            ("Certificate No", "ISO123456"),
            ("Standard", "ISO 9001:2015"),
            ("Issuing Authority", "Global Quality Registrar (GQR)"),
            ("Expiry / Valid Until", "2027-08-15")
        ],
        [
            "This document is submitted as proof of valid quality management standards compliance for Bid TNDR-2026-IT-0049."
        ]
    )

    # 2. Apex Global - Submitted Bid with Intentional MISMATCH and EXPIRED/MISSING fields
    create_sample_pdf(
        DEMO_BIDS_DIR / "Apex_Global_Bid_Submission.pdf",
        "TENDER SUBMISSION & COMPLIANCE BID",
        [
            ("Tender Reference", "TNDR-2026-SEC-0112"),
            ("Vendor Legal Name", "Apex Global Solutions Ltd"),
            ("Goods & Services Tax (GSTIN)", "27AAACA9999P1Z3"),
            ("Corporate Identity Number (CIN)", "L98765MH2015PLC654321"),
            ("Offered Product", "Surveillance Camera SC-4K")
        ],
        [
            "Apex Global Solutions Ltd submits technical bid for Municipal Security Equipment.",
            "Notice of Variation: ISO 9001 certificate submitted under renewal application code ISO999999 instead of registered reference certificate ISO-REF-88442.",
            "Experience document is omitted pending auditor signoff."
        ],
        table_data=[
            ["Declared Item", "Submitted Value"],
            ["Vendor Name", "Apex Global Solutions Ltd"],
            ["GSTIN", "27AAACA9999P1Z3"],
            ["CIN", "L98765MH2015PLC654321"],
            ["ISO Certificate No.", "ISO999999 (MISMATCH vs ISO-REF-88442)"],
            ["ISO Certificate Expiry", "2024-01-01 (EXPIRED)"]
        ]
    )

    create_sample_pdf(
        DEMO_BIDS_DIR / "Apex_Global_ISO_Certificate.pdf",
        "QUALITY SYSTEM CERTIFICATE - ISO 9001",
        [
            ("Company Name", "Apex Global Solutions Ltd"),
            ("Certificate Number", "ISO999999"),
            ("Valid Until", "2024-01-01")
        ],
        [
            "Submitted Certificate copy indicating differing certificate number and past validity date."
        ]
    )

    print(f"[Seed] Demo bid documents generated in {DEMO_BIDS_DIR}")


if __name__ == "__main__":
    seed_reference_data()
    generate_sample_officer_bids()
