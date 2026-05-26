import axios from "axios";

const API_BASE_URL = "http://211.188.50.216:8000";

/**
 * 대시보드 목록 조회
 * GET /dashboard
 */
export async function fetchDashboard() {
  const response = await axios.get(`${API_BASE_URL}/dashboard`);
  return response.data;
}

/**
 * 이슈 상세 조회
 * GET /dashboard/{id}
 */
export async function fetchDashboardDetail(id) {
  const response = await axios.get(`${API_BASE_URL}/dashboard/${id}`);
  return response.data;
}

/**
 * 분야별 이슈 묶음 조회
 * GET /dashboard/categories
 */
export async function fetchDashboardCategories() {
  const response = await axios.get(`${API_BASE_URL}/dashboard/categories`);
  return response.data;
}

/**
 * 지도/지역/기관/연령 분석 데이터 조회
 * GET /dashboard/map-data
 */
export async function fetchDashboardMapData() {
  const response = await axios.get(`${API_BASE_URL}/dashboard/map-data`);
  return response.data;
}

/**
 * 통합검색
 * GET /search?query=검색어
 */
export async function searchIssues(query) {
  const response = await axios.get(`${API_BASE_URL}/search`, {
    params: { query },
  });

  return response.data;
}

/**
 * 자주 찾는 검색어
 * GET /search/popular-keywords
 */
export async function fetchPopularKeywords() {
  const response = await axios.get(`${API_BASE_URL}/search/popular-keywords`);
  return response.data;
}

/**
 * 검색 자동완성
 * GET /search/suggestions?query=입력값
 */
export async function fetchSearchSuggestions(query) {
  const response = await axios.get(`${API_BASE_URL}/search/suggestions`, {
    params: query ? { query } : {},
  });

  return response.data;
}

/**
 * AI 검색 도우미 챗봇
 * POST /chat/search-assistant
 */
export async function askSearchAssistant(message) {
  const response = await axios.post(`${API_BASE_URL}/chat/search-assistant`, {
    message,
  });

  return response.data;
}

/**
 * 기존 페이지 코드 호환용 별칭
 * 다른 페이지에서 fetchIssues, fetchIssueDetail로 import해도 오류 안 나게 함
 */
export const fetchIssues = fetchDashboard;
export const fetchIssueDetail = fetchDashboardDetail;