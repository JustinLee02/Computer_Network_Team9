from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any

class ConnectionManager:
    """투표용 + 채팅용 WebSocket 연결 관리"""
    def __init__(self):
        # vote WS 는 websocket 객체 아이디를 키로
        self.active_votes: Dict[int, WebSocket] = {}
        # chat WS 는 nickname 을 키로
        self.active_chats: Dict[str, WebSocket] = {}

    # --- 투표용 메서드 ---
    async def connect_vote(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_votes[id(websocket)] = websocket

    def disconnect_vote(self, websocket: WebSocket) -> None:
        """연결 해제 시 호출"""
        self.active_votes.pop(id(websocket), None)

    async def broadcast_vote(self, message: Any) -> None:
        """모든 투표 WS 클라이언트에 JSON 전송"""
        for ws_id, ws in list(self.active_votes.items()):
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                # 끊긴 연결은 정리
                self.disconnect_vote(ws)

    # --- 채팅용 메서드 ---
    async def connect_chat(self, nickname: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_chats[nickname] = websocket

    def disconnect_chat(self, nickname: str) -> None:
        self.active_chats.pop(nickname, None)

    async def broadcast_chat(self, message: str) -> None:
        """모든 채팅 WS 클라이언트에 텍스트 전송"""
        for nick, ws in list(self.active_chats.items()):
            try:
                await ws.send_text(message)
            except WebSocketDisconnect:
                self.disconnect_chat(nick)

# 전역 매니저
manager = ConnectionManager()