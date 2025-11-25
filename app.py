# app.py (modifikasi + endpoint gambar)
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import math
import socket
import psutil
import io

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import EmailStr, BaseModel, computed_field

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, Session

# import models (tambahkan TlxResponse)
from models import Base, Keylog, Posture, User, TlxResponse, NordicBodymapResponse

import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import shapiro

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
DB_URL = "postgresql://postgres:123@10.34.239.190:5433/riset-prod"
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

# --- Existing routes (unchanged) ---
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

class NordicOut(BaseModel):
    id: int
    user_email: EmailStr
    created_at: datetime
    name: str

    nbm_0:  int; nbm_1:  int; nbm_2:  int; nbm_3:  int; nbm_4:  int; nbm_5:  int; nbm_6:  int
    nbm_7:  int; nbm_8:  int; nbm_9:  int; nbm_10: int; nbm_11: int; nbm_12: int; nbm_13: int
    nbm_14: int; nbm_15: int; nbm_16: int; nbm_17: int; nbm_18: int; nbm_19: int; nbm_20: int
    nbm_21: int; nbm_22: int; nbm_23: int; nbm_24: int; nbm_25: int; nbm_26: int

    # property helper dari model
    @computed_field
    def total_score(self) -> int:
        return sum(
            getattr(self, f"nbm_{i}", 0) for i in range(1, 28)
        )

    model_config = dict(from_attributes=True)

