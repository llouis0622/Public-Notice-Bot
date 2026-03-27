import hashlib
import re
from datetime import datetime


CATEGORY_KEYWORDS = {
    "장학금": ["장학", "장학금"],
    "인턴": ["인턴", "창업", "스타트업"],
    "교육": ["교육", "강의", "연수", "훈련", "과정"],
    "정책": ["정책", "지원사업", "지원 사업", "복지"],
    "채용": ["채용", "취업", "구인", "모집"],
    "대외활동": ["대외활동", "봉사", "서포터즈", "공모"],
}

SECTION_LABELS = {
    "eligibility_text": ["지원자격", "신청자격", "지원 자격", "참가자격"],
    "benefits_text": ["지원내용", "지원 내용", "혜택", "지원금액", "지원금"],
    "apply_method_text": ["신청방법", "신청 방법", "접수방법", "참가방법"],
    "requirements_text": ["제출서류", "제출 서류", "구비서류"],
}

DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",
    r"\d{4}\.\d{2}\.\d{2}",
    r"\d{4}/\d{2}/\d{2}",
    r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일",
]


def compute_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()


def is_duplicate(raw_hash, existing_hashes):
    return raw_hash in existing_hashes


def normalize(raw):
    content = raw.get("raw_content") or ""
    result = {
        "source": raw.get("source"),
        "url": raw.get("url"),
        "title": raw.get("title"),
        "organization": raw.get("organization"),
        "region": "부산",
        "raw_hash": compute_hash(content),
        "deadline_at": None,
        "start_at": None,
        "end_at": None,
        "eligibility_text": None,
        "benefits_text": None,
        "apply_method_text": None,
        "requirements_text": None,
        "category": None,
    }

    deadline_raw = raw.get("deadline_at") or _extract_deadline(content)
    result["deadline_at"] = _parse_date(deadline_raw)

    for field, labels in SECTION_LABELS.items():
        result[field] = _extract_section(content, labels)

    result["category"] = _detect_category(raw.get("title") or "", content)

    return result


def _extract_deadline(content):
    for label in ["신청기간", "접수기간", "마감일", "마감"]:
        idx = content.find(label)
        if idx == -1:
            continue
        snippet = content[idx:idx + 80]
        dates = _find_dates(snippet)
        if len(dates) >= 2:
            return dates[1]
        if dates:
            return dates[0]
    return None


def _find_dates(text):
    results = []
    for pattern in DATE_PATTERNS:
        for m in re.finditer(pattern, text):
            results.append((m.start(), m.group()))
    results.sort(key=lambda x: x[0])
    return [v for _, v in results]


def _parse_date(value):
    if not value:
        return None
    value = re.sub(r"[년월]", "-", value).replace("일", "").replace(" ", "").replace(".", "-").replace("/", "-")
    value = re.sub(r"-+", "-", value).strip("-")
    for fmt in ("%Y-%m-%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def _extract_section(content, labels):
    lines = content.split("\n")
    for i, line in enumerate(lines):
        for label in labels:
            if label in line:
                colon_idx = line.find(":")
                if colon_idx != -1:
                    value = line[colon_idx + 1:].strip()
                    if value:
                        return value
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
    return None


def _detect_category(title, content):
    combined = title + " " + content
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return category
    return None
