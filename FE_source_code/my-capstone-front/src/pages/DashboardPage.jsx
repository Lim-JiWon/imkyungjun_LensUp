import { Link } from "react-router-dom";
import "../styles/SubPage.css";

const dashboardCards = [
  {
    label: "대시보드 요소 1",
    title: "오늘의 민원 이슈",
    description:
      "현재 선택된 이슈의 제목, 상태, 출처, 위험도를 중심으로 핵심 현황을 보여줍니다.",
    chips: ["이슈 제목", "상태", "위험도"],
  },
  {
    label: "대시보드 요소 2",
    title: "연관 키워드와 원인",
    description:
      "이슈와 함께 자주 등장하는 키워드와 원인 후보를 함께 배치해 맥락을 빠르게 이해할 수 있습니다.",
    chips: ["연관 키워드", "원인 후보", "맥락 파악"],
    highlight: true,
  },
  {
    label: "대시보드 요소 3",
    title: "이슈 강도와 요약",
    description:
      "점수 기반 강도 표시와 AI 브리핑을 통해 현재 이슈가 얼마나 중요한지 직관적으로 확인할 수 있습니다.",
    chips: ["점수", "AI 브리핑", "중요도"],
  },
];

function DashboardPage() {
  return (
    <section className="subpage-section">
      <div className="subpage-container">
        <div className="subpage-topbar">
          <div></div>
          <Link to="/" className="subpage-back-link">
            ← 메인으로 돌아가기
          </Link>
        </div>

        <div className="subpage-hero">
          <div className="subpage-badge">분석 대시보드 소개</div>
          <h1 className="subpage-title">
            한 화면에서 보는
            <br />
            민원 이슈 분석
          </h1>
          <p className="subpage-subtitle">
            오늘의 민원 이슈, AI 브리핑, 연관 키워드, 이슈 강도, 원인 분석을
            한 화면 안에서 확인할 수 있도록 구성한 대시보드입니다.
          </p>
        </div>

        <div className="subpage-main-card">
          <div className="subpage-grid">
            {dashboardCards.map((card) => (
              <div
                key={card.title}
                className={`subpage-card ${card.highlight ? "highlight" : ""}`}
              >
                <div className="subpage-label">{card.label}</div>
                <div className="subpage-card-title">{card.title}</div>
                <div className="subpage-card-desc">{card.description}</div>
                <div className="subpage-chip-wrap">
                  {card.chips.map((chip) => (
                    <span key={chip} className="subpage-chip">
                      {chip}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="subpage-bottom-grid">
            <div className="subpage-info-card">
              <div className="subpage-label">시각화 목적</div>
              <div className="subpage-info-title">데이터를 바로 읽히게 구성</div>
              <div className="subpage-info-desc">
                복잡한 분석 결과를 표와 수치만 보여주는 대신, 카드형 UI와 점수,
                키워드, 요약 구조로 더 쉽게 읽히도록 설계합니다.
              </div>
            </div>

            <div className="subpage-info-card">
              <div className="subpage-label">주요 데이터</div>
              <div className="subpage-info-title">상태 · 위험도 · 키워드</div>
              <div className="subpage-info-desc">
                현재 이슈 상태와 위험도, 연관 키워드, 원인 후보를 묶어서 보여주기 때문에
                사용자가 핵심 정보를 빠르게 파악할 수 있습니다.
              </div>
            </div>

            <div className="subpage-info-card">
              <div className="subpage-label">활용 방식</div>
              <div className="subpage-info-title">실시간 탐지 결과 확인</div>
              <div className="subpage-info-desc">
                선택한 이슈를 기준으로 상세 정보가 바뀌는 흐름을 통해,
                실제 데모 시나리오에서 바로 활용할 수 있게 구성합니다.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default DashboardPage; 