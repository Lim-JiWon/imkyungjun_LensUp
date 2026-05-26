import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/TopicComplaintPage.css";

const API_BASE_URL = "https://api.minwon-ai.kr";

function normalizeCategoryData(data) {
  if (!data) return [];

  if (Array.isArray(data)) {
    return data.map((item, index) => ({
      category:
        item.category ||
        item.name ||
        item.title ||
        item.category_name ||
        `카테고리 ${index + 1}`,
      issues: item.issues || item.items || item.data || [],
    }));
  }

  if (Array.isArray(data.categories)) {
    return data.categories.map((item, index) => ({
      category:
        item.category ||
        item.name ||
        item.title ||
        item.category_name ||
        `카테고리 ${index + 1}`,
      issues: item.issues || item.items || item.data || [],
    }));
  }

  if (Array.isArray(data.category_groups)) {
    return data.category_groups.map((item, index) => ({
      category:
        item.category ||
        item.name ||
        item.title ||
        item.category_name ||
        `카테고리 ${index + 1}`,
      issues: item.issues || item.items || item.data || [],
    }));
  }

  if (typeof data === "object") {
    return Object.entries(data).map(([key, value]) => ({
      category: key,
      issues: Array.isArray(value) ? value : value?.issues || [],
    }));
  }

  return [];
}

function getIssueId(issue) {
  const directId =
    issue?.id ??
    issue?.issue_id ??
    issue?.issueId ??
    issue?.dashboard_id ??
    issue?.dashboardId ??
    null;

  if (directId !== null && directId !== undefined && directId !== "") {
    return directId;
  }

  const detailApi = issue?.detail_api || issue?.detailApi;

  if (detailApi) {
    try {
      const path = detailApi.startsWith("http")
        ? new URL(detailApi).pathname
        : detailApi;

      const parts = path.split("/").filter(Boolean);
      return parts[parts.length - 1] || null;
    } catch {
      return null;
    }
  }

  return null;
}

function getStatusLabel(issue) {
  const statusValue = String(issue?.signal_status || issue?.status || "")
    .toLowerCase()
    .trim();

  if (statusValue === "critical") return "강한 징후";
  if (statusValue === "growing") return "증가 추세";
  if (statusValue === "watch") return "관찰 필요";
  if (statusValue === "stable") return "안정";
  if (statusValue === "warning") return "주의";
  if (statusValue === "alert") return "경고";
  if (statusValue === "normal") return "정상";
  if (statusValue === "high") return "강한 징후";
  if (statusValue === "medium") return "관찰 필요";
  if (statusValue === "low") return "안정";

  const riskValue = String(issue?.risk_level || "")
    .toLowerCase()
    .trim();

  if (riskValue === "critical") return "강한 징후";
  if (riskValue === "high") return "강한 징후";
  if (riskValue === "medium") return "관찰 필요";
  if (riskValue === "watch") return "관찰 필요";
  if (riskValue === "low") return "안정";

  const score = Number(issue?.score);

  if (!Number.isNaN(score)) {
    if (score >= 80) return "강한 징후";
    if (score >= 60) return "증가 추세";
    if (score >= 40) return "관찰 필요";
    return "안정";
  }

  return "관찰 필요";
}

function getRiskLabel(riskLevel) {
  const value = String(riskLevel || "").toLowerCase().trim();

  if (value === "critical") return "매우 높음";
  if (value === "high") return "높음";
  if (value === "medium") return "보통";
  if (value === "low") return "낮음";
  if (value === "watch") return "관찰 필요";

  return riskLevel || "미정";
}

function getKeywordText(keyword) {
  if (typeof keyword === "string") return keyword;

  if (keyword && typeof keyword === "object") {
    return (
      keyword.keyword ||
      keyword.name ||
      keyword.label ||
      keyword.text ||
      keyword.title ||
      ""
    );
  }

  return "";
}

