import { Link } from "react-router-dom";
import "../styles/DemoFlowPage.css";

const flowSteps = [
  {
    number: "01",
    label: "민원 데이터 수집",
    title: "공공 민원 데이터를 자동으로 가져옵니다",
    description:
      "국민권익위원회 민원 빅데이터 API를 기반으로 급등 키워드, 오늘의 이슈, 연관 키워드, 민원 건수 데이터를 수집합니다.",
    tags: ["공공데이터 API", "민원 데이터", "키워드 수집"],
  },
  {
    number: "02",
    label: "키워드·이슈 분석",
    title: "반복적으로 증가하는 민원 흐름을 분석합니다",
    description:
      "수집된 키워드와 민원 흐름을 바탕으로 어떤 이슈가 최근 증가하고 있는지 판단하고, 관련 키워드를 함께 묶어 분석합니다.",
    tags: ["급등 키워드", "연관어", "이슈 탐지"],
    highlight: true,
  },
  {
    number: "03",
    label: "AI 요약 생성",
    title: "복잡한 민원 내용을 짧게 요약합니다",
    description:
      "민원 건수, 변화율, 주요 키워드, 원인 후보를 바탕으로 사용자가 쉽게 이해할 수 있는 요약과 전망 문장을 생성합니다.",
    tags: ["AI 브리핑", "요약", "전망"],
  },
  {
    number: "04",
    label: "대시보드 표시",
    title: "분석 결과를 화면에서 바로 확인합니다",
    description:
      "오늘의 이슈, 위험도, 연관 키워드, 지역별 민원, 기관별 순위 등을 카드형 대시보드와 지도 화면으로 시각화합니다.",
    tags: ["대시보드", "지도", "시각화"],
  },
];

const demoScenario = [
  {
    title: "사용자 진입",
    description: "메인 화면에서 오늘 감지된 핵심 민원 이슈를 확인합니다.",
  },
  {
    title: "이슈 선택",
    description: "관심 있는 민원 이슈를 클릭해 상세 요약과 위험도를 확인합니다.",
  },
  {
    title: "키워드 확인",
    description: "연관 키워드와 원인 후보를 통해 민원 발생 배경을 파악합니다.",
  },
  {
    title: "지역 분석",
    description: "지도와 순위 데이터를 통해 어느 지역에 민원이 집중되는지 확인합니다.",
  },
];

const checkItems = [
  "API 데이터 수집 여부 확인",
  "이슈 요약 및 위험도 표시",
  "연관 키워드와 원인 후보 확인",
  "지역별 민원 시각화 확인",
  "검색 및 주제별 민원 페이지 연동",
];

function DemoFlowPage() {
  return (
    <main className="demo-flow-page">
      <div className="demo-flow-container">
        <div className="demo-flow-topbar">
          <div className="demo-flow-logo">
            <span />
          </div>

          <Link to="/" className="demo-flow-back-link">
            메인으로 돌아가기
          </Link>
        </div>

        <section className="demo-flow-hero">
          <div className="demo-flow-hero-text">
            <span className="demo-flow-badge">시연 흐름</span>

            <h1>
              민원 데이터가
              <br />
              화면에 표시되기
              <br />
              까지
            </h1>

            <p>
              공공데이터 API에서 민원 데이터를 수집하고, 키워드 분석과 AI 요약을
              거쳐 사용자가 볼 수 있는 대시보드 화면으로 연결되는 전체 흐름을
              단계별로 보여줍니다.
            </p>

            <div className="demo-flow-actions">
              <Link to="/dashboard" className="demo-flow-primary-button">
                분석 대시보드 보기
              </Link>
              <Link to="/complaints" className="demo-flow-secondary-button">
                민원 보기
              </Link>
            </div>
          </div>

          <div className="demo-flow-hero-card">
            <div className="demo-flow-mini-header">
              <span>실시간 처리 흐름</span>
              <strong>Running</strong>
            </div>

            <div className="demo-flow-pipeline">
              <div>
                <b>API</b>
                <span>데이터 수집</span>
              </div>
              <div>
                <b>AI</b>
                <span>요약 생성</span>
              </div>
              <div>
                <b>DB</b>
                <span>결과 저장</span>
              </div>
              <div>
                <b>WEB</b>
                <span>화면 표시</span>
              </div>
            </div>

            <div className="demo-flow-progress-card">
              <div className="progress-top">
                <span>시연 준비도</span>
                <strong>92%</strong>
              </div>
              <div className="progress-track">
                <div className="progress-fill" />
              </div>
              <p>데이터 수집, 분석, 대시보드 표시 흐름을 기준으로 구성했습니다.</p>
            </div>
          </div>
        </section>

        <section className="demo-flow-summary-grid">
          <article>
            <span>수집</span>
            <strong>API</strong>
            <p>민원 데이터를 자동으로 가져옵니다.</p>
          </article>

          <article className="active">
            <span>분석</span>
            <strong>AI</strong>
            <p>키워드와 민원 흐름을 요약합니다.</p>
          </article>

          <article>
            <span>저장</span>
            <strong>DB</strong>
            <p>분석 결과를 서버 DB에 저장합니다.</p>
          </article>

          <article>
            <span>표시</span>
            <strong>WEB</strong>
            <p>사용자 화면에 카드와 지도로 보여줍니다.</p>
          </article>
        </section>

        <section className="demo-flow-main-section">
          <div className="demo-flow-section-header">
            <span>전체 프로세스</span>
            <h2>시연은 아래 흐름으로 진행됩니다</h2>
          </div>

          <div className="demo-flow-step-list">
            {flowSteps.map((step) => (
              <article
                key={step.number}
                className={`demo-flow-step-card ${
                  step.highlight ? "highlight" : ""
                }`}
              >
                <div className="step-number">{step.number}</div>

                <div className="step-content">
                  <span className="step-label">{step.label}</span>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>

                  <div className="step-tag-wrap">
                    {step.tags.map((tag) => (
                      <span key={tag}>{tag}</span>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="demo-flow-bottom-grid">
          <div className="demo-flow-scenario-card">
            <div className="demo-flow-section-header small">
              <span>사용자 시나리오</span>
              <h2>실제 화면에서 보는 순서</h2>
            </div>

            <div className="scenario-list">
              {demoScenario.map((item, index) => (
                <div key={item.title} className="scenario-item">
                  <b>{index + 1}</b>
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="demo-flow-check-card">
            <div className="demo-flow-section-header small">
              <span>시연 체크리스트</span>
              <h2>시연전 확인해야할 항목</h2>
            </div>

            <div className="check-list">
              {checkItems.map((item) => (
                <div key={item} className="check-item">
                  <span>✓</span>
                  <p>{item}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

export default DemoFlowPage;