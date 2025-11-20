"""
Silence Removal Service
Removes silent parts from an audio file using pydub.
"""

from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def remove_silence(input_audio_path, output_audio_path, silence_thresh=-40, min_silence_len=500):
    """
    Removes silence from the audio file and saves the processed version.

    Args:
        input_audio_path (str): Path to the original audio file
        output_audio_path (str): Path to save trimmed audio
        silence_thresh (int): Threshold in dBFS below which is considered silence
        min_silence_len (int): Minimum silence length (ms) to trim

    Returns:
        str: Path to the processed audio file
    """

    audio = AudioSegment.from_file(input_audio_path)

    # Detect non-silent chunks
    nonsilent_chunks = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=audio.dBFS + silence_thresh
    )

    if not nonsilent_chunks:
        # If no speech found, return original
        audio.export(output_audio_path, format="mp3")
        return output_audio_path

    # Combine speech chunks
    processed_audio = AudioSegment.empty()
    for start, end in nonsilent_chunks:
        processed_audio += audio[start:end]

    processed_audio.export(output_audio_path, format="mp3")
    return output_audio_path