function TopicComplaintPage() {
  const navigate = useNavigate();

  const [categoryGroups, setCategoryGroups] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("전체");
  const [searchText, setSearchText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadCategories() {
      try {
        setIsLoading(true);
        setErrorMessage("");

        const response = await axios.get(`${API_BASE_URL}/dashboard/categories`);
        const normalized = normalizeCategoryData(response.data);

        setCategoryGroups(normalized);

        if (normalized.length > 0) {
          setSelectedCategory("전체");
        }
      } catch (error) {
        console.error(error);
        setErrorMessage("주제별 민원 데이터를 불러오지 못했습니다.");
      } finally {
        setIsLoading(false);
      }
    }

    loadCategories();
  }, []);

  const categories = useMemo(() => {
    return ["전체", ...categoryGroups.map((group) => group.category)];
  }, [categoryGroups]);

  const allIssues = useMemo(() => {
    return categoryGroups.flatMap((group) =>
      group.issues.map((issue) => ({
        ...issue,
        category: issue.category || group.category,
      }))
    );
  }, [categoryGroups]);

  const filteredIssues = useMemo(() => {
    let result =
      selectedCategory === "전체"
        ? allIssues
        : allIssues.filter((issue) => issue.category === selectedCategory);

    if (searchText.trim()) {
      const keyword = searchText.trim().toLowerCase();

      result = result.filter((issue) => {
        const title = issue.title || "";
        const summary = issue.summary || "";
        const topKeyword = issue.top_keyword || "";
        const keywords = Array.isArray(issue.keywords)
          ? issue.keywords.map(getKeywordText).join(" ")
          : "";

        return `${title} ${summary} ${topKeyword} ${keywords}`
          .toLowerCase()
          .includes(keyword);
      });
    }

    return result;
  }, [allIssues, selectedCategory, searchText]);

  const handleIssueClick = (issue) => {
    const issueId = getIssueId(issue);

    if (!issueId) {
      alert("이 이슈는 상세 페이지로 이동할 수 있는 ID가 없습니다.");
      return;
    }

    navigate(`/issues/${issueId}`);
  };

  const handleIssueKeyDown = (event, issue) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleIssueClick(issue);
    }
  };

  return (
    <main className="topic-page">
      <section className="topic-hero">
        <p className="topic-eyebrow">민원 이슈 탐색</p>
        <h1>주제별 민원 보기</h1>
        <p className="topic-description">
          민원 이슈를 분야별로 나누어 확인할 수 있습니다.
          카테고리를 선택하면 해당 분야의 주요 민원 징후와 키워드를 볼 수 있습니다.
        </p>
      </section>

      <section className="topic-search-box">
        <input
          type="text"
          placeholder="민원 제목, 키워드, 요약 검색"
          value={searchText}
          onChange={(event) => setSearchText(event.target.value)}
        />
      </section>

      <section className="topic-layout">
        <aside className="topic-category-panel">
          <h2>주제 선택</h2>

          <div className="topic-category-list">
            {categories.map((category) => (
              <button
                key={category}
                type="button"
                className={
                  selectedCategory === category
                    ? "topic-category-button active"
                    : "topic-category-button"
                }
                onClick={() => setSelectedCategory(category)}
              >
                <span>{category}</span>
                <strong>
                  {category === "전체"
                    ? allIssues.length
                    : allIssues.filter((issue) => issue.category === category)
                        .length}
                </strong>
              </button>
            ))}
          </div>
        </aside>

        <section className="topic-content">
          <div className="topic-content-header">
            <div>
              <p>선택한 주제</p>
              <h2>{selectedCategory}</h2>
            </div>
            <span>{filteredIssues.length}개 이슈</span>
          </div>

          {isLoading && (
            <div className="topic-state-box">
              주제별 민원 데이터를 불러오는 중입니다.
            </div>
          )}

          {!isLoading && errorMessage && (
            <div className="topic-state-box error">{errorMessage}</div>
          )}

          {!isLoading && !errorMessage && filteredIssues.length === 0 && (
            <div className="topic-state-box">
              표시할 민원 이슈가 없습니다.
            </div>
          )}

          {!isLoading && !errorMessage && filteredIssues.length > 0 && (
            <div className="topic-card-grid">
              {filteredIssues.map((issue, index) => {
                const keywordList = (
                  issue.keywords ||
                  issue.category_tags ||
                  issue.cluster_keywords ||
                  []
                )
                  .map(getKeywordText)
                  .filter(Boolean)
                  .slice(0, 5);

                return (
                  <article
                    key={issue.id || issue.issue_key || index}
                    className="topic-issue-card"
                    role="button"
                    tabIndex={0}
                    title="이슈 상세 페이지로 이동"
                    onClick={() => handleIssueClick(issue)}
                    onKeyDown={(event) => handleIssueKeyDown(event, issue)}
                    style={{ cursor: "pointer" }}
                  >
                    <div className="topic-card-top">
                      <span className="topic-chip">{issue.category}</span>
                      <span className="topic-score">
                        {issue.score !== undefined && issue.score !== null
                          ? `${Math.round(Number(issue.score))}점`
                          : "점수 없음"}
                      </span>
                    </div>

                    <h3>{issue.title || "제목 없음"}</h3>

                    <p className="topic-summary">
                      {issue.summary || "요약 정보가 없습니다."}
                    </p>

                    <div className="topic-meta-row">
                      <div>
                        <span>징후 상태</span>
                        <strong>{getStatusLabel(issue)}</strong>
                      </div>

                      <div>
                        <span>위험도</span>
                        <strong>{getRiskLabel(issue.risk_level)}</strong>
                      </div>

                      <div>
                        <span>민원 수</span>
                        <strong>{issue.complaint_count ?? 0}건</strong>
                      </div>
                    </div>

                    <div className="topic-keywords">
                      {keywordList.map((keyword) => (
                        <span key={keyword}>#{keyword}</span>
                      ))}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

export default TopicComplaintPage;