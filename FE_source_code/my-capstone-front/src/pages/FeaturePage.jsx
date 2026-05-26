import "../styles/FeaturePage.css";
import { Link } from "react-router-dom";

const features = [
  {
    number: "01",
    title: "민원 징후 탐지",
    description:
      "공공 민원 데이터에서 갑자기 증가하는 이슈를 감지하고, 위험도를 점수와 단계로 보여줍니다.",
    detail: "급등 키워드, 민원 건수, 위험 점수를 함께 분석",
  },
  {
    number: "02",
    title: "핵심·급등 키워드 분석",
    description:
      "현재 민원에서 중요하게 떠오르는 핵심 키워드와 급등 키워드를 분리해 보여줍니다.",
    detail: "핵심 키워드 · 급등 키워드 · 연관 키워드 제공",
  },
  {
    number: "03",
    title: "AI 요약과 전망",
    description:
      "수집된 민원 흐름을 바탕으로 현재 상황을 요약하고, 앞으로 확산될 가능성을 문장으로 설명합니다.",
    detail: "요약 · 원인 · 향후 전망 자동 생성",
  },
  {
    number: "04",
    title: "키워드 트렌드 시각화",
    description:
      "특정 키워드가 시간에 따라 어떻게 변화했는지 확인할 수 있어 이슈의 흐름을 빠르게 파악할 수 있습니다.",
    detail: "일자별 키워드 변화 추적",
  },
  {
    number: "05",
    title: "민원 검색과 자동완성",
    description:
      "사용자가 입력한 검색어와 관련된 민원 이슈를 찾고, 유사 키워드까지 함께 추천합니다.",
    detail: "검색어 별칭 · 연관어 · 자동완성 지원",
  },
  {
    number: "06",
    title: "대시보드 기반 운영",
    description:
      "전체 이슈 수, 고위험 이슈, 평균 점수 등을 한 화면에서 확인해 운영자가 빠르게 상황을 판단할 수 있습니다.",
    detail: "Backend2 API 기반 실시간 화면 구성",
  },
];

export default function CoreFeaturesPage() {
  return (
    <main className="core-page">
      <section className="core-hero">
        <Link to="/" className="back-main-link">
          ← 메인으로 돌아가기
        </Link>

        <div className="hero-label">Public Complaint Intelligence</div>

        <h1>
          민원 데이터를 읽고,
          <br />
          사회 이슈의 징후를 먼저 발견합니다.
        </h1>

        <p>
          흩어져 있는 공공 민원 데이터를 분석해 핵심 키워드, 급등 흐름,
          위험도, 요약과 전망까지 한 화면에서 확인할 수 있는 AI 기반 민원
          분석 시스템입니다.
        </p>
      </section>

      <section className="core-intro">
        <div>
          <span className="section-kicker">Core Features</span>
          <h2>복잡한 민원 흐름을 쉽게 이해할 수 있게</h2>
        </div>

        <p>
          단순히 데이터를 보여주는 것이 아니라, 어떤 이슈가 커지고 있는지,
          왜 중요한지, 앞으로 어떻게 확산될 수 있는지를 사용자가 빠르게
          판단할 수 있도록 구성했습니다.
        </p>
      </section>

      <section className="feature-grid">
        {features.map((feature) => (
          <article className="feature-card" key={feature.number}>
            <div className="feature-top">
              <span>{feature.number}</span>
              <div className="feature-dot" />
            </div>

            <h3>{feature.title}</h3>
            <p>{feature.description}</p>

            <div className="feature-detail">{feature.detail}</div>
          </article>
        ))}
      </section>

      <section className="core-highlight">
        <div className="highlight-content">
          <span className="section-kicker">Why it matters</span>
          <h2>
            민원은 단순한 불편 신고가 아니라,
            <br />
            사회 문제의 초기 신호일 수 있습니다.
          </h2>
          <p>
            이 시스템은 민원 데이터를 기반으로 반복적으로 등장하는 문제와
            갑자기 증가하는 키워드를 분석하여, 행정 대응이 필요한 이슈를 더
            빠르게 발견할 수 있도록 돕습니다.
          </p>
        </div>

        <div className="highlight-panel">
          <div className="panel-item">
            <strong>45.0</strong>
            <span>징후 점수</span>
          </div>
          <div className="panel-item">
            <strong>360건</strong>
            <span>관련 민원</span>
          </div>
          <div className="panel-item">
            <strong>WATCH</strong>
            <span>관찰 필요</span>
          </div>
        </div>
      </section>
    </main>
  );
}