import os
from sqlalchemy import select

from src.tasks.celery_app import app
from src.crawler.busan_gov import BusanGovCrawler
from src.crawler.busan_youth import BusanYouthCrawler
from src.pipeline.normalizer import normalize
from src.pipeline.chunker import chunk_posting
from src.pipeline.embedder import OpenAIEmbedder, embed_chunks
from src.db.models import Posting, Chunk
from src.api.deps import get_db_session

SOURCES = {
    "busan_gov": BusanGovCrawler,
    "busan_youth": BusanYouthCrawler,
}


def run_pipeline(raw_items):
    api_key = os.environ.get("OPENAI_API_KEY", "")
    embedder = OpenAIEmbedder(api_key=api_key)
    saved = 0
    skipped = 0

    with get_db_session() as session:
        for raw in raw_items:
            normalized = normalize(raw)
            existing = session.execute(
                select(Posting).where(Posting.url == normalized["url"])
            ).scalar_one_or_none()

            if existing and existing.raw_hash == normalized["raw_hash"]:
                skipped += 1
                continue

            chunks = chunk_posting(normalized)
            embed_chunks(chunks, embedder)

            if existing:
                session.delete(existing)
                session.flush()

            posting = Posting(
                source=normalized["source"],
                url=normalized["url"],
                title=normalized["title"],
                organization=normalized.get("organization"),
                category=normalized.get("category"),
                region=normalized.get("region"),
                eligibility_text=normalized.get("eligibility_text"),
                benefits_text=normalized.get("benefits_text"),
                requirements_text=normalized.get("requirements_text"),
                apply_method_text=normalized.get("apply_method_text"),
                deadline_at=normalized.get("deadline_at"),
                raw_hash=normalized["raw_hash"],
            )
            session.add(posting)
            session.flush()

            for chunk in chunks:
                session.add(Chunk(
                    posting_id=posting.id,
                    chunk_type=chunk["chunk_type"],
                    content=chunk["content"],
                    source_span_start=chunk.get("source_span_start"),
                    source_span_end=chunk.get("source_span_end"),
                    embedding=chunk.get("embedding"),
                ))

            saved += 1

    return {"saved": saved, "skipped": skipped}


def crawl_source(source):
    if source not in SOURCES:
        raise ValueError(f"알 수 없는 소스: {source}")

    crawler = SOURCES[source]()
    raw_items = []

    page = 1
    while True:
        urls = crawler.fetch_list(page=page)
        if not urls:
            break
        for url in urls:
            html = crawler.fetch_detail(url)
            if html:
                parsed = crawler.parse_detail(html)
                parsed["url"] = url
                raw_items.append(parsed)
        page += 1
        if page > 5:
            break

    result = run_pipeline(raw_items)
    result["source"] = source
    return result


def crawl_all():
    return [crawl_source(source) for source in SOURCES]


@app.task(name="src.tasks.crawler_tasks.crawl_all_task", bind=True, max_retries=3)
def crawl_all_task(self):
    try:
        return crawl_all()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@app.task(name="src.tasks.crawler_tasks.crawl_source_task", bind=True, max_retries=3)
def crawl_source_task(self, source):
    try:
        return crawl_source(source)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
