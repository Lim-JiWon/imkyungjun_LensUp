import { useEffect, useMemo, useState } from "react";
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

function getStatusLabel(status) {
  if (status === "warning") return "위험 징후";
  if (status === "growing") return "확산 중";
  if (status === "watch") return "주의 관찰";
  if (status === "stable") return "안정";
  return status || "상태 미정";
}

function getRiskLabel(riskLevel) {
  if (riskLevel === "critical") return "매우 높음";
  if (riskLevel === "high") return "높음";
  if (riskLevel === "medium") return "보통";
  if (riskLevel === "low") return "낮음";
  return riskLevel || "미정";
}

function TopicComplaintPage() {
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
          ? issue.keywords.join(" ")
          : "";

        return `${title} ${summary} ${topKeyword} ${keywords}`
          .toLowerCase()
          .includes(keyword);
      });
    }

    return result;
  }, [allIssues, selectedCategory, searchText]);

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
            <div className="topic-state-box">주제별 민원 데이터를 불러오는 중입니다.</div>
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
              {filteredIssues.map((issue, index) => (
                <article
                  key={issue.id || issue.issue_key || index}
                  className="topic-issue-card"
                >
                  <div className="topic-card-top">
                    <span className="topic-chip">{issue.category}</span>
                    <span className="topic-score">
                      {issue.score !== undefined && issue.score !== null
                        ? `${issue.score}점`
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
                      <strong>{getStatusLabel(issue.status)}</strong>
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
                    {(issue.keywords || issue.category_tags || [])
                      .slice(0, 5)
                      .map((keyword) => (
                        <span key={keyword}>#{keyword}</span>
                      ))}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

export default TopicComplaintPage;