import { Link } from "react-router-dom";
import "../styles/TechStackPage.css";

const coreStacks = [
  {
    label: "Frontend",
    title: "React + Vite",
    description:
      "사용자가 보는 메인 화면, 민원 보기, 분석 대시보드, 지도 기반 화면을 구성합니다.",
    tags: ["React", "Vite", "Router", "Axios"],
  },
  {
    label: "Backend",
    title: "FastAPI",
    description:
      "프론트엔드에서 필요한 민원 이슈 목록, 상세 조회, 검색, 대시보드 데이터를 API로 제공합니다.",
    tags: ["FastAPI", "REST API", "CORS", "Server"],
    main: true,
  },
  {
    label: "Database",
    title: "PostgreSQL",
    description:
      "수집·분석된 민원 이슈, 키워드, 원인, 요약, 지도 분석 데이터를 저장하고 조회합니다.",
    tags: ["PostgreSQL", "SQLAlchemy", "Issue Data"],
  },
];

const architectureItems = [
  {
    step: "01",
    title: "공공데이터 수집",
    text: "국민권익위원회 민원 빅데이터 API에서 급등 키워드, 오늘의 이슈, 연관 키워드 데이터를 가져옵니다.",
  },
  {
    step: "02",
    title: "분석 결과 생성",
    text: "민원 건수, 변화율, 위험도, 연관어를 기반으로 이슈 단위의 분석 결과를 만듭니다.",
  },
  {
    step: "03",
    title: "DB 저장",
    text: "분석된 이슈, 요약, 키워드, 원인 후보를 PostgreSQL에 저장합니다.",
  },
  {
    step: "04",
    title: "화면 표시",
    text: "React 화면에서 API를 호출해 대시보드, 검색, 지도, 주제별 민원 페이지에 표시합니다.",
  },
];

const apiItems = [
  {
    method: "GET",
    path: "/dashboard",
    desc: "메인 대시보드 이슈 목록 조회",
  },
  {
    method: "GET",
    path: "/dashboard/categories",
    desc: "주제별 민원 이슈 묶음 조회",
  },
  {
    method: "GET",
    path: "/dashboard/map-data",
    desc: "지역·기관·카테고리 분석 데이터 조회",
  },
  {
    method: "GET",
    path: "/search",
    desc: "키워드 기반 민원 이슈 검색",
  },
];

const roleCards = [
  {
    title: "프론트엔드",
    desc: "사용자가 이해하기 쉬운 화면을 만들고, API 응답을 카드·그래프·지도 형태로 시각화합니다.",
  },
  {
    title: "백엔드",
    desc: "프론트에서 필요한 데이터를 정리해 전달하고, DB와 API 사이의 흐름을 안정적으로 연결합니다.",
  },
  {
    title: "데이터베이스",
    desc: "이슈, 요약, 키워드, 원인, 지도 분석 데이터를 저장하고 빠르게 조회할 수 있게 관리합니다.",
  },
];

function TechStackPage() {
  return (
    <main className="tech-page">
      <div className="tech-container">
        <div className="tech-topbar">
          <div className="tech-symbol">
            <span />
            <span />
            <span />
          </div>

          <Link to="/" className="tech-back-link">
            메인으로 돌아가기
          </Link>
        </div>

        <section className="tech-hero">
          <div className="tech-hero-left">
            <span className="tech-badge">프로젝트 기술 스택</span>

            <h1>
              민원 데이터를
              <br />
              서비스로 연결
              <br />
              하는 기술 구조
            </h1>

            <p>
              이 프로젝트는 공공데이터 API에서 민원 데이터를 수집하고, 백엔드에서
              분석 결과를 저장한 뒤, 프론트엔드에서 사용자가 이해하기 쉬운 화면으로
              보여주는 구조로 구성되어 있습니다.
            </p>

            <div className="tech-hero-buttons">
              <Link to="/dashboard" className="tech-primary-button">
                대시보드 보기
              </Link>
              <Link to="/demo" className="tech-secondary-button">
                시연 흐름 보기
              </Link>
            </div>
          </div>

          <div className="tech-hero-right">
            <div className="tech-system-card">
              <div className="system-center">
                <span>MINWON</span>
                <strong>AI</strong>
              </div>

              <div className="system-node node-front">
                <b>React</b>
                <span>화면 구성</span>
              </div>

              <div className="system-node node-api">
                <b>FastAPI</b>
                <span>API 서버</span>
              </div>

              <div className="system-node node-db">
                <b>PostgreSQL</b>
                <span>데이터 저장</span>
              </div>

              <div className="system-node node-data">
                <b>Public API</b>
                <span>민원 데이터</span>
              </div>
            </div>
          </div>
        </section>

        <section className="tech-stack-section">
          <div className="tech-section-heading">
            <span>Core Stack</span>
            <h2>서비스 구현에 사용한 핵심 기술</h2>
          </div>

          <div className="tech-stack-grid">
            {coreStacks.map((stack) => (
              <article
                key={stack.label}
                className={`tech-stack-card ${stack.main ? "main" : ""}`}
              >
                <div className="tech-stack-label">{stack.label}</div>
                <h3>{stack.title}</h3>
                <p>{stack.description}</p>

                <div className="tech-tag-wrap">
                  {stack.tags.map((tag) => (
                    <span key={tag}>{tag}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="tech-architecture-section">
          <div className="tech-section-heading">
            <span>Architecture</span>
            <h2>데이터가 화면까지 전달되는 흐름</h2>
          </div>

          <div className="architecture-timeline">
            {architectureItems.map((item) => (
              <article key={item.step} className="architecture-item">
                <div className="architecture-step">{item.step}</div>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="tech-api-section">
          <div className="tech-api-left">
            <div className="tech-section-heading">
              <span>API Connection</span>
              <h2>프론트와 백엔드를 연결하는 주요 API</h2>
            </div>

            <p className="tech-api-desc">
              프론트엔드는 Axios를 이용해 백엔드 API를 호출하고, 응답받은 데이터를
              화면의 카드, 검색 결과, 지도 분석, 주제별 민원 목록으로 표시합니다.
            </p>
          </div>

          <div className="tech-api-list">
            {apiItems.map((api) => (
              <article key={api.path} className="tech-api-card">
                <div>
                  <span className="api-method">{api.method}</span>
                  <strong>{api.path}</strong>
                </div>
                <p>{api.desc}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="tech-role-section">
          {roleCards.map((role) => (
            <article key={role.title} className="tech-role-card">
              <h3>{role.title}</h3>
              <p>{role.desc}</p>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

export default TechStackPage;