import base64
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent import IrisAgent
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware


load_dotenv()

app = FastAPI()

class NgrokMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

app.add_middleware(NgrokMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

agent = IrisAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent.start()
    print("Iris ready")
    yield
    await agent.close()

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status":"Iris is ready"}


@app.get("/novnc", response_class=HTMLResponse)
async def novnc():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * { margin: 0; padding: 0; }
            body { background: #000; overflow: hidden; }
            iframe { 
                width: 100vw; 
                height: 100vh; 
                border: none; 
                display: block;
            }
        </style>
    </head>
    <body>
        <iframe src="http://localhost:6080/vnc.html?autoconnect=true&reconnect=true&resize=scale&show_dot=true&password="></iframe>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Frontend connected")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "task":
                task = message.get("task","")
                print(f"Recieved task: {task}")

                await websocket.send_text(json.dumps({
                    "type":"status",
                    "message":f"Starting task: {task}"
                }))

                async def on_step(step_data):
                    ss = base64.b64encode(step_data["screenshot"]).decode("utf-8")

                    await websocket.send_text(json.dumps({
                        "type":"step",
                        "step":step_data["step"],
                        "thought":step_data.get("thought",""),
                        "action":step_data.get("action",""),
                        "result":step_data.get("result",""),
                        "screenshot":ss
                    }))

                result = await agent.run_task(task, on_step= on_step)

                await websocket.send_text(json.dumps({
                    "type":"done",
                    "result":result
                }))

            elif message.get("type") == "stop":
                agent.stop()
                await websocket.send_text(json.dumps({
                    "type":"status",
                    "message":"Agent stopped"
                }))

    except WebSocketDisconnect:
        print("Frontend disconnected")
        agent.stop()


