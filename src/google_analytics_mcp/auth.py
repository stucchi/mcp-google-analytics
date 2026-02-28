"""Service Account authentication for Google Analytics APIs."""

from __future__ import annotations

import json

from google.oauth2.service_account import Credentials

from google_analytics_mcp.config import SCOPES, get_config


def get_credentials() -> Credentials:
    """Load service account credentials.

    Priority:
    1. GA_CREDENTIALS env var (raw JSON string — best for MCP config)
    2. GA_CREDENTIALS_PATH env var or default file path
    """
    cfg = get_config()

    if cfg.credentials_json:
        info = json.loads(cfg.credentials_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    if cfg.credentials_path.exists():
        return Credentials.from_service_account_file(
            str(cfg.credentials_path), scopes=SCOPES
        )

    raise NotConfiguredError()


SETUP_GUIDE = """\
Google Analytics MCP is not configured yet. Follow these steps:

1. Go to Google Cloud Console → IAM & Admin → Service Accounts
   https://console.cloud.google.com/iam-admin/serviceaccounts
   - Create a new project (or select an existing one)
   - Click "+ Create Service Account", give it any name, click "Done"

2. Create a JSON key:
   - Click the service account you just created
   - Go to "Keys" tab → "Add Key" → "Create new key" → JSON → Download

3. Enable the APIs in your GCP project:
   - Google Analytics Admin API: https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com
   - Google Analytics Data API: https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com

4. Grant access in GA4:
   - Go to GA4 → Admin → Property Access Management
   - Click "+" → add the service account email (it looks like name@project.iam.gserviceaccount.com)
   - Give it "Editor" role

5. Configure this MCP server:
   - Open the JSON file you downloaded in step 2
   - Copy the entire content
   - Set it as the GA_CREDENTIALS environment variable in your MCP client config

   Example for Claude Desktop (claude_desktop_config.json):
   {
     "mcpServers": {
       "google-analytics": {
         "command": "uvx",
         "args": ["google-analytics-4-mcp"],
         "env": {
           "GA_CREDENTIALS": "<paste the entire JSON here>"
         }
       }
     }
   }

   Example for Claude Code:
   claude mcp add google-analytics -e GA_CREDENTIALS='<paste JSON>' -- uvx google-analytics-4-mcp

That's it! Restart your MCP client and try again.\
"""


class NotConfiguredError(Exception):
    def __init__(self) -> None:
        super().__init__(SETUP_GUIDE)


def check_credentials() -> dict:
    """Check auth status. Returns a dict with status info."""
    try:
        creds = get_credentials()
        return {
            "authenticated": True,
            "service_account_email": creds.service_account_email,
            "project_id": creds.project_id,
            "scopes": list(creds.scopes or []),
        }
    except Exception as e:
        return {"authenticated": False, "reason": str(e)}
