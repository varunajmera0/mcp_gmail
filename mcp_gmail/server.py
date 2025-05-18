from fastmcp import FastMCP
from .auth import get_gmail_service
from .exceptions import ServiceError, AttachmentError
from .config import settings
from email.mime.text import MIMEText
import base64, os, zipfile, io
from PyPDF2 import PdfReader, PdfWriter

mcp = FastMCP(name="mcp_gmail_server")

# Internal safe wrapper for listing messages
def _safe_list(q, max_results):
    try:
        svc = get_gmail_service()
        resp = svc.users().messages().list(
            userId='me', q=q, maxResults=max_results
        ).execute()
        return resp.get('messages', [])
    except Exception as e:
        raise ServiceError(f"List messages failed: {e}")

@mcp.tool("gmail://messages")
def list_messages(q: str = None, max_results: int = 10):
    return _safe_list(q, max_results)

@mcp.tool("gmail://search")
def search_messages(q: str, max_results: int = 10):
    return _safe_list(q, max_results)

@mcp.resource("gmail://messages/{msg_id}")
def get_message(msg_id: str):
    try:
        svc = get_gmail_service()
        return svc.users().messages().get(
            userId='me', id=msg_id, format='full'
        ).execute()
    except Exception as e:
        raise ServiceError(f"Get message failed: {e}")

@mcp.tool("gmail://send")
def send_email(to: str, subject: str, body: str):
    try:
        svc = get_gmail_service()
        mime = MIMEText(body)
        mime['to'] = to
        mime['subject'] = subject
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
        return svc.users().messages().send(
            userId='me', body={'raw': raw}
        ).execute()
    except Exception as e:
        raise ServiceError(f"Send email failed: {e}")

@mcp.tool("gmail://attachments")
def download_attachments(
    msg_id: str,
    save_dir: str = None,
    password: str = None
) -> dict[str, list[str]]:
    save_dir = save_dir or settings.ATTACHMENT_SAVE_DIR
    print("save_dir", save_dir, settings.ATTACHMENT_SAVE_DIR)
    os.makedirs(save_dir, exist_ok=True)
    saved, protected = [], []

    try:
        svc = get_gmail_service()
        msg = svc.users().messages().get(
            userId='me', id=msg_id, format='full'
        ).execute()
        parts = msg.get('payload', {}).get('parts', [])
    except Exception as e:
        raise ServiceError(f"Fetch message failed: {e}")

    for p in parts:
        fn = p.get('filename')
        atid = p.get('body', {}).get('attachmentId')
        if not fn or not atid:
            continue
        try:
            raw = svc.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=atid
            ).execute().get('data')
            data = base64.urlsafe_b64decode(raw.encode())
            path = os.path.join(save_dir, fn)

            if fn.lower().endswith('.zip'):
                zf = zipfile.ZipFile(io.BytesIO(data))
                enc = any(i.flag_bits & 1 for i in zf.infolist())
                if enc:
                    if not password:
                        protected.append(fn)
                        continue
                    zf.extractall(path=save_dir, pwd=password.encode())
                else:
                    zf.extractall(path=save_dir)
                saved.extend([os.path.join(save_dir, i.filename) for i in zf.infolist()])
            elif fn.lower().endswith('.pdf') and settings.ENABLE_PDF_DECRYPTION:
                reader = PdfReader(io.BytesIO(data))
                if reader.is_encrypted:
                    if not password or not reader.decrypt(password):
                        protected.append(fn)
                        continue
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(path, 'wb') as f:
                    writer.write(f)
                saved.append(path)
            else:
                with open(path, 'wb') as f:
                    f.write(data)
                saved.append(path)
        except Exception as e:
            raise AttachmentError(f"{fn} failed: {e}")

    return {"saved": saved, "protected": protected}

if __name__ == "__main__":
    mcp.run(
        transport=settings.MCP_TRANSPORT,
        host=settings.MCP_SERVER_HOST,
        port=settings.MCP_SERVER_PORT
    )