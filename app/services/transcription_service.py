#!/usr/bin/env python3
"""
Transcription Service
Handles audio transcription with speaker diarization using Google Cloud Speech-to-Text V2 API
"""

import os
import json
import time
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.cloud import storage
from google.auth import default

MAX_AUDIO_LENGTH_SECS = 8 * 60 * 60  # 8 hours


def upload_to_gcs(local_file_path, bucket_name, blob_name):
    """
    Upload a local file to Google Cloud Storage.
    Uses Application Default Credentials (gcloud auth application-default login).
    
    Args:
        local_file_path (str): Path to the local audio file
        bucket_name (str): GCS bucket name
        blob_name (str): Name for the file in GCS
    
    Returns:
        str: GCS URI of the uploaded file
    """
    print(f"Uploading {local_file_path} to gs://{bucket_name}/{blob_name}...")
    
    # Get default credentials
    credentials, project = default()
    
    # Initialize storage client with credentials
    storage_client = storage.Client(credentials=credentials, project=project)
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.upload_from_filename(local_file_path)
    
    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    print(f"File uploaded successfully to {gcs_uri}")
    return gcs_uri


def _perform_transcription(audio_gcs_uri, gcs_output_folder, project_id, 
                          language_code="en-US", 
                          min_speaker_count=2, max_speaker_count=5):
    """
    Internal function to perform transcription with diarization.
    
    Args:
        audio_gcs_uri (str): GCS URI of the audio file
        gcs_output_folder (str): GCS folder for output
        project_id (str): Google Cloud project ID
        language_code (str): Language code (default: "en-US")
        min_speaker_count (int): Minimum number of speakers (default: 2)
        max_speaker_count (int): Maximum number of speakers (default: 5)
    
    Returns:
        dict: Transcription response from API
    """
    
    # Get default credentials
    credentials, _ = default()
    
    # Initialize the Speech client
    client = SpeechClient(
        credentials=credentials,
        client_options=ClientOptions(
            api_endpoint="us-speech.googleapis.com",
        ),
    )
    
    print(f"Processing audio file: {audio_gcs_uri}")
    print("Using Chirp 3 model for improved accuracy...")
    
    # Configure recognition with Chirp 3 model
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config={},
        features=cloud_speech.RecognitionFeatures(
            diarization_config=cloud_speech.SpeakerDiarizationConfig(
                min_speaker_count=min_speaker_count,
                max_speaker_count=max_speaker_count,
            ),
            enable_automatic_punctuation=True,
        ),
        model="chirp_3",
        language_codes=[language_code],
    )
    
    # Configure output to GCS
    output_config = cloud_speech.RecognitionOutputConfig(
        gcs_output_config=cloud_speech.GcsOutputConfig(uri=gcs_output_folder),
    )
    
    files = [cloud_speech.BatchRecognizeFileMetadata(uri=audio_gcs_uri)]
    
    # Create batch recognize request
    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{project_id}/locations/us/recognizers/_",
        config=config,
        files=files,
        recognition_output_config=output_config,
    )
    
    print("Sending batch recognition request to Google Speech-to-Text V2 API...")
    print("This may take a while depending on the audio file size...")
    
    # Perform the transcription
    operation = client.batch_recognize(request=request)
    
    print("Waiting for operation to complete...")
    response = operation.result(timeout=3 * MAX_AUDIO_LENGTH_SECS)
    
    return response


