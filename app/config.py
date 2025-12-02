#!/usr/bin/env python3
"""
App configuration: load env and define shared directories/constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directories
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
RESULTS_DIR = Path(os.getenv("RESULTS_DIR", "results"))

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Google Cloud settings (read from env)
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
