from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from agent.graph import compiled_graph
from fastapi.middleware.cors import CORSMiddleware
from agent import kb

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your Vercel/ChatGPT frontend URL before the demo
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
_recent_logs: list[dict] = []  # in-memory ring buffer — fine for a demo

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    msg = (await request.json())["message"]
    result = compiled_graph.invoke({
        "chat_id": str(msg["chat"]["id"]),
        "question": msg["text"],
    })
    _recent_logs.append({
        "chat_id": result["chat_id"],
        "question": result["question"],
        "trace": result["trace"],
    })
    _recent_logs[:] = _recent_logs[-50:]
    return {"ok": True}

@app.on_event("startup")
async def startup():
    kb.refresh_index()

@app.get("/logs")
async def get_logs():
    return {"logs": _recent_logs}