def _download_and_format_transcription(gcs_output_folder, bucket_name):
    """
    Download and format the transcription results from GCS.
    
    Args:
        gcs_output_folder (str): GCS folder containing transcription results
        bucket_name (str): GCS bucket name
    
    Returns:
        str: Formatted transcription text
    """
    print(f"Downloading transcription results from {gcs_output_folder}...")
    
    # Get default credentials
    credentials, project = default()
    
    # Initialize storage client
    storage_client = storage.Client(credentials=credentials, project=project)
    
    bucket = storage_client.bucket(bucket_name)
    
    # List all JSON files in the output folder
    prefix = gcs_output_folder.replace(f"gs://{bucket_name}/", "")
    blobs = bucket.list_blobs(prefix=prefix)
    
    transcription_segments = []
    
    for blob in blobs:
        if blob.name.endswith('.json'):
            print(f"Processing {blob.name}...")
            content = blob.download_as_text()
            result = json.loads(content)
            
            # Extract transcription with speaker labels
            if 'results' in result:
                for res in result['results']:
                    if 'alternatives' in res and len(res['alternatives']) > 0:
                        alternative = res['alternatives'][0]
                        
                        if 'words' in alternative:
                            current_speaker = None
                            current_text = []
                            
                            for word_info in alternative['words']:
                                speaker_label = word_info.get('speakerLabel', word_info.get('speakerTag', 'Unknown'))
                                word = word_info.get('word', '')
                                
                                if speaker_label != current_speaker:
                                    # Save previous segment
                                    if current_speaker is not None:
                                        transcription_segments.append({
                                            'speaker': current_speaker,
                                            'text': ' '.join(current_text)
                                        })
                                    
                                    # Start new segment
                                    current_speaker = speaker_label
                                    current_text = [word]
                                else:
                                    current_text.append(word)
                            
                            # Add the last segment
                            if current_speaker is not None:
                                transcription_segments.append({
                                    'speaker': current_speaker,
                                    'text': ' '.join(current_text)
                                })
    
    # Format output
    if not transcription_segments:
        return "No transcription results found."
    
    output = "=" * 80 + "\n"
    output += "TRANSCRIPTION WITH SPEAKER DIARIZATION (Chirp 3 Model)\n"
    output += "=" * 80 + "\n\n"
    
    for segment in transcription_segments:
        output += f"Speaker {segment['speaker']}:\n"
        output += f"{segment['text']}\n\n"
    
    return output


def transcribe_audio(audio_file_path, bucket_name, project_id, 
                     language_code="en-US", 
                     min_speaker_count=2, max_speaker_count=5,
                     save_to_file=True):
    """
    Main function to transcribe audio with speaker diarization.
    
    Args:
        audio_file_path (str): Path to the local audio file
        bucket_name (str): Google Cloud Storage bucket name
        project_id (str): Google Cloud project ID
        language_code (str): Language code (default: "en-US")
        min_speaker_count (int): Minimum number of speakers (default: 2)
        max_speaker_count (int): Maximum number of speakers (default: 5)
        save_to_file (bool): Whether to save transcription to a file (default: True)
    
    Returns:
        dict: Dictionary containing:
            - transcription (str): Formatted transcription text
            - output_file (str): Path to saved transcription file (if save_to_file=True)
            - gcs_uri (str): GCS URI of uploaded audio
            - gcs_output_folder (str): GCS folder with results
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If required parameters are missing
        Exception: If transcription fails
    """
    
    # Validate inputs
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    if not bucket_name:
        raise ValueError("bucket_name is required")
    
    if not project_id:
        raise ValueError("project_id is required")
    
    # Generate unique blob names
    timestamp = int(time.time())
    audio_filename = os.path.basename(audio_file_path)
    audio_blob_name = f"audio-files/{timestamp}_{audio_filename}"
    output_folder_name = f"transcripts/{timestamp}_{audio_filename.rsplit('.', 1)[0]}"
    
    # Upload audio file to GCS
    audio_gcs_uri = upload_to_gcs(audio_file_path, bucket_name, audio_blob_name)
    gcs_output_folder = f"gs://{bucket_name}/{output_folder_name}"
    
    # Transcribe the audio
    print("\n" + "=" * 80)
    response = _perform_transcription(
        audio_gcs_uri, 
        gcs_output_folder, 
        project_id,
        language_code=language_code,
        min_speaker_count=min_speaker_count,
        max_speaker_count=max_speaker_count
    )
    
    print(f"\nBatch recognition completed!")
    print(f"Results saved to: {gcs_output_folder}")
    
    # Download and format the transcription
    formatted_transcription = _download_and_format_transcription(
        gcs_output_folder, 
        bucket_name
    )
    
    print("\n" + formatted_transcription)
    
    result = {
        'transcription': formatted_transcription,
        'gcs_uri': audio_gcs_uri,
        'gcs_output_folder': gcs_output_folder
    }
    
    # Save to local file if requested
    if save_to_file:
        output_file = audio_file_path.rsplit('.', 1)[0] + '_transcription.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_transcription)
        
        print(f"Transcription saved locally to: {output_file}")
        result['output_file'] = output_file
    
    print("=" * 80 + "\n")
    
    return result


if __name__ == "__main__":
    # Test the transcription service
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python transcription_service.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    bucket = os.environ.get("GCS_BUCKET_NAME")
    project = os.environ.get("GOOGLE_PROJECT_ID")
    
    if not bucket or not project:
        print("Error: GCS_BUCKET_NAME and GOOGLE_PROJECT_ID must be set in .env file")
        sys.exit(1)
    
    try:
        result = transcribe_audio(audio_file, bucket, project)
        print(f"\nSuccess! Transcription saved to: {result.get('output_file')}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
