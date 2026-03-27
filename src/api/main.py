from fastapi import FastAPI
from src.api.routes import chat, postings, crawl, recommend

app = FastAPI(title="Public Notice Bot")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(chat.router)
app.include_router(postings.router)
app.include_router(crawl.router)
app.include_router(recommend.router)
