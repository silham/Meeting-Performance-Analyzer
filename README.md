# Audio Transcription with Speaker Diarization

This Python script transcribes MP3 audio files using Google Cloud Speech-to-Text V2 API with the **Chirp 3 model** for improved accuracy and speaker diarization (speaker identification).

## Features

- Transcribes MP3 audio files with **Chirp 3 model** for superior accuracy
- Identifies different speakers in the audio
- Segments transcription by speaker
- Batch recognition for long audio files (up to 8 hours)
- Saves transcription to a text file
- Supports automatic punctuation
- Uses Google Cloud Storage for processing large files
- Uses Application Default Credentials (ADC) for secure authentication

## Quick Start

For users who already have Google Cloud set up:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Authenticate with Google Cloud
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# 3. Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/speech.admin'

# 4. Create .env file
echo "GCS_BUCKET_NAME=your-bucket-name" > .env
echo "GOOGLE_PROJECT_ID=your-project-id" >> .env

# 5. Run the script
python transcribe_audio.py your-audio.mp3
```

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud SDK**: Install the `gcloud` CLI tool for authentication
3. **Speech-to-Text V2 API**: Enable the Cloud Speech-to-Text V2 API in your project
4. **Cloud Storage**: Create a Google Cloud Storage bucket for audio files and transcripts
5. **Python 3.7+**: Make sure you have Python 3.7 or higher installed
6. **IAM Permissions**: Your Google account needs `roles/speech.admin` and `roles/storage.objectAdmin`

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install google-cloud-speech google-cloud-storage google-api-core python-dotenv
```

### 2. Install Google Cloud SDK

If you don't have the `gcloud` CLI installed:

1. Visit: https://cloud.google.com/sdk/docs/install
2. Follow the installation instructions for your operating system
3. After installation, initialize gcloud:
   ```bash
   gcloud init
   ```

### 3. Create a Google Cloud Storage Bucket

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "Cloud Storage" > "Buckets"
3. Click "Create Bucket"
4. Choose a unique name for your bucket (e.g., `my-transcription-bucket`)
5. Select a location (recommend: US)
6. Choose "Standard" storage class
7. Click "Create"

### 4. Authenticate with Google Cloud

You need to authenticate with Google Cloud using Application Default Credentials:

```bash
gcloud auth application-default login
```

This will open a browser window for you to sign in with your Google account. The credentials will be stored locally at `~/.config/gcloud/application_default_credentials.json`.

After authentication, set the quota project:

```bash
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

### 5. Grant IAM Permissions

Your authenticated user needs the following IAM roles:

```bash
# Get your authenticated email
gcloud auth list --filter=status:ACTIVE --format="value(account)"

# Grant Speech-to-Text permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/speech.admin'

# Grant Cloud Storage permissions (if not already an Owner)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/storage.objectAdmin'
```

Replace:
- `YOUR_PROJECT_ID` with your Google Cloud project ID
- `YOUR_EMAIL@gmail.com` with your authenticated Google account email

### 6. Configure Environment Variables

Create a `.env` file in the project directory:

```bash
touch .env
```

Then edit the `.env` file and add your details:

```
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_PROJECT_ID=your-project-id
```

**Where to find:**
- **Bucket Name**: Created in step 3 (just the name, without `gs://`)
- **Project ID**: Find it in the Google Cloud Console header or by running `gcloud config get-value project`

**Note**: You no longer need a `GOOGLE_API_KEY` as the script uses Application Default Credentials.

### 7. Enable Required APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. Search and enable these APIs:
   - **Cloud Speech-to-Text API** (V2)
   - **Cloud Storage API**
5. Click "Enable" for each

## Usage

### Basic Usage

Once you have completed the setup steps:

```bash
python transcribe_audio.py path/to/your/audio.mp3
```

The script will:
1. Authenticate using your Application Default Credentials
2. Upload the audio file to Google Cloud Storage
3. Send it to the Speech-to-Text V2 API for transcription with speaker diarization
4. Download and format the results
5. Save the transcription locally

### Alternative: Using Environment Variables

If you prefer not to use a `.env` file, set the environment variables directly:

```bash
export GCS_BUCKET_NAME='your-bucket-name'
export GOOGLE_PROJECT_ID='your-project-id'
python transcribe_audio.py path/to/your/audio.mp3
```

Or in one line:
```bash
GCS_BUCKET_NAME='your-bucket-name' GOOGLE_PROJECT_ID='your-project-id' python transcribe_audio.py audio.mp3
```

## Output

The script will:
1. Display the transcription in the console, segmented by speaker
2. Save the transcription to a text file named `<audio_filename>_transcription.txt`

