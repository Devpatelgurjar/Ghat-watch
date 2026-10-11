"""FastAPI main application entry point for Ghat Watch."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import REPORTS_DIR
from app.routes import router

app = FastAPI(
    title="Ghat Watch API",
    description="Decision-support web app ranking Bhopal immersion ghats by water quality risk for Durga Visarjan 2026.",
    version="1.0.0",
)

# Enable CORS for local Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(router)

# Serve report PDFs statically with byte-range support for direct page links
if REPORTS_DIR.exists():
    app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")


@app.get("/")
def root():
    return {
        "app": "Ghat Watch API",
        "status": "online",
        "target_event": "Durga Visarjan · 20 October 2026",
        "target_user": "Bhopal Municipal Corporation (BMC) Immersion Planning Officer",
        "endpoints": {
            "ghats": "/api/ghats",
            "ghat_detail": "/api/ghats/{id}",
            "brief": "/api/brief?lang=en|hi",
            "meta": "/api/meta",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
