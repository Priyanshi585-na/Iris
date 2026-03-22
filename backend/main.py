import base64
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent import IrisAgent

load_dotenv()

agent = IrisAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent.start()
    print("Iris ready")
    yield
    await agent.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "Iris is ready"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Frontend connected")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "task":
                task = message.get("task", "")
                print(f"Recieved task: {task}")

                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": f"Starting task: {task}"
                }))

                async def on_step(step_data):
                    ss = base64.b64encode(step_data["screenshot"]).decode("utf-8")
                    await websocket.send_text(json.dumps({
                        "type": "step",
                        "step": step_data["step"],
                        "thought": step_data.get("thought", ""),
                        "action": step_data.get("action", ""),
                        "result": step_data.get("result", ""),
                        "screenshot": ss
                    }))

                result = await agent.run_task(task, on_step=on_step)

                await websocket.send_text(json.dumps({
                    "type": "done",
                    "result": result
                }))

            elif message.get("type") == "stop":
                agent.stop()
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": "Agent stopped"
                }))

    except WebSocketDisconnect:
        print("Frontend disconnected")
        agent.stop()