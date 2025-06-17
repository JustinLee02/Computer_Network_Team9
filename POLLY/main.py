from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware   # ← 추가
from pathlib import Path

from app.api.votes   import router as votes_router
from app.api.health  import router as health_router
from app.ws.endpoint import router as ws_router
from app.ws.chat_endpoint import router as chat_ws_router

app = FastAPI()

# ─── CORS 설정 ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],            # GET, POST, PUT, DELETE 등 전부
    allow_headers=["*"],            # Content-Type, Authorization 등 전부
    allow_credentials=True,         # 쿠키·인증헤더 허용
)

# ─── Static 파일 서빙 ───────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── REST API 라우트 등록 ────────────────────────────
app.include_router(votes_router)
app.include_router(health_router)

# ─── WebSocket 라우트 등록 ──────────────────────────
app.include_router(ws_router)
app.include_router(chat_ws_router)

# ─── index.html 반환 ─────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    html = (Path(__file__).parent / "static" / "index.html")\
               .read_text(encoding="utf-8")
    return HTMLResponse(html)