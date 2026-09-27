/**
 * Multi-Language (English & Hindi) Localization Support for VeriBid
 * Supports seamless instant switching and persistence via localStorage.
 */

const translations = {
  en: {
    // Navbar
    brand_title: "AI Bid Compliance",
    brand_sub: "| Verification System",
    nav_dashboard: "Dashboard",
    nav_new_audit: "New Audit",
    nav_previous_audits: "Previous Audits",
    nav_reports: "Reports",
    nav_reference_portal: "Reference Portal",
    btn_new_audit: "New Audit",

    // Dashboard
    dash_title: "Compliance Verification Dashboard",
    dash_subtitle: "Automated verification of submitted bid credentials against trusted organization records.",
    metric_total: "Total Audits",
    metric_compliant: "Compliant",
    metric_mismatch: "Mismatches / Flagged",
    metric_review: "Manual Review Required",
    demo_box_title: "Demo Test Profiles:",
    demo_box_sub: "Run pre-loaded sample bids to test match vs discrepancy handling:",
    btn_demo_match: "Run ABC Tech (Full Match)",
    btn_demo_mismatch: "Run Apex Global (Mismatch / Expired)",
    recent_audits_title: "Recent Audits",
    view_all: "View all",
    th_audit_id: "Audit ID",
    th_company_name: "Company Name",
    th_tender_ref: "Tender Ref",
    th_uploaded_files: "Uploaded Files",
    th_summary: "Verification Summary",
    th_status: "Status",
    th_created: "Created",
    th_actions: "Actions",
    no_records: "No compliance audits recorded.",

    // New Audit Form
    breadcrumb_dash: "Dashboard",
    breadcrumb_new: "New Audit",
    new_audit_title: "New Bid Compliance Verification",
    new_audit_subtitle: "Upload tender documents to extract company data and cross-verify with trusted reference records.",
    card_audit_params: "Audit Parameters & Document Upload",
    lbl_audit_id: "Audit ID",
    help_audit_id: "Unique audit reference code.",
    lbl_tender_ref: "Tender / RFP Reference",
    help_tender_ref: "Optional procurement reference identifier.",
    lbl_tender_title: "Tender Title",
    lbl_vendor_name: "Vendor Name (Optional)",
    help_vendor_name: "If left blank, company name is identified from uploaded files.",
    lbl_upload_docs: "Upload Documents",
    dropzone_title: "Drag and drop tender documents here",
    dropzone_subtitle: "PDF, DOCX, TXT, or scan images",
    btn_choose_files: "Choose Files",
    btn_cancel: "Cancel",
    btn_start_verification: "Start AI Verification",
    sample_docs_note: "Need sample test documents? Use one-click sample verification:",
    test_abc_match: "Test: ABC Tech (Matching)",
    test_apex_mismatch: "Test: Apex Global (Mismatch)",

    // Results Dashboard
    results_title: "Compliance Verification Results",
    lbl_audited_company: "Audited Company / Vendor",
    lbl_overall_status: "Overall Compliance Status",
    stat_matched: "Matched",
    stat_mismatched: "Mismatched",
    stat_missing: "Missing",
    stat_expired: "Expired",
    ai_summary_title: "Automated Findings Summary",
    btn_translate_summary: "Translate Summary to Hindi (हिन्दी)",
    btn_show_original: "Show Original English",
    table_field_title: "Field-by-Field Verification",
    table_field_subtitle: "Click row for source & details",
    th_field: "Field",
    th_submitted: "Submitted Data",
    th_reference: "Reference Data",
    th_result: "Result",
    th_details: "Details",
    cert_comparison_title: "Certificate File Comparison",
    btn_download_pdf: "Download PDF Report",
    footer_report_note: "Official audit dossier available for download and record archiving.",

    // Reference Portal
    ref_portal_title: "Reference Data Portal",
    ref_portal_sub: "| Admin",
    nav_companies: "Companies",
    nav_add_company: "Add Company",
    nav_api_docs: "REST API Docs",
    btn_open_officer_app: "Open Officer App",
    ref_companies_title: "Trusted Reference Companies",
    ref_companies_subtitle: "Master database records used as the trusted reference for compliance checks.",

    // Audit History & Reports
    audit_history_title: "Audit History",
    audit_history_subtitle: "Repository of all processed bid compliance audits.",
    filter_placeholder: "Search by Audit ID, Company Name, Tender ID, or GSTIN...",
    all_statuses: "All Statuses",
    btn_filter: "Filter",
    th_gstin: "GSTIN",
    btn_view: "View",
    btn_pdf: "PDF",
    reports_title: "Generated Compliance Reports",
    reports_subtitle: "Downloadable PDF audit dossiers.",
    th_report_file: "Report File",
    th_generated_date: "Generated Date",
    th_download: "Download"
  },

  hi: {
    // Navbar
    brand_title: "एआई बोली अनुपालन",
    brand_sub: "| सत्यापन प्रणाली",
    nav_dashboard: "डैशबोर्ड",
    nav_new_audit: "नया ऑडिट",
    nav_previous_audits: "पिछले ऑडिट",
    nav_reports: "रिपोर्ट्स",
    nav_reference_portal: "संदर्भ पोर्टल",
    btn_new_audit: "नया ऑडिट",

    // Dashboard
    dash_title: "अनुपालन सत्यापन डैशबोर्ड",
    dash_subtitle: "विश्वसनीय संगठन रिकॉर्ड के विरुद्ध प्रस्तुत निविदा दस्तावेजों का स्वचालित सत्यापन।",
    metric_total: "कुल ऑडिट",
    metric_compliant: "पूर्ण अनुपालन",
    metric_mismatch: "विसंगति / बेमेल",
    metric_review: "समीक्षा आवश्यक",
    demo_box_title: "डेमो टेस्ट प्रोफाइल:",
    demo_box_sub: "सत्यापन और विसंगति परीक्षण के लिए पूर्व-लोड किए गए नमूना निविदाएं चलाएं:",
    btn_demo_match: "एबीसी टेक चलाएं (पूर्ण मेल)",
    btn_demo_mismatch: "एपेक्स ग्लोबल चलाएं (बेमेल / समाप्त)",
    recent_audits_title: "हालिया ऑडिट सूची",
    view_all: "सभी देखें",
    th_audit_id: "ऑडिट आईडी",
    th_company_name: "कंपनी का नाम",
    th_tender_ref: "निविदा संदर्भ",
    th_uploaded_files: "अपलोड फाइलें",
    th_summary: "सत्यापन सारांश",
    th_status: "स्थिति",
    th_created: "दिनांक",
    th_actions: "कार्रवाई",
    no_records: "कोई ऑडिट दर्ज नहीं है।",

    // New Audit Form
    breadcrumb_dash: "डैशबोर्ड",
    breadcrumb_new: "नया ऑडिट",
    new_audit_title: "नई निविदा अनुपालन सत्यापन",
    new_audit_subtitle: "कंपनी डेटा निकालने और अधिकृत रिकॉर्ड से मिलान के लिए निविदा दस्तावेज अपलोड करें।",
    card_audit_params: "ऑडिट पैरामीटर और दस्तावेज अपलोड",
    lbl_audit_id: "ऑडिट आईडी",
    help_audit_id: "विशिष्ट ऑडिट संदर्भ पहचान कोड।",
    lbl_tender_ref: "निविदा / आरएफपी संदर्भ संख्या",
    help_tender_ref: "वैकल्पिक खरीद संदर्भ पहचानकर्ता।",
    lbl_tender_title: "निविदा शीर्षक",
    lbl_vendor_name: "विक्रेता का नाम (वैकल्पिक)",
    help_vendor_name: "खाली छोड़ने पर दस्तावेजों से एआई द्वारा निकाला जाएगा।",
    lbl_upload_docs: "निविदा दस्तावेज अपलोड करें",
    dropzone_title: "दस्तावेजों को यहां खींचें और छोड़ें (Drag & Drop)",
    dropzone_subtitle: "पीडीएफ, डॉक्स, टेक्स्ट या स्कैन की गई प्रतियां",
    btn_choose_files: "फाइलें चुनें",
    btn_cancel: "रद्द करें",
    btn_start_verification: "एआई सत्यापन शुरू करें",
    sample_docs_note: "नमूना परीक्षण दस्तावेज चाहिए? एक क्लिक में चलाएं:",
    test_abc_match: "परीक्षण: एबीसी टेक (समान)",
    test_apex_mismatch: "परीक्षण: एपेक्स ग्लोबल (बेमेल)",

    // Results Dashboard
    results_title: "अनुपालन सत्यापन परिणाम",
    lbl_audited_company: "सत्यापित कंपनी / विक्रेता",
    lbl_overall_status: "समग्र अनुपालन स्थिति",
    stat_matched: "मेल खाया (Matched)",
    stat_mismatched: "बेमेल (Mismatched)",
    stat_missing: "अनुपलब्ध (Missing)",
    stat_expired: "समाप्त (Expired)",
    ai_summary_title: "स्वचालित निष्कर्ष सारांश",
    btn_translate_summary: "हिंदी में सारांश देखें",
    btn_show_original: "मूल अंग्रेजी देखें",
    table_field_title: "फ़ील्ड-वार सत्यापन विवरण",
    table_field_subtitle: "स्रोत और विवरण के लिए पंक्ति पर क्लिक करें",
    th_field: "सत्यापन फ़ील्ड",
    th_submitted: "प्रस्तुत डेटा",
    th_reference: "संदर्भ रिकॉर्ड डेटा",
    th_result: "सत्यापन परिणाम",
    th_details: "विवरण",
    cert_comparison_title: "प्रमाणपत्र फ़ाइल स्तर तुलना",
    btn_download_pdf: "पीडीएफ रिपोर्ट डाउनलोड करें",
    footer_report_note: "आधिकारिक ऑडिट रिपोर्ट डाउनलोड और रिकॉर्ड संग्रह के लिए तैयार है।",

    // Reference Portal
    ref_portal_title: "कंपनी संदर्भ डेटा पोर्टल",
    ref_portal_sub: "| व्यवस्थापक",
    nav_companies: "कंपनियां",
    nav_add_company: "कंपनी जोड़ें",
    nav_api_docs: "रेस्ट एपीआई प्रलेखन",
    btn_open_officer_app: "अधिकारी पोर्टल खोलें",
    ref_companies_title: "विश्वसनीय संदर्भ कंपनियां",
    ref_companies_subtitle: "संगठन द्वारा अनुपालन जांच के लिए बनाए गए आधिकारिक संदर्भ रिकॉर्ड।",

    // Audit History & Reports
    audit_history_title: "ऑडिट इतिहास",
    audit_history_subtitle: "सभी संसाधित बोली अनुपालन ऑडिट का रिपॉजिटरी।",
    filter_placeholder: "ऑडिट आईडी, कंपनी का नाम, निविदा आईडी या जीएसटीएन द्वारा खोजें...",
    all_statuses: "सभी स्थितियां",
    btn_filter: "फ़िल्टर करें",
    th_gstin: "जीएसटीएन (GSTIN)",
    btn_view: "देखें",
    btn_pdf: "पीडीएफ",
    reports_title: "उत्पन्न अनुपालन रिपोर्ट्स",
    reports_subtitle: "डाउनलोड करने योग्य पीडीएफ ऑडिट डॉसियर।",
    th_report_file: "रिपोर्ट फ़ाइल",
    th_generated_date: "उत्पादन तिथि",
    th_download: "डाउनलोड"
  }
};

/**
 * Applies the selected language to all elements with data-i18n attributes.
 */
function setLanguage(lang) {
  if (!translations[lang]) lang = 'en';
  localStorage.setItem('veribid_lang', lang);

  // Update text of elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });

  // Update placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (translations[lang][key]) {
      el.setAttribute('placeholder', translations[lang][key]);
    }
  });

  // Update language switcher buttons
  const btnEn = document.getElementById('lang-btn-en');
  const btnHi = document.getElementById('lang-btn-hi');
  if (btnEn && btnHi) {
    if (lang === 'hi') {
      btnHi.classList.add('active', 'btn-primary');
      btnHi.classList.remove('btn-outline-light', 'btn-outline-secondary');
      btnEn.classList.remove('active', 'btn-primary');
      btnEn.classList.add('btn-outline-secondary');
    } else {
      btnEn.classList.add('active', 'btn-primary');
      btnEn.classList.remove('btn-outline-light', 'btn-outline-secondary');
      btnHi.classList.remove('active', 'btn-primary');
      btnHi.classList.add('btn-outline-secondary');
    }
  }

  // Update dynamic badges / results if present
  updateDynamicStatuses(lang);

  // Dispatch event for custom components
  window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: lang } }));
}

function updateDynamicStatuses(lang) {
  // Update status badge texts in tables
  const statusBadges = document.querySelectorAll('.badge');
  statusBadges.forEach(b => {
    const text = b.textContent.trim();
    if (lang === 'hi') {
      if (text === 'COMPLIANT' || text.includes('COMPLIANT')) b.innerHTML = '<i class="fa-solid fa-check-circle me-1"></i> अनुपालन (COMPLIANT)';
      else if (text === 'DISCREPANCY' || text.includes('DISCREPANCY')) b.innerHTML = '<i class="fa-solid fa-circle-xmark me-1"></i> विसंगति (DISCREPANCY)';
      else if (text === 'REVIEW' || text === 'REVIEW REQUIRED' || text.includes('REVIEW')) b.innerHTML = '<i class="fa-solid fa-triangle-exclamation me-1"></i> समीक्षा (REVIEW)';
      else if (text === 'MATCH') b.textContent = 'समान (MATCH)';
      else if (text === 'MISMATCH') b.textContent = 'बेमेल (MISMATCH)';
      else if (text === 'MISSING') b.textContent = 'अनुपलब्ध (MISSING)';
      else if (text === 'EXPIRED') b.textContent = 'समाप्त (EXPIRED)';
    } else {
      if (text.includes('अनुपालन')) b.innerHTML = '<i class="fa-solid fa-check-circle me-1"></i> COMPLIANT';
      else if (text.includes('विसंगति')) b.innerHTML = '<i class="fa-solid fa-circle-xmark me-1"></i> DISCREPANCY';
      else if (text.includes('समीक्षा')) b.innerHTML = '<i class="fa-solid fa-triangle-exclamation me-1"></i> REVIEW REQUIRED';
      else if (text.includes('समान')) b.textContent = 'MATCH';
      else if (text.includes('बेमेल')) b.textContent = 'MISMATCH';
      else if (text.includes('अनुपलब्ध')) b.textContent = 'MISSING';
      else if (text.includes('समाप्त')) b.textContent = 'EXPIRED';
    }
  });
}

// Auto-run on DOM load
document.addEventListener('DOMContentLoaded', () => {
  const currentLang = localStorage.getItem('veribid_lang') || 'en';
  setLanguage(currentLang);
});
