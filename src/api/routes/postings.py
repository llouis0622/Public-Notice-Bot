from fastapi import APIRouter
from src.api.deps import get_db_session
from src.db.models import Posting, CATEGORIES
from sqlalchemy import select

router = APIRouter()

VALID_CATEGORIES = set(CATEGORIES)


def fetch_postings(session, category=None, limit=50):
    stmt = select(Posting).order_by(Posting.created_at.desc()).limit(limit)
    if category:
        stmt = stmt.where(Posting.category == category)
    rows = session.execute(stmt).scalars().all()
    return [
        {
            "id": str(r.id),
            "source": r.source,
            "title": r.title,
            "category": r.category,
            "deadline_at": r.deadline_at.isoformat() if r.deadline_at else None,
            "url": r.url,
        }
        for r in rows
    ]


@router.get("/postings")
def list_postings(category: str = None, limit: int = 50):
    with get_db_session() as session:
        return fetch_postings(session, category=category, limit=limit)
