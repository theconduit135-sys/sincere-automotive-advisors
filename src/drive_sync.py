"""
Google Drive sync — uploads generated outputs back to the
'1787 NotebookLM Content Engine' Drive folder.
"""

import os
import json
from pathlib import Path
from typing import Optional


DRIVE_FOLDER_ID = "1SBEcHCG1Ep_WNC_Bb1g8zRAdWW3x5Arp"

MIME_TYPES = {
    ".json": "application/json",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


class DriveSync:
    """
    Uploads local output files to the 1787 NotebookLM Content Engine
    folder in Google Drive.

    Requires the google-auth + google-api-python-client packages OR
    can be driven via the MCP Google Drive tools in the Claude Code
    environment (see upload_via_mcp for that path).
    """

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_CREDENTIALS_PATH")
        self.service = None

    def connect(self):
        try:
            from googleapiclient.discovery import build
            from google.oauth2 import service_account

            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/drive.file"],
            )
            self.service = build("drive", "v3", credentials=creds)
            return True
        except Exception as e:
            print(f"  ⚠ Drive API connection failed: {e}")
            print("  → Use upload_file_content() to upload individual files instead.")
            return False

    def upload_file(self, local_path: Path, folder_id: str = DRIVE_FOLDER_ID) -> Optional[str]:
        if not self.service:
            raise RuntimeError("Not connected. Call connect() first.")

        from googleapiclient.http import MediaFileUpload

        suffix = local_path.suffix.lower()
        mime = MIME_TYPES.get(suffix, "application/octet-stream")

        file_metadata = {
            "name": local_path.name,
            "parents": [folder_id],
        }
        media = MediaFileUpload(str(local_path), mimetype=mime)
        result = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id,name")
            .execute()
        )
        print(f"  ✓ Uploaded {local_path.name} → Drive ID: {result['id']}")
        return result["id"]

    def upload_outputs(self, output_dir: str = "outputs") -> list[str]:
        """Upload all generated output files to Drive."""
        if not self.service:
            if not self.connect():
                return []

        uploaded = []
        for path in Path(output_dir).rglob("*"):
            if path.is_file() and path.suffix in MIME_TYPES:
                file_id = self.upload_file(path)
                if file_id:
                    uploaded.append(file_id)
        return uploaded

    def get_file_content_for_mcp(self, local_path: Path) -> dict:
        """
        Return file content in a format ready to pass to the
        MCP Google Drive create_file tool.
        """
        suffix = local_path.suffix.lower()
        mime = MIME_TYPES.get(suffix, "text/plain")

        if suffix in (".json", ".md", ".txt"):
            return {
                "title": local_path.name,
                "textContent": local_path.read_text(),
                "contentMimeType": mime,
                "parentId": DRIVE_FOLDER_ID,
            }
        else:
            import base64
            return {
                "title": local_path.name,
                "base64Content": base64.b64encode(local_path.read_bytes()).decode(),
                "contentMimeType": mime,
                "parentId": DRIVE_FOLDER_ID,
            }
