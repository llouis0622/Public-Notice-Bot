from datetime import datetime, timezone

CATEGORY_BONUS = 20.0
REGION_BONUS = 10.0
DEADLINE_MAX_BONUS = 30.0
DEADLINE_WINDOW_DAYS = 30


def score_posting(posting, profile, now=None):
    if now is None:
        now = datetime.now(timezone.utc)

    deadline = posting.get("deadline_at")
    if deadline:
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if deadline < now:
            return 0

    score = 10.0

    preferred = profile.get("categories") or []
    if posting.get("category") in preferred:
        score += CATEGORY_BONUS

    if profile.get("region") and posting.get("region") == profile["region"]:
        score += REGION_BONUS

    if deadline:
        days_left = (deadline - now).days
        if 0 <= days_left <= DEADLINE_WINDOW_DAYS:
            urgency = (DEADLINE_WINDOW_DAYS - days_left) / DEADLINE_WINDOW_DAYS
            score += DEADLINE_MAX_BONUS * urgency

    return score


def rank_postings(postings, profile, now=None):
    scored = []
    for posting in postings:
        s = score_posting(posting, profile, now=now)
        scored.append({**posting, "score": s})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
