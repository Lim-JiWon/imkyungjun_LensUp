const API_BASE_URL = "http://211.188.50.216:8000";

export async function fetchDashboard() {
  const response = await fetch(`${API_BASE_URL}/dashboard`);

  if (!response.ok) {
    throw new Error("대시보드 데이터를 불러오지 못했습니다.");
  }

  const data = await response.json();

  // 혹시 응답이 { data: { issues: [] } } 형태여도 대응
  return data.data ?? data;
}

export async function fetchIssueDetail(issueId) {
  const response = await fetch(`${API_BASE_URL}/issues/${issueId}`);

  if (!response.ok) {
    throw new Error("이슈 상세 데이터를 불러오지 못했습니다.");
  }

  const data = await response.json();

  return data.data ?? data;
}