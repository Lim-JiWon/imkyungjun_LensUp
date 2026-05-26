from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class RawComplaint(Base):
    __tablename__ = "raw_complaints"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)  # 데이터 출처
    external_id = Column(String(255), unique=True, nullable=False)  # 공공데이터 원본 ID
    title = Column(String(255), nullable=False)  # 제목
    content = Column(Text, nullable=True)  # 본문/설명
    region = Column(String(100), nullable=True)  # 지역
    category = Column(String(100), nullable=True)  # 민원/이슈 카테고리
    status = Column(String(50), default="collected")  # collected / processed
    occurred_at = Column(DateTime, nullable=True)  # 실제 발생 시각
    collected_at = Column(DateTime(timezone=True), server_default=func.now())  # 수집 시각
