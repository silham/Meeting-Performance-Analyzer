#!/usr/bin/env python3
"""
Audio Extractor Service
Extracts audio from video files using FFmpeg and optionally removes silent parts
"""

import os
import subprocess
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import split_on_silence


def extract_audio_from_video(video_path, output_audio_path=None, audio_format="mp3", remove_silence=False):
    """
    Extract audio from a video file using FFmpeg and optionally remove silent parts.
    
    Args:
        video_path (str): Path to the input video file
        output_audio_path (str, optional): Path for the output audio file.
        audio_format (str): Output audio format (mp3, wav, flac, etc.). Default: mp3
        remove_silence (bool): Whether to remove silent parts. Default: False
    
    Returns:
        str: Path to the extracted audio file
    """
    
    # Check if video file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Check FFmpeg installation
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed. Please install it.")
    
    # Generate output path if not provided
    if output_audio_path is None:
        video_path_obj = Path(video_path)
        output_audio_path = str(video_path_obj.with_suffix(f'.{audio_format}'))
    
    # Extract audio using FFmpeg
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
        '-vn',
        '-acodec', codec,
        '-ab', '192k',
        '-ar', '44100',
        '-ac', '2',
        '-y',
        output_audio_path
    ]
    
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    # Remove silence if requested
    if remove_silence:
        audio = AudioSegment.from_file(output_audio_path)
        chunks = split_on_silence(
            audio,
            min_silence_len=700,
            silence_thresh=audio.dBFS-16,
            keep_silence=100
        )
        if chunks:
            processed_audio = AudioSegment.empty()
            for chunk in chunks:
                processed_audio += chunk
            processed_audio.export(output_audio_path, format=audio_format)
    
    return output_audio_path


def get_video_info(video_path):
    """Unchanged - uses ffprobe"""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    try:
        import json
        command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        info = json.loads(result.stdout.decode('utf-8'))
        return info
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise RuntimeError(f"Failed to get video info:\n{error_message}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse video info: {str(e)}")
