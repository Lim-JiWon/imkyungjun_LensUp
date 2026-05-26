import { useEffect, useMemo, useState } from "react";
import InfoTooltip from "../components/InfoTooltip";
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
    path: "M214 166 L232 154 L252 160 L258 181 L244 199 L218 196 L204 181 Z",
    labelX: 232,
    labelY: 178,
  },
  {
    key: "인천",
    label: "인천",
    aliases: ["인천", "인천광역시"],
    path: "M150 174 L183 154 L211 165 L204 197 L171 210 L142 196 Z",
    labelX: 176,
    labelY: 184,
  },
  {
    key: "경기",
    label: "경기",
    aliases: ["경기", "경기도"],
    path:
      "M176 103 L236 78 L304 96 L339 143 L333 214 L284 265 L220 250 L169 219 L137 175 Z",
    labelX: 260,
    labelY: 134,
  },
  {
    key: "강원",
    label: "강원",
    aliases: ["강원", "강원도", "강원특별자치도"],
    path:
      "M308 61 L457 44 L553 121 L584 244 L529 326 L416 309 L338 220 L343 142 Z",
    labelX: 453,
    labelY: 167,
  },
  {
    key: "충북",
    label: "충북",
    aliases: ["충북", "충청북도"],
    path:
      "M280 268 L345 225 L419 306 L401 399 L328 440 L255 388 L238 318 Z",
    labelX: 335,
    labelY: 340,
  },
  {
    key: "충남",
    label: "충남",
    aliases: ["충남", "충청남도"],
    path:
      "M111 251 L211 230 L273 283 L255 392 L194 439 L101 408 L61 328 Z",
    labelX: 167,
    labelY: 338,
  },
  {
    key: "세종",
    label: "세종",
    aliases: ["세종", "세종특별자치시"],
    path: "M230 304 L263 292 L285 318 L274 355 L236 351 L217 326 Z",
    labelX: 252,
    labelY: 324,
  },
  {
    key: "대전",
    label: "대전",
    aliases: ["대전", "대전광역시"],
    path: "M234 367 L271 354 L300 381 L287 419 L247 423 L221 393 Z",
    labelX: 261,
    labelY: 390,
  },
  {
    key: "전북",
    label: "전북",
    aliases: ["전북", "전라북도", "전북특별자치도"],
    path:
      "M112 430 L208 447 L290 430 L330 501 L286 588 L187 610 L93 561 L55 489 Z",
    labelX: 198,
    labelY: 516,
  },
  {
    key: "광주",
    label: "광주",
    aliases: ["광주", "광주광역시"],
    path: "M145 627 L187 613 L218 640 L205 681 L158 682 L132 653 Z",
    labelX: 175,
    labelY: 649,
  },
  {
    key: "전남",
    label: "전남",
    aliases: ["전남", "전라남도"],
    path:
      "M80 580 L182 609 L268 604 L321 678 L279 783 L161 824 L54 783 L21 694 Z",
    labelX: 163,
    labelY: 720,
  },
  {
    key: "경북",
    label: "경북",
    aliases: ["경북", "경상북도"],
    path:
      "M407 320 L532 324 L607 430 L586 573 L493 635 L380 592 L315 500 L334 431 Z",
    labelX: 483,
    labelY: 466,
  },
  {
    key: "대구",
    label: "대구",
    aliases: ["대구", "대구광역시"],
    path: "M413 560 L456 536 L495 563 L484 607 L438 618 L405 590 Z",
    labelX: 452,
    labelY: 578,
  },
  {
    key: "울산",
    label: "울산",
    aliases: ["울산", "울산광역시"],
    path: "M545 612 L606 597 L633 641 L608 693 L548 690 L518 648 Z",
    labelX: 580,
    labelY: 646,
  },
  {
    key: "경남",
    label: "경남",
    aliases: ["경남", "경상남도"],
    path:
      "M298 592 L401 603 L506 642 L533 724 L471 806 L349 790 L263 720 L238 649 Z",
    labelX: 394,
    labelY: 707,
  },
  {
    key: "부산",
    label: "부산",
    aliases: ["부산", "부산광역시"],
    path: "M491 714 L552 706 L589 752 L560 805 L497 796 L465 751 Z",
    labelX: 526,
    labelY: 755,
  },
  {
    key: "제주",
    label: "제주",
    aliases: ["제주", "제주도", "제주특별자치도"],
    path: "M298 875 L407 854 L492 884 L460 934 L337 952 L258 918 Z",
    labelX: 377,
    labelY: 902,
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

function getRegionColor(count, maxCount) {
  if (!count || count <= 0) {
    return "rgba(226, 232, 240, 0.95)";
  }

  const ratio = Math.min(count / Math.max(maxCount, 1), 1);
  const alpha = 0.2 + ratio * 0.75;

  return `rgba(239, 68, 68, ${alpha})`;
}

function getTextColor(count, maxCount) {
  if (!count || count <= 0) return "#64748b";

  const ratio = count / Math.max(maxCount, 1);

  return ratio > 0.48 ? "#ffffff" : "#334155";
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
  mapWrap: {
    width: "100%",
    display: "flex",
    justifyContent: "center",
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
  legend: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "12px",
    marginTop: "20px",
    color: "#64748b",
    fontSize: "13px",
    fontWeight: 800,
  },
  legendBar: {
    flex: 1,
    height: "12px",
    borderRadius: "999px",
    background:
      "linear-gradient(90deg, rgba(254, 226, 226, 1), rgba(239, 68, 68, 0.95))",
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

  const maxRegionCount = useMemo(() => {
    const regionCounts = KOREA_REGIONS.map((region) => {
      const stat = findRegionStat(regionRank, region);
      return getRegionCount(stat);
    });

    return Math.max(...regionCounts, 1);
  }, [regionRank]);

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
              보여주는 캡스톤 프로젝트 데모입니다.
            </p>

            <div className="pill-row">
              <div className="pill">#실시간 징후 탐지</div>
              <div className="pill">#지역·기관 분석</div>
              <div className="pill">#AI 브리핑 요약</div>
              <div className="pill">#신뢰 가능한 공공데이터</div>
            </div>

            <div className="down-arrow">⌄</div>
          </section>

          <div className="dashboard-stage" id="dashboard">
            <div className="edge-card edge-left">
              <div className="floating-icon">🔔</div>
              <div className="floating-title">징후 탐지</div>
              <div className="floating-desc">
                급증 키워드와 민원 흐름을 빠르게 파악
              </div>
            </div>

            <div className="dashboard-wrap">
              <div className="dashboard">
                <div className="main-panel">
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
                        {todayIssue?.source || "출처 없음"}
                      </div>
                    </div>

                    <div className="stat-box">
                      <div className="label">상태</div>
                      <div className="value">
                        {todayIssue?.signal_status ||
                          todayIssue?.status ||
                          "-"}
                      </div>
                    </div>

                    <div className="stat-box">
                      <div className="label">위험도</div>
                      <div className="value">
                        {todayIssue?.risk_level || "-"}
                      </div>
                    </div>
                  </div>

                  <div className="chart-box">
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

                <div className="side-column">
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
                </div>
              </div>
            </div>

            <div className="edge-card edge-right">
              <div className="floating-icon">📝</div>
              <div className="floating-title">이슈 브리핑</div>
              <div className="floating-desc">
                AI가 핵심 내용을 짧고 선명하게 요약
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
                지역별 민원 이슈 수를 기준으로 지도 색상을 다르게 표시합니다.
                민원이 많은 지역일수록 진한 빨간색으로 보입니다.
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
                    <span>대한민국 지역별 민원 지도</span>
                    <span style={regionSectionStyles.mapSmall}>
                      색이 진할수록 민원 이슈 수가 많음
                    </span>
                  </div>

                  <div style={regionSectionStyles.mapWrap}>
                    <svg
                      viewBox="0 0 660 980"
                      role="img"
                      aria-label="지역별 민원 이슈 지도"
                      style={{
                        width: "100%",
                        maxWidth: "560px",
                        height: "auto",
                      }}
                    >
                      <rect
                        x="0"
                        y="0"
                        width="660"
                        height="980"
                        rx="26"
                        fill="#eaf7ff"
                      />

                      <path
                        d="M167 104 L236 70 L309 60 L457 43 L553 120 L584 244 L607 430 L633 641 L589 752 L560 805 L471 806 L337 952 L258 918 L161 824 L54 783 L21 694 L55 489 L61 328 L137 175 Z"
                        fill="rgba(255,255,255,0.45)"
                        stroke="rgba(148,163,184,0.35)"
                        strokeWidth="3"
                      />

                      {KOREA_REGIONS.map((region) => {
                        const stat = findRegionStat(regionRank, region);
                        const count = getRegionCount(stat);
                        const isSelected = selectedRegionKey === region.key;
                        const fill = getRegionColor(count, maxRegionCount);
                        const textColor = getTextColor(count, maxRegionCount);

                        return (
                          <g key={region.key}>
                            <path
                              d={region.path}
                              fill={fill}
                              stroke={isSelected ? "#1d4ed8" : "#ffffff"}
                              strokeWidth={isSelected ? 6 : 3}
                              strokeLinejoin="round"
                              strokeLinecap="round"
                              onClick={() => setSelectedRegionKey(region.key)}
                              style={{
                                cursor: "pointer",
                                filter: isSelected
                                  ? "drop-shadow(0 12px 18px rgba(37, 99, 235, 0.24))"
                                  : "drop-shadow(0 8px 12px rgba(15, 23, 42, 0.08))",
                                transition: "all 0.2s ease",
                              }}
                            />

                            <text
                              x={region.labelX}
                              y={region.labelY}
                              textAnchor="middle"
                              dominantBaseline="middle"
                              onClick={() => setSelectedRegionKey(region.key)}
                              style={{
                                cursor: "pointer",
                                fill: textColor,
                                fontSize: 20,
                                fontWeight: 950,
                                pointerEvents: "auto",
                              }}
                            >
                              {region.label}
                            </text>

                            <text
                              x={region.labelX}
                              y={region.labelY + 25}
                              textAnchor="middle"
                              dominantBaseline="middle"
                              onClick={() => setSelectedRegionKey(region.key)}
                              style={{
                                cursor: "pointer",
                                fill: textColor,
                                fontSize: 14,
                                fontWeight: 850,
                                pointerEvents: "auto",
                              }}
                            >
                              {count ? `${count}건` : "-"}
                            </text>
                          </g>
                        );
                      })}
                    </svg>
                  </div>

                  <div style={regionSectionStyles.legend}>
                    <span>적음</span>
                    <div style={regionSectionStyles.legendBar}></div>
                    <span>많음</span>
                  </div>
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

                  <div style={regionSectionStyles.issueList}>
                    <h3 style={regionSectionStyles.sideTitle}>
                      선택 지역 관련 이슈
                    </h3>

                    {selectedRegionIssues.length > 0 ? (
                      selectedRegionIssues.map((issue, index) => (
                        <div
                          key={`${issue.id || issue.title || index}`}
                          style={regionSectionStyles.issueItem}
                        >
                          <p style={regionSectionStyles.issueTitle}>
                            {issue.title || issue.name || "제목 없는 이슈"}
                          </p>

                          <div style={regionSectionStyles.issueMeta}>
                            {getRegionName(issue) || selectedRegion.label} ·{" "}
                            {issue.risk_level || issue.status || "상태 없음"} ·{" "}
                            점수 {issue.score ?? "-"}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div style={regionSectionStyles.issueItem}>
                        <p style={regionSectionStyles.issueTitle}>
                          선택한 지역의 상세 이슈가 아직 없습니다.
                        </p>

                        <div style={regionSectionStyles.issueMeta}>
                          지역 순위 데이터 기준으로는{" "}
                          {selectedRegionCount || 0}건이 확인됩니다.
                        </div>
                      </div>
                    )}
                  </div>
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