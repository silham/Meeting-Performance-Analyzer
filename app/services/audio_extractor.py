#!/usr/bin/env python3
"""
Audio Extractor Service
Extracts audio from video files using FFmpeg
"""

import os
import subprocess
from pathlib import Path


def extract_audio_from_video(video_path, output_audio_path=None, audio_format="mp3"):
    """
    Extract audio from a video file using FFmpeg.
    
    Args:
        video_path (str): Path to the input video file
        output_audio_path (str, optional): Path for the output audio file.
                                          If None, uses same name as video with audio extension
        audio_format (str): Output audio format (mp3, wav, flac, etc.). Default: mp3
    
    Returns:
        str: Path to the extracted audio file
    
    Raises:
        FileNotFoundError: If video file doesn't exist
        RuntimeError: If FFmpeg is not installed or extraction fails
    """
    
    # Check if video file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Check if FFmpeg is installed
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except FileNotFoundError:
        raise RuntimeError(
            "FFmpeg is not installed. Please install it:\n"
            "  macOS: brew install ffmpeg\n"
            "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
            "  Windows: Download from https://ffmpeg.org/download.html"
        )
    
    # Generate output path if not provided
    if output_audio_path is None:
        video_path_obj = Path(video_path)
        output_audio_path = str(video_path_obj.with_suffix(f'.{audio_format}'))
    
    print(f"Extracting audio from video: {video_path}")
    print(f"Output audio file: {output_audio_path}")
    
    # Extract audio using FFmpeg
    try:
        # FFmpeg command to extract audio
        # -i: input file
        # -vn: no video (audio only)
        # -acodec: audio codec (libmp3lame for mp3, pcm_s16le for wav, flac for flac)
        # -ab: audio bitrate
        # -ar: audio sample rate
        # -ac: audio channels
        
        codec_map = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'flac': 'flac',
            'aac': 'aac',
            'm4a': 'aac',
            'ogg': 'libvorbis'
        }
        
        codec = codec_map.get(audio_format.lower(), 'libmp3lame')
        
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', codec,
            '-ab', '192k',  # Audio bitrate
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            '-y',  # Overwrite output file if it exists
            output_audio_path
        ]
        
        # Run FFmpeg
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        print(f"✓ Audio extracted successfully: {output_audio_path}")
        return output_audio_path
        
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise RuntimeError(f"Failed to extract audio from video:\n{error_message}")


def get_video_info(video_path):
    """
    Get information about a video file using FFprobe.
    
    Args:
        video_path (str): Path to the video file
    
    Returns:
        dict: Video information including duration, codec, resolution, etc.
    """
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    try:
        command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        import json
        info = json.loads(result.stdout.decode('utf-8'))
        return info
        
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise RuntimeError(f"Failed to get video info:\n{error_message}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse video info: {str(e)}")


if __name__ == "__main__":
    # Test the audio extractor
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_extractor.py <video_file>")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    try:
        audio_file = extract_audio_from_video(video_file)
        print(f"\nSuccess! Audio saved to: {audio_file}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
