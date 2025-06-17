import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime
from uuid import uuid4

from app.schemas import VoteCreate, VoteSummary, VoteStatus, VoteOptions, OptionCount
from app.manager import manager

router = APIRouter()
DATA_FILE = Path(__file__).parent.parent / "votes_data.json"

# in-memory + 파일 로드
try:
    votes: Dict[str, dict] = json.loads(DATA_FILE.read_text(encoding="utf-8"))
except FileNotFoundError:
    votes = {}

def save_votes():
    DATA_FILE.write_text(
        json.dumps(votes, default=str, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

@router.post("/votes")
async def create_vote(vote: VoteCreate):
    vid = str(uuid4())
    votes[vid] = {
        "title":       vote.title,
        "description": vote.description,
        "options":     vote.options,
        "counts":      {o: 0 for o in vote.options},
        "created_at":  datetime.utcnow(),
        "active":      True
    }
    save_votes()

    await manager.broadcast({
        "type":        "vote_created",
        "vote_id":     vid,
        "title":       vote.title,
        "description": vote.description,
        "options":     vote.options
    })

    return {"status": "ok", "vote_id": vid}

@router.get("/votes", response_model=List[VoteSummary])
async def list_votes():
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
            status       = status
        ))
    return summaries

@router.get("/votes/{vote_id}/options", response_model=VoteOptions)
async def get_vote_options_detail(vote_id: str):
    if vote_id not in votes:
        raise HTTPException(404, detail="vote_id를 찾을 수 없습니다.")
    data = votes[vote_id]
    counts = data["counts"]
    total  = sum(counts.values())

    options = [
        OptionCount(option=opt, votes=counts.get(opt, 0))
        for opt in data["options"]
    ]

    return VoteOptions(
        options     = options,
        total_votes = total
    )