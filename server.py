"""
Cannabis CRM & Compliance Automation System
FastAPI Main Application Server
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.api import router as api_router
from backend.database import init_db

# Initialize database
init_db()

app = FastAPI(
    title="Cannabis Compliance CRM System",
    description="Full-Stack Automation and CRM Platform for Cannabis Compliance Specialists",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Frontend directories
BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_frontend_root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Cannabis CRM API is active. Frontend index.html not yet deployed."}

@app.get("/favicon.ico")
def serve_favicon():
    favicon_file = FRONTEND_DIR / "favicon.svg"
    if favicon_file.exists():
        return FileResponse(favicon_file, media_type="image/svg+xml")
    return {"status": "not found"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n=======================================================")
    print(f"[*] CANNABIS CRM & COMPLIANCE AUTOMATION SYSTEM (v2.0)")
    print(f"[*] Running at: http://127.0.0.1:{port}")
    print(f"[*] API Documentation: http://127.0.0.1:{port}/docs")
    print(f"=======================================================\n")
    uvicorn.run("server:app", host="127.0.0.1", port=port, reload=True)
