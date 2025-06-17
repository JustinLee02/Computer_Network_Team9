import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.ws.manager import manager

router = APIRouter()

@router.websocket("/ws/chat/{user_id}")
async def chat_ws(
    websocket: WebSocket,
    user_id: str,
    nickname: str = Query(...)
):
    # 1) 연결
    await manager.connect_chat(user_id, websocket)
    print(f"{nickname} 접속")

    try:
        while True:
            data = await websocket.receive_text()
            msg  = json.loads(data)
            if msg.get("type") == "chat_message":
                text = msg.get("message", "").strip()
                if text:
                    payload = {
                        "type": "chat_message",
                        "data": {
                            "nickname":  nickname,
                            "message":   text,
                            "timestamp": datetime.now().strftime("%H:%M")
                        }
                    }
                    # 2) 브로드캐스트
                    await manager.broadcast_chat(
                        json.dumps(payload, ensure_ascii=False)
                    )
                    print(f"{nickname}: {text}")
    except WebSocketDisconnect:
        print(f"{nickname} 연결 해제")
        manager.disconnect_chat(user_id)