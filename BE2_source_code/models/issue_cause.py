from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class IssueCause(Base):
    __tablename__ = "issue_causes"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    cause_text = Column(String, nullable=False)
    cause_order = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("issue_id", "cause_order", name="uq_issue_cause_order"),
    )

    issue = relationship("Issue", back_populates="causes")
