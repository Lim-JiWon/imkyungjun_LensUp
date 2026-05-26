import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchDashboardDetail } from "../api/issues";
import "../styles/IssueDetailPage.css";

const DEFAULT_SOURCE_LABEL = "국민권익위원회 민원빅데이터";

function getSourceLabel(source) {
  const value = String(source || "").trim();

  if (!value || value === "null" || value === "undefined" || value === "-") {
    return DEFAULT_SOURCE_LABEL;
  }

  const lowerValue = value.toLowerCase();

  if (
    lowerValue === "public_complaint_api" ||
    lowerValue === "complaint_bigdata" ||
    lowerValue === "minwon_bigdata" ||
    lowerValue === "minwon" ||
    lowerValue === "public_api"
  ) {
    return DEFAULT_SOURCE_LABEL;
  }

  return value;
}

function getRiskLabel(riskLevel) {
  const value = String(riskLevel || "").toLowerCase().trim();

  if (value === "critical") return "매우 높음";
  if (value === "high") return "높음";
  if (value === "medium") return "보통";
  if (value === "low") return "낮음";
  if (value === "watch") return "관찰 필요";

  return riskLevel || "위험도 없음";
}

function getStatusLabel(status) {
  const value = String(status || "").toLowerCase().trim();

  if (value === "critical") return "강한 징후";
  if (value === "growing") return "증가 추세";
  if (value === "watch") return "관찰 필요";
  if (value === "stable") return "안정";
  if (value === "low") return "낮음";
  if (value === "medium") return "보통";
  if (value === "high") return "높음";
  if (value === "normal") return "정상";
  if (value === "warning") return "주의";
  if (value === "alert") return "경고";

  return status || "상태 없음";
}

function getTrendDirectionLabel(direction) {
  const value = String(direction || "").toLowerCase().trim();

  if (value === "up" || value === "increase" || value === "increasing") {
    return "증가";
  }

  if (value === "down" || value === "decrease" || value === "decreasing") {
    return "감소";
  }

  if (value === "flat" || value === "stable") {
    return "유지";
  }

  if (value === "mixed") {
    return "혼합";
  }

  return direction || "-";
}

function toTextList(list) {
  if (!Array.isArray(list)) return [];

  return list
    .map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") {
        return (
          item.keyword ||
          item.cause_text ||
          item.cause ||
          item.text ||
          item.label ||
          item.name ||
          ""
        );
      }
      return "";
    })
    .filter(Boolean);
}

function IssueDetailPage() {
  const { id } = useParams();

  const [issue, setIssue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDetail() {
      try {
        setLoading(true);
        setError("");

        const data = await fetchDashboardDetail(id);
        setIssue(data);
      } catch (err) {
        console.error(err);
        setError("이슈 상세 정보를 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadDetail();
    }
  }, [id]);

  const keywords = useMemo(() => {
    if (!issue) return [];

    return toTextList([
      ...(issue.related_keywords || []),
      ...(issue.keywords || []),
      ...(issue.category_tags || []),
      ...(issue.cluster_keywords || []),
      ...(issue.rising_keywords || []),
    ]);
  }, [issue]);

  const causes = useMemo(() => {
    if (!issue) return [];
    return toTextList(issue.causes);
  }, [issue]);

  const score = Math.round(
    Math.max(0, Math.min(100, Number(issue?.score ?? 0)))
  );

  if (loading) {
    return (
      <main className="issue-detail-page">
        <div className="issue-detail-container">
          <p className="issue-detail-loading">상세 정보를 불러오는 중입니다...</p>
        </div>
      </main>
    );
  }

  if (error || !issue) {
    return (
      <main className="issue-detail-page">
        <div className="issue-detail-container">
          <Link to="/search" className="back-link">
            ← 검색으로 돌아가기
          </Link>
          <p className="issue-detail-error">
            {error || "표시할 이슈가 없습니다."}
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="issue-detail-page">
      <div className="issue-detail-container">
        <Link to="/search" className="back-link">
          ← 검색으로 돌아가기
        </Link>

        <section className="issue-detail-hero">
          <div className="issue-detail-meta">
            <span>{getSourceLabel(issue.source)}</span>
            <span>{getRiskLabel(issue.risk_level)}</span>
            <span>{getStatusLabel(issue.signal_status || issue.status)}</span>
          </div>

          <h1>{issue.title || "제목 없는 이슈"}</h1>

          <p>{issue.summary || "요약 정보가 없습니다."}</p>
        </section>

        <section className="issue-detail-grid">
          <div className="issue-detail-card score-card">
            <h2>이슈 강도</h2>

            <div className="score-number">
              {score}
              <span>/100</span>
            </div>

            <div className="score-bar">
              <div style={{ width: `${score}%` }} />
            </div>
          </div>

          <div className="issue-detail-card">
            <h2>기본 정보</h2>

            <div className="info-list">
              <div>
                <span>민원 건수</span>
                <strong>{issue.complaint_count ?? "-"}건</strong>
              </div>

              <div>
                <span>대표 키워드</span>
                <strong>{issue.top_keyword || "-"}</strong>
              </div>

              <div>
                <span>변화 방향</span>
                <strong>{getTrendDirectionLabel(issue.trend_direction)}</strong>
              </div>

              <div>
                <span>카테고리</span>
                <strong>{issue.category || "-"}</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="issue-detail-card">
          <h2>AI 브리핑</h2>
          <p className="detail-text">
            {issue.summary || "브리핑 정보가 없습니다."}
          </p>
        </section>

        <section className="issue-detail-card">
          <h2>전망</h2>
          <p className="detail-text">
            {issue.forecast || "전망 정보가 없습니다."}
          </p>
        </section>

        <section className="issue-detail-card">
          <h2>원인 분석</h2>

          <div className="tag-list">
            {causes.length > 0 ? (
              causes.map((cause, index) => (
                <span key={`${cause}-${index}`}>{cause}</span>
              ))
            ) : (
              <span>원인 정보 없음</span>
            )}
          </div>
        </section>

        <section className="issue-detail-card">
          <h2>연관 키워드</h2>

          <div className="tag-list blue">
            {keywords.length > 0 ? (
              keywords.map((keyword, index) => (
                <span key={`${keyword}-${index}`}>#{keyword}</span>
              ))
            ) : (
              <span>키워드 없음</span>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export default IssueDetailPage;