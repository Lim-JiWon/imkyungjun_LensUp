import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import "../styles/DashboardPage.css";

const API_BASE_URL = "https://api.minwon-ai.kr";
const REFRESH_INTERVAL_MS = 30000;

function normalizeDashboardPayload(payload) {
  if (Array.isArray(payload)) return payload;

  if (Array.isArray(payload?.issues)) return payload.issues;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.items)) return payload.items;
  if (Array.isArray(payload?.dashboards)) return payload.dashboards;

  if (Array.isArray(payload?.data?.issues)) return payload.data.issues;
  if (Array.isArray(payload?.data?.results)) return payload.data.results;
  if (Array.isArray(payload?.data?.items)) return payload.data.items;

  return [];
}

function toNumber(value, defaultValue = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : defaultValue;
}

function getIssueScore(issue) {
  return toNumber(
    issue?.score ??
      issue?.risk_score ??
      issue?.signal_score ??
      issue?.issue_score ??
      issue?.match_score,
    0
  );
}

function getComplaintCount(issue) {
  return toNumber(
    issue?.complaint_count ??
      issue?.count ??
      issue?.total_count ??
      issue?.doc_count,
    0
  );
}

function getIssueTitle(issue) {
  return (
    issue?.title ||
    issue?.issue_title ||
    issue?.top_keyword ||
    issue?.keyword ||
    "제목 없는 민원 이슈"
  );
}

function getIssueStatus(issue) {
  return (
    issue?.signal_status ||
    issue?.status ||
    issue?.trend_direction ||
    "상태 확인 중"
  );
}

function getIssueSummary(issue) {
  return (
    issue?.summary ||
    issue?.signal_message ||
    issue?.forecast ||
    issue?.description ||
    "이 이슈에 대한 요약 정보가 아직 없습니다."
  );
}

function isStrongSignal(issue) {
  const score = getIssueScore(issue);
  const riskLevel = String(issue?.risk_level || "").toLowerCase();
  const status = String(issue?.signal_status || issue?.status || "");

  return (
    score >= 80 ||
    riskLevel.includes("critical") ||
    riskLevel.includes("high") ||
    status.includes("강한") ||
    status.includes("위험") ||
    status.includes("확산")
  );
}

function collectKeywords(issue) {
  const keywordSources = [
    issue?.rising_keywords,
    issue?.keywords,
    issue?.cluster_keywords,
    issue?.related_keywords,
    issue?.category_tags,
  ];

  const result = [];

  keywordSources.forEach((source) => {
    if (Array.isArray(source)) {
      source.forEach((item) => {
        if (typeof item === "string") {
          result.push(item);
        } else if (item?.keyword) {
          result.push(item.keyword);
        } else if (item?.name) {
          result.push(item.name);
        } else if (item?.word) {
          result.push(item.word);
        }
      });
    }
  });

  if (issue?.top_keyword) result.push(issue.top_keyword);
  if (issue?.category) result.push(issue.category);

  return [...new Set(result.filter(Boolean))];
}

function extractTrendValues(issue) {
  const trends = issue?.keyword_trends || issue?.trends || issue?.trend || [];

  if (!Array.isArray(trends)) return [];

  return trends
    .map((item) => {
      if (typeof item === "number") return item;
      return toNumber(item?.value ?? item?.count ?? item?.score, null);
    })
    .filter((value) => value !== null && Number.isFinite(value));
}

function getChartBars(issue) {
  const trendValues = extractTrendValues(issue);

  if (trendValues.length > 0) {
    const max = Math.max(...trendValues, 1);

    return trendValues.slice(-12).map((value) => {
      const height = Math.max(18, Math.round((value / max) * 100));
      return height;
    });
  }

  const score = Math.max(getIssueScore(issue), 10);

  return [34, 42, 38, 52, 47, 68, 58, 76, 88, Math.min(100, score + 10)];
}

