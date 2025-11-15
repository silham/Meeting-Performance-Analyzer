#!/usr/bin/env python3
"""
Video/Audio Transcription Tool
Main entry point for transcribing audio from video files or audio files directly
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Import our services
from services.audio_extractor import extract_audio_from_video
from services.transcription_service import transcribe_audio

# Load environment variables
load_dotenv()


def is_video_file(file_path):
    """
    Check if the file is a video based on its extension.
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        bool: True if video file, False otherwise
    """
    video_extensions = [
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', 
        '.webm', '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv'
    ]
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in video_extensions


def is_audio_file(file_path):
    """
    Check if the file is an audio file based on its extension.
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        bool: True if audio file, False otherwise
    """
    audio_extensions = [
        '.mp3', '.wav', '.flac', '.m4a', '.aac', 
        '.ogg', '.wma', '.opus', '.amr'
    ]
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in audio_extensions


def process_file(file_path, bucket_name, project_id, 
                language_code="en-US", 
                min_speakers=2, max_speakers=5,
                keep_audio=False):
    """
    Process a video or audio file and generate transcription.
    
    Args:
        file_path (str): Path to video or audio file
        bucket_name (str): GCS bucket name
        project_id (str): Google Cloud project ID
        language_code (str): Language code for transcription
        min_speakers (int): Minimum number of speakers
        max_speakers (int): Maximum number of speakers
        keep_audio (bool): Keep extracted audio file (for videos)
    
    Returns:
        dict: Transcription results
    """
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    audio_file_path = file_path
    extracted_audio = False
    
    # If video file, extract audio first
    if is_video_file(file_path):
        print(f"📹 Detected video file: {file_path}")
        print("🎵 Extracting audio from video...\n")
        
        try:
            audio_file_path = extract_audio_from_video(file_path)
            extracted_audio = True
            print()
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio from video: {str(e)}")
    
    elif is_audio_file(file_path):
        print(f"🎵 Detected audio file: {file_path}\n")
    
    else:
        raise ValueError(
            f"Unsupported file format: {Path(file_path).suffix}\n"
            "Supported formats:\n"
            "  Video: .mp4, .avi, .mov, .mkv, .flv, .wmv, .webm, etc.\n"
            "  Audio: .mp3, .wav, .flac, .m4a, .aac, .ogg, etc."
        )
    
    # Transcribe the audio
    print("🎤 Starting transcription with speaker diarization...\n")
    
    try:
        result = transcribe_audio(
            audio_file_path,
            bucket_name,
            project_id,
            language_code=language_code,
            min_speaker_count=min_speakers,
            max_speaker_count=max_speakers,
            save_to_file=True
        )
        
        # Clean up extracted audio if requested
        if extracted_audio and not keep_audio:
            try:
                os.remove(audio_file_path)
                print(f"🧹 Cleaned up temporary audio file: {audio_file_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete temporary audio file: {str(e)}")
        
        return result
        
    except Exception as e:
        # Clean up extracted audio on error
        if extracted_audio and os.path.exists(audio_file_path):
            try:
                os.remove(audio_file_path)
            except:
                pass
        raise e


def main():
    """Main entry point for the application."""
    
    parser = argparse.ArgumentParser(
        description='Transcribe audio from video or audio files with speaker diarization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe a video file
  python main.py video.mp4
  
  # Transcribe an audio file
  python main.py audio.mp3
  
  # Specify language and speaker count
  python main.py video.mp4 --language es-ES --min-speakers 3 --max-speakers 6
  
  # Keep extracted audio file from video
  python main.py video.mp4 --keep-audio

Environment Variables (set in .env file):
  GCS_BUCKET_NAME      Google Cloud Storage bucket name
  GOOGLE_PROJECT_ID    Google Cloud project ID
        """
    )
    
    parser.add_argument(
        'file',
        help='Path to video or audio file to transcribe'
    )
    
    parser.add_argument(
        '--language', '-l',
        default='en-US',
        help='Language code (default: en-US). Examples: es-ES, fr-FR, de-DE'
    )
    
    parser.add_argument(
        '--min-speakers',
        type=int,
        default=2,
        help='Minimum number of speakers (default: 2)'
    )
    
    parser.add_argument(
        '--max-speakers',
        type=int,
        default=5,
        help='Maximum number of speakers (default: 5)'
    )
    
    parser.add_argument(
        '--keep-audio',
        action='store_true',
        help='Keep extracted audio file (for video files only)'
    )
    
    parser.add_argument(
        '--bucket',
        help='GCS bucket name (overrides .env file)'
    )
    
    parser.add_argument(
        '--project',
        help='Google Cloud project ID (overrides .env file)'
    )
    
    args = parser.parse_args()
    
    # Get configuration
    bucket_name = args.bucket or os.environ.get("GCS_BUCKET_NAME")
    project_id = args.project or os.environ.get("GOOGLE_PROJECT_ID")
    
    # Validate configuration
    if not bucket_name:
        print("❌ Error: GCS_BUCKET_NAME not found")
        print("\nPlease set it in your .env file or use --bucket option:")
        print("  GCS_BUCKET_NAME=your-bucket-name")
        sys.exit(1)
    
    if not project_id:
        print("❌ Error: GOOGLE_PROJECT_ID not found")
        print("\nPlease set it in your .env file or use --project option:")
        print("  GOOGLE_PROJECT_ID=your-project-id")
        sys.exit(1)
    
    # Check authentication
    try:
        from google.auth import default
        credentials, _ = default()
        print("✓ Authentication found\n")
    except Exception as e:
        print("❌ Error: Google Cloud authentication not found")
        print("\nPlease authenticate with:")
        print("  gcloud auth application-default login")
        print("  gcloud auth application-default set-quota-project YOUR_PROJECT_ID")
        print("\nSee README.md for detailed setup instructions.")
        sys.exit(1)
    
    # Process the file
    try:
        print("=" * 80)
        print(f"🎬 Processing: {args.file}")
        print("=" * 80 + "\n")
        
        result = process_file(
            args.file,
            bucket_name,
            project_id,
            language_code=args.language,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers,
            keep_audio=args.keep_audio
        )
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        if result.get('output_file'):
            print(f"📄 Transcription saved to: {result['output_file']}")
        print(f"☁️  GCS URI: {result['gcs_uri']}")
        print(f"📁 GCS Output: {result['gcs_output_folder']}")
        print("=" * 80 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nCommon issues:")
        print("1. Make sure FFmpeg is installed (for video files)")
        print("   macOS: brew install ffmpeg")
        print("2. Ensure Speech-to-Text V2 API is enabled")
        print("3. Check that you have the necessary IAM permissions")
        print("4. Verify your .env file has correct values")
        print("\nSee README.md for detailed troubleshooting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
