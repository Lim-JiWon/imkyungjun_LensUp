import { useEffect, useMemo, useState } from "react";
import InfoTooltip from "../components/InfoTooltip";
import KoreaGisMap from "../components/KoreaGisMap";
import {
  fetchDashboard,
  fetchDashboardDetail,
  fetchDashboardMapData,
} from "../api/issues";
import "../styles/DemoLanding.css";

const REFRESH_INTERVAL_MS = 30000;

const KOREA_REGIONS = [
  {
    key: "서울",
    label: "서울",
    aliases: ["서울", "서울특별시"],
  },
  {
    key: "부산",
    label: "부산",
    aliases: ["부산", "부산광역시"],
  },
  {
    key: "대구",
    label: "대구",
    aliases: ["대구", "대구광역시"],
  },
  {
    key: "인천",
    label: "인천",
    aliases: ["인천", "인천광역시"],
  },
  {
    key: "광주",
    label: "광주",
    aliases: ["광주", "광주광역시"],
  },
  {
    key: "대전",
    label: "대전",
    aliases: ["대전", "대전광역시"],
  },
  {
    key: "울산",
    label: "울산",
    aliases: ["울산", "울산광역시"],
  },
  {
    key: "세종",
    label: "세종",
    aliases: ["세종", "세종특별자치시"],
  },
  {
    key: "경기",
    label: "경기",
    aliases: ["경기", "경기도"],
  },
  {
    key: "강원",
    label: "강원",
    aliases: ["강원", "강원도", "강원특별자치도"],
  },
  {
    key: "충북",
    label: "충북",
    aliases: ["충북", "충청북도"],
  },
  {
    key: "충남",
    label: "충남",
    aliases: ["충남", "충청남도"],
  },
  {
    key: "전북",
    label: "전북",
    aliases: ["전북", "전라북도", "전북특별자치도"],
  },
  {
    key: "전남",
    label: "전남",
    aliases: ["전남", "전라남도"],
  },
  {
    key: "경북",
    label: "경북",
    aliases: ["경북", "경상북도"],
  },
  {
    key: "경남",
    label: "경남",
    aliases: ["경남", "경상남도"],
  },
  {
    key: "제주",
    label: "제주",
    aliases: ["제주", "제주도", "제주특별자치도"],
  },
];

function getTextValue(item) {
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
}

function getTrendValue(item) {
  if (typeof item === "number") return item;
  if (typeof item === "string") return Number(item);

  if (item && typeof item === "object") {
    return Number(
      item.value ??
        item.count ??
        item.complaint_count ??
        item.score ??
        0
    );
  }

  return 0;
}

function getTrendLabel(item, index) {
  if (item && typeof item === "object") {
    return item.date || item.label || item.name || `${index + 1}`;
  }

  return `${index + 1}`;
}

function getScoreValue(issue) {
  const score = Number(issue?.score ?? 0);
  return Number.isFinite(score) ? score : 0;
}

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

  return riskLevel || "-";
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

  return status || "-";
}

function normalizeTextList(...lists) {
  const result = [];

  lists.forEach((list) => {
    if (!Array.isArray(list)) return;

    list.forEach((item) => {
      const value = getTextValue(item);

      if (value && !result.includes(value)) {
        result.push(value);
      }
    });
  });

  return result;
}

function toArray(value) {
  if (Array.isArray(value)) return value;

  if (value && typeof value === "object") {
    return Object.entries(value).map(([key, item]) => {
      if (item && typeof item === "object") {
        return {
          region: key,
          ...item,
        };
      }

      return {
        region: key,
        count: item,
      };
    });
  }

  return [];
}

function getRegionName(item) {
  if (!item || typeof item !== "object") return "";

  return (
    item.region ||
    item.region_name ||
    item.name ||
    item.label ||
    item.sido ||
    item.city ||
    item.area ||
    item.location ||
    ""
  );
}

function getRegionCount(item) {
  if (typeof item === "number") return item;

  if (!item || typeof item !== "object") return 0;

  const count = Number(
    item.count ??
      item.issue_count ??
      item.complaint_count ??
      item.total_count ??
      item.value ??
      item.score ??
      item._count ??
      0
  );

  return Number.isFinite(count) ? count : 0;
}

