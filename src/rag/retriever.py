from src.db.vector_store import search_similar_chunks


class Retriever:
    def __init__(self, session, embedder):
        self.session = session
        self.embedder = embedder

    def search(self, query, top_k=10):
        vector = self.embedder.embed(query)
        rows = search_similar_chunks(self.session, vector, top_k=top_k)
        return [dict(row._mapping) for row in rows]
