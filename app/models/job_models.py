from typing import Optional
from pydantic import BaseModel

class TranscriptionRequest(BaseModel):
    language_code: str = "en-US"
    min_speakers: int = 2
    max_speakers: int = 5
    keep_audio: bool = False


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: str
    filename: str
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    result_file: Optional[str] = None
    transcription: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    message: str
    status: str
