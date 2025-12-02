"""
File utility helpers (get_file_type, save uploaded file, etc)
"""

from pathlib import Path
from fastapi import UploadFile

video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv']
audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.opus', '.amr']

def get_file_type(filename: str) -> str:
    """Determine if file is video or audio"""
    ext = Path(filename).suffix.lower()
    if ext in video_extensions:
        return 'video'
    elif ext in audio_extensions:
        return 'audio'
    else:
        return 'unknown'

def save_upload_file(upload_file: UploadFile, destination: Path):
    """
    Save a FastAPI UploadFile to destination Path.
    """
    with open(destination, "wb") as buffer:
        # stream copy
        shutil_write = None
        try:
            # use shutil.copyfileobj semantics without importing shutil repeatedly
            from shutil import copyfileobj
            copyfileobj(upload_file.file, buffer)
        finally:
            # ensure file-like is closed by FastAPI on client side
            try:
                upload_file.file.close()
            except Exception:
                pass
