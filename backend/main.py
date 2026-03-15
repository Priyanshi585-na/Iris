import httpx
import base64
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent import IrisAgent
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse, Response
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
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:6080/vnc.html",
            headers={"ngrok-skip-browser-warning": "true"}
        )
        content = response.text
        # Fix relative URLs to point back through our proxy
        content = content.replace('src="', 'src="/novnc-static/')
        content = content.replace('href="', 'href="/novnc-static/')
        return HTMLResponse(content)

@app.get("/novnc-static/{path:path}")
async def novnc_static(path: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:6080/{path}",
            headers={"ngrok-skip-browser-warning": "true"}
        )
        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "text/plain")
        )




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


