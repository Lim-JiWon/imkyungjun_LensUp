from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class IssueKeywordTrend(Base):
    __tablename__ = "issue_keyword_trends"
    __table_args__ = (
        UniqueConstraint(
            "issue_id",
            "trend_date",
            "trend_order",
            name="uq_issue_keyword_trends_issue_date_order",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    trend_date = Column(String(20), nullable=False)
    trend_value = Column(Integer, nullable=False)
    trend_order = Column(Integer, nullable=False, default=0)

    issue = relationship("Issue", back_populates="keyword_trends")
