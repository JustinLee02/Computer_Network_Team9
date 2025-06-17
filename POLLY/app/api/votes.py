import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List
from datetime import datetime
from uuid import uuid4

from app.schemas import (
    VoteCreate,
    VoteSummary,
    VoteStatus,
    VoteOptions,
    OptionCount
)
from app.manager import manager

router = APIRouter()
DATA_FILE = Path(__file__).parent.parent / "votes_data.json"

# in-memory 상태 + JSON 파일 로드
try:
    votes: Dict[str, dict] = json.loads(
        DATA_FILE.read_text(encoding="utf-8")
    )
except FileNotFoundError:
    votes = {}

def save_votes():
    DATA_FILE.write_text(
        json.dumps(votes, default=str, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

@router.post("/votes")
async def create_vote(vote: VoteCreate):
    """
    투표 생성:
    - title, description, options, is_public, password 모두 필수
    - 비공개 투표에는 password가 반드시 설정돼야 함
    """
    vid = str(uuid4())
    votes[vid] = {
        "title":       vote.title,
        "description": vote.description,
        "options":     vote.options,
        "counts":      {o: 0 for o in vote.options},
        "created_at":  datetime.utcnow(),
        "active":      True,
        "is_public":   vote.is_public,
        "password":    vote.password
    }
    save_votes()

    # WebSocket 브로드캐스트 (생성 알림)
    await manager.broadcast({
        "type":        "vote_created",
        "vote_id":     vid,
        "title":       vote.title,
        "description": vote.description,
        "options":     vote.options,
        "is_public":   vote.is_public
    })

    return {"status": "ok", "vote_id": vid}

@router.get("/votes", response_model=List[VoteSummary])
async def list_votes():
    """
    모든 투표 목록 요약 조회:
    - vote_id, title, description, total_votes, created_at, option_count, status, is_public 반환
    """
    summaries: List[VoteSummary] = []
    for vid, data in votes.items():
        total = sum(data["counts"].values())
        status = VoteStatus.ongoing if data["active"] else VoteStatus.finished

        summaries.append(VoteSummary(
            vote_id      = vid,
            title        = data["title"],
            description  = data["description"],
            total_votes  = total,
            created_at   = data["created_at"],
            option_count = len(data["options"]),
            status       = status,
            is_public    = data.get("is_public", True)
        ))
    return summaries

@router.get(
    "/votes/{vote_id}/options",
    response_model=VoteOptions
)
async def get_vote_options_detail(
    vote_id: str,
    password: str = Query(
        ...,
        min_length=1,
        description="비공개 투표일 경우엔 생성 시 설정한 비밀번호, 공개 투표면 어떤 값이든 상관없음"
    )
):
    """
    특정 투표의 옵션별 득표 수와 전체 투표 수를 반환.
    - 공개 투표: password 값 무시
    - 비공개 투표: password가 일치해야 조회 가능
    """
    if vote_id not in votes:
        raise HTTPException(status_code=404, detail="vote_id를 찾을 수 없습니다.")

    data = votes[vote_id]

    # 비공개 투표일 때만 password 검증
    if not data.get("is_public", True):
        if password != data.get("password"):
            raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다.")

    counts = data["counts"]          # { option_text: count }
    total  = sum(counts.values())

    options = [
        OptionCount(option=opt, votes=counts.get(opt, 0))
        for opt in data["options"]
    ]

    return VoteOptions(options=options, total_votes=total)