function normalizeRegionText(value) {
  return String(value ?? "")
    .replace(/\s/g, "")
    .replace(/특별자치시/g, "")
    .replace(/특별자치도/g, "")
    .replace(/특별시/g, "")
    .replace(/광역시/g, "")
    .replace(/자치도/g, "")
    .replace(/도/g, "")
    .trim();
}

function isSameRegion(regionName, region) {
  const target = normalizeRegionText(regionName);

  if (!target) return false;

  const aliases = [region.key, region.label, ...(region.aliases || [])];

  return aliases.some((alias) => {
    const normalizedAlias = normalizeRegionText(alias);

    return target.includes(normalizedAlias) || normalizedAlias.includes(target);
  });
}

function findRegionStat(regionRank, region) {
  return regionRank.find((item) => isSameRegion(getRegionName(item), region));
}

const regionSectionStyles = {
  section: {
    maxWidth: "1180px",
    margin: "80px auto 0",
    padding: "0 20px 80px",
  },
  header: {
    textAlign: "center",
    marginBottom: "34px",
  },
  badge: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "9px 15px",
    borderRadius: "999px",
    background: "#e8f2ff",
    color: "#2563eb",
    fontSize: "14px",
    fontWeight: 900,
    marginBottom: "18px",
  },
  title: {
    margin: 0,
    fontSize: "clamp(34px, 5vw, 56px)",
    lineHeight: 1.15,
    letterSpacing: "-0.055em",
    fontWeight: 950,
    color: "#0f172a",
  },
  desc: {
    maxWidth: "680px",
    margin: "18px auto 0",
    fontSize: "18px",
    lineHeight: 1.75,
    letterSpacing: "-0.03em",
    color: "#64748b",
    fontWeight: 650,
  },
  layout: {
    display: "grid",
    gridTemplateColumns: "1.05fr 0.95fr",
    gap: "24px",
    alignItems: "stretch",
  },
  card: {
    borderRadius: "34px",
    background: "rgba(255, 255, 255, 0.92)",
    boxShadow: "0 24px 70px rgba(15, 23, 42, 0.1)",
    border: "1px solid rgba(226, 232, 240, 0.9)",
    padding: "28px",
    backdropFilter: "blur(16px)",
  },
  mapCard: {
    borderRadius: "34px",
    background: "linear-gradient(180deg, #eff8ff 0%, #dff0ff 100%)",
    boxShadow: "0 24px 70px rgba(15, 23, 42, 0.1)",
    border: "1px solid rgba(191, 219, 254, 0.9)",
    padding: "28px",
    backdropFilter: "blur(16px)",
  },
  mapTitle: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    marginBottom: "18px",
    color: "#0f172a",
    fontWeight: 950,
  },
  mapSmall: {
    fontSize: "13px",
    color: "#64748b",
    fontWeight: 800,
  },
  sideTitle: {
    margin: "0 0 16px",
    fontSize: "24px",
    letterSpacing: "-0.04em",
    color: "#0f172a",
    fontWeight: 950,
  },
  selectedBox: {
    borderRadius: "26px",
    background: "linear-gradient(135deg, #2563eb, #60a5fa)",
    color: "white",
    padding: "24px",
    marginBottom: "18px",
    boxShadow: "0 18px 42px rgba(37, 99, 235, 0.24)",
  },
  selectedLabel: {
    fontSize: "14px",
    fontWeight: 900,
    opacity: 0.86,
    marginBottom: "8px",
  },
  selectedRegion: {
    fontSize: "34px",
    fontWeight: 950,
    letterSpacing: "-0.05em",
    marginBottom: "6px",
  },
  selectedCount: {
    fontSize: "17px",
    fontWeight: 850,
    opacity: 0.95,
  },
  rankList: {
    display: "grid",
    gap: "10px",
  },
  rankItem: {
    display: "grid",
    gridTemplateColumns: "42px 1fr auto",
    alignItems: "center",
    gap: "12px",
    borderRadius: "20px",
    background: "#f8fafc",
    padding: "14px 16px",
  },
  rankNumber: {
    width: "34px",
    height: "34px",
    borderRadius: "14px",
    background: "#eff6ff",
    color: "#2563eb",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 950,
  },
  rankName: {
    fontSize: "16px",
    fontWeight: 900,
    color: "#0f172a",
  },
  rankCount: {
    color: "#ef4444",
    fontWeight: 950,
  },
  issueList: {
    marginTop: "18px",
    display: "grid",
    gap: "10px",
  },
  issueItem: {
    borderRadius: "18px",
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    padding: "14px 16px",
  },
  issueTitle: {
    margin: "0 0 6px",
    fontSize: "15px",
    fontWeight: 900,
    color: "#0f172a",
    lineHeight: 1.45,
  },
  issueMeta: {
    fontSize: "13px",
    color: "#64748b",
    fontWeight: 700,
  },
};

