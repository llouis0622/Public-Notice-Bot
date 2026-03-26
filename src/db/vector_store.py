from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

def get_engine(db_url):
    return create_engine(db_url)

def get_session_factory(engine):
    return sessionmaker(bind=engine)

def enable_pgvector(engine):
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

def create_tables(engine):
    Base.metadata.create_all(engine)

def create_hnsw_index(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding
            ON chunks
            USING hnsw (embedding vector_cosine_ops)
        """))
        conn.commit()

def search_similar_chunks(session, query_embedding, top_k=10):
    vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
    result = session.execute(
        text("""
            SELECT id, posting_id, chunk_type, content,
                   source_span_start, source_span_end,
                   embedding <=> CAST(:vec AS vector) AS distance
            FROM chunks
            ORDER BY distance ASC
            LIMIT :top_k
        """),
        {"vec": vec_str, "top_k": top_k}
    )
    return result.fetchall()