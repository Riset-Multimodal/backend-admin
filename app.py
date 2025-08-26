# app.py
from pathlib import Path
from typing import Optional, Dict, Any, List

import math
import socket
import psutil

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Keylog, Posture, User  # asumsi sudah ada .as_dict() di tiap model

# --- FastAPI app & CORS ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sesuaikan jika perlu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB setup ---
DB_URL = "postgresql://postgres:123@proxy.bccdev.id:11015/riset_db"
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.create_all(engine)  # hindari di produksi

# --- Static files ---
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# --- Dependency: DB session ---
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper: pagination ---
def paginate_query(query, page: int, per_page: int) -> Dict[str, Any]:
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20

    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page
    results = query.offset(offset).limit(per_page).all()

    data = [item.as_dict() for item in results]
    pagination_meta = {
        "total": total,
        "per_page": per_page,
        "page": page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
    return {"data": data, "pagination": pagination_meta}

# --- Routes ---

@app.get("/keylog")
def get_keylogs(
    email: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Keylog)
        if email:
            query = query.filter(Keylog.user_email == email)
        return paginate_query(query, page, per_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posture")
def get_postures(
    email: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Posture)
        if email:
            query = query.filter(Posture.user_email == email)
        query = query.order_by(asc(Posture.timestamp))
        return paginate_query(query, page, per_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def get_users(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        users = db.query(User).all()
        return [u.as_dict() for u in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system")
def system_api():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        net_io = psutil.net_io_counters()
        net_sent = round(net_io.bytes_sent / (1024 * 1024), 2)
        net_recv = round(net_io.bytes_recv / (1024 * 1024), 2)
        return {
            "ip": ip,
            "cpu": cpu,
            "memory": memory,
            "net_sent": net_sent,
            "net_recv": net_recv,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_path))


# --- Dev server entrypoint (optional) ---
# Jalankan: uvicorn app:app --host 0.0.0.0 --port 5000 --reload
