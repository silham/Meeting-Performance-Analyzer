# Audio Transcription with Speaker Diarization

This Python script transcribes MP3 audio files using Google Cloud Speech-to-Text V2 API with the **Chirp 3 model** for improved accuracy and speaker diarization (speaker identification).

## Features

- 🎬 **Extracts audio from video files** (MP4, AVI, MOV, MKV, etc.)
- 🎵 **Transcribes audio files** with **Chirp 3 model** for superior accuracy
- 👥 **Identifies different speakers** in the audio (speaker diarization)
- 📝 **Segments transcription by speaker**
- ⏱️ **Batch recognition** for long audio files (up to 8 hours)
- 💾 **Saves transcription to text file**
- 🔤 **Automatic punctuation** for natural reading
- ☁️ **Uses Google Cloud Storage** for processing large files
- 🔐 **Secure authentication** with Application Default Credentials (ADC)
- 🏗️ **Modular architecture** with separate services for audio extraction and transcription

## Quick Start

For users who already have Google Cloud set up:

```bash
# 1. Install FFmpeg (macOS)
brew install ffmpeg

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Authenticate with Google Cloud
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# 4. Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/speech.admin'

# 5. Create .env file
echo "GCS_BUCKET_NAME=your-bucket-name" > .env
echo "GOOGLE_PROJECT_ID=your-project-id" >> .env

# 6. Run the script
python main.py video.mp4
# or
python main.py audio.mp3
```

## Prerequisites

1. **Python 3.7+**: Make sure you have Python 3.7 or higher installed
2. **FFmpeg**: Required for extracting audio from video files
3. **Google Cloud Account**: You need a Google Cloud account with billing enabled
4. **Google Cloud SDK**: Install the `gcloud` CLI tool for authentication
5. **Speech-to-Text V2 API**: Enable the Cloud Speech-to-Text V2 API in your project
6. **Cloud Storage**: Create a Google Cloud Storage bucket for audio files and transcripts
7. **IAM Permissions**: Your Google account needs `roles/speech.admin` and `roles/storage.objectAdmin`

## Setup Instructions

### 1. Install FFmpeg

FFmpeg is required to extract audio from video files.

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

**Verify installation:**
```bash
ffmpeg -version
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install google-cloud-speech google-cloud-storage google-api-core python-dotenv
```

### 3. Install Google Cloud SDK

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

**Transcribe a video file:**
```bash
python main.py video.mp4
```

**Transcribe an audio file:**
```bash
python main.py audio.mp3
```

The script will:
1. Detect if input is video or audio
2. Extract audio from video (if needed)
3. Upload to Google Cloud Storage
4. Transcribe with speaker diarization using Chirp 3
5. Download and format results
6. Save transcription locally

### Advanced Usage

**Specify language:**
```bash
python main.py video.mp4 --language es-ES
```

**Set speaker count:**
```bash
python main.py audio.mp3 --min-speakers 3 --max-speakers 6
```

**Keep extracted audio file:**
```bash
python main.py video.mp4 --keep-audio
```

**Override environment variables:**
```bash
python main.py video.mp4 --bucket my-bucket --project my-project-id
```

**Get help:**
```bash
python main.py --help
```

### Supported File Formats

**Video formats:**
- MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V, MPG, MPEG, 3GP, OGV

**Audio formats:**
- MP3, WAV, FLAC, M4A, AAC, OGG, WMA, Opus, AMR

### Language Codes

Common language codes for transcription:
- `en-US` - English (US)
- `en-GB` - English (UK)
- `es-ES` - Spanish (Spain)
- `fr-FR` - French
- `de-DE` - German
- `ja-JP` - Japanese
- `zh-CN` - Chinese (Simplified)

See full list: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages

## Output

The script will:
1. Display progress and status messages
2. Show the transcription in the console, segmented by speaker
3. Save the transcription to a text file named `<filename>_transcription.txt`

### Example Session

```bash
$ python main.py interview.mp4

================================================================================
🎬 Processing: interview.mp4
================================================================================

📹 Detected video file: interview.mp4
🎵 Extracting audio from video...

Extracting audio from video: interview.mp4
Output audio file: interview.mp3
✓ Audio extracted successfully: interview.mp3

🎤 Starting transcription with speaker diarization...

✓ Authentication found
Uploading interview.mp3 to gs://my-bucket/audio-files/1763191807_interview.mp3...
File uploaded successfully to gs://my-bucket/audio-files/1763191807_interview.mp3

================================================================================
Processing audio file: gs://my-bucket/audio-files/1763191807_interview.mp3
Using Chirp 3 model for improved accuracy...
Sending batch recognition request to Google Speech-to-Text V2 API...
This may take a while depending on the audio file size...
Waiting for operation to complete...

Batch recognition completed!
Results saved to: gs://my-bucket/transcripts/1763191807_interview
Downloading transcription results from gs://my-bucket/transcripts/1763191807_interview...
Processing transcripts/1763191807_interview/interview_transcript_abc123.json...

================================================================================
TRANSCRIPTION WITH SPEAKER DIARIZATION (Chirp 3 Model)
================================================================================

Speaker 1:
Hello, thanks for joining us today. Can you tell us about your background?

Speaker 2:
Sure, I'd be happy to. I have over 10 years of experience in software development.

Speaker 1:
That's impressive. What technologies do you specialize in?

Speaker 2:
I mainly work with Python, JavaScript, and cloud technologies like Google Cloud and AWS.


Transcription saved locally to: interview_transcription.txt
================================================================================

================================================================================
✅ SUCCESS!
================================================================================
📄 Transcription saved to: interview_transcription.txt
☁️  GCS URI: gs://my-bucket/audio-files/1763191807_interview.mp3
📁 GCS Output: gs://my-bucket/transcripts/1763191807_interview
================================================================================
```

### Example output file:
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

## Project Structure

```
.
├── app/
│   ├── main.py                     # FastAPI entrypoint
│   ├── routers/                    # API routes
│   │   ├── health.py
│   │   ├── jobs.py
│   │   └── transcribe.py
│   ├── background/
│   │   └── processor.py            # Background task engine
│   ├── services/
│   │   ├── audio_extractor.py
│   │   └── transcription_service.py
│   ├── utils/
│   │   ├── file_utils.py
│   │   └── job_utils.py
│   └── models/
│       └── job_models.py           # Pydantic models
│
├── uploads/                        # Temporary input files
├── results/                        # Final transcription JSON/text
│
├── static/
│   ├── index.html
│   ├── script.js
│   └── styles.css
│
├── requirements.txt
├── start.sh
├── .env
└── README_WEBAPP.md (this file)
```

### Services

**Audio Extractor** (`services/audio_extractor.py`)
- Extracts audio from video files using FFmpeg
- Supports multiple video formats
- Configurable audio quality and format
- Can be used standalone

**Transcription Service** (`services/transcription_service.py`)
- Handles Google Cloud Speech-to-Text V2 API integration
- Speaker diarization with Chirp 3 model
- GCS upload and result retrieval
- Formats transcription with speaker labels
- Can be used standalone

**Main Script** (`main.py`)
- Integrates both services
- CLI interface with argparse
- Automatic file type detection
- Error handling and validation

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
