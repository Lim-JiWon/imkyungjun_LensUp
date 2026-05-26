from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class IssueKeyword(Base):
    __tablename__ = "issue_keywords"
    __table_args__ = (
        UniqueConstraint("issue_id", "keyword_type", "keyword_order", name="uq_issue_keywords_issue_type_order"),
    )

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    keyword_type = Column(String(50), nullable=False, default="keyword")
    keyword_order = Column(Integer, nullable=False, default=0)

    issue = relationship("Issue", back_populates="keywords")
