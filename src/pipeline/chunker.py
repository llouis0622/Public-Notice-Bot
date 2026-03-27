from src.db.models import CHUNK_TYPES

SECTION_MAP = {
    "지원자격": "eligibility_text",
    "신청방법": "apply_method_text",
    "혜택": "benefits_text",
    "마감일": None,
}


def chunk_posting(normalized):
    chunks = []
    raw = normalized.get("raw_content") or ""

    for chunk_type in CHUNK_TYPES:
        if chunk_type == "기타":
            continue
        if chunk_type == "마감일":
            deadline = normalized.get("deadline_at")
            if deadline:
                content = str(deadline)
                span = _find_span(raw, content)
                chunks.append(_make_chunk(chunk_type, content, span))
            continue
        field = SECTION_MAP.get(chunk_type)
        if field:
            text = normalized.get(field)
            if text:
                span = _find_span(raw, text)
                chunks.append(_make_chunk(chunk_type, text, span))

    if not chunks or not any(c["chunk_type"] != "기타" for c in chunks):
        content = raw or normalized.get("title") or ""
        chunks.append(_make_chunk("기타", content, (0, len(content))))
    elif raw:
        covered = set()
        for chunk in chunks:
            s, e = chunk["source_span_start"], chunk["source_span_end"]
            if s is not None and e is not None:
                covered.update(range(s, e))
        uncovered_parts = []
        start = None
        for i, ch in enumerate(raw):
            if i not in covered:
                if start is None:
                    start = i
            else:
                if start is not None:
                    segment = raw[start:i].strip()
                    if segment:
                        uncovered_parts.append((segment, start, i))
                    start = None
        if start is not None:
            segment = raw[start:].strip()
            if segment:
                uncovered_parts.append((segment, start, len(raw)))
        for segment, s, e in uncovered_parts:
            chunks.append(_make_chunk("기타", segment, (s, e)))

    return chunks


def _make_chunk(chunk_type, content, span):
    s, e = span if span else (None, None)
    return {
        "chunk_type": chunk_type,
        "content": content,
        "source_span_start": s,
        "source_span_end": e,
    }


def _find_span(raw, text):
    if not raw or not text:
        return (None, None)
    idx = raw.find(text)
    if idx == -1:
        return (None, None)
    return (idx, idx + len(text))
