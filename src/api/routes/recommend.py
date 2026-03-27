from fastapi import APIRouter
from pydantic import BaseModel
from src.api.deps import get_db_session
from src.api.routes.postings import fetch_postings
from src.recommender.ranker import rank_postings

router = APIRouter()


class UserProfile(BaseModel):
    age: int = None
    categories: list = []
    region: str = None


@router.post("/recommend")
def recommend(profile: UserProfile, limit: int = 20):
    with get_db_session() as session:
        postings = fetch_postings(session, limit=200)
    ranked = rank_postings(postings, profile.model_dump())
    return ranked[:limit]
