import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from .config import settings
from .exceptions import AuthError


def get_gmail_service():
    """
    Authenticate via OAuth2 and return a Gmail API service.
    Raises AuthError on failure.
    """
    creds = None
    try:
        if os.path.exists(settings.GMAIL_TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(
                settings.GMAIL_TOKEN_PATH, settings.SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GMAIL_CREDENTIALS_PATH, settings.SCOPES
                )
                creds = flow.run_local_server(
                    host=settings.MCP_SERVER_HOST,
                    port=settings.GMAIL_OAUTH_PORT
                )
            with open(settings.GMAIL_TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        raise AuthError(f"Failed to init Gmail service: {e}")