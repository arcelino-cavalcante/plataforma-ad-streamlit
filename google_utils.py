import os
import json
from typing import List, Dict, Optional

import requests
import streamlit as st

APPS_SCRIPT_URL = os.environ.get("APPS_SCRIPT_URL") or st.secrets.get("APPS_SCRIPT_URL")


def _call_apps_script(action: str, payload: Optional[dict] = None, files=None):
    """Send a request to the configured Apps Script URL."""
    if not APPS_SCRIPT_URL:
        raise RuntimeError("APPS_SCRIPT_URL not configured")
    data = {"action": action}
    if payload:
        data.update(payload)
    resp = requests.post(APPS_SCRIPT_URL, data=data, files=files, timeout=30)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return resp.text


def append_rows(sheet_name: str, rows: List[List]):
    """Append rows to a sheet via Apps Script."""
    payload = {"sheet": sheet_name, "rows": json.dumps(rows)}
    _call_apps_script("append_rows", payload)


def load_rows(sheet_name: str) -> List[Dict]:
    """Load all rows from a sheet via Apps Script."""
    payload = {"sheet": sheet_name}
    result = _call_apps_script("load_rows", payload)
    if isinstance(result, dict) and "data" in result:
        return result["data"]
    if isinstance(result, list):
        return result
    return []


def upload_file(file_bytes: bytes, filename: str, client_name: str) -> str:
    """Upload a file via Apps Script and return the created link."""
    files = {"file": (filename, file_bytes)}
    payload = {"filename": filename, "client": client_name}
    result = _call_apps_script("upload_file", payload, files=files)
    if isinstance(result, dict):
        return result.get("link", "")
    return str(result)
