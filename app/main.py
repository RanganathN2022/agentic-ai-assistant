from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routes import chat, upload
from app.db.memory_store import init_db

init_db()

app = FastAPI(title="Enterprise Agentic AI")

app.include_router(chat.router)
app.include_router(upload.router)

# ✅ Redirect root to docs
@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/docs")