import os
from contextlib import contextmanager
from src.db.vector_store import get_engine, get_session_factory

_engine = None
_session_factory = None


def _get_factory():
    global _engine, _session_factory
    if _session_factory is None:
        db_url = os.environ.get("DATABASE_URL", "postgresql://notice_user:notice_pass@localhost:5433/public_notice_bot")
        _engine = get_engine(db_url)
        _session_factory = get_session_factory(_engine)
    return _session_factory


@contextmanager
def get_db_session():
    factory = _get_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_rag_pipeline():
    import os
    from openai import OpenAI
    from src.pipeline.embedder import OpenAIEmbedder
    from src.rag.retriever import Retriever
    from src.rag.reranker import Reranker
    from src.rag.generator import Generator

    api_key = os.environ.get("OPENAI_API_KEY", "")
    embedder = OpenAIEmbedder(api_key=api_key)
    client = OpenAI(api_key=api_key)

    class RAGPipeline:
        def __init__(self, session):
            self.retriever = Retriever(session=session, embedder=embedder)
            self.reranker = Reranker()
            self.generator = Generator(client=client)

        def answer(self, query, top_k=10, rerank_top_k=5):
            chunks = self.retriever.search(query, top_k=top_k)
            chunks = self.reranker.rerank(query, chunks, top_k=rerank_top_k)
            return self.generator.generate(query, chunks)

    with get_db_session() as session:
        return RAGPipeline(session)
