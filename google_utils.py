import os
import io
import tempfile
import json
import streamlit as st
from typing import List, Dict

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_NAME = os.environ.get("GOOGLE_SHEETS_FILE", "PlataformaAD_Dados")
FOLDER_ROOT_NAME = os.environ.get("GOOGLE_DRIVE_ROOT", "PlataformaAD_Documentos")

_creds = None
_gc = None
_drive_service = None


def get_credentials():
    global _creds
    if _creds is None:
        json_data = st.secrets.get("GOOGLE_CREDS_JSON")
        if json_data:
            if isinstance(json_data, str):
                json_text = json_data
            else:
                json_text = json.dumps(json_data)
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
                tmp.write(json_text)
                tmp_path = tmp.name
            _creds = Credentials.from_service_account_file(tmp_path, scopes=SCOPES)
        else:
            creds_path = os.environ.get("GOOGLE_CREDS")
            if not creds_path:
                raise RuntimeError("Missing GOOGLE_CREDS or GOOGLE_CREDS_JSON")
            _creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return _creds


def get_gspread_client():
    global _gc
    if _gc is None:
        _gc = gspread.authorize(get_credentials())
    return _gc


def get_drive_service():
    global _drive_service
    if _drive_service is None:
        _drive_service = build("drive", "v3", credentials=get_credentials())
    return _drive_service


def get_spreadsheet():
    gc = get_gspread_client()
    try:
        return gc.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        return gc.create(SPREADSHEET_NAME)


def get_worksheet(sheet_name: str):
    sh = get_spreadsheet()
    try:
        return sh.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return sh.add_worksheet(title=sheet_name, rows="100", cols="20")


def append_rows(sheet_name: str, rows: List[List]):
    ws = get_worksheet(sheet_name)
    ws.append_rows(rows, value_input_option="USER_ENTERED")


def load_rows(sheet_name: str) -> List[Dict]:
    ws = get_worksheet(sheet_name)
    records = ws.get_all_records()
    return records


def get_or_create_folder(name: str, parent_id: str = None) -> str:
    drive = get_drive_service()
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    res = drive.files().list(q=query, fields="files(id, name)").execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = drive.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_file(file_bytes: bytes, filename: str, client_name: str) -> str:
    drive = get_drive_service()
    root_id = get_or_create_folder(FOLDER_ROOT_NAME)
    client_id = get_or_create_folder(client_name, parent_id=root_id)
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype="application/octet-stream")
    file_metadata = {"name": filename, "parents": [client_id]}
    f = drive.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    return f.get("webViewLink")
