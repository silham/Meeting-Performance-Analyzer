#!/usr/bin/env python3
"""
Background task to process transcription (moved from original app.py).
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.utils.job_utils import update_job_status, jobs_db
from app.utils.file_utils import get_file_type
from app.config import RESULTS_DIR, GCS_BUCKET_NAME, GOOGLE_PROJECT_ID

# Keep using services from project root 'services' (unchanged)
from app.services.audio_extractor import extract_audio_from_video
from app.services.transcription_service import transcribe_audio


async def process_transcription(
    job_id: str,
    file_path: Path,
    filename: str,
    language_code: str,
    min_speakers: int,
    max_speakers: int,
    keep_audio: bool
):
    """Background task to process transcription (identical logic to original)."""
    try:
        update_job_status(job_id, 'processing', 'Analyzing file...')

        # Get environment variables (also available through app.config)
        bucket_name = GCS_BUCKET_NAME or os.environ.get("GCS_BUCKET_NAME")
        project_id = GOOGLE_PROJECT_ID or os.environ.get("GOOGLE_PROJECT_ID")

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
            # move from result['output_file'] to results folder
            shutil.move(result['output_file'], result_path)
            result['output_file'] = str(result_path)

        # Clean up extracted audio if required
        if extracted_audio and not keep_audio and audio_file_path.exists():
            try:
                audio_file_path.unlink()
            except Exception:
                pass

        # Clean up original uploaded file
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

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
        try:
            if file_path and file_path.exists():
                file_path.unlink()
        except Exception:
            pass
