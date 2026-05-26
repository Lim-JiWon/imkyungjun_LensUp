from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from database import Base


class DashboardExtraSnapshot(Base):
    __tablename__ = "dashboard_extra_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(String(255), nullable=True, index=True)
    date_from = Column(String(50), nullable=True)
    date_to = Column(String(50), nullable=True)
    target = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)

    payload_json = Column(JSONB, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
