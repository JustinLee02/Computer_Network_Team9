from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    """투표용 + 채팅용 WebSocket 연결 관리"""
    def __init__(self):
        self.active_votes: Dict[str, WebSocket] = {}
        self.active_chats: Dict[str, WebSocket] = {}

    # --- 투표용 메서드 (기존) ---
    async def connect_vote(self, websocket: WebSocket):
        await websocket.accept()
        self.active_votes[id(websocket)] = websocket

    async def broadcast_vote(self, message: dict):
        for ws in list(self.active_votes.values()):
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                self.active_votes.pop(id(ws), None)

    # --- 채팅용 메서드 ---
    async def connect_chat(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_chats[user_id] = websocket

    async def broadcast_chat(self, message_json: str):
        for user_id, ws in list(self.active_chats.items()):
            try:
                await ws.send_text(message_json)
            except WebSocketDisconnect:
                self.active_chats.pop(user_id, None)

    def disconnect_chat(self, user_id: str):
        self.active_chats.pop(user_id, None)

manager = ConnectionManager()