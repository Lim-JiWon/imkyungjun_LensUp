const API_BASE_URL = "http://211.188.50.216:8000";

export async function fetchSearchResults(query) {
  const searchParams = new URLSearchParams({
    query,
  });

  const response = await fetch(`${API_BASE_URL}/search?${searchParams.toString()}`);

  if (!response.ok) {
    throw new Error("검색 결과를 불러오지 못했습니다.");
  }

  const data = await response.json();

  return data;
}