function formatUpdatedTime(date) {
  if (!date) return "아직 갱신 전";

  return new Intl.DateTimeFormat("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

function DashboardPage() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  async function loadDashboardData(isRefresh = false) {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setErrorMessage("");

      const response = await fetch(`${API_BASE_URL}/dashboard`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`대시보드 API 오류: ${response.status}`);
      }

      const payload = await response.json();
      const issueList = normalizeDashboardPayload(payload);

      setIssues(issueList);
      setLastUpdated(new Date());
    } catch (error) {
      console.error("대시보드 데이터 불러오기 실패:", error);
      setErrorMessage(
        "백엔드에서 대시보드 데이터를 불러오지 못했습니다. API 연결 상태를 확인해주세요."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadDashboardData(false);

    const timer = setInterval(() => {
      loadDashboardData(true);
    }, REFRESH_INTERVAL_MS);

    return () => clearInterval(timer);
  }, []);

  const sortedIssues = useMemo(() => {
    return [...issues].sort((a, b) => {
      const scoreGap = getIssueScore(b) - getIssueScore(a);

      if (scoreGap !== 0) return scoreGap;

      return getComplaintCount(b) - getComplaintCount(a);
    });
  }, [issues]);

  const coreIssue = sortedIssues[0] || null;

  const dashboardStats = useMemo(() => {
    const totalIssues = issues.length;
    const strongSignalCount = issues.filter(isStrongSignal).length;

    const scoreList = issues
      .map(getIssueScore)
      .filter((score) => Number.isFinite(score) && score > 0);

    const averageScore =
      scoreList.length > 0
        ? Math.round(
            scoreList.reduce((sum, score) => sum + score, 0) / scoreList.length
          )
        : 0;

    const allKeywords = issues.flatMap(collectKeywords);
    const uniqueKeywords = [...new Set(allKeywords)];

    return [
      {
        label: "오늘 감지된 이슈",
        value: totalIssues,
        unit: "건",
        description: "백엔드 대시보드 데이터 기준",
      },
      {
        label: "강한 징후",
        value: strongSignalCount,
        unit: "건",
        description: "확산 가능성이 높은 이슈",
        active: true,
      },
      {
        label: "평균 위험도",
        value: averageScore,
        unit: "점",
        description: "전체 이슈 평균 점수",
      },
      {
        label: "급등 키워드",
        value: uniqueKeywords.length,
        unit: "개",
        description: "중복 제거된 주요 키워드",
      },
    ];
  }, [issues]);

  const coreIssueTitle = coreIssue
    ? getIssueTitle(coreIssue)
    : loading
      ? "대시보드 데이터 불러오는 중"
      : "표시할 핵심 이슈가 없습니다";

  const coreIssueScore = coreIssue ? Math.round(getIssueScore(coreIssue)) : 0;
  const coreIssueStatus = coreIssue ? getIssueStatus(coreIssue) : "대기 중";
  const coreIssueSummary = coreIssue ? getIssueSummary(coreIssue) : "";
  const coreIssueKeywords = coreIssue
    ? collectKeywords(coreIssue).slice(0, 6)
    : [];
  const chartBars = coreIssue ? getChartBars(coreIssue) : [20, 20, 20, 20, 20];

  const topIssues = sortedIssues.slice(0, 5);
  const strongIssues = sortedIssues.filter(isStrongSignal).slice(0, 4);

  return (
    <main className="dashboard-page">
      <div className="dashboard-container">
        <div className="dashboard-topbar">
          <div className="dashboard-logo-dot" />

          <div className="dashboard-topbar-actions">
            <button
              type="button"
              className="dashboard-refresh-button"
              onClick={() => loadDashboardData(true)}
              disabled={loading || refreshing}
            >
              {refreshing ? "갱신 중..." : "데이터 새로고침"}
            </button>

            <Link to="/" className="dashboard-back-link">
              메인으로 돌아가기
            </Link>
          </div>
        </div>

        {errorMessage && (
          <div className="dashboard-error-box">
            <strong>데이터 연결 오류</strong>
            <p>{errorMessage}</p>
          </div>
        )}

        <section className="dashboard-hero">
          <div className="dashboard-hero-text">
            <span className="dashboard-badge">분석 대시보드</span>

            <h1>
              민원 흐름을
              <br />
              한 화면에서 쉽게 확인하세요
            </h1>

            <p>
              백엔드에서 받아온 민원 이슈 데이터를 기준으로 오늘의 핵심 이슈,
              강한 징후, 평균 위험도, 급등 키워드를 자동 계산해 보여줍니다.
            </p>

            <div className="dashboard-live-row">
              <span className="dashboard-live-dot" />
              <span>
                마지막 갱신: {formatUpdatedTime(lastUpdated)}
                {refreshing ? " · 새 데이터 확인 중" : ""}
              </span>
            </div>

            <div className="dashboard-hero-actions">
              <Link to="/" className="dashboard-primary-button">
                메인 화면 보기
              </Link>
              <Link to="/complaints" className="dashboard-secondary-button">
                민원 보기
              </Link>
            </div>
          </div>

          <div className="dashboard-hero-card">
            <div className="hero-card-header">
              <span>오늘의 핵심 이슈</span>
              <strong>
                {isStrongSignal(coreIssue || {})
                  ? "강한 징후"
                  : coreIssueStatus}
              </strong>
            </div>

            <div className="hero-card-title">{coreIssueTitle}</div>

            <p className="hero-card-summary">
              {loading
                ? "백엔드에서 데이터를 불러오고 있습니다."
                : coreIssueSummary}
            </p>

            <div className="hero-chart">
              {chartBars.map((height, index) => (
                <span
                  key={`${height}-${index}`}
                  style={{ height: `${height}%` }}
                />
              ))}
            </div>

            <div className="hero-keyword-wrap">
              {coreIssueKeywords.length > 0 ? (
                coreIssueKeywords.map((keyword) => (
                  <span key={keyword}>#{keyword}</span>
                ))
              ) : (
                <span>키워드 없음</span>
              )}
            </div>

            <div className="hero-card-footer">
              <div>
                <span>위험도</span>
                <strong>{coreIssueScore}점</strong>
              </div>
              <div>
                <span>상태</span>
                <strong>{coreIssueStatus}</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="dashboard-stat-grid">
          {dashboardStats.map((stat) => (
            <article
              key={stat.label}
              className={`dashboard-stat-card ${stat.active ? "active" : ""}`}
            >
              <span>{stat.label}</span>
              <div>
                <strong>{loading ? "-" : stat.value}</strong>
                <em>{stat.unit}</em>
              </div>
              <p>{stat.description}</p>
            </article>
          ))}
        </section>

        <section className="dashboard-content-grid">
          <div className="dashboard-main-panel">
            <div className="dashboard-section-header">
              <span>실시간 이슈 목록</span>
              <h2>위험도 기준 주요 민원 이슈</h2>
            </div>

            {loading ? (
              <div className="dashboard-empty-box">
                대시보드 데이터를 불러오는 중입니다.
              </div>
            ) : topIssues.length > 0 ? (
              <div className="dashboard-issue-list">
                {topIssues.map((issue, index) => {
                  const keywords = collectKeywords(issue).slice(0, 4);
                  const score = Math.round(getIssueScore(issue));
                  const status = getIssueStatus(issue);

                  return (
                    <article
                      key={
                        issue.id ||
                        issue.issue_key ||
                        `${getIssueTitle(issue)}-${index}`
                      }
                      className="dashboard-issue-card"
                    >
                      <div className="issue-rank">{index + 1}</div>

                      <div className="issue-body">
                        <div className="issue-top-row">
                          <span className="issue-status">{status}</span>
                          <strong>{score}점</strong>
                        </div>

                        <h3>{getIssueTitle(issue)}</h3>
                        <p>{getIssueSummary(issue)}</p>

                        <div className="issue-chip-wrap">
                          {keywords.length > 0 ? (
                            keywords.map((keyword) => (
                              <span key={keyword}>#{keyword}</span>
                            ))
                          ) : (
                            <span>키워드 없음</span>
                          )}
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="dashboard-empty-box">
                백엔드에서 표시할 이슈가 아직 없습니다.
              </div>
            )}
          </div>

          <aside className="dashboard-side-panel">
            <div className="dashboard-section-header small">
              <span>연동 상태</span>
              <h2>백엔드 데이터 기준으로 자동 갱신됩니다</h2>
            </div>

            <div className="dashboard-sync-list">
              <div>
                <span>API</span>
                <strong>GET /dashboard</strong>
              </div>

              <div>
                <span>갱신 주기</span>
                <strong>30초</strong>
              </div>

              <div>
                <span>불러온 이슈</span>
                <strong>{issues.length}건</strong>
              </div>

              <div>
                <span>최근 갱신</span>
                <strong>{formatUpdatedTime(lastUpdated)}</strong>
              </div>
            </div>

            <div className="dashboard-mini-note">
              <strong>계산 기준</strong>
              <p>
                강한 징후는 점수 80점 이상, risk_level이 critical/high,
                또는 상태값에 강한·위험·확산 문구가 포함된 이슈를 기준으로
                계산합니다.
              </p>
            </div>
          </aside>
        </section>

        <section className="dashboard-insight-section">
          <div className="dashboard-section-header">
            <span>강한 징후</span>
            <h2>우선 확인이 필요한 민원 흐름</h2>
          </div>

          {strongIssues.length > 0 ? (
            <div className="dashboard-insight-grid">
              {strongIssues.map((issue, index) => (
                <article
                  key={
                    issue.id ||
                    issue.issue_key ||
                    `${getIssueTitle(issue)}-strong-${index}`
                  }
                  className="dashboard-insight-card"
                >
                  <span className="insight-score">
                    {Math.round(getIssueScore(issue))}점
                  </span>
                  <h3>{getIssueTitle(issue)}</h3>
                  <p>{getIssueSummary(issue)}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="dashboard-empty-box">
              현재 강한 징후로 분류된 이슈가 없습니다.
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

export default DashboardPage;