function DemoLanding() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedIssueId, setSelectedIssueId] = useState(null);
  const [selectedIssueDetail, setSelectedIssueDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");

  const [currentTopIssueIndex, setCurrentTopIssueIndex] = useState(0);

  const [mapData, setMapData] = useState(null);
  const [mapLoading, setMapLoading] = useState(true);
  const [mapError, setMapError] = useState("");
  const [selectedRegionKey, setSelectedRegionKey] = useState("서울");

  useEffect(() => {
    let alive = true;

    async function loadIssues({ silent = false } = {}) {
      try {
        if (!silent) {
          setLoading(true);
        }

        setError("");

        const data = await fetchDashboard();

        const issueList = Array.isArray(data?.issues)
          ? data.issues
          : Array.isArray(data)
          ? data
          : [];

        if (!alive) return;

        setIssues(issueList);
      } catch (err) {
        console.error(err);

        if (!alive) return;

        if (!silent) {
          setError("이슈 목록을 불러오지 못했습니다.");
        }
      } finally {
        if (alive && !silent) {
          setLoading(false);
        }
      }
    }

    loadIssues();

    const timer = setInterval(() => {
      loadIssues({ silent: true });
    }, REFRESH_INTERVAL_MS);

    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    let alive = true;

    async function loadMapData({ silent = false } = {}) {
      try {
        if (!silent) {
          setMapLoading(true);
        }

        setMapError("");

        const data = await fetchDashboardMapData();

        if (!alive) return;

        setMapData(data || null);
      } catch (err) {
        console.error(err);

        if (!alive) return;

        if (!silent) {
          setMapError("지역별 민원 데이터를 불러오지 못했습니다.");
        }
      } finally {
        if (alive && !silent) {
          setMapLoading(false);
        }
      }
    }

    loadMapData();

    const timer = setInterval(() => {
      loadMapData({ silent: true });
    }, REFRESH_INTERVAL_MS);

    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  const topScoreIssues = useMemo(() => {
    if (!Array.isArray(issues)) return [];

    return [...issues]
      .sort((a, b) => getScoreValue(b) - getScoreValue(a))
      .slice(0, 5);
  }, [issues]);

  useEffect(() => {
    if (topScoreIssues.length === 0) {
      if (selectedIssueId !== null) {
        setSelectedIssueId(null);
      }

      if (currentTopIssueIndex !== 0) {
        setCurrentTopIssueIndex(0);
      }

      return;
    }

    const currentIndex = topScoreIssues.findIndex(
      (issue) => issue.id === selectedIssueId
    );

    if (currentIndex >= 0) {
      if (currentTopIssueIndex !== currentIndex) {
        setCurrentTopIssueIndex(currentIndex);
      }

      return;
    }

    setCurrentTopIssueIndex(0);
    setSelectedIssueId(topScoreIssues[0].id);
  }, [topScoreIssues, selectedIssueId, currentTopIssueIndex]);

  useEffect(() => {
    let alive = true;

    async function loadIssueDetail({ silent = false } = {}) {
      if (!selectedIssueId) {
        setSelectedIssueDetail(null);
        setDetailError("");
        return;
      }

      try {
        if (!silent) {
          setDetailLoading(true);
          setSelectedIssueDetail(null);
        }

        setDetailError("");

        const data = await fetchDashboardDetail(selectedIssueId);

        if (!alive) return;

        setSelectedIssueDetail(data);
      } catch (err) {
        console.error(err);

        if (!alive) return;

        if (!silent) {
          if (err?.response?.status === 404) {
            setDetailError("해당 이슈를 찾을 수 없습니다.");
          } else {
            setDetailError("이슈 상세 정보를 불러오지 못했습니다.");
          }

          setSelectedIssueDetail(null);
        }
      } finally {
        if (alive && !silent) {
          setDetailLoading(false);
        }
      }
    }

    loadIssueDetail();

    const timer = setInterval(() => {
      loadIssueDetail({ silent: true });
    }, REFRESH_INTERVAL_MS);

    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [selectedIssueId]);

  const selectedIssueFromList = useMemo(() => {
    if (!Array.isArray(issues) || issues.length === 0) return null;

    const foundIssue = issues.find((issue) => issue.id === selectedIssueId);

    if (foundIssue) return foundIssue;

    return topScoreIssues[currentTopIssueIndex] || topScoreIssues[0] || null;
  }, [issues, selectedIssueId, topScoreIssues, currentTopIssueIndex]);

  const todayIssue = selectedIssueDetail || selectedIssueFromList;

  const todayKeywords = useMemo(() => {
    if (!todayIssue) return [];

    return normalizeTextList(
      todayIssue.related_keywords,
      todayIssue.keywords,
      todayIssue.category_tags,
      todayIssue.cluster_keywords,
      todayIssue.rising_keywords
    );
  }, [todayIssue]);

  const todayCauses = useMemo(() => {
    if (!todayIssue || !Array.isArray(todayIssue.causes)) return [];

    return todayIssue.causes
      .map((item) => getTextValue(item))
      .filter(Boolean);
  }, [todayIssue]);

  const trendRows = useMemo(() => {
    const rawTrends =
      todayIssue?.keyword_trends ||
      todayIssue?.keywordTrends ||
      todayIssue?.trends ||
      todayIssue?.trend_values ||
      [];

    if (!Array.isArray(rawTrends)) return [];

    return rawTrends
      .map((item, index) => ({
        label: getTrendLabel(item, index),
        value: getTrendValue(item),
      }))
      .filter((item) => Number.isFinite(item.value));
  }, [todayIssue]);

  const maxTrendValue = useMemo(() => {
    if (trendRows.length === 0) return 1;

    return Math.max(...trendRows.map((item) => item.value), 1);
  }, [trendRows]);

  const regionRank = useMemo(() => {
    return toArray(mapData?.region_rank)
      .map((item) => ({
        ...item,
        _regionName: getRegionName(item),
        _count: getRegionCount(item),
      }))
      .filter((item) => item._regionName)
      .sort((a, b) => b._count - a._count);
  }, [mapData]);

  const regionIssues = useMemo(() => {
    return toArray(mapData?.issues);
  }, [mapData]);

  const selectedRegion = useMemo(() => {
    return (
      KOREA_REGIONS.find((region) => region.key === selectedRegionKey) ||
      KOREA_REGIONS[0]
    );
  }, [selectedRegionKey]);

  const selectedRegionStat = useMemo(() => {
    return findRegionStat(regionRank, selectedRegion);
  }, [regionRank, selectedRegion]);

  const selectedRegionCount = getRegionCount(selectedRegionStat);

  const selectedRegionIssues = useMemo(() => {
    return regionIssues
      .filter((issue) => isSameRegion(getRegionName(issue), selectedRegion))
      .slice(0, 3);
  }, [regionIssues, selectedRegion]);

  const scoreValue = Math.round(
    Math.max(0, Math.min(100, Number(todayIssue?.score ?? 0)))
  );

  const topIssuePositionText =
    topScoreIssues.length > 0
      ? `${currentTopIssueIndex + 1} / ${topScoreIssues.length}`
      : "0 / 0";

  function moveTopIssue(direction) {
    if (topScoreIssues.length === 0) return;

    const safeCurrentIndex =
      currentTopIssueIndex >= 0 && currentTopIssueIndex < topScoreIssues.length
        ? currentTopIssueIndex
        : 0;

    const nextIndex =
      (safeCurrentIndex + direction + topScoreIssues.length) %
      topScoreIssues.length;

    const nextIssue = topScoreIssues[nextIndex];

    if (!nextIssue) return;

    setCurrentTopIssueIndex(nextIndex);
    setSelectedIssueId(nextIssue.id);
  }

  return (
    <div>
      <main className="hero" id="service">
        <div className="bg-circle bg1"></div>
        <div className="bg-circle bg2"></div>
        <div className="bg-circle bg3"></div>

        <div className="floating-card fc3">
          <div className="floating-icon">📊</div>
          <div className="floating-title">기관·지역 분석</div>
          <div className="floating-desc">
            어디서 많이 발생하는지 한눈에 확인
          </div>
        </div>

        <div className="floating-card fc4">
          <div className="floating-icon">👥</div>
          <div className="floating-title">맞춤 인사이트</div>
          <div className="floating-desc">
            관심 주제별 분석 결과를 개인화 제공
          </div>
        </div>

        <section className="content">
          <section className="hero-top">
            <div className="badge">
              공공 민원 데이터 기반 AI 사회문제 징후 탐지 시스템
            </div>

            <h1>
              사회문제의 조짐을
              <br />
              더 쉽고 직관적으로
            </h1>

            <p className="subtitle">
              급등 키워드, 지역·기관별 민원 흐름, 이슈 브리핑을 한 화면에서
              보여주는 서비스 입니다.
            </p>

            <div className="pill-row">
              <div className="pill">#실시간 징후 탐지</div>
              <div className="pill">#지역·기관 분석</div>
              <div className="pill">#AI 브리핑 요약</div>
              <div className="pill">#신뢰 가능한 공공데이터</div>
            </div>

            <div className="down-arrow">⌄</div>
          </section>

          <div
            className="dashboard-stage"
            id="dashboard"
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "stretch",
              width: "100%",
              paddingLeft: "24px",
              paddingRight: "24px",
            }}
          >
            <div
              className="dashboard-wrap"
              style={{
                width: "min(1540px, 100%)",
                maxWidth: "1540px",
              }}
            >
              <div
                className="dashboard"
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "minmax(0, 1.35fr) minmax(360px, 0.95fr)",
                  gap: "24px",
                  alignItems: "stretch",
                }}
              >
                <div className="main-panel" style={{ minWidth: 0 }}>
                  <div className="panel-top">
                    <div
                      style={{
                        width: "100%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: "16px",
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => moveTopIssue(-1)}
                        disabled={topScoreIssues.length <= 1}
                        aria-label="이전 민원 이슈 보기"
                        style={{
                          width: "44px",
                          height: "44px",
                          borderRadius: "999px",
                          border: "none",
                          background:
                            topScoreIssues.length <= 1
                              ? "rgba(148, 163, 184, 0.2)"
                              : "rgba(37, 99, 235, 0.12)",
                          color:
                            topScoreIssues.length <= 1 ? "#94a3b8" : "#2563eb",
                          fontSize: "28px",
                          fontWeight: 800,
                          cursor:
                            topScoreIssues.length <= 1
                              ? "not-allowed"
                              : "pointer",
                          flexShrink: 0,
                        }}
                      >
                        ‹
                      </button>

                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div className="panel-label">오늘의 민원 이슈</div>

                        <div
                          style={{
                            marginTop: "6px",
                            marginBottom: "8px",
                            fontSize: "13px",
                            fontWeight: 800,
                            color: "#2563eb",
                          }}
                        >
                          {topIssuePositionText}
                        </div>

                        <div className="panel-title">
                          {loading
                            ? "불러오는 중..."
                            : error
                            ? "이슈를 불러오지 못했습니다."
                            : detailLoading
                            ? "상세 불러오는 중..."
                            : todayIssue?.title || "표시할 이슈가 없습니다."}
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() => moveTopIssue(1)}
                        disabled={topScoreIssues.length <= 1}
                        aria-label="다음 민원 이슈 보기"
                        style={{
                          width: "44px",
                          height: "44px",
                          borderRadius: "999px",
                          border: "none",
                          background:
                            topScoreIssues.length <= 1
                              ? "rgba(148, 163, 184, 0.2)"
                              : "rgba(37, 99, 235, 0.12)",
                          color:
                            topScoreIssues.length <= 1 ? "#94a3b8" : "#2563eb",
                          fontSize: "28px",
                          fontWeight: 800,
                          cursor:
                            topScoreIssues.length <= 1
                              ? "not-allowed"
                              : "pointer",
                          flexShrink: 0,
                        }}
                      >
                        ›
                      </button>
                    </div>
                  </div>

                  <div className="stats">
                    <div className="stat-box">
                      <div className="label">출처</div>
                      <div className="value">
                        {getSourceLabel(todayIssue?.source)}
                      </div>
                    </div>

                    <div className="stat-box">
                      <div className="label">상태</div>
                      <div className="value">
                        {getStatusLabel(
                          todayIssue?.signal_status || todayIssue?.status
                        )}
                      </div>
                    </div>

                    <div className="stat-box">
                      <div className="label">위험도</div>
                      <div className="value">
                        {getRiskLabel(todayIssue?.risk_level)}
                      </div>
                    </div>
                  </div>

                  <div className="chart-section" style={{ marginTop: "20px" }}>
                    <div className="side-title side-title-with-tooltip">
                      <span>최근 키워드 추이</span>
                      <InfoTooltip text="기간 내 민원 언급량 변화에 따른 그래프입니다." />
                    </div>

                    <div className="chart-box" style={{ marginTop: 0 }}>
                      {trendRows.length > 0 ? (
                        trendRows.map((item, index) => {
                          const height =
                            item.value > 0
                              ? Math.max((item.value / maxTrendValue) * 120, 24)
                              : 12;

                          return (
                            <div
                              key={`${item.label}-${index}`}
                              className="bar"
                              title={`${item.label}: ${item.value}`}
                              style={{
                                height: `${height}px`,
                                animationDelay: `${index * 0.08}s`,
                              }}
                            />
                          );
                        })
                      ) : (
                        <div className="chart-empty">트렌드 데이터 없음</div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="side-column" style={{ minWidth: 0 }}>
                  <div className="side-card">
                    <div className="side-title side-title-with-tooltip">
                      <span>AI 브리핑</span>
                      <InfoTooltip text="AI가 최근 민원 흐름과 핵심 특징을 짧게 요약한 내용입니다." />
                    </div>

                    <div className="side-text">
                      {loading
                        ? "불러오는 중..."
                        : error
                        ? "브리핑을 불러오지 못했습니다."
                        : detailLoading
                        ? "상세 불러오는 중..."
                        : todayIssue?.summary || "요약 없음"}
                    </div>
                  </div>

                  <div className="side-card">
                    <div className="side-title side-title-with-tooltip">
                      <span>이슈 강도</span>
                      <InfoTooltip text="백엔드에서 내려준 이슈 점수(score) 기준으로 표시한 값입니다." />
                    </div>

                    <div className="score-row">
                      <div>
                        <div className="score">{scoreValue}</div>
                        <div className="score-sub">/ 100</div>
                      </div>

                      <div className="progress">
                        <div
                          className="progress-fill"
                          style={{ width: `${scoreValue}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="side-card">
                    <div className="side-title side-title-with-tooltip">
                      <span>원인 분석</span>
                      <InfoTooltip text="백엔드가 전달한 원인 후보 목록입니다." />
                    </div>

                    <div className="tags">
                      {todayCauses.length > 0 ? (
                        todayCauses.map((cause, index) => (
                          <span className="tag" key={`${cause}-${index}`}>
                            {cause}
                          </span>
                        ))
                      ) : (
                        <span className="tag">원인 정보 없음</span>
                      )}
                    </div>
                  </div>

                  <div className="side-card">
                    <div className="side-title side-title-with-tooltip">
                      <span>연관 키워드</span>
                      <InfoTooltip text="해당 이슈와 함께 많이 나타나는 관련 키워드입니다." />
                    </div>

                    <div className="tags">
                      {todayKeywords.length > 0 ? (
                        todayKeywords.map((tag, index) => (
                          <span className="tag" key={`${tag}-${index}`}>
                            #{tag}
                          </span>
                        ))
                      ) : (
                        <span className="tag">키워드 없음</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <section style={regionSectionStyles.section}>
            <div style={regionSectionStyles.header}>
              <div style={regionSectionStyles.badge}>
                오늘의 지역별 민원 모아보기
              </div>

              <h2 style={regionSectionStyles.title}>
                어느 지역에서
                <br />
                민원이 많이 발생했는지 한눈에
              </h2>

              <p style={regionSectionStyles.desc}>
                대한민국 GIS 기반 시·도 행정구역을 기준으로 지역별 민원 이슈
                수를 지도 위에 표시합니다.
              </p>
            </div>

            {mapLoading && (
              <div style={regionSectionStyles.card}>
                지역별 민원 데이터를 불러오는 중입니다.
              </div>
            )}

            {mapError && !mapLoading && (
              <div style={regionSectionStyles.card}>{mapError}</div>
            )}

            {!mapLoading && !mapError && (
              <div style={regionSectionStyles.layout}>
                <div style={regionSectionStyles.mapCard}>
                  <div style={regionSectionStyles.mapTitle}>
                    <span>대한민국 기반 민원 지도</span>
                    <span style={regionSectionStyles.mapSmall}></span>
                  </div>

                  <KoreaGisMap
                    regionRank={regionRank}
                    selectedRegionKey={selectedRegionKey}
                    onSelectRegion={setSelectedRegionKey}
                  />
                </div>

                <div style={regionSectionStyles.card}>
                  <h3 style={regionSectionStyles.sideTitle}>
                    지역별 민원 순위
                  </h3>

                  <div style={regionSectionStyles.selectedBox}>
                    <div style={regionSectionStyles.selectedLabel}>
                      선택한 지역
                    </div>

                    <div style={regionSectionStyles.selectedRegion}>
                      {selectedRegion.label}
                    </div>

                    <div style={regionSectionStyles.selectedCount}>
                      민원 이슈 수 {selectedRegionCount || 0}건
                    </div>
                  </div>

                  <div style={regionSectionStyles.rankList}>
                    {regionRank.length > 0 ? (
                      regionRank.slice(0, 5).map((item, index) => (
                        <button
                          key={`${item._regionName}-${index}`}
                          type="button"
                          onClick={() => {
                            const matched = KOREA_REGIONS.find((region) =>
                              isSameRegion(item._regionName, region)
                            );

                            if (matched) {
                              setSelectedRegionKey(matched.key);
                            }
                          }}
                          style={{
                            ...regionSectionStyles.rankItem,
                            border: "none",
                            textAlign: "left",
                            cursor: "pointer",
                          }}
                        >
                          <div style={regionSectionStyles.rankNumber}>
                            {index + 1}
                          </div>

                          <div style={regionSectionStyles.rankName}>
                            {item._regionName}
                          </div>

                          <div style={regionSectionStyles.rankCount}>
                            {item._count}건
                          </div>
                        </button>
                      ))
                    ) : (
                      <div style={regionSectionStyles.issueMeta}>
                        표시할 지역 순위 데이터가 없습니다.
                      </div>
                    )}
                  </div>

                  {selectedRegionIssues.length > 0 && (
                    <div style={regionSectionStyles.issueList}>
                      <h3 style={regionSectionStyles.sideTitle}>
                        선택 지역 관련 이슈
                      </h3>

                      {selectedRegionIssues.map((issue, index) => (
                        <div
                          key={`${issue.id || issue.title || index}`}
                          style={regionSectionStyles.issueItem}
                        >
                          <p style={regionSectionStyles.issueTitle}>
                            {issue.title || issue.name || "제목 없는 이슈"}
                          </p>

                          <div style={regionSectionStyles.issueMeta}>
                            {getRegionName(issue) || selectedRegion.label} ·{" "}
                            {issue.risk_level
                              ? getRiskLabel(issue.risk_level)
                              : getStatusLabel(issue.status || "상태 없음")}{" "}
                            · 점수 {issue.score ?? "-"}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </section>
        </section>
      </main>
    </div>
  );
}

export default DemoLanding;