Example output:
```
================================================================================
TRANSCRIPTION WITH SPEAKER DIARIZATION
================================================================================

Speaker 1:
Hello, how are you today?

Speaker 2:
I'm doing great, thanks for asking. How about you?

Speaker 1:
I'm doing well too. Let's discuss the project details.
```

## How It Works

1. **Authenticate**: Uses Application Default Credentials (ADC) from `gcloud auth application-default login`
2. **Upload**: The script uploads your local audio file to Google Cloud Storage
3. **Process**: Uses Speech-to-Text V2 API with Chirp 3 model for batch recognition
4. **Diarize**: Identifies and labels different speakers in the audio
5. **Download**: Retrieves the transcription results from Cloud Storage
6. **Format**: Organizes the transcript by speaker segments
7. **Save**: Saves the formatted transcription to a local text file

## Authentication Method

This script uses **Application Default Credentials (ADC)** for authentication, which is more secure and flexible than API keys:

- **OAuth 2.0**: Uses OAuth 2.0 credentials instead of static API keys
- **IAM-based**: Permissions are controlled through Google Cloud IAM roles
- **Automatic refresh**: Credentials are automatically refreshed when needed
- **Local storage**: Credentials stored securely at `~/.config/gcloud/application_default_credentials.json`
- **No hardcoded secrets**: No API keys need to be stored in your code or `.env` file

The Speech-to-Text V2 API's `batch_recognize` method requires OAuth 2.0 credentials and cannot use API keys alone.

## Configuration

You can modify the following parameters in the script:

- `language_code`: Default is "en-US". Change for other languages (e.g., "es-ES", "fr-FR")
- `min_speaker_count`: Minimum number of speakers (default: 2)
- `max_speaker_count`: Maximum number of speakers (default: 5)
- `model`: Using "chirp_3" for best accuracy (Google's latest model)

## Supported Audio Formats

The script uses `auto_decoding_config` which automatically detects and supports:
- MP3
- FLAC
- WAV
- OGG
- AMR
- And many other audio formats

## Limitations

- Audio file length: Up to **8 hours** with batch recognition
- Audio file size: Virtually unlimited (uses Cloud Storage)
- Processing time: Can take several minutes for long audio files
- Cost: See pricing information below

## Troubleshooting

### "Permission denied" or "403 Permission 'speech.recognizers.recognize' denied"

This means your authenticated user lacks the necessary IAM permissions. Fix it by:

```bash
# Grant Speech-to-Text permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/speech.admin'
```

Make sure you have:
- Enabled the Speech-to-Text V2 API and Cloud Storage API
- Granted the proper IAM roles (`roles/speech.admin` and `roles/storage.objectAdmin`)
- Billing enabled on your Google Cloud project
- Set the quota project with `gcloud auth application-default set-quota-project YOUR_PROJECT_ID`

### "API requires a quota project"

If you see: `"Your application is authenticating by using local Application Default Credentials. The speech.googleapis.com API requires a quota project"`, run:

```bash
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### "Authentication not found"

If you get authentication errors:

1. Make sure you've run `gcloud auth application-default login`
2. Check that the credentials file exists at `~/.config/gcloud/application_default_credentials.json`
3. Try re-authenticating:
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project YOUR_PROJECT_ID
   ```

### "Bucket not found"

- Verify the bucket name in your `.env` file is correct
- Make sure the bucket exists in your Google Cloud project
- Check that you have write permissions to the bucket
- Ensure your authenticated user has `roles/storage.objectAdmin` or similar role

### "Operation timeout"

- For very long audio files (>4 hours), increase the timeout in the script
- Check that the audio file was uploaded to GCS successfully
- Monitor the operation in Google Cloud Console

## Cost Information

**Google Cloud Speech-to-Text V2 API (Chirp 3 Model) pricing:**
- First 60 minutes per month: Free
- Standard data logging: $0.016 per 15 seconds
- Data logging opt-out: $0.024 per 15 seconds
- Speaker diarization: Included at no extra cost

**Google Cloud Storage pricing:**
- Storage: ~$0.020 per GB per month
- Operations: Minimal cost for uploads/downloads

Check current pricing at: https://cloud.google.com/speech-to-text/pricing

## Why Chirp 3 Model?

The Chirp 3 model is Google's latest and most accurate speech recognition model:
- **Better accuracy** than previous models (Chirp, Chirp 2)
- **Improved speaker diarization** for distinguishing speakers
- **Better handling** of accents, background noise, and multiple speakers
- **Automatic punctuation** that works more naturally
- Optimized for real-world audio conditions

## License

This script is provided as-is for educational purposes.
