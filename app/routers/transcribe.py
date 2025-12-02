from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
from datetime import datetime

from app.models.job_models import JobResponse
from app.utils.file_utils import get_file_type, save_upload_file
from app.utils.job_utils import jobs_db
from app.background.processor import process_transcription
from app.config import UPLOAD_DIR

router = APIRouter()

@router.post("/api/transcribe", response_model=JobResponse)
async def create_transcription_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language_code: str = Form("en-US"),
    min_speakers: int = Form(2),
    max_speakers: int = Form(5),
    keep_audio: bool = Form(False)
):
    """
    Upload a video or audio file for transcription
    """
    # Validate file type
    file_type = get_file_type(file.filename)
    if file_type == 'unknown':
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {Path(file.filename).suffix}"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file
    file_extension = Path(file.filename).suffix
    upload_path = UPLOAD_DIR / f"{job_id}{file_extension}"

    try:
        # Save file contents
        with open(upload_path, "wb") as buffer:
            from shutil import copyfileobj
            copyfileobj(file.file, buffer)
        try:
            file.file.close()
        except Exception:
            pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create job record
    jobs_db[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'progress': 'File uploaded, queued for processing',
        'filename': file.filename,
        'file_type': file_type,
        'created_at': datetime.now().isoformat(),
        'completed_at': None,
        'error': None,
        'result_file': None,
        'transcription': None
    }

    # Add background task
    background_tasks.add_task(
        process_transcription,
        job_id,
        upload_path,
        file.filename,
        language_code,
        min_speakers,
        max_speakers,
        keep_audio
    )

    return JobResponse(
        job_id=job_id,
        message="Transcription job created successfully",
        status="queued"
    )
