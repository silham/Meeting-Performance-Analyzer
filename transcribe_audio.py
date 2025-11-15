#!/usr/bin/env python3
"""
Audio Transcription Script with Speaker Diarization
Uses Google Cloud Speech-to-Text V2 API with Chirp 3 model for improved accuracy
"""

import os
import sys
import json
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.cloud import storage
from google.auth import default
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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


def transcribe_audio_with_diarization(audio_gcs_uri, gcs_output_folder, project_id, 
                                      language_code="en-US", 
                                      min_speaker_count=2, max_speaker_count=5):
    """
    Transcribe audio file with speaker diarization using Google Speech-to-Text V2 API.
    Uses Chirp 3 model for improved accuracy.
    
    Args:
        audio_gcs_uri (str): GCS URI of the audio file (e.g., gs://bucket/audio.mp3)
        gcs_output_folder (str): GCS folder for output (e.g., gs://bucket/transcripts)
        project_id (str): Google Cloud project ID
        language_code (str): Language code (default: "en-US")
        min_speaker_count (int): Minimum number of speakers (default: 2)
        max_speaker_count (int): Maximum number of speakers (default: 5)
    
    Returns:
        dict: Transcription results with speaker information
    """
    
    # Get default credentials (from gcloud auth application-default login)
    credentials, _ = default()
    
    # Initialize the Speech client with credentials and US endpoint
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
    
    # Perform the transcription (long-running operation)
    operation = client.batch_recognize(request=request)
    
    print("Waiting for operation to complete...")
    response = operation.result(timeout=3 * MAX_AUDIO_LENGTH_SECS)
    
    return response


def download_and_format_transcription(gcs_output_folder, bucket_name):
    """
    Download and format the transcription results from GCS.
    Uses Application Default Credentials (gcloud auth application-default login).
    
    Args:
        gcs_output_folder (str): GCS folder containing transcription results
        bucket_name (str): GCS bucket name
    
    Returns:
        str: Formatted transcription text
    """
    print(f"Downloading transcription results from {gcs_output_folder}...")
    
    # Get default credentials
    credentials, project = default()
    
    # Initialize storage client with credentials
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


def main():
    """Main function to run the transcription script."""
    
    # Check if audio file path is provided
    if len(sys.argv) < 2:
        print("Usage: python transcribe_audio.py <path_to_audio_file.mp3>")
        print("\nRequired environment variables:")
        print("  GCS_BUCKET_NAME - Your Google Cloud Storage bucket name")
        print("  GOOGLE_PROJECT_ID - Your Google Cloud project ID")
        print("\nRequired authentication:")
        print("  Run 'gcloud auth application-default login' to authenticate")
        sys.exit(1)
    
    audio_file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: File not found: {audio_file_path}")
        sys.exit(1)
    
    # Check authentication for Cloud Storage and Speech API
    try:
        credentials, _ = default()
        print("✓ Authentication found")
    except Exception as e:
        print("\nError: Google Cloud authentication not found.")
        print("\nYou need to authenticate with Google Cloud to use Cloud Storage and Speech-to-Text API.")
        print("Please run the following command first:")
        print("\n  gcloud auth application-default login")
        print("\nThis will open a browser for you to sign in with your Google account.")
        print("After authentication, run this script again.")
        print("\nIf you don't have gcloud CLI installed:")
        print("  Visit: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)
    
    # Get GCS bucket name
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    if not bucket_name:
        print("Error: GCS_BUCKET_NAME not found in environment variables.")
        print("Please add it to your .env file: GCS_BUCKET_NAME=your-bucket-name")
        sys.exit(1)
    
    # Get project ID
    project_id = os.environ.get("GOOGLE_PROJECT_ID")
    if not project_id:
        print("Error: GOOGLE_PROJECT_ID not found in environment variables.")
        print("Please add it to your .env file: GOOGLE_PROJECT_ID=your-project-id")
        sys.exit(1)
    
    try:
        # Generate unique blob names
        import time
        timestamp = int(time.time())
        audio_filename = os.path.basename(audio_file_path)
        audio_blob_name = f"audio-files/{timestamp}_{audio_filename}"
        output_folder_name = f"transcripts/{timestamp}_{audio_filename.rsplit('.', 1)[0]}"
        
        # Upload audio file to GCS
        audio_gcs_uri = upload_to_gcs(audio_file_path, bucket_name, audio_blob_name)
        gcs_output_folder = f"gs://{bucket_name}/{output_folder_name}"
        
        # Transcribe the audio
        print("\n" + "=" * 80)
        response = transcribe_audio_with_diarization(
            audio_gcs_uri, 
            gcs_output_folder, 
            project_id
        )
        
        print(f"\nBatch recognition completed!")
        print(f"Results saved to: {gcs_output_folder}")
        
        # Download and format the transcription
        formatted_transcription = download_and_format_transcription(
            gcs_output_folder, 
            bucket_name
        )
        
        print("\n" + formatted_transcription)
        
        # Save to local file
        output_file = audio_file_path.rsplit('.', 1)[0] + '_transcription.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_transcription)
        
        print(f"Transcription saved locally to: {output_file}")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nError during transcription: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nCommon issues:")
        print("1. Make sure you have enabled the Speech-to-Text V2 API in your Google Cloud project")
        print("   Visit: https://console.cloud.google.com/apis/library/speech.googleapis.com")
        print("\n2. Ensure your authenticated user has the necessary IAM roles:")
        print("   - roles/speech.admin (or roles/speech.editor)")
        print("   - roles/storage.objectAdmin (or roles/storage.objectCreator)")
        print("\n3. Grant permissions using:")
        print(f"   gcloud projects add-iam-policy-binding {project_id} \\")
        print(f"       --member='user:YOUR_EMAIL@gmail.com' \\")
        print("       --role='roles/speech.admin'")
        print("\n4. Make sure the GCS bucket exists and you have write permissions")
        print("5. Ensure the audio file is in a supported format (MP3, FLAC, WAV, etc.)")
        print("\n6. If issues persist, try re-authenticating:")
        print("   gcloud auth application-default login")
        sys.exit(1)


if __name__ == "__main__":
    main()
