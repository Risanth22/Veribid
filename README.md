# AI Bid & Company Compliance Verification System

An automated, professional compliance verification web application that verifies whether information submitted by a vendor or company in bid/tender documents matches the trusted reference information maintained separately by the organization.

---

## 1. System Architecture

The solution implements two logically separate systems communicating exclusively via a REST API:

```
┌───────────────────────────────────────────────────────────┐
│               A. Main AI Audit Application                │
│                   (Officer Dashboard)                     │
│                    Port: 5000                             │
│                                                           │
│  - Officer Document Upload (PDF, DOCX, TXT)               │
│  - Document Text Extraction Engine                        │
│  - Gemini AI Document Reasoning                           │
│  - Submitted Data Database (submissions collection)       │
│  - Field-by-Field Verification Engine                     │
│  - Interactive Results Dashboard                          │
│  - Official PDF Audit Report Generator                    │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼ HTTP REST API
┌───────────────────────────────────────────────────────────┐
│           B. Company Reference Data Website & API         │
│                 (Administrator Portal)                    │
│                    Port: 5001                             │
│                                                           │
│  - Authorized Admin Portal                                │
│  - Trusted Legal Identity & Registrations                 │
│  - Approved Products & Technical Specifications           │
│  - Reference Certificates & Expiry Dates                  │
│  - Official Reference Documents Archive                   │
│  - Reference Database (reference_companies collection)    │
│  - Public REST API (/api/reference/...)                   │
└───────────────────────────────────────────────────────────┘
```

---

## 2. Core Workflow

```
OFFICER
  ↓
Upload multiple bid documents (PDF/DOCX)
  ↓
Original documents saved to submission-specific vault
  ↓
Gemini extracts structured vendor data (JSON)
  ↓
Data stored in SUBMITTED DATABASE
  ↓
Identify company (Priority: GSTIN → CIN → Company ID → Company Name)
  ↓
Call separate REFERENCE REST API (Port 5001)
  ↓
Retrieve trusted reference records & official certificates
  ↓
Perform Field-by-Field Verification:
  - Exact Deterministic Rules (GSTIN, CIN, Cert Number, Dates, Experience)
  - Gemini Semantic Analysis (Technical Specifications, Complex Terms)
  - Certificate/File-Level Verification
  ↓
Generate status per field: MATCH, MISMATCH, MISSING, EXPIRED, NOT FOUND, REQUIRES REVIEW
  ↓
Gemini generates executive AI summary grounded in verified comparison findings
  ↓
Generate downloadable official PDF Compliance Audit Dossier
```

---

## 3. Technology Stack

* **Backend**: Python 3, Flask, Jinja2, Werkzeug
* **AI & Document Understanding**: Google Gemini API (`gemini-2.5-flash` / `gemini-1.5-flash`)
* **Document Processing**: PyMuPDF, PyPDF, python-docx
* **Reporting**: ReportLab (Official PDF Audit Dossier)
* **Database**: MongoDB (via `pymongo`) with built-in zero-config persistent JSON storage fallback
* **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, FontAwesome 6, Vanilla JavaScript

---

## 4. Directory Structure

```text
ai-compliance-system/
├── main_audit_app/
│   ├── app.py                     # Main Flask Application (Port 5000)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── audit_routes.py        # Dashboard, New Audit, Verification, Reports
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_extraction.py # PDF/DOCX multi-document text extractor
│   │   ├── gemini_service.py      # Gemini structured extraction & semantic analysis
│   │   ├── reference_api.py       # REST API client for Reference Portal
│   │   ├── verification_engine.py # Deterministic & semantic verification logic
│   │   └── report_generator.py    # ReportLab downloadable PDF report generator
│   ├── templates/
│   │   ├── base.html              # Officer portal layout & navigation
│   │   ├── dashboard.html         # Officer metrics & quick demo triggers
│   │   ├── new_audit.html         # Drag-and-drop document upload
│   │   ├── results.html           # Verification results dashboard & tables
│   │   ├── audits_list.html       # Searchable historical audits
│   │   └── reports.html           # PDF reports download repository
│   ├── static/
│   │   ├── css/style.css          # Modern dark/light responsive styles
│   │   └── js/main.js             # Drag-drop, table expansion & progress handlers
│   └── uploads/                   # Vault for uploaded officer documents
│
├── reference_portal/
│   ├── app.py                     # Reference Portal Flask Server (Port 5001)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── portal_routes.py       # Admin CRUD UI for reference companies & certs
│   │   └── api_routes.py          # Reference REST API (/api/reference/...)
│   ├── templates/
│   │   ├── base.html              # Admin portal layout
│   │   ├── companies.html         # Filterable trusted company list
│   │   ├── company_detail.html    # Company profile, products & certificates
│   │   ├── company_form.html      # Add/edit trusted company records
│   │   └── api_docs.html          # Interactive live REST API tester
│   ├── static/
│   │   ├── css/portal.css         # Reference Portal styles
│   │   └── js/portal.js           # Admin helper scripts
│   └── reference_documents/       # Storage for verified certificates & PDFs
│
├── database/
│   ├── __init__.py
│   ├── db.py                      # Separate collections manager (MongoDB/fallback)
│   ├── seed_data.py               # Generates trusted profiles & sample demo bid PDFs
│   └── storage/                   # Persistent local database files
│
├── demo_files/
│   └── sample_bids/               # Pre-generated realistic bid PDFs for testing
│
├── reports/                       # Generated downloadable audit PDF reports
├── .env                           # GEMINI_API_KEY and port configurations
├── requirements.txt               # All Python package requirements
├── run.py                         # Single-command launcher for both services
└── README.md
```

