import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from src.db.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://notice_user:notice_pass@localhost:5433/public_notice_bot")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(engine)

with engine.connect() as conn:
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_chunks_embedding
        ON chunks
        USING hnsw (embedding vector_cosine_ops)
    """))
    conn.commit()

print("Migration complete.")
