from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class IssueSearchAlias(Base):
    __tablename__ = "issue_search_aliases"

    __table_args__ = (
        UniqueConstraint(
            "issue_id",
            "alias",
            name="uq_issue_search_alias_issue_id_alias",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    issue_id = Column(
        Integer,
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alias = Column(String(255), nullable=False, index=True)

    alias_order = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    issue = relationship("Issue")
