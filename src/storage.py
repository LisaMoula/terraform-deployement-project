"""Storage helper: writes to Azure Data Lake (ADLS Gen2) when a connection
string is set (STORAGE_CONNECTION_STRING), otherwise uses the local filesystem."""

from __future__ import annotations

import os

CONNECTION_STRING = os.getenv("STORAGE_CONNECTION_STRING", "")
LANDING_CONTAINER = "landing"
GOLD_CONTAINER = "gold"


def adls_enabled() -> bool:
    return bool(CONNECTION_STRING)


def _service():
    from azure.storage.blob import BlobServiceClient

    return BlobServiceClient.from_connection_string(CONNECTION_STRING)


def upload_text(container: str, blob_name: str, text: str) -> str:
    client = _service().get_blob_client(container=container, blob=blob_name)
    client.upload_blob(text.encode("utf-8"), overwrite=True)
    return f"adls://{container}/{blob_name}"


def download_text(container: str, blob_name: str) -> str:
    client = _service().get_blob_client(container=container, blob=blob_name)
    return client.download_blob().readall().decode("utf-8")
