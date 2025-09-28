import os
import time
import json
import subprocess
import requests
from pathlib import Path

STORAGE_PATH = "/storage"
INPUT_PATH = f"{STORAGE_PATH}/input"
OUTPUT_PATH = f"{STORAGE_PATH}/output"
API_URL = os.getenv("API_URL", "http://api-service:8080")

def process_video(job_data):
    """Process video based on job configuration"""
    input_file = f"{INPUT_PATH}/{job_data['input_filename']}"
    output_file = f"{OUTPUT_PATH}/{job_data['output_filename']}"
    
    # Ensure output directory exists
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    
    # Build ffmpeg command based on job type
    if job_data['operation'] == 'compress':
        cmd = [
            'ffmpeg', '-i', input_file,
            '-c:v', 'libx264', '-crf', '28',
            '-c:a', 'aac', '-b:a', '128k',
            '-y', output_file
        ]
    elif job_data['operation'] == 'resize':
        resolution = job_data.get('resolution', '720x480')
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vf', f'scale={resolution}',
            '-c:a', 'copy',
            '-y', output_file
        ]
    elif job_data['operation'] == 'thumbnail':
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vf', 'thumbnail,scale=320:240',
            '-frames:v', '1',
            '-y', output_file
        ]
    
    print(f"Processing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return result.returncode == 0

def update_job_status(job_id, status, message=""):
    """Update job status via API"""
    try:
        requests.post(f"{API_URL}/jobs/{job_id}/status", 
                     json={"status": status, "message": message})
    except Exception as e:
        print(f"Failed to update job status: {e}")

def main():
    """Main worker loop"""
    print("FFmpeg Worker starting...")
    
    while True:
        try:
            # Poll for new jobs
            response = requests.get(f"{API_URL}/jobs/next")
            if response.status_code == 200:
                job = response.json()
                job_id = job['id']
                
                print(f"Processing job {job_id}")
                update_job_status(job_id, "processing")
                
                if process_video(job):
                    update_job_status(job_id, "completed")
                    print(f"Job {job_id} completed successfully")
                else:
                    update_job_status(job_id, "failed", "FFmpeg processing failed")
                    print(f"Job {job_id} failed")
            
            time.sleep(5)  # Poll every 5 seconds
            
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
