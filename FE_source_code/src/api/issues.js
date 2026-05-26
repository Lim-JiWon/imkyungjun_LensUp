import axios from "axios";

const API_BASE_URL = "https://api.minwon-ai.kr";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

/**
 * 대시보드 목록 조회
 * GET /dashboard
 */
export async function fetchDashboard() {
  const response = await api.get("/dashboard");
  return response.data;
}

/**
 * 이슈 상세 조회
 * GET /dashboard/{id}
 */
export async function fetchDashboardDetail(id) {
  const response = await api.get(`/dashboard/${id}`);
  return response.data;
}

/**
 * 분야별 이슈 묶음 조회
 * GET /dashboard/categories
 */
export async function fetchDashboardCategories() {
  const response = await api.get("/dashboard/categories");
  return response.data;
}

/**
 * 지도/지역/기관/연령 분석 데이터 조회
 * GET /dashboard/map-data
 */
export async function fetchDashboardMapData() {
  const response = await api.get("/dashboard/map-data");
  return response.data;
}

/**
 * 통합검색
 * GET /search?query=검색어
 */
export async function searchIssues(query) {
  const response = await api.get("/search", {
    params: { query },
  });

  return response.data;
}

/**
 * 자주 찾는 검색어
 * GET /search/popular-keywords
 */
export async function fetchPopularKeywords() {
  const response = await api.get("/search/popular-keywords");
  return response.data;
}

/**
 * 검색 자동완성
 * GET /search/suggestions?query=입력값
 */
export async function fetchSearchSuggestions(query) {
  const response = await api.get("/search/suggestions", {
    params: query ? { query } : {},
  });

  return response.data;
}

/**
 * AI 검색 도우미 챗봇
 * POST /chat/search-assistant
 */
export async function askSearchAssistant(message) {
  const response = await api.post("/chat/search-assistant", {
    message,
  });

  return response.data;
}

/**
 * 기존 페이지 코드 호환용 별칭
 */
export const fetchIssues = fetchDashboard;
export const fetchIssueDetail = fetchDashboardDetail;