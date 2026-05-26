from database import Base, engine

from models.issue import Issue
from models.issue_summary import IssueSummary
from models.issue_keyword import IssueKeyword
from models.issue_cause import IssueCause
from models.issue_keyword_trend import IssueKeywordTrend
from models.issue_search_alias import IssueSearchAlias
from models.dashboard_region_ranking import DashboardRegionRanking
from models.dashboard_extra_snapshot import DashboardExtraSnapshot


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ tables created successfully")


if __name__ == "__main__":
    create_tables()
