import { Link } from "react-router-dom";
import "../styles/SubPage.css";

const flowCards = [
  {
    label: "시연 단계 1",
    title: "데이터 수집",
    description:
      "공공 민원 데이터를 가져와 필요한 항목을 정리하고 분석 가능한 형태로 준비합니다.",
    chips: ["공공 API", "수집", "전처리"],
  },
  {
    label: "시연 단계 2",
    title: "이슈 생성",
    description:
      "민원 흐름과 키워드 변화를 기반으로 주요 이슈를 만들고 요약, 위험도, 원인 후보를 연결합니다.",
    chips: ["이슈 생성", "요약", "위험도"],
    highlight: true,
  },
  {
    label: "시연 단계 3",
    title: "화면 반영",
    description:
      "생성된 결과를 대시보드와 브리핑 카드에 연결하여 사용자가 바로 볼 수 있게 합니다.",
    chips: ["API 연동", "대시보드", "시각화"],
  },
];

function DemoFlowPage() {
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
          <div className="subpage-badge">서비스 시연 흐름</div>
          <h1 className="subpage-title">
            데이터가 화면으로 이어지는
            <br />
            전체 시연 과정
          </h1>
          <p className="subpage-subtitle">
            수집된 민원 데이터가 분석되고, 이슈로 정리된 뒤, 최종적으로 메인 화면과
            대시보드에 반영되는 흐름을 단계별로 보여주는 페이지입니다.
          </p>
        </div>

        <div className="subpage-main-card">
          <div className="subpage-grid">
            {flowCards.map((card) => (
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
              <div className="subpage-label">흐름 요약</div>
              <div className="subpage-info-title">수집 → 분석 → 반영</div>
              <div className="subpage-info-desc">
                전체 시연은 데이터를 가져오는 단계부터 이슈를 정리하고
                프론트 화면에 반영하는 단계까지 자연스럽게 이어지도록 구성됩니다.
              </div>
            </div>

            <div className="subpage-info-card">
              <div className="subpage-label">발표 포인트</div>
              <div className="subpage-info-title">서비스 동작 구조를 한눈에 설명</div>
              <div className="subpage-info-desc">
                이 페이지는 캡스톤 발표나 시연 때,
                서비스가 어떻게 동작하는지 순서대로 설명하는 데 적합합니다.
              </div>
            </div>

            <div className="subpage-info-card">
              <div className="subpage-label">연결 의미</div>
              <div className="subpage-info-title">백엔드와 프론트 연결 결과</div>
              <div className="subpage-info-desc">
                분석 결과가 실제 화면에 반영된다는 점을 보여주기 때문에
                팀 프로젝트 전체 흐름을 설명하는 핵심 페이지가 됩니다.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default DemoFlowPage;