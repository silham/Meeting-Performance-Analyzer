#!/usr/bin/env python3
"""
FastAPI Web Application for Audio/Video Transcription
Provides REST API endpoints and serves a web interface
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from services.audio_extractor import extract_audio_from_video
from services.transcription_service import transcribe_audio

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Meeting Performance Analyzer",
    description="Transcribe audio from video/audio files with speaker diarization",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# In-memory storage for job status (use Redis/database in production)
jobs_db = {}

# Pydantic models
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


# Helper functions
def get_file_type(filename: str) -> str:
    """Determine if file is video or audio"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv']
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.opus', '.amr']
    
    ext = Path(filename).suffix.lower()
    if ext in video_extensions:
        return 'video'
    elif ext in audio_extensions:
        return 'audio'
    else:
        return 'unknown'


def update_job_status(job_id: str, status: str, progress: str = "", error: str = None, 
                     transcription: str = None, result_file: str = None):
    """Update job status in the database"""
    if job_id in jobs_db:
        jobs_db[job_id]['status'] = status
        jobs_db[job_id]['progress'] = progress
        if error:
            jobs_db[job_id]['error'] = error
        if transcription:
            jobs_db[job_id]['transcription'] = transcription
        if result_file:
            jobs_db[job_id]['result_file'] = result_file
        if status == 'completed' or status == 'failed':
            jobs_db[job_id]['completed_at'] = datetime.now().isoformat()


async def process_transcription(
    job_id: str,
    file_path: Path,
    filename: str,
    language_code: str,
    min_speakers: int,
    max_speakers: int,
    keep_audio: bool
):
    """Background task to process transcription"""
    try:
        update_job_status(job_id, 'processing', 'Analyzing file...')
        
        # Get environment variables
        bucket_name = os.environ.get("GCS_BUCKET_NAME")
        project_id = os.environ.get("GOOGLE_PROJECT_ID")
        
        if not bucket_name or not project_id:
            raise ValueError("GCS_BUCKET_NAME and GOOGLE_PROJECT_ID must be set")
        
        audio_file_path = file_path
        extracted_audio = False
        
        # Check file type and extract audio if needed
        file_type = get_file_type(filename)
        
        if file_type == 'video':
            update_job_status(job_id, 'processing', 'Extracting audio from video...')
            audio_file_path = Path(extract_audio_from_video(str(file_path)))
            extracted_audio = True
        elif file_type == 'audio':
            update_job_status(job_id, 'processing', 'Processing audio file...')
        else:
            raise ValueError(f"Unsupported file format: {Path(filename).suffix}")
        
        # Transcribe audio
        update_job_status(job_id, 'processing', 'Transcribing with speaker diarization...')
        
        result = transcribe_audio(
            str(audio_file_path),
            bucket_name,
            project_id,
            language_code=language_code,
            min_speaker_count=min_speakers,
            max_speaker_count=max_speakers,
            save_to_file=True
        )
        
        # Move result file to results directory
        if 'output_file' in result:
            result_filename = f"{job_id}_transcription.txt"
            result_path = RESULTS_DIR / result_filename
            shutil.move(result['output_file'], result_path)
            result['output_file'] = str(result_path)
        
        # Clean up
        if extracted_audio and not keep_audio and audio_file_path.exists():
            audio_file_path.unlink()
        
        # Clean up original uploaded file
        if file_path.exists():
            file_path.unlink()
        
        # Update job status
        update_job_status(
            job_id,
            'completed',
            'Transcription completed successfully',
            transcription=result.get('transcription'),
            result_file=result.get('output_file')
        )
        
    except Exception as e:
        error_msg = str(e)
        update_job_status(job_id, 'failed', f'Error: {error_msg}', error=error_msg)
        
        # Clean up on error
        if file_path.exists():
            file_path.unlink()


# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    html_file = Path("static/index.html")
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse(content="<h1>Meeting Performance Analyzer API</h1><p>Upload interface coming soon...</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Meeting Performance Analyzer",
        "version": "1.0.0"
    }


@app.post("/api/transcribe", response_model=JobResponse)
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
    
    - **file**: Video or audio file to transcribe
    - **language_code**: Language code (default: en-US)
    - **min_speakers**: Minimum number of speakers (default: 2)
    - **max_speakers**: Maximum number of speakers (default: 5)
    - **keep_audio**: Keep extracted audio file from video (default: False)
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
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
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


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a transcription job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**jobs_db[job_id])


@app.get("/api/jobs")
async def list_jobs(limit: int = 10):
    """List all transcription jobs"""
    jobs = list(jobs_db.values())
    # Sort by created_at descending
    jobs.sort(key=lambda x: x['created_at'], reverse=True)
    return {"jobs": jobs[:limit], "total": len(jobs)}


@app.get("/api/jobs/{job_id}/download")
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


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a transcription job and its results"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    # Delete result file if exists
    if job.get('result_file'):
        result_path = Path(job['result_file'])
        if result_path.exists():
            result_path.unlink()
    
    # Remove from database
    del jobs_db[job_id]
    
    return {"message": "Job deleted successfully"}


# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
