#!/usr/bin/env python3
"""
Test script to verify the services are working correctly
"""

import os
import sys

def test_imports():
    """Test that all services can be imported"""
    print("Testing imports...")
    try:
        from services import extract_audio_from_video, transcribe_audio
        print("✓ Services imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import services: {str(e)}")
        return False

def test_ffmpeg():
    """Test that FFmpeg is installed"""
    print("\nTesting FFmpeg installation...")
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print("✓ FFmpeg is installed")
        return True
    except FileNotFoundError:
        print("✗ FFmpeg is not installed")
        print("  Install with: brew install ffmpeg (macOS)")
        return False
    except Exception as e:
        print(f"✗ Error checking FFmpeg: {str(e)}")
        return False

def test_environment():
    """Test that environment variables are set"""
    print("\nTesting environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    bucket = os.environ.get("GCS_BUCKET_NAME")
    project = os.environ.get("GOOGLE_PROJECT_ID")
    
    if not bucket:
        print("✗ GCS_BUCKET_NAME not set in .env file")
        return False
    else:
        print(f"✓ GCS_BUCKET_NAME: {bucket}")
    
    if not project:
        print("✗ GOOGLE_PROJECT_ID not set in .env file")
        return False
    else:
        print(f"✓ GOOGLE_PROJECT_ID: {project}")
    
    return True

def test_auth():
    """Test that Google Cloud authentication is working"""
    print("\nTesting Google Cloud authentication...")
    try:
        from google.auth import default
        credentials, project = default()
        print("✓ Google Cloud authentication found")
        if project:
            print(f"  Project: {project}")
        return True
    except Exception as e:
        print("✗ Authentication not found")
        print("  Run: gcloud auth application-default login")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Running System Tests")
    print("=" * 60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("FFmpeg", test_ffmpeg),
        ("Environment", test_environment),
        ("Authentication", test_auth)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error in {name} test: {str(e)}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nYou can now run:")
        print("  python main.py your-video.mp4")
        print("  python main.py your-audio.mp3")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
