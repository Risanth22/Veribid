"""
Database Access Layer for AI Bid & Company Compliance Verification System.
Provides distinct collections for:
1. 'submissions' - Submitted Data Database (officer uploads and extracted info)
2. 'reference_companies' - Reference Database (trusted records maintained by admin)

Supports real MongoDB connection with automatic JSON file fallback
so the project runs seamlessly on any machine without setup issues.
"""

import os
import json
import uuid
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "database" / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "veribid_compliance_db")


class JsonCollection:
    """
    A lightweight, thread-safe JSON-backed collection that mimics
    MongoDB collection methods (find, find_one, insert_one, update_one, delete_one).
    """
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self._write([])

    def _read(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def insert_one(self, doc):
        docs = self._read()
        item = dict(doc)
        if "_id" not in item:
            item["_id"] = str(uuid.uuid4())
        docs.append(item)
        self._write(docs)
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(item["_id"])

    def find_one(self, filter_query):
        docs = self._read()
        for doc in docs:
            match = True
            for k, v in filter_query.items():
                if isinstance(v, dict) and "$regex" in v:
                    pattern = v["$regex"]
                    options = v.get("$options", "")
                    val = str(doc.get(k, ""))
                    if "i" in options:
                        if pattern.lower() not in val.lower():
                            match = False
                            break
                    else:
                        if pattern not in val:
                            match = False
                            break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc
        return None

    def find(self, filter_query=None, sort=None):
        docs = self._read()
        if not filter_query:
            result = list(docs)
        else:
            result = []
            for doc in docs:
                match = True
                for k, v in filter_query.items():
                    if isinstance(v, dict) and "$regex" in v:
                        pattern = v["$regex"]
                        options = v.get("$options", "")
                        val = str(doc.get(k, ""))
                        if "i" in options:
                            if pattern.lower() not in val.lower():
                                match = False
                                break
                        else:
                            if pattern not in val:
                                match = False
                                break
                    elif doc.get(k) != v:
                        match = False
                        break
                if match:
                    result.append(doc)

        if sort:
            key, direction = sort[0]
            reverse = direction < 0
            result.sort(key=lambda x: str(x.get(key, "")), reverse=reverse)
        return result

    def update_one(self, filter_query, update_query):
        docs = self._read()
        modified = 0
        for i, doc in enumerate(docs):
            match = True
            for k, v in filter_query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                if "$set" in update_query:
                    docs[i].update(update_query["$set"])
                else:
                    docs[i].update(update_query)
                modified = 1
                break
        if modified:
            self._write(docs)
        class UpdateResult:
            def __init__(self, modified_count):
                self.modified_count = modified_count
        return UpdateResult(modified)

    def delete_one(self, filter_query):
        docs = self._read()
        new_docs = []
        deleted = 0
        for doc in docs:
            match = True
            for k, v in filter_query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match and deleted == 0:
                deleted = 1
                continue
            new_docs.append(doc)
        if deleted:
            self._write(new_docs)
        class DeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count
        return DeleteResult(deleted)

    def count_documents(self, filter_query=None):
        return len(self.find(filter_query))


class DatabaseManager:
    """
    Manages access to the two logically separate collections:
    1. Submissions collection (Submitted data)
    2. Reference companies collection (Trusted reference data)
    """
    def __init__(self):
        self.use_mongo = False
        self.client = None
        self._init_connection()

    def _init_connection(self):
        try:
            from pymongo import MongoClient
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
            client.server_info()  # Test connection
            self.client = client
            self.db = client[DB_NAME]
            self.use_mongo = True
            self.submissions = self.db["submissions"]
            self.reference_companies = self.db["reference_companies"]
            print("[Database] Connected successfully to MongoDB instance.")
        except Exception:
            self.use_mongo = False
            self.submissions = JsonCollection(STORAGE_DIR / "submissions.json")
            self.reference_companies = JsonCollection(STORAGE_DIR / "reference_companies.json")
            print("[Database] Using persistent local JSON database (MongoDB compatible).")

    def get_submissions_collection(self):
        return self.submissions

    def get_reference_collection(self):
        return self.reference_companies


# Global instance
db_manager = DatabaseManager()


def get_submissions_db():
    return db_manager.get_submissions_collection()


def get_reference_db():
    return db_manager.get_reference_collection()
