from app.services.audio_extractor import extract_audio_from_video
from app.services.transcription_service import transcribe_audio
from app.utils.job_utils import update_job_status
from app.config import RESULTS_DIR, GCS_BUCKET_NAME, GOOGLE_PROJECT_ID
from app.utils.file_utils import get_file_type
import shutil
import os
from pathlib import Path

async def process_transcription(
    job_id: str,
    file_path: Path,
    filename: str,
    language_code: str,
    min_speakers: int,
    max_speakers: int,
    keep_audio: bool
):
    """Background task to process transcription."""
    try:
        update_job_status(job_id, 'processing', 'Analyzing file...')
        bucket_name = GCS_BUCKET_NAME or os.environ.get("GCS_BUCKET_NAME")
        project_id = GOOGLE_PROJECT_ID or os.environ.get("GOOGLE_PROJECT_ID")

        if not bucket_name or not project_id:
            raise ValueError("GCS_BUCKET_NAME and GOOGLE_PROJECT_ID must be set")

        audio_file_path = file_path
        extracted_audio = False
        file_type = get_file_type(filename)

        if file_type == 'video':
            update_job_status(job_id, 'processing', 'Extracting audio from video (removing silence)...')
            audio_file_path = Path(extract_audio_from_video(str(file_path), remove_silence=True))
            extracted_audio = True
        elif file_type == 'audio':
            update_job_status(job_id, 'processing', 'Processing audio file...')
        else:
            raise ValueError(f"Unsupported file format: {Path(filename).suffix}")

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

        if 'output_file' in result:
            result_filename = f"{job_id}_transcription.txt"
            result_path = RESULTS_DIR / result_filename
            shutil.move(result['output_file'], result_path)
            result['output_file'] = str(result_path)

        if extracted_audio and not keep_audio and audio_file_path.exists():
            audio_file_path.unlink()

        if file_path.exists():
            file_path.unlink()

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
        if file_path.exists():
            file_path.unlink()
