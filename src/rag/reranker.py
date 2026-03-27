import math


def _bm25_score(query, text, k1=1.5, b=0.75, avg_len=50):
    query_terms = query.split()
    tokens = text.split()
    doc_len = len(tokens)
    freq_map = {}
    for t in tokens:
        freq_map[t] = freq_map.get(t, 0) + 1

    score = 0.0
    for term in query_terms:
        f = freq_map.get(term, 0)
        idf = math.log(2.0)
        tf = (f * (k1 + 1)) / (f + k1 * (1 - b + b * doc_len / avg_len))
        score += idf * tf
    return score


class Reranker:
    def rerank(self, query, chunks, top_k=None):
        scored = []
        for chunk in chunks:
            score = _bm25_score(query, chunk.get("content", ""))
            scored.append({**chunk, "rerank_score": score})
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        if top_k is not None:
            scored = scored[:top_k]
        return scored