@app.get(
    "/nordic",
    response_model=List[NordicOut],
    summary="List Nordic Body Map responses (optionally filter by email)"
)
def list_nordic(
    email: Optional[EmailStr] = Query(None, description="Jika diisi, filter berdasarkan user email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):

    q = (
        db.query(NordicBodymapResponse, User.name.label("name"))
        .join(User, NordicBodymapResponse.user_email == User.user_email)
        .order_by(NordicBodymapResponse.created_at.desc())
    )

    if email:
        q = q.filter(NordicBodymapResponse.user_email == str(email))

    rows = q.offset(offset).limit(limit).all()

    return [
        NordicOut(
            **{**row.NordicBodymapResponse.__dict__, "name": row.name}
        )
        for row in rows
    ]


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

# ----------------- helper functions for TLX processing -----------------
DIMENSI = ["mental", "physical", "temporal", "performance", "effort", "frustration"]
PAIR_ATTRS = [f"pair_q{i}" for i in range(1, 16)]

def compute_scores_from_rows(rows):
    """
    rows: list of TlxResponse ORM objects
    returns: list of dicts {id, user_email, skor}
    """
    results = []
    for r in rows:
        # compute bobot per dimensi (count of times chosen in pair_q1..q15)
        bobot = {d: 0 for d in DIMENSI}
        for attr in PAIR_ATTRS:
            val = getattr(r, attr)
            if val is None:
                continue
            # val is an Enum member or string depending on ORM; convert to string name
            if isinstance(val, str):
                key = val
            else:
                # Enum
                key = val.value if hasattr(val, "value") else str(val)
            if key in bobot:
                bobot[key] += 1

        # rating values: use likert_performance property logic if available
        def _rating_for(dim):
            if dim == "performance":
                # try model property first
                perf_raw = getattr(r, "likert_performance_raw", None)
                if perf_raw is None:
                    return 0
                try:
                    perf_raw_int = int(perf_raw)
                except Exception:
                    perf_raw_int = perf_raw
                # if raw seems 1..10 then transform as in model: 11 - raw
                if perf_raw_int <= 10:
                    return max(1, 11 - perf_raw_int)
                # otherwise assume already 0..100-like rating
                return perf_raw_int
            else:
                attrname = {
                    "mental": "likert_mental",
                    "physical": "likert_physical",
                    "temporal": "likert_temporal",
                    "effort": "likert_effort",
                    "frustration": "likert_frustration",
                }[dim]
                return getattr(r, attrname, 0)

        # compute WWL like code: sum(rating * bobot) / 15
        WWL = 0
        for d in DIMENSI:
            rating = _rating_for(d)
            wb = bobot.get(d, 0)
            WWL += (rating * wb)
        skor = None
        try:
            skor = round(WWL / 15, 2)
        except Exception:
            skor = None

        results.append({
            "id": r.id,
            "user_email": r.user_email,
            "skor": skor,
            "bobot": bobot,
        })
    return results

def kategori_tlx(skor):
    if skor is None:
        return "Belum Dihitung"
    if skor < 50:
        return "Ringan"
    if skor <= 80:
        return "Sedang"
    return "Berat"

# ----------------- Plot endpoints -----------------

@app.get("/tlx/plot/wwl.png")
def plot_wwl(email: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    """
    Returns PNG image: grafik skor NASA-TLX per responden + rata-rata + BKA/BKB
    """
    try:
        q = db.query(TlxResponse)
        q = q.filter(~TlxResponse.user_email.like("%@test.com"))
        rows = q.order_by(asc(TlxResponse.created_at)).all()
        if not rows:
            raise HTTPException(status_code=404, detail="No TLX responses found")

        computed = compute_scores_from_rows(rows)
        skor_list = [c["skor"] for c in computed if c["skor"] is not None]
        if len(skor_list) == 0:
            raise HTTPException(status_code=404, detail="No computed scores available")

        N = len(skor_list)
        rata2 = float(np.mean(skor_list))
        std = float(np.std(skor_list, ddof=1)) if N > 1 else 0.0
        BKA = rata2 + 3 * std
        BKB = rata2 - 3 * std

        # plot
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(range(1, N + 1), skor_list, marker="o", label="Skor Beban")
        ax.axhline(rata2, linestyle="--", label=f"Rata-rata = {rata2:.2f}")
        ax.axhline(BKA, linestyle="--", label=f"BKA = {BKA:.2f}")
        ax.axhline(BKB, linestyle="--", label=f"BKB = {BKB:.2f}")
        ax.set_title("Grafik Uji Keseragaman Skor NASA-TLX")
        ax.set_xlabel("Responden")
        ax.set_ylabel("Skor NASA-TLX")
        ax.legend()

        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tlx/plot/aspects.png")
def plot_aspects(email: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    """
    Returns PNG image: rata-rata tiap aspek/dimensi NASA-TLX (bar chart)
    """
    try:
        q = db.query(TlxResponse)
        q = q.filter(~TlxResponse.user_email.like("%@test.com"))
        rows = q.all()
        if not rows:
            raise HTTPException(status_code=404, detail="No TLX responses found")

        # compute ratings mean per dimensi
        ratings_sum = {d: 0.0 for d in DIMENSI}
        counts = {d: 0 for d in DIMENSI}
        for r in rows:
            # performance special
            # reuse logic from compute_scores
            def _rating_for(dim):
                if dim == "performance":
                    perf_raw = getattr(r, "likert_performance_raw", None)
                    if perf_raw is None:
                        return 0
                    try:
                        perf_raw_int = int(perf_raw)
                    except Exception:
                        perf_raw_int = perf_raw
                    if perf_raw_int <= 10:
                        return max(1, 11 - perf_raw_int)
                    return perf_raw_int
                else:
                    attrname = {
                        "mental": "likert_mental",
                        "physical": "likert_physical",
                        "temporal": "likert_temporal",
                        "effort": "likert_effort",
                        "frustration": "likert_frustration",
                    }[dim]
                    return getattr(r, attrname, 0)

            for d in DIMENSI:
                v = _rating_for(d)
                if v is not None:
                    ratings_sum[d] += v
                    counts[d] += 1

        rata_dimensi = {d: (ratings_sum[d] / counts[d] if counts[d] else 0) for d in DIMENSI}

        # plot bar chart
        fig, ax = plt.subplots(figsize=(8, 4.5))
        keys = list(rata_dimensi.keys())
        vals = [rata_dimensi[k] for k in keys]
        ax.bar(keys, vals)
        ax.set_title("Perbandingan Aspek NASA-TLX")
        ax.set_ylabel("Rata-rata Skor")
        ax.set_xticklabels(keys, rotation=45)

        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tlx/plot/categories.png")
def plot_categories(email: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    """
    Returns PNG image: distribusi kategori WWL (Ringan/Sedang/Berat)
    """
    try:
        q = db.query(TlxResponse)
        q = q.filter(~TlxResponse.user_email.like("%@test.com"))
        rows = q.all()
        if not rows:
            raise HTTPException(status_code=404, detail="No TLX responses found")

        computed = compute_scores_from_rows(rows)
        kategori_counts = {}
        for c in computed:
            k = kategori_tlx(c["skor"])
            kategori_counts[k] = kategori_counts.get(k, 0) + 1

        # ensure canonical order
        order = ["Ringan", "Sedang", "Berat", "Belum Dihitung"]
        labels = [o for o in order if o in kategori_counts]
        counts = [kategori_counts[l] for l in labels]

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(labels, counts)
        ax.set_title("Distribusi Kategori Beban Kerja (WWL)")
        ax.set_ylabel("Jumlah Responden")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, int(yval),
                    ha='center', va='bottom')

        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
