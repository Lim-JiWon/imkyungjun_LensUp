
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { fetchSearchResults } from "../api/search";
import "../styles/SearchPage.css";

function getRiskLabel(riskLevel) {
  const value = String(riskLevel || "").toLowerCase();

  if (value === "critical") return "매우 높음";
  if (value === "high") return "높음";
  if (value === "medium") return "보통";
  if (value === "low") return "낮음";

  return riskLevel || "-";
}

function SearchPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const queryFromUrl = searchParams.get("query") || "";

  const [inputValue, setInputValue] = useState(queryFromUrl);
  const [results, setResults] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [normalizedQuery, setNormalizedQuery] = useState("");
  const [selectedRisk, setSelectedRisk] = useState("all");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setInputValue(queryFromUrl);
  }, [queryFromUrl]);

  useEffect(() => {
    async function loadSearchResults() {
      if (!queryFromUrl.trim()) {
        setResults([]);
        setTotalCount(0);
        setNormalizedQuery("");
        return;
      }

      try {
        setLoading(true);
        setError("");

        const data = await fetchSearchResults(queryFromUrl);

        setResults(Array.isArray(data.results) ? data.results : []);
        setTotalCount(data.count ?? data.results?.length ?? 0);
        setNormalizedQuery(data.normalized_query || queryFromUrl);
      } catch (err) {
        console.error(err);
        setError("검색 결과를 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    }

    loadSearchResults();
  }, [queryFromUrl]);

  const filteredResults = useMemo(() => {
    if (selectedRisk === "all") return results;

    return results.filter(
      (item) => String(item.risk_level || "").toLowerCase() === selectedRisk
    );
  }, [results, selectedRisk]);

  function handleSubmit(event) {
    event.preventDefault();

    const trimmed = inputValue.trim();

    if (!trimmed) return;

    navigate(`/search?query=${encodeURIComponent(trimmed)}`);
  }

  return (
    <div className="search-page">
      <main className="search-main">
        <section className="search-hero">
          <Link to="/" className="search-back-link">
            ← 메인으로 돌아가기
          </Link>

          <div className="search-kicker">Complaint Search</div>

          <h1>
            {queryFromUrl ? (
              <>
                “{queryFromUrl}” 관련 민원 이슈를
                <br />
                찾고 있어요
              </>
            ) : (
              <>
                궁금한 민원 키워드를
                <br />
                검색해보세요
              </>
            )}
          </h1>

          <p>
            핵심 키워드, 급등 키워드, 연관어를 기준으로 관련 민원 이슈를
            찾아 보여줍니다.
          </p>

          <form className="search-form" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="예: 주차, 공원, 전기차, 장애인"
              value={inputValue}
              onChange={(event) => setInputValue(event.target.value)}
            />
            <button type="submit">검색</button>
          </form>
        </section>

        <section className="search-result-section">
          <div className="result-header">
            <div>
              <span className="result-label">Search Results</span>
              <h2>
                {loading
                  ? "검색 중입니다"
                  : queryFromUrl
                  ? `${totalCount}개의 이슈를 찾았어요`
                  : "검색어를 입력해주세요"}
              </h2>

              {normalizedQuery && (
                <p>
                  검색어 정규화 결과: <strong>{normalizedQuery}</strong>
                </p>
              )}
            </div>

            <div className="risk-filter-row">
              <button
                type="button"
                className={selectedRisk === "all" ? "active" : ""}
                onClick={() => setSelectedRisk("all")}
              >
                전체
              </button>

              <button
                type="button"
                className={selectedRisk === "critical" ? "active" : ""}
                onClick={() => setSelectedRisk("critical")}
              >
                매우 높음
              </button>

              <button
                type="button"
                className={selectedRisk === "high" ? "active" : ""}
                onClick={() => setSelectedRisk("high")}
              >
                높음
              </button>

              <button
                type="button"
                className={selectedRisk === "medium" ? "active" : ""}
                onClick={() => setSelectedRisk("medium")}
              >
                보통
              </button>
            </div>
          </div>

          {loading && (
            <div className="search-state-card">
              검색 결과를 불러오는 중...
            </div>
          )}

          {error && <div className="search-state-card error">{error}</div>}

          {!loading && !error && queryFromUrl && filteredResults.length === 0 && (
            <div className="search-state-card">
              조건에 맞는 이슈가 없습니다.
            </div>
          )}

          {!loading && !error && filteredResults.length > 0 && (
            <div className="search-card-list">
              {filteredResults.map((issue) => (
                <Link
                  to={`/issues/${issue.id}`}
                  className="search-result-card"
                  key={issue.id}
                >
                  <div className="card-left">
                    <div className="card-meta">
                      <span>{getRiskLabel(issue.risk_level)}</span>
                    </div>

                    <h3>{issue.title || "제목 없음"}</h3>

                    <p>{issue.summary || "요약 정보가 없습니다."}</p>

                    <div className="card-keywords">
                      {issue.top_keyword && <span>#{issue.top_keyword}</span>}

                      {Array.isArray(issue.keywords) &&
                        issue.keywords.slice(0, 4).map((keyword, index) => (
                          <span key={`${keyword}-${index}`}>#{keyword}</span>
                        ))}
                    </div>
                  </div>

                  <div className="card-right">
                    <div className="score-circle">
                      <strong>{Math.round(Number(issue.score || 0))}</strong>
                      <span>/100</span>
                    </div>

                    <div className="detail-link">자세히 보기</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default SearchPage; 