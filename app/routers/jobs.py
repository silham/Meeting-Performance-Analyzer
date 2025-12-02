from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path

from app.utils.job_utils import jobs_db
from app.models.job_models import JobStatus

router = APIRouter(prefix="/api")

@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a transcription job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(**jobs_db[job_id])


@router.get("/jobs")
async def list_jobs(limit: int = 10):
    """List all transcription jobs"""
    jobs = list(jobs_db.values())
    # Sort by created_at descending
    jobs.sort(key=lambda x: x['created_at'], reverse=True)
    return {"jobs": jobs[:limit], "total": len(jobs)}


@router.get("/jobs/{job_id}/download")
async def download_transcription(job_id: str):
    """Download the transcription result file"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Transcription not completed yet")

    if not job.get('result_file'):
        raise HTTPException(status_code=404, detail="Result file not found")

    result_path = Path(job['result_file'])
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Result file not found on disk")

    return FileResponse(
        path=result_path,
        filename=f"{job['filename']}_transcription.txt",
        media_type="text/plain"
    )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a transcription job and its results"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    # Delete result file if exists
    if job.get('result_file'):
        result_path = Path(job['result_file'])
        if result_path.exists():
            try:
                result_path.unlink()
            except Exception:
                pass

    # Remove from database
    del jobs_db[job_id]

    return {"message": "Job deleted successfully"}
