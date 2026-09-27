"""
Audit Report Generator.
Generates an official, publication-quality PDF compliance audit report
matching all specification requirements.
"""

import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_pdf_report(submission_record, verification_result):
    """
    Builds a comprehensive PDF report for an audit submission.
    Returns: filepath to generated PDF.
    """
    audit_id = submission_record.get("audit_id", "AUDIT-000")
    company_name = verification_result.get("company_name") or submission_record.get("company_name", "Vendor Submission")
    timestamp = submission_record.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    filename = f"{audit_id}_compliance_report.pdf"
    filepath = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    header_sub_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    ai_summary_style = ParagraphStyle(
        'AiSummary',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # 1. Header Block with Logo
    logo_path = BASE_DIR / "main_audit_app" / "static" / "img" / "logo.jpg"
    if logo_path.exists():
        try:
            from reportlab.platypus import Image as RLImage
            logo_img = RLImage(str(logo_path), width=100, height=45)
            title_paras = [
                Paragraph("AI BID & COMPANY COMPLIANCE VERIFICATION SYSTEM", header_title_style),
                Paragraph("OFFICIAL COMPLIANCE AUDIT & VERIFICATION REPORT &bull; STRICT CONFIDENTIAL", header_sub_style)
            ]
            header_table = Table([[logo_img, title_paras]], colWidths=[110, 430])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(header_table)
        except Exception:
            story.append(Paragraph("AI BID & COMPANY COMPLIANCE VERIFICATION SYSTEM", header_title_style))
            story.append(Paragraph("OFFICIAL COMPLIANCE AUDIT & VERIFICATION REPORT &bull; STRICT CONFIDENTIAL", header_sub_style))
    else:
        story.append(Paragraph("AI BID & COMPANY COMPLIANCE VERIFICATION SYSTEM", header_title_style))
        story.append(Paragraph("OFFICIAL COMPLIANCE AUDIT & VERIFICATION REPORT &bull; STRICT CONFIDENTIAL", header_sub_style))

    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=10))

    # Meta Table
    stats = verification_result.get("summary_stats", {})
    overall_status = stats.get("overall_status", "MANUAL REVIEW REQUIRED")
    
    status_bg = colors.HexColor('#ecfdf5') if "COMPLIANT" in overall_status and "NON" not in overall_status else colors.HexColor('#fef2f2')
    status_fg = colors.HexColor('#059669') if "COMPLIANT" in overall_status and "NON" not in overall_status else colors.HexColor('#dc2626')

    meta_data = [
        [
            Paragraph("<b>Audit ID:</b> " + audit_id, body_style),
            Paragraph("<b>Audit Date:</b> " + str(timestamp), body_style)
        ],
        [
            Paragraph("<b>Vendor / Company:</b> " + company_name, body_style),
            Paragraph("<b>Tender Ref:</b> " + submission_record.get("tender_id", "TNDR-GENERAL-2026"), body_style)
        ],
        [
            Paragraph("<b>Overall Compliance:</b> <b>" + overall_status + "</b>", ParagraphStyle('St', parent=body_style, textColor=status_fg)),
            Paragraph(f"<b>Findings:</b> {stats.get('matched', 0)} Matched | {stats.get('mismatched', 0)} Mismatched | {stats.get('missing', 0)} Missing | {stats.get('expired', 0)} Expired", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 2. AI Summary Section
    story.append(Paragraph("AI Executive Findings Summary", section_title_style))
    ai_text = verification_result.get("ai_summary", "No automated summary available.")
    ai_box_data = [[Paragraph(ai_text, ai_summary_style)]]
    ai_table = Table(ai_box_data, colWidths=[540])
    ai_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f9ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#bae6fd')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(ai_table)
    story.append(Spacer(1, 10))

    # 3. Documents Received
    story.append(Paragraph("Documents Received & Analyzed", section_title_style))
    docs_uploaded = submission_record.get("uploaded_documents", [])
    doc_rows = [["Filename", "File Size", "Traceable Origin"]]
    for d in docs_uploaded:
        sz = d.get("size", 0)
        sz_str = f"{sz / 1024:.1f} KB" if sz > 0 else "N/A"
        doc_rows.append([
            Paragraph(d.get("original_name", d.get("filename", "Doc")), body_style),
            Paragraph(sz_str, body_style),
            Paragraph("Officer Bid Submission Vault", body_style)
        ])
    docs_table = Table(doc_rows, colWidths=[280, 100, 160])
    docs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(docs_table)
    story.append(Spacer(1, 10))

    # 4. Field-by-Field Verification Table
    story.append(Paragraph("Field-by-Field Compliance Verification Results", section_title_style))
    fields = verification_result.get("field_results", [])
    table_rows = [["Audit Field", "Submitted Value", "Reference Value", "Status", "Source / Document"]]
    
    for f in fields:
        status_val = f.get("status", "REVIEW")
        status_color = "#059669" if status_val == "MATCH" else "#dc2626" if status_val in ["MISMATCH", "EXPIRED"] else "#d97706"
        
        status_cell = Paragraph(
            f"<font color='{status_color}'><b>{status_val}</b></font>",
            body_style
        )
        
        sub_cell = Paragraph(str(f.get("submitted", "-"))[:120], body_style)
        ref_cell = Paragraph(str(f.get("reference", "-"))[:120], body_style)
        f_name_cell = Paragraph(f"<b>{f.get('field')}</b>", body_style)
        src_cell = Paragraph(str(f.get("source_document", "-")), body_style)
        
        table_rows.append([f_name_cell, sub_cell, ref_cell, status_cell, src_cell])

    fields_table = Table(table_rows, colWidths=[120, 120, 120, 75, 105])
    fields_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(fields_table)
    story.append(Spacer(1, 10))

    # 5. Certificate Verification Breakdown
    cert_comps = verification_result.get("cert_comparisons", [])
    if cert_comps:
        story.append(Paragraph("Certificate-Level Verification Checks", section_title_style))
        for c in cert_comps:
            c_rows = [["Property", "Submitted Certificate", "Reference Record", "Result"]]
            for chk in c.get("checks", []):
                chk_stat = chk.get("status", "REVIEW")
                col = "#059669" if chk_stat == "MATCH" else "#dc2626"
                c_rows.append([
                    Paragraph(f"<b>{chk.get('property')}</b>", body_style),
                    Paragraph(str(chk.get("submitted", "-")), body_style),
                    Paragraph(str(chk.get("reference", "-")), body_style),
                    Paragraph(f"<font color='{col}'><b>{chk_stat}</b></font>", body_style)
                ])
            c_tbl = Table(c_rows, colWidths=[140, 150, 150, 100])
            c_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(Paragraph(f"<b>Certificate: {c.get('certificate_name')}</b> (Submitted File: {c.get('submitted_file')})", body_style))
            story.append(c_tbl)
            story.append(Spacer(1, 6))

    # 6. Statutory Disclaimer & Sign-off
    story.append(Spacer(1, 12))
    disclaimer_text = (
        "<b>OFFICIAL COMPLIANCE DISCLAIMER:</b> This automated verification report was compiled using deterministic "
        "business rules and Gemini AI document reasoning. This report serves as an assistive technical decision-support tool "
        "for procurement and compliance officers. Final tender award and legal procurement decisions must be formally approved "
        "by the designated organizational authority."
    )
    disclaimer_data = [[Paragraph(disclaimer_text, ParagraphStyle('Disc', parent=body_style, fontSize=7.5, leading=10, textColor=colors.HexColor('#64748b')))]]
    disc_table = Table(disclaimer_data, colWidths=[540])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(disc_table)

    # Build PDF
    doc.build(story)
    return str(filepath)
