from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="Faceted Search API", version="1.0")

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

@app.get("/health")
async def health():
    return {"status": "ok"}