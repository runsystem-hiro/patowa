# /home/pi/patowa/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, asyncio, random
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field

app = FastAPI(title="Dummy Occupancy API (shared state)")
templates = Jinja2Templates(directory="templates")

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== 設定 =====
CAPACITY = {"toilet": 2, "smoking": 8, "toilet2": 3, "shower1": 1, "shower2": 1, "checkin": 3, "checkout": 2}
UPDATE_INTERVAL_SEC = 5  # サーバの状態更新周期（全端末共通）

# ===== 共有状態 =====
STATE = {
    "toilet": {
        "capacity": CAPACITY["toilet"], "in_use": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    "smoking": {
        "capacity": CAPACITY["smoking"], "in_use": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    "toilet2": {
        "capacity": CAPACITY["toilet2"], "in_use": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    "shower1": {
        "capacity": CAPACITY["shower1"], "in_use": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    "shower2": {
        "capacity": CAPACITY["shower2"], "in_use": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    "checkin": {
        "capacity": CAPACITY["checkin"], "in_use": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    "checkout": {
        "capacity": CAPACITY["checkout"], "in_use": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
}

def _rand_step(cur: int, cap: int) -> int:
    # 均等 ±1（混雑バイアスなし）
    delta = random.choice([-1, 0, 1])  # やや増えやすいバイアス例(-1, 0, 1, 1)
    nxt = max(0, min(cap, cur + delta))
    return nxt

async def _update_loop():
    # 起動時の初期化（適当な初期人数）
    for k, cap in CAPACITY.items():
        STATE[k]["in_use"] = random.randint(0, cap)
        STATE[k]["updated_at"] = datetime.now(timezone.utc).isoformat()

    while True:
        try:
            for k, cap in CAPACITY.items():
                cur = STATE[k]["in_use"]
                STATE[k]["in_use"] = _rand_step(cur, cap)
                STATE[k]["updated_at"] = datetime.now(timezone.utc).isoformat()
            # ほんの少しジッターを入れて同時多発アクセス時のスパイクを避ける
            await asyncio.sleep(UPDATE_INTERVAL_SEC + random.uniform(-0.2, 0.2))
        except Exception as e:
            print("update_loop error:", e)  # ループが死なないようにキャッチしてログ
            await asyncio.sleep(1)

@app.on_event("startup")
async def on_startup():
    random.seed()
    asyncio.create_task(_update_loop())

# ====== スキーマ ======
Area = Literal["toilet", "smoking", "toilet2", "shower1", "shower2", "checkin", "checkout"]

class Status(BaseModel):
    area: Area = Field(..., description="エリア識別子")
    capacity: int = Field(..., ge=0, description="定員（最大同時利用数）")
    in_use: int = Field(..., ge=0, description="現在利用中の人数")
    updated_at: datetime = Field(..., description="UTCのISO8601時刻")

class Health(BaseModel):
    ok: bool
    time: datetime

def status_from_state(area: Area) -> Status:
    s = STATE[area]
    # STATEは文字列ISOを持っているのでdatetimeへ変換
    return Status(
        area=area,
        capacity=s["capacity"],
        in_use=s["in_use"],
        updated_at=datetime.fromisoformat(s["updated_at"])
    )

# ===== UI =====
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dev", response_class=HTMLResponse)
async def dev(request: Request):
    return templates.TemplateResponse("dev.html", {"request": request})

# ===== API =====
@app.get("/api/status/toilet", response_model=Status)
def toilet_status():
    return status_from_state("toilet")

@app.get("/api/status/smoking", response_model=Status)
def smoking_status():
    return status_from_state("smoking")

@app.get("/api/status/toilet2", response_model=Status)
def toilet2_status():
    return status_from_state("toilet2")

@app.get("/api/status/shower1", response_model=Status)
def shower1_status():
    return status_from_state("shower1")

@app.get("/api/status/shower2", response_model=Status)
def shower2_status():
    return status_from_state("shower2")

@app.get("/api/status/checkin", response_model=Status)
def checkin_status():
    return status_from_state("checkin")


@app.get("/api/status/checkout", response_model=Status)
def checkout_status():
    return status_from_state("checkout")

# 簡易ヘルスチェック
@app.get("/healthz", response_model=Health)
def health():
    return Health(ok=True, time=datetime.now(timezone.utc))
