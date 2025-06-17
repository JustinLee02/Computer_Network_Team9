from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    """투표용 + 채팅용 WebSocket 연결 관리"""
    def __init__(self):
        self.active_votes: Dict[int, WebSocket] = {}
        self.active_chats: Dict[str, WebSocket] = {}

    # --- 투표용 메서드 ---
    async def connect_vote(self, websocket: WebSocket):
        await websocket.accept()
        self.active_votes[id(websocket)] = websocket

    async def broadcast_vote(self, message: dict):
        for ws_id, ws in list(self.active_votes.items()):
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                self.active_votes.pop(ws_id, None)

    # --- 채팅용 메서드 (nickname 기반) ---
    async def connect_chat(self, nickname: str, websocket: WebSocket):
        await websocket.accept()
        self.active_chats[nickname] = websocket
        print(f"{nickname} 채팅 연결됨")

    async def broadcast_chat(self, message: str):
        for nick, ws in list(self.active_chats.items()):
            try:
                await ws.send_text(message)
            except WebSocketDisconnect:
                self.active_chats.pop(nick, None)
                print(f"{nick} 채팅 연결 해제")

    def disconnect_chat(self, nickname: str):
        if nickname in self.active_chats:
            del self.active_chats[nickname]
            print(f"{nickname} 채팅 연결 해제")

# 전역 매니저 인스턴스
manager = ConnectionManager()