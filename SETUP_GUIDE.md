# Quick Setup Guide

## Step-by-Step Setup for Google Cloud Transcription

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Google Cloud SDK
If you don't have `gcloud` CLI installed:
- Visit: https://cloud.google.com/sdk/docs/install
- Download and install for your operating system
- After installation, initialize:
  ```bash
  gcloud init
  ```

### 3. Get Your Google Cloud Project ID
```bash
# Option 1: Using gcloud
gcloud config get-value project

# Option 2: Using the Console
1. Go to https://console.cloud.google.com/
2. Look at the top of the page - your project ID is shown next to the project name
3. Or click the project dropdown and copy the "ID" column
```

### 4. Authenticate with Google Cloud
```bash
# Authenticate using Application Default Credentials
gcloud auth application-default login

# Set the quota project (replace YOUR_PROJECT_ID)
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

This will open a browser for you to sign in. Your credentials will be stored at `~/.config/gcloud/application_default_credentials.json`.

### 5. Grant IAM Permissions
```bash
# Get your authenticated email
gcloud auth list --filter=status:ACTIVE --format="value(account)"

# Grant Speech-to-Text permissions (replace YOUR_PROJECT_ID and YOUR_EMAIL)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/speech.admin'

# Grant Cloud Storage permissions (if not already an Owner)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/storage.objectAdmin'
```

### 6. Create a Cloud Storage Bucket
```bash
# Option 1: Using the Console
1. Go to https://console.cloud.google.com/storage
2. Click "Create Bucket"
3. Enter a unique name (e.g., "my-transcription-bucket")
4. Choose "Region: us-east1" or nearest to you
5. Click "Create"

# Option 2: Using gcloud CLI
gcloud storage buckets create gs://your-bucket-name --location=us-east1
```

### 7. Enable Required APIs
```bash
# Option 1: Using the Console
1. Go to https://console.cloud.google.com/apis/library
2. Search for "Speech-to-Text API" → Enable
3. Search for "Cloud Storage API" → Enable

# Option 2: Using gcloud CLI
gcloud services enable speech.googleapis.com
gcloud services enable storage.googleapis.com
```

### 8. Configure .env File
Create a `.env` file in the project directory:

```bash
# Copy the example file
cp .env.example .env

# Edit the file with your values
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_PROJECT_ID=your-project-id
```

**Note**: No API key is needed! The script uses Application Default Credentials.

### 9. Test the Setup
```bash
python transcribe_audio.py test_audio.mp3
```

## Common Issues

### "Permission 'speech.recognizers.recognize' denied"
This means your user lacks IAM permissions. Fix it:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/speech.admin'
```

### "API requires a quota project"
Set the quota project for your credentials:
```bash
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### "Authentication not found"
Authenticate with Application Default Credentials:
```bash
gcloud auth application-default login
```

### "API not enabled"
Enable the required APIs:
```bash
gcloud services enable speech.googleapis.com storage.googleapis.com
```

### "Bucket not found"
Make sure the bucket name in `.env` matches exactly (no `gs://` prefix)

### "Permission denied on bucket"
Grant storage permissions:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member='user:YOUR_EMAIL@gmail.com' \
    --role='roles/storage.objectAdmin'
```

## Example .env File

```bash
# No API key needed!
GCS_BUCKET_NAME=my-transcription-bucket
GOOGLE_PROJECT_ID=my-project-12345
```

## Authentication Flow

This script uses **Application Default Credentials (ADC)** instead of API keys:

1. You authenticate once with `gcloud auth application-default login`
2. Your OAuth 2.0 credentials are stored locally
3. The script automatically uses these credentials
4. Permissions are managed through IAM roles
5. More secure than static API keys

## Pricing Estimate

For a 1-hour audio file:
- Speech-to-Text: ~$3.84 (240 x 15-second chunks x $0.016)
- Cloud Storage: < $0.01 (temporary storage)
- **Total: ~$3.85 per hour of audio**

First 60 minutes per month are **FREE**!
