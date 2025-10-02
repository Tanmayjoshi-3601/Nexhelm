from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

# Create FastAPI instance
app = FastAPI(title="Nexhelm POC")

# CORS Middleware - allows react frontend (which runs on port 3000) to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


class ConnectionManager:
    """Manages Websocket connections"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self,websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        "Disconnect a client"
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_message(self, message: str, websocket: WebSocket):
        """ Send message to a specific client"""
        await websocket.send_text(message)
    
    async def broadcast(self, message:str):
        for connection in self.active_connections:
            await connection.send_text(message)
    

# create a connection manager
manager = ConnectionManager()

@app.get("/")
def read_root():
    "Test endpoint to verify server is running"
    return {"message":"Nexhelm POC running!"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    # accept connection
    await manager.connect(websocket)

    try:
        while True:
            # wait for message from client
            data = await websocket.recieve_text()
            print(f"Recieved: {data}")

            # echo back to sender
            await manager.send_message(f"Echo: {data}", websocket)

            # broadcast to all clients
            await manager.broadcast(f"Someone said {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected")


@app.get("/health")
def health_check():
    "Health check endpoint"
    return {"status":"healthy"}

if __name__ == "__main__":
    # run the server
    uvicorn.run(
        "main:app", # tells uvicorn to run the 'app' from main.py
        host = '0.0.0.0',
        port = 8001,
        reload = True
    )