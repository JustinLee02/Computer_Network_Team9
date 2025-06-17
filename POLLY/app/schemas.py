from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class VoteStatus(str, Enum):
    ongoing = "진행중"
    finished = "종료"

class VoteCreate(BaseModel):
    title: str = Field(..., min_length=1, description="투표 주제")
    description: Optional[str] = Field(None, max_length=500, description="투표 설명 (선택)")
    options: List[str] = Field(..., description="선택지 리스트 (2~8개)")
    is_public: bool = Field(..., description="공개 여부 (False면 비공개)")
    password: str = Field(..., min_length=4, max_length=20, description="투표 비밀번호 (필수)")

    @validator("options")
    def validate_options(cls, v):
        if not (2 <= len(v) <= 8):
            raise ValueError("선택지는 2개 이상, 8개 이하이어야 합니다.")
        for opt in v:
            if not opt.strip():
                raise ValueError("선택지는 빈 문자열일 수 없습니다.")
        return v

class VoteSummary(BaseModel):
    vote_id: str
    title: str
    description: Optional[str]
    total_votes: int
    created_at: datetime
    option_count: int
    status: VoteStatus
    is_public: bool

class OptionCount(BaseModel):
    option: str
    votes: int

class VoteOptions(BaseModel):
    options: List[OptionCount]
    total_votes: int

class WSMessage(BaseModel):
    type: str
    payload: Dict[str, Any]