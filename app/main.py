#!/usr/bin/env python3
"""
FastAPI entrypoint (modularized from original app.py)
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import UPLOAD_DIR, RESULTS_DIR
from app.routers import health, transcribe, jobs

app = FastAPI(
    title="Meeting Performance Analyzer",
    description="Transcribe audio from video/audio files with speaker diarization",
    version="1.0.0"
)

# Enable CORS (same permissive configuration as before)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(transcribe.router)
app.include_router(jobs.router)

# Serve root HTML page (same behavior as original)
@app.get("/", response_class=HTMLResponse)
async def root():
    html_file = Path("static/index.html")
    if html_file.exists():
        # FileResponse will serve the actual HTML file (so static assets still work)
        return FileResponse(html_file)
    return HTMLResponse(content="<h1>Meeting Performance Analyzer API</h1><p>Upload interface coming soon...</p>")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
