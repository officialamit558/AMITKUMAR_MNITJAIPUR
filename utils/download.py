import requests
import os
import tempfile
from urllib.parse import urlparse

def get_temp_dir():
    return tempfile.gettempdir()     # Works on Windows, Linux, Mac

def download_file(url: str) -> str:
    temp_dir = get_temp_dir()

    # Extract filename from URL or fallback
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = "document"

    # Build full path
    file_path = os.path.join(temp_dir, filename)

    try:
        response = requests.get(url, stream=True, timeout=25)
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"Download failed: {e}")

    # Save file
    try:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        raise Exception(f"Saving file failed: {e}")

    # Verify file exists and size > 0
    if not os.path.exists(file_path):
        raise Exception("Download succeeded but file was not saved.")

    if os.path.getsize(file_path) == 0:
        raise Exception("Downloaded file is empty.")

    return file_path
