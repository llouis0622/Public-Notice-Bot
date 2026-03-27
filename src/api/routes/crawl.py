from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

KNOWN_SOURCES = {"busan_gov", "busan_youth"}


def trigger_crawl(sources):
    return {"queued": sources}


class CrawlRequest(BaseModel):
    sources: list


@router.post("/crawl", status_code=202)
def crawl(req: CrawlRequest):
    unknown = [s for s in req.sources if s not in KNOWN_SOURCES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"알 수 없는 소스: {unknown}")
    result = trigger_crawl(req.sources)
    return result
