# Meeting Performance Analyzer - Web Application

A modern web application for transcribing audio from video/audio files with AI-powered speaker diarization using Google Cloud Speech-to-Text V2 API.

## 🌟 Features

- **🎬 Video & Audio Support**: Upload video files (MP4, AVI, MOV, etc.) or audio files (MP3, WAV, etc.)
- **👥 Speaker Diarization**: Automatically identifies and labels different speakers
- **🌍 Multi-language Support**: Transcribe in multiple languages
- **💻 Modern Web Interface**: Beautiful, responsive UI built with vanilla JavaScript
- **⚡ Real-time Updates**: Live job status tracking
- **📊 FastAPI Backend**: High-performance async API
- **☁️ Cloud-powered**: Uses Google Cloud Speech-to-Text V2 with Chirp 3 model

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │   Frontend (HTML/CSS/JavaScript)                    │    │
│  │   - File upload interface                           │    │
│  │   - Job status monitoring                           │    │
│  │   - Result viewer                                   │    │
│  └──────────────────┬──────────────────────────────────┘    │
└────────────────────┼──────────────────────────────────────┘
                     │ REST API
┌────────────────────┼──────────────────────────────────────┐
│                    ▼                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   FastAPI Backend (app.py)                          │   │
│  │   - File upload handling                            │   │
│  │   - Background job processing                       │   │
│  │   - API endpoints                                   │   │
│  └──────────────────┬──────────────────────────────────┘   │
└────────────────────┼──────────────────────────────────────┘
                     │
┌────────────────────┼──────────────────────────────────────┐
│                    ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Services Layer                                     │  │
│  │   ┌────────────────┐    ┌──────────────────────┐    │  │
│  │   │ Audio Extractor│    │ Transcription Service│    │  │
│  │   │  (FFmpeg)      │───▶│  (GCloud API)        │    │  │
│  │   └────────────────┘    └──────────────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
.
├── app.py                          # FastAPI application
├── main.py                         # CLI tool (legacy)
├── start.sh                        # Startup script
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── services/
│   ├── __init__.py
│   ├── audio_extractor.py         # Video → Audio extraction
│   └── transcription_service.py   # Audio → Text transcription
├── static/
│   ├── index.html                 # Main web interface
│   ├── styles.css                 # Styling
│   └── script.js                  # Frontend logic
├── uploads/                       # Temporary file uploads
├── results/                       # Transcription results
└── README_WEBAPP.md              # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+**
2. **FFmpeg** (for video processing)
3. **Google Cloud Account** with billing enabled
4. **Google Cloud SDK** installed and configured

### Installation

1. **Clone the repository**
   ```bash
   cd /path/to/project
   ```

2. **Install FFmpeg**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   ```

3. **Set up Google Cloud Authentication**
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project YOUR_PROJECT_ID
   ```

4. **Grant IAM Permissions**
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member='user:YOUR_EMAIL@gmail.com' \
       --role='roles/speech.admin'
   ```

5. **Configure Environment Variables**
   
   Create a `.env` file:
   ```bash
   GCS_BUCKET_NAME=your-bucket-name
   GOOGLE_PROJECT_ID=your-project-id
   ```

6. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Option 1: Using the startup script (recommended)**
```bash
./start.sh
```

**Option 2: Manual start**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- 🌐 **Web Interface**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

## 📖 API Endpoints

### Health Check
```http
GET /api/health
```
Returns server health status.

### Create Transcription Job
```http
POST /api/transcribe
Content-Type: multipart/form-data

Parameters:
  - file: File (required) - Video or audio file
  - language_code: string (default: "en-US")
  - min_speakers: integer (default: 2)
  - max_speakers: integer (default: 5)
  - keep_audio: boolean (default: false)

Response:
{
  "job_id": "uuid",
  "message": "Transcription job created successfully",
  "status": "queued"
}
```

### Get Job Status
```http
GET /api/jobs/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "completed",
  "progress": "Transcription completed successfully",
  "filename": "video.mp4",
  "created_at": "2025-11-28T10:00:00",
  "completed_at": "2025-11-28T10:05:00",
  "transcription": "Speaker 1:\nHello..."
}
```

### List Jobs
```http
GET /api/jobs?limit=10

Response:
{
  "jobs": [...],
  "total": 5
}
```

### Download Transcription
```http
GET /api/jobs/{job_id}/download

