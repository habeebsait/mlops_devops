from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phishing Detection Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="project/src/dashboard/static"), name="static")

# Store active websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

# Data models
class MetricUpdate(BaseModel):
    type: str  # 'metric' or 'alert'
    data: dict

@app.get("/")
async def get_dashboard():
    return FileResponse("project/src/dashboard/static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/metrics")
async def receive_metrics(update: MetricUpdate):
    """
    Endpoint for the monitor to push updates.
    """
    await manager.broadcast(update.dict())
    return {"status": "received"}

class ManualCheckRequest(BaseModel):
    text: str

@app.post("/api/check")
async def manual_check(request: ManualCheckRequest):
    """
    Heuristic check for demo purposes.
    """
    text = request.text.lower()
    suspicious_keywords = ['login', 'verify', 'account', 'update', 'security', 'confirm', 'bank', 'alert']
    
    score = 0
    for word in suspicious_keywords:
        if word in text:
            score += 1
            
    if score > 0:
        return {"result": "PHISHING", "confidence": min(0.6 + (score * 0.1), 0.99)}
    else:
        return {"result": "SAFE", "confidence": 0.95}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
