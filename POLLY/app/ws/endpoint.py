# app/ws/endpoint.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.schemas import WSMessage
from app.manager import manager
from app.api.votes import votes, save_votes   # ← 추가

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            msg  = WSMessage.parse_obj(data)

            if msg.type == "cast_vote":
                vid, choice = msg.payload["vote_id"], msg.payload["choice"]
                if vid in votes and choice in votes[vid]["counts"]:
                    votes[vid]["counts"][choice] += 1
                    save_votes()   # ← 변경된 counts 파일에도 저장

                    counts = votes[vid]["counts"]
                    total  = sum(counts.values())
                    await manager.broadcast({
                        "type":        "vote_update",
                        "vote_id":     vid,
                        "counts":      counts,
                        "total_votes": total
                    })

            # chat, memo 처리 생략…
    except WebSocketDisconnect:
        manager.disconnect(ws)