Returns: text/plain file
```

### Delete Job
```http
DELETE /api/jobs/{job_id}

Response:
{
  "message": "Job deleted successfully"
}
```

## 💡 Usage Examples

### Using the Web Interface

1. **Open your browser** to http://localhost:8000
2. **Click "Choose video or audio file"** and select your file
3. **Configure options**:
   - Select language
   - Set speaker count range
   - Choose whether to keep extracted audio
4. **Click "Start Transcription"**
5. **Monitor progress** in the Jobs list
6. **View or download** results when complete

### Using the API with curl

```bash
# Upload and transcribe
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@meeting.mp4" \
  -F "language_code=en-US" \
  -F "min_speakers=2" \
  -F "max_speakers=5"

# Check status
curl "http://localhost:8000/api/jobs/{job_id}"

# Download result
curl "http://localhost:8000/api/jobs/{job_id}/download" -o transcription.txt
```

### Using Python requests

```python
import requests
import time

# Upload file
with open('meeting.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/transcribe',
        files={'file': f},
        data={
            'language_code': 'en-US',
            'min_speakers': 2,
            'max_speakers': 5
        }
    )

job_id = response.json()['job_id']
print(f"Job ID: {job_id}")

# Poll for completion
while True:
    status = requests.get(f'http://localhost:8000/api/jobs/{job_id}').json()
    print(f"Status: {status['status']} - {status['progress']}")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)

# Download result
if status['status'] == 'completed':
    result = requests.get(f'http://localhost:8000/api/jobs/{job_id}/download')
    with open('transcription.txt', 'wb') as f:
        f.write(result.content)
```

## 🎨 Frontend Features

- **Drag & Drop Upload**: Easy file selection
- **Real-time Progress**: Live status updates
- **Job History**: View all transcription jobs
- **Result Viewer**: In-browser transcription viewer
- **Copy to Clipboard**: Quick text copying
- **Responsive Design**: Works on desktop and mobile
- **Dark-friendly UI**: Beautiful gradient design

## 🔧 Configuration

### Environment Variables

- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name
- `GOOGLE_PROJECT_ID`: Google Cloud project ID

### Supported Languages

- `en-US` - English (US)
- `en-GB` - English (UK)
- `es-ES` - Spanish
- `fr-FR` - French
- `de-DE` - German
- `ja-JP` - Japanese
- `zh-CN` - Chinese (Simplified)
- `ar-SA` - Arabic
- `hi-IN` - Hindi

[See full list](https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages)

### Supported File Formats

**Video**: MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V, MPG, MPEG, 3GP, OGV

**Audio**: MP3, WAV, FLAC, M4A, AAC, OGG, WMA, Opus, AMR

## 🔒 Security Considerations

### Production Deployment

1. **Use HTTPS**: Always use SSL/TLS in production
2. **Add Authentication**: Implement user authentication
3. **Rate Limiting**: Add request rate limiting
4. **File Validation**: Validate file types and sizes
5. **Persistent Storage**: Use database instead of in-memory storage
6. **Secure Secrets**: Use secret management service
7. **CORS**: Restrict CORS origins to your domain

### Example Production Setup

```python
# Add authentication
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/transcribe")
async def create_transcription_job(
    token: str = Depends(security),
    ...
):
    # Verify token
    ...

# Add rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/transcribe")
@limiter.limit("5/minute")
async def create_transcription_job(...):
    ...
```

## 📊 Monitoring & Logging

### Enable Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Monitoring

Use the `/api/health` endpoint for health checks:

```bash
# Add to cron or monitoring service
curl http://localhost:8000/api/health
```

## 🐛 Troubleshooting

### Common Issues

**1. "FFmpeg not found"**
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
```

**2. "Permission denied" errors**
```bash
# Grant IAM permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/speech.admin'
```

**3. "API requires quota project"**
```bash
# Set quota project
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

**4. Port already in use**
```bash
# Use different port
uvicorn app:app --port 8001
```

## 🚢 Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t meeting-analyzer .
docker run -p 8000:8000 -v $(pwd)/.env:/app/.env meeting-analyzer
```

### Cloud Deployment

Deploy to Google Cloud Run, AWS ECS, or Azure Container Instances for scalable production hosting.

## 📝 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open a GitHub issue.
