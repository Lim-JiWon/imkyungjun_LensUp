from sqlalchemy import Column, Integer, ForeignKey, Text, String
from sqlalchemy.orm import relationship

from database import Base


class IssueSummary(Base):
    __tablename__ = "issue_summaries"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    summary_type = Column(String(50), nullable=False)
    summary_text = Column(Text, nullable=False)

    issue = relationship("Issue", back_populates="summaries")
