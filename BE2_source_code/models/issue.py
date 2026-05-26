from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship
from models.issue_keyword_trend import IssueKeywordTrend
from database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_key = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=True)
    target = Column(String, nullable=True)
    status = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    complaint_count = Column(Integer, nullable=True)
    top_keyword = Column(String, nullable=True)
    category = Column(String(100), nullable=True)
    batch_id = Column(String, nullable=True)
    

    summaries = relationship(
        "IssueSummary",
        back_populates="issue",
        cascade="all, delete-orphan"
    )
    keywords = relationship(
        "IssueKeyword",
        back_populates="issue",
        cascade="all, delete-orphan"
    )
    causes = relationship(
        "IssueCause",
        back_populates="issue",
        cascade="all, delete-orphan"
    )
    keyword_trends = relationship(
    "IssueKeywordTrend",
    back_populates="issue",
    cascade="all, delete-orphan",
    )
