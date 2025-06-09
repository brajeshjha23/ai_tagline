import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd
import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from pyngrok import ngrok
import threading
import time

ngrok.set_auth_token("2xzc5Cq4UND7P5xOGoBgSMlxsVu_4ADaFx9BEhUyBz4V2SkH9")


# Import your existing modules
from image_details_extractor import generate_product_description
from tagline_generator import generate_luxury_tagline_from_json

# Initialize FastAPI app
app = FastAPI(
    title="Product Processing Service",
    description="API for processing product data with AI-generated descriptions and taglines",
    version="1.0.0"
)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Request models
class ProcessRequest(BaseModel):
    file_path: str

class JobStatus(BaseModel):
    job_id: str
    status: str  # 'queued', 'processing', 'completed', 'failed'
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0
    total_items: int = 0
    current_item: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

def generate_job_id() -> str:
    """Generate unique job ID based on current timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"job_{timestamp}_{unique_id}"

def save_to_excel(results: List[Dict], output_file: str):
    """
    Saves the scraped data to an Excel file, flattening nested structures
    and storing all individual reviews in one column (one row per product).
    """
    excel_data = []
    for result in results:
        # Base fields for this product
        row = {
            "URL": result.get("url", ""),
            # "Editor's Notes": result.get("Editor's Notes", ""),
            "Images": ", ".join(result.get("Images", [])),
            "Overall Rating": result.get("Reviews", {}).get("overall_rating", ""),
            "Number of Reviews": result.get("Reviews", {}).get("number_of_reviews", ""),
            # Newly added fields
            "Product Description": result.get("Product Description", ""),
            "Luxury Tagline": result.get("Luxury Tagline", "")
        }

        # Add other product-specific keys
        for key, value in result.items():
            if key not in ["url", "Editor's Notes", "Images", "Reviews", "Product Description", "Luxury Tagline"]:
                if isinstance(value, list):
                    row[key] = ", ".join(value)
                elif isinstance(value, dict):
                    continue
                else:
                    row[key] = value

        # Aggregate all individual reviews into one string
        individual_reviews = result.get("Reviews", {}).get("individual_reviews", [])
        review_strings = []
        for review in individual_reviews:
            reviewer = review.get("reviewer", "")
            date = review.get("date", "")
            rating = review.get("rating", "")
            title = review.get("title", "")
            description = review.get("description", "")
            recommend = review.get("recommend", "")
            thumbs_up = review.get("thumbs_up", 0)
            thumbs_down = review.get("thumbs_down", 0)

            single_review = (
                f"{reviewer} ({date}) rated {rating}:\n"
                f"Title: {title}\n"
                f"Description: {description}\n"
                f"Recommend: {recommend}, Thumbs Up: {thumbs_up}, Thumbs Down: {thumbs_down}"
            )
            review_strings.append(single_review)

        row["All Reviews"] = "\n\n".join(review_strings)
        excel_data.append(row)

    df = pd.DataFrame(excel_data)
    df.to_excel(output_file, index=False)

async def process_products_job(job_id: str, input_json_path: str):
    """Background job to process products"""
    try:
        # Generate output paths based on job_id
        output_dir = Path("api_outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_json_path = output_dir / f"{job_id}_processed.json"
        output_excel_path = output_dir / f"{job_id}_processed.xlsx"
        # Update job status to processing
        job_data = {
            "job_id": job_id,
            "status": "processing",
            "started_at": datetime.now().isoformat(),
            "progress": 0
        }
        redis_client.hset(f"job:{job_id}", mapping=job_data)

        # Load JSON file
        if not os.path.exists(input_json_path):
            raise FileNotFoundError(f"Input file not found: {input_json_path}")
            
        with open(input_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_items = len(data)
        redis_client.hset(f"job:{job_id}", "total_items", total_items)

        # Process each product
        for i, item in enumerate(data):
            current_url = item.get('url', f'Item {i+1}')
            
            # Update progress
            redis_client.hset(f"job:{job_id}", mapping={
                "progress": i,
                "current_item": current_url
            })

            print(f"Processing: {current_url}")
            images = item.get("Images", [])
            
            # Generate product description from images
            if images:
                product_description = generate_product_description(images)
            else:
                product_description = {}

            # Generate luxury tagline
            luxury_tagline = generate_luxury_tagline_from_json(product_description, item)
            item["Product Description"] = product_description
            item["Luxury Tagline"] = luxury_tagline
            
            print(f"Completed: {current_url}")

        # Create output directories if they don't exist
        output_dir.mkdir(exist_ok=True)

        # Save updated JSON
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Save to Excel
        save_to_excel(data, str(output_excel_path))

        # Update job status to completed
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "progress": total_items,
            "current_item": "All items completed",
            "result": json.dumps({
                "output_json_path": str(output_json_path),
                "output_excel_path": str(output_excel_path), 
                "total_processed": total_items
            })
        })

    except Exception as e:
        # Update job status to failed
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "failed",
            "completed_at": datetime.now().isoformat(),
            "error": str(e)
        })
        print(f"Job {job_id} failed: {str(e)}")

def worker():
    """Background worker to process jobs from Redis queue"""
    while True:
        try:
            # Pop job from queue (blocking operation)
            job_data = redis_client.blpop("job_queue", timeout=1)
            if job_data:
                job_info = json.loads(job_data[1])
                job_id = job_info["job_id"]
                
                # Run the processing job
                asyncio.run(process_products_job(
                    job_id,
                    job_info["input_json_path"]
                ))
        except Exception as e:
            print(f"Worker error: {str(e)}")
            time.sleep(1)

@app.on_event("startup")
async def startup_event():
    """Start background worker and ngrok tunnel"""
    # Start background worker thread
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    
    # Start ngrok tunnel
    try:
        public_url = ngrok.connect(8000)
        print(f"🌍 Public URL: {public_url}")
        print(f"🔗 Access your API at: {public_url}/docs")
    except Exception as e:
        print(f"Failed to start ngrok: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Product Processing Service is running!", "timestamp": datetime.now().isoformat()}

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a specific job"""
    try:
        job_data = redis_client.hgetall(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")

        # ─────── Fix: ensure 'result' is a dict, not a raw JSON string ───────
        if job_data.get("result"):
            try:
                job_data["result"] = json.loads(job_data["result"])
            except json.JSONDecodeError:
                # If for some reason it isn’t valid JSON, you can leave it as None or raise an error.
                job_data["result"] = None

        return JobStatus(**job_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    try:
        job_keys = redis_client.keys("job:*")
        jobs = []
        for key in job_keys:
            job_data = redis_client.hgetall(key)
            jobs.append(job_data)
        
        # Sort by created_at (newest first)
        jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job record"""
    try:
        deleted = redis_client.delete(f"job:{job_id}")
        if not deleted:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"message": f"Job {job_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{job_id}/{file_type}")
async def download_result(job_id: str, file_type: str):
    """Download the result files (json/excel)"""
    try:
        job_data = redis_client.hgetall(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job_data.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        result = json.loads(job_data.get("result", "{}"))
        
        if file_type == "json":
            file_path = result.get("output_json_path")
        elif file_type == "excel":
            file_path = result.get("output_excel_path")
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Use 'json' or 'excel'")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-and-process")
async def upload_and_process(file: UploadFile = File(...)):
    """Upload a JSON file and immediately start processing"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are allowed")
        
        # Create uploads directory
        upload_dir = Path("api_uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate JSON format
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Generate unique job ID
        job_id = generate_job_id()
        
        # Create job record in Redis
        job_data = {
            "job_id": job_id,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "total_items": 0,
            "input_file": str(file_path),
            "original_filename": file.filename
        }
        redis_client.hset(f"job:{job_id}", mapping=job_data)
        
        # Add job to queue
        job_info = {
            "job_id": job_id,
            "input_json_path": str(file_path)
        }
        redis_client.rpush("job_queue", json.dumps(job_info))
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "File uploaded and processing started",
            "created_at": datetime.now().isoformat(),
            "original_filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def verify_password(password: str):
    if password != "12345":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
def verify_password(password: str):
    if password != "12345":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.delete("/admin/clear-queue")
async def clear_queue(password: str):
    """Clear the Redis job queue and all job records if password matches"""
    verify_password(password)
    try:
        # Clear job queue
        redis_client.delete("job_queue")
        
        # Clear all job records
        job_keys = redis_client.keys("job:*")
        deleted_jobs = 0
        if job_keys:
            deleted_jobs = redis_client.delete(*job_keys)
        
        return {
            "message": "Queue cleared successfully",
            "deleted_jobs": deleted_jobs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/admin/queue-info")
async def get_queue_info():
    """Get information about the current queue status"""
    try:
        queue_length = redis_client.llen("job_queue")
        job_keys = redis_client.keys("job:*")
        
        # Count jobs by status
        status_counts = {}
        for key in job_keys:
            job_data = redis_client.hgetall(key)
            status = job_data.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "queue_length": queue_length,
            "total_jobs": len(job_keys),
            "status_breakdown": status_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Make sure Redis is running
    try:
        redis_client.ping()
        print("✅ Redis connection successful")
    except redis.ConnectionError:
        print("❌ Redis connection failed. Please make sure Redis server is running.")
        print("💡 Install and start Redis:")
        print("   - Windows: Download from https://redis.io/download")
        print("   - macOS: brew install redis && brew services start redis")
        print("   - Linux: sudo apt-get install redis-server && sudo systemctl start redis")
        exit(1)
    
    # Create necessary directories
    os.makedirs("api_outputs", exist_ok=True)
    os.makedirs("api_uploads", exist_ok=True)
    
    print("🚀 Starting FastAPI server...")
    print("📚 API Documentation will be available at:")
    print("   - Local: http://localhost:8000/docs")
    print("   - Public: [ngrok URL]/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)