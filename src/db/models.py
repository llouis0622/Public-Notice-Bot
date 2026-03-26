from sqlalchemy import (
    Column, String, Text, DateTime, Integer,
    ForeignKey, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()

CATEGORIES = ("장학금", "인턴", "교육", "정책", "채용", "대외활동")
CHUNK_TYPES = ("지원자격", "신청방법", "혜택", "마감일", "기타")


class Posting(Base):
    __tablename__ = "postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(100), nullable=False)
    url = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    organization = Column(String(200))
    category = Column(String(20))
    region = Column(String(100))
    eligibility_text = Column(Text)
    benefits_text = Column(Text)
    requirements_text = Column(Text)
    apply_method_text = Column(Text)
    deadline_at = Column(DateTime(timezone=True))
    start_at = Column(DateTime(timezone=True))
    end_at = Column(DateTime(timezone=True))
    raw_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("url", name="uq_postings_url"),
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    posting_id = Column(UUID(as_uuid=True), ForeignKey("postings.id", ondelete="CASCADE"), nullable=False)
    chunk_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    source_span_start = Column(Integer)
    source_span_end = Column(Integer)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())