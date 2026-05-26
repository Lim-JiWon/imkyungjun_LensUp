from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from database import Base


class DashboardRegionRanking(Base):
    __tablename__ = "dashboard_region_rankings"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(String(255), nullable=True, index=True)
    source = Column(String(255), nullable=True)
    target = Column(String(100), nullable=True)

    date_from = Column(String(50), nullable=True)
    date_to = Column(String(50), nullable=True)

    rank = Column(Integer, nullable=False)
    region = Column(String(100), nullable=False)
    count = Column(Integer, nullable=False)
    ratio = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
