"""
Job utilities: in-memory jobs DB and helper to update status.
"""

from datetime import datetime
from typing import Optional

# In-memory storage for job status (same as original; swap to Redis/DB in production)
jobs_db = {}

def update_job_status(job_id: str, status: str, progress: str = "", error: Optional[str] = None,
                      transcription: Optional[str] = None, result_file: Optional[str] = None):
    """Update job status in the in-memory jobs_db"""
    if job_id in jobs_db:
        jobs_db[job_id]['status'] = status
        jobs_db[job_id]['progress'] = progress
        if error:
            jobs_db[job_id]['error'] = error
        if transcription:
            jobs_db[job_id]['transcription'] = transcription
        if result_file:
            jobs_db[job_id]['result_file'] = result_file
        if status in ('completed', 'failed'):
            jobs_db[job_id]['completed_at'] = datetime.now().isoformat()
