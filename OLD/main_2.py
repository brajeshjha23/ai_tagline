import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd
import sqlite3
import threading
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from pyngrok import ngrok
import time

ngrok.set_auth_token("2xzc5Cq4UND7P5xOGoBgSMlxsVu_4ADaFx9BEhUyBz4V2SkH9")

# Import existing modules
from image_details_extractor import generate_product_description
from tagline_generator import generate_luxury_tagline_from_json
from analytics_matcher import match_headline_to_keyword

# Initialize FastAPI app
app = FastAPI(
    title="Product Processing Service",
    description="API for processing product data with AI-generated descriptions and taglines",
    version="1.0.0"
)

# SQLite connection handling
local_data = threading.local()

def get_db():
    if not hasattr(local_data, "db"):
        local_data.db = sqlite3.connect('jobs.db', check_same_thread=False)
        local_data.db.execute('''CREATE TABLE IF NOT EXISTS jobs
                                 (job_id TEXT PRIMARY KEY,
                                  status TEXT,
                                  created_at TEXT,
                                  started_at TEXT,
                                  completed_at TEXT,
                                  progress INTEGER,
                                  total_items INTEGER,
                                  current_item TEXT,
                                  result TEXT,
                                  error TEXT,
                                  input_file TEXT,
                                  original_filename TEXT)''')
    return local_data.db

# Request models
class ProcessRequest(BaseModel):
    file_path: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0
    total_items: int = 0
    current_item: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

def generate_job_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"job_{timestamp}_{unique_id}"

async def process_products_job(job_id: str, input_json_path: str):
    try:
        output_dir = Path("api_outputs")
        output_dir.mkdir(exist_ok=True)
        
        db = get_db()
        c = db.cursor()
        started_at = datetime.now().isoformat()
        c.execute("UPDATE jobs SET status = 'processing', started_at = ? WHERE job_id = ?", (started_at, job_id))
        db.commit()
        
        if not os.path.exists(input_json_path):
            raise FileNotFoundError(f"Input file not found: {input_json_path}")
            
        with open(input_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total_items = len(data)
        c.execute("UPDATE jobs SET total_items = ? WHERE job_id = ?", (total_items, job_id))
        db.commit()
        res = {}
        
        for i, item in enumerate(data):
            current_url = item.get('url', f'Item {i+1}')
            c.execute("UPDATE jobs SET progress = ?, current_item = ? WHERE job_id = ?", (i, current_url, job_id))
            db.commit()
            
            print(f"Processing: {current_url}")
            images = item.get("Images", [])
            if images:
                product_description = generate_product_description(images)
            else:
                product_description = {}

            product_name = item.get("product_name", [])

            if product_name:
                analytics = match_headline_to_keyword(product_name)
            else:
                analytics = {}

            luxury_tagline = generate_luxury_tagline_from_json(product_description, item, analytics)

            res[current_url] = luxury_tagline
        result_json = json.dumps(res, ensure_ascii=False)
        
        completed_at = datetime.now().isoformat()
        c.execute("UPDATE jobs SET status = 'completed', completed_at = ?, progress = ?, current_item = ?, result = ? WHERE job_id = ?",
                  (completed_at, total_items, "All items completed", result_json, job_id))
        db.commit()
    
    except Exception as e:
        db = get_db()
        c = db.cursor()
        completed_at = datetime.now().isoformat()
        c.execute("UPDATE jobs SET status = 'failed', completed_at = ?, error = ? WHERE job_id = ?", 
                  (completed_at, str(e), job_id))
        db.commit()
        print(f"Job {job_id} failed: {str(e)}")

def worker():
    while True:
        try:
            db = get_db()
            c = db.cursor()
            c.execute("SELECT job_id, input_file FROM jobs WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1")
            row = c.fetchone()
            if row:
                job_id, input_json_path = row
                started_at = datetime.now().isoformat()
                c.execute("UPDATE jobs SET status = 'processing', started_at = ? WHERE job_id = ?", (started_at, job_id))
                db.commit()
                asyncio.run(process_products_job(job_id, input_json_path))
            else:
                time.sleep(1)
        except Exception as e:
            print(f"Worker error: {str(e)}")
            time.sleep(1)

@app.on_event("startup")
async def startup_event():
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    try:
        public_url = ngrok.connect(8000)
        print(f"🌍 Public URL: {public_url}")
        print(f"🔗 Access your API at: {public_url}/docs")
    except Exception as e:
        print(f"Failed to start ngrok: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Product Processing Service is running!", "timestamp": datetime.now().isoformat()}

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    try:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = c.fetchone()
        if row:
            columns = [column[0] for column in c.description]
            job_data = dict(zip(columns, row))
            if job_data.get("result"):
                job_data["result"] = json.loads(job_data["result"])
            return JobStatus(**job_data)
        else:
            raise HTTPException(status_code=404, detail="Job not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def list_jobs():
    try:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        rows = c.fetchall()
        columns = [column[0] for column in c.description]
        jobs = [dict(zip(columns, row)) for row in rows]
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    try:
        db = get_db()
        c = db.cursor()
        c.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
        db.commit()
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"message": f"，可能 {job_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-and-process")
async def upload_and_process(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are allowed")
        
        upload_dir = Path("api_uploads")
        upload_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        job_id = generate_job_id()
        created_at = datetime.now().isoformat()
        
        db = get_db()
        c = db.cursor()
        c.execute('''INSERT INTO jobs 
                     (job_id, status, created_at, progress, total_items, input_file, original_filename)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (job_id, 'queued', created_at, 0, 0, str(file_path), file.filename))
        db.commit()
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "File uploaded and processing started",
            "created_at": created_at,
            "original_filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def verify_password(password: str):
    if password != "12345":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.delete("/admin/clear-queue")
async def clear_queue(password: str):
    verify_password(password)
    try:
        db = get_db()
        c = db.cursor()
        c.execute("DELETE FROM jobs WHERE status = 'queued'")
        deleted_count = c.rowcount
        db.commit()
        return {
            "message": "Queue cleared successfully",
            "deleted_jobs": deleted_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/queue-info")
async def get_queue_info():
    try:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status")
        status_counts = dict(c.fetchall())
        c.execute("SELECT COUNT(*) FROM jobs WHERE status = 'queued'")
        queue_length = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = c.fetchone()[0]
        return {
            "queue_length": queue_length,
            "total_jobs": total_jobs,
            "status_breakdown": status_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    os.makedirs("api_uploads", exist_ok=True)
    
    print("🚀 Starting FastAPI server...")
    print("📚 API Documentation will be available at:")
    print("   - Local: http://localhost:8000/docs")
    print("   - Public: [ngrok URL]/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)