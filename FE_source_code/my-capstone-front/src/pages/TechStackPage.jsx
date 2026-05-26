import { Link } from "react-router-dom";
import "../styles/SubPage.css";

const stackCards = [
  {
    label: "Frontend",
    title: "React",
    description:
      "메인 화면, 분석 대시보드, 시연 흐름, 팀 소개 같은 사용자 화면을 구성합니다.",
    chips: ["React", "Vite", "UI 구성"],
  },
  {
    label: "Backend",
    title: "FastAPI",
    description:
      "이슈 목록, 상세 조회, 분석 데이터 전달을 위한 API 서버와 연동 구조를 담당합니다.",
    chips: ["FastAPI", "REST API", "데이터 연동"],
    highlight: true,
  },
  {
    label: "Database",
    title: "PostgreSQL",
    description:
      "수집 및 분석된 이슈 데이터와 키워드, 원인 정보 등을 저장하고 조회합니다.",
    chips: ["PostgreSQL", "저장", "조회"],
  },
];

function TechStackPage() {
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
          <div className="subpage-badge">프로젝트 기술 스택</div>
          <h1 className="subpage-title">
            서비스 구현에 사용한
            <br />
            주요 기술 구성
          </h1>
          <p className="subpage-subtitle">
            프론트엔드, 백엔드, 데이터베이스, API 연동 구조를 중심으로
            캡스톤 프로젝트 데모에 맞춘 기술 스택을 정리한 페이지입니다.
          </p>
        </div>

        <div className="subpage-main-card">
          <div className="subpage-grid">
            {stackCards.map((card) => (
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
              <div className="subpage-label">프론트엔드 역할</div>
              <div className="subpage-info-title">사용자가 보는 화면 구성</div>
              <div className="subpage-info-desc">
                메인 랜딩, 분석 카드, 팀 소개, 시연 흐름 같은 페이지를 구성하고
                백엔드 API 결과를 사용자 화면에 시각적으로 반영합니다.
              </div>
            </div>

            <div className="subpage-info-card">
              <div className="subpage-label">백엔드 역할</div>
              <div className="subpage-info-title">데이터 전달과 서비스 로직 처리</div>
              <div className="subpage-info-desc">
                수집·분석된 결과를 저장하고 프론트에서 필요한 형태로 조회할 수 있도록
                API를 제공하는 역할을 담당합니다.
              </div>
            </div>

            <div className="subpage-info-card">
              <div className="subpage-label">프로젝트 구조</div>
              <div className="subpage-info-title">화면과 데이터의 연결 중심</div>
              <div className="subpage-info-desc">
                각 영역이 분리되어 있지만 API를 기준으로 자연스럽게 연결되도록 설계하여
                실제 캡스톤 데모에 적합한 구조를 만듭니다.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default TechStackPage;