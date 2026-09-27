"""
Reference API Client.
The Main Audit Application interacts with the Reference System exclusively
via this service making REST calls to the Reference API endpoints.
Main Application -> Reference API -> Reference Database
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

REFERENCE_API_URL = os.getenv("REFERENCE_API_URL", "http://127.0.0.1:5001/api/reference")


class ReferenceApiClient:
    def __init__(self, base_url=None):
        self.base_url = (base_url or REFERENCE_API_URL).rstrip("/")

    def get_company(self, identifier):
        """
        Retrieves trusted company reference data by identifier (GSTIN, CIN, company_id, or name).
        Calls GET /api/reference/company/{identifier}
        """
        if not identifier:
            return {"success": False, "error": "No identifier provided"}

        url = f"{self.base_url}/company/{requests.utils.quote(str(identifier))}"
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                return data
            elif resp.status_code == 404:
                return {"success": False, "error": f"Reference company not found for '{identifier}' — manual review required."}
            else:
                return {"success": False, "error": f"Reference API returned status {resp.status_code}"}
        except requests.exceptions.RequestException as e:
            print(f"[Reference API Client] Network request to {url} failed: {e}. Falling back to internal reference db query.")
            return self._internal_fallback_get_company(identifier)

    def get_certificates(self, company_id):
        """Calls GET /api/reference/company/{company_id}/certificates"""
        url = f"{self.base_url}/company/{requests.utils.quote(str(company_id))}/certificates"
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return resp.json().get("certificates", [])
        except Exception:
            pass
        comp_res = self.get_company(company_id)
        if comp_res.get("success"):
            return comp_res.get("data", {}).get("certificates", [])
        return []

    def get_documents(self, company_id):
        """Calls GET /api/reference/company/{company_id}/documents"""
        url = f"{self.base_url}/company/{requests.utils.quote(str(company_id))}/documents"
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return resp.json().get("documents", [])
        except Exception:
            pass
        comp_res = self.get_company(company_id)
        if comp_res.get("success"):
            return comp_res.get("data", {}).get("documents", [])
        return []

    def get_all_companies(self):
        """Calls GET /api/reference/companies"""
        url = f"{self.base_url}/companies"
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return resp.json().get("data", [])
        except Exception:
            pass
        # Fallback
        try:
            from database.db import get_reference_db
            return get_reference_db().find()
        except Exception:
            return []

    def _internal_fallback_get_company(self, identifier):
        """Direct db fallback if Reference Portal server is not actively started on port 5001."""
        try:
            from database.db import get_reference_db
            db = get_reference_db()
            
            comp = db.find_one({"company_id": identifier})
            if comp:
                return {"success": True, "source": "company_id", "data": comp}
            
            comp = db.find_one({"gstin": str(identifier).upper()})
            if comp:
                return {"success": True, "source": "gstin", "data": comp}

            comp = db.find_one({"cin": str(identifier).upper()})
            if comp:
                return {"success": True, "source": "cin", "data": comp}

            all_companies = db.find()
            clean_id = str(identifier).lower().replace("pvt", "").replace("ltd", "").replace(".", "").strip()
            for c in all_companies:
                c_name = c.get("company_name", "").lower().replace("pvt", "").replace("ltd", "").replace(".", "").strip()
                if c_name == clean_id or clean_id in c_name or c_name in clean_id:
                    return {"success": True, "source": "company_name", "data": c}

            return {"success": False, "error": f"Reference company not found for '{identifier}' — manual review required."}
        except Exception as e:
            return {"success": False, "error": str(e)}


reference_client = ReferenceApiClient()
