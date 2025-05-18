from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError, model_validator


class Settings(BaseSettings):
    # OAuth and token file paths
    GMAIL_CREDENTIALS_PATH: str = Field("../credentials.json", env="GMAIL_CREDENTIALS_PATH")
    GMAIL_TOKEN_PATH: str = Field("token.json", env="GMAIL_TOKEN_PATH")
    GMAIL_OAUTH_PORT: int = Field(8080, env="GMAIL_OAUTH_PORT")

    # Server transport and binding
    MCP_TRANSPORT: str = Field("sse", env="MCP_TRANSPORT")
    MCP_SERVER_HOST: str = Field("localhost", env="MCP_SERVER_HOST")
    MCP_SERVER_PORT: int = Field(8000, env="MCP_SERVER_PORT")

    # Gmail API scopes (comma-separated or JSON list in .env)
    SCOPES: list[str] | None = Field(None, env="SCOPES")

    # Attachment options
    ATTACHMENT_SAVE_DIR: str = Field("attachments", env="ATTACHMENT_SAVE_DIR")
    ENABLE_PDF_DECRYPTION: bool = Field(True, env="ENABLE_PDF_DECRYPTION")

    BASE_URL_PROTOCOL: str = Field("http", env="BASE_URL_PROTOCOL")

    class Config:
        # Specifies the .env file for environment variables
        env_file = str(Path(__file__).resolve().parents[1] / ".env")

    @model_validator(mode="before")
    def _parse_scopes(cls, values):
        raw = values.get("SCOPES")
        if raw is None:
            # default single scope
            values["SCOPES"] = ["https://www.googleapis.com/auth/gmail.modify"]
        elif isinstance(raw, str):
            # split comma-separated string
            values["SCOPES"] = [s.strip() for s in raw.split(",") if s.strip()]
        return values


try:
    # Loads and parses .env via BaseSettings mechanism
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Configuration error: {e}")
    # Specifies the .env file for environment variables
    env_file = ".env"