---

## 5. Quick Start Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Verify your `.env` file contains your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=5000
REFERENCE_PORTAL_PORT=5001
```

### Step 3: Start the Complete System
Run the unified launcher:
```bash
python run.py
```

This single command will:
1. Initialize the **Reference Database** and generate sample reference PDFs.
2. Generate sample officer bid submissions for Company 1 and Company 2.
3. Start the **Company Reference Portal & REST API** on `http://127.0.0.1:5001`.
4. Start the **Main AI Audit Application** on `http://127.0.0.1:5000`.

---

## 6. How to Demonstrate (Demo Guide)

### Option A: 1-Click Instant Demo (Fastest)
1. Open `http://127.0.0.1:5000` in your web browser.
2. In the **Instant Presentation Demo Triggers** section:
   - Click **"Demo 1: ABC Tech (Full MATCH)"**:
     - Automatically verifies `ABC Technologies Pvt Ltd`.
     - Demonstrates 100% compliance across GSTIN, CIN, ISO 9001, Product (Industrial Router), and specs.
   - Click **"Demo 2: Apex Global (MISMATCH/EXPIRED)"**:
     - Automatically verifies `Apex Global Solutions Ltd`.
     - Demonstrates detection of **MISMATCH** (differing ISO certificate number) and **EXPIRED** certification.
3. On the **Results Dashboard**, view:
   - Status counters (Matched, Mismatched, Missing, Expired).
   - Gemini executive findings explanation.
   - Expandable field-by-field verification table.
   - Certificate-level comparison table.
   - Click **"Download Official PDF Report"** to inspect the generated PDF dossier.

### Option B: Officer Upload Workflow
1. Go to **"New Audit"** (`http://127.0.0.1:5000/audit/new`).
2. Drag and drop any PDF/DOCX from `demo_files/sample_bids/`:
   - `ABC_Tech_Bid_Submission.pdf`
   - `ABC_Tech_ISO_Certificate.pdf`
3. Click **"START AI VERIFICATION"**.
4. The system extracts structured fields, queries the Reference API, executes the verification checks, and redirects to the completed Results Dashboard.

### Option C: Inspecting the Company Reference Portal
1. Open `http://127.0.0.1:5001` in your browser.
2. View, add, or edit trusted company records.
3. Upload new reference certificates or documents.
4. Visit **"Reference REST API"** (`http://127.0.0.1:5001/api-docs`) to test live endpoints with the built-in API console.

---

## 7. Reference REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/reference/companies` | List all trusted companies (supports `?q=search`) |
| `GET` | `/api/reference/company/{identifier}` | Retrieve company by GSTIN, CIN, ID, or Name |
| `GET` | `/api/reference/company/{id}/certificates` | Get verified certificates for company |
| `GET` | `/api/reference/company/{id}/documents` | Get verified reference documents |
| `GET` | `/api/reference/document/{filename}` | Download official reference certificate PDF |
| `POST` | `/api/reference/company` | Add a new trusted company |
| `PUT` | `/api/reference/company/{id}` | Update company record |

---

## 8. Security & Data Integrity

* **Gemini API Key Security**: The API key is securely loaded from `.env` on the backend only and is never transmitted to the client.
* **Database Separation**: Submitted officer data and trusted company reference data are maintained in strictly isolated collections (`submissions` vs `reference_companies`).
* **Deterministic Decision Logic**: Numerical IDs, GSTIN, CIN, registration numbers, and dates are checked with deterministic Python rules. Gemini is used for unstructured document extraction, semantic specification comparison, and executive summary generation.
* **Disclaimer**: The generated reports clearly indicate that they provide technical decision-support and that final procurement awards require designated officer sign-off.
