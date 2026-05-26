import { Link } from "react-router-dom";
import "../styles/TeamIntroPage.css";

const teamMembers = [
  {
    role: "Backend 1",
    name: "임지원",
    shortName: "B1",
    title: "데이터 수집·분석 파이프라인",
    description:
      "공공 민원 데이터를 수집하고 전처리한 뒤, 분석 결과와 요약에 필요한 기반 데이터를 생성합니다.",
    tasks: ["공공데이터 API", "전처리", "분석 결과 생성", "키워드 추출"],
    color: "blue",
  },
  {
    role: "Backend 2",
    name: "박경수",
    shortName: "B2",
    title: "서버·DB·API·배포",
    description:
      "FastAPI 서버와 PostgreSQL DB를 구성하고, 프론트엔드가 사용할 수 있는 API와 배포 환경을 담당합니다.",
    tasks: ["FastAPI 서버", "DB 설계", "API 연동", "배포 관리"],
    color: "dark",
    highlight: true,
  },
  {
    role: "Frontend",
    name: "차도준",
    shortName: "FE",
    title: "사용자 화면·시각화 구현",
    description:
      "메인 화면, 분석 대시보드, 지도 기반 화면, 주제별 민원 페이지 등 사용자가 직접 보는 UI를 구현합니다.",
    tasks: ["React UI", "대시보드", "지도 화면", "사용자 흐름"],
    color: "sky",
  },
];

const collaborationSteps = [
  {
    number: "01",
    title: "데이터 수집",
    text: "공공데이터 API에서 민원 키워드와 이슈 데이터를 가져옵니다.",
  },
  {
    number: "02",
    title: "분석 결과 생성",
    text: "민원 흐름, 연관 키워드, 위험도, 원인 후보를 정리합니다.",
  },
  {
    number: "03",
    title: "서버 저장·API 제공",
    text: "분석 결과를 DB에 저장하고 프론트에서 사용할 API로 제공합니다.",
  },
  {
    number: "04",
    title: "화면 시각화",
    text: "사용자가 이해하기 쉬운 카드, 지도, 검색 화면으로 표현합니다.",
  },
];

const projectValues = [
  {
    label: "Problem",
    title: "민원 속 사회문제 조짐 파악",
    description:
      "단순 민원 목록이 아니라 반복적으로 증가하는 키워드와 지역·기관 흐름을 통해 문제의 조짐을 빠르게 확인합니다.",
  },
  {
    label: "Solution",
    title: "AI 기반 이슈 요약과 대시보드",
    description:
      "분석된 민원 데이터를 요약, 위험도, 키워드, 지도 시각화로 제공하여 복잡한 데이터를 쉽게 이해할 수 있게 합니다.",
  },
  {
    label: "Goal",
    title: "시연 가능한 완성형 서비스",
    description:
      "데이터 수집부터 API 연동, 화면 표시까지 하나의 흐름으로 연결해 캡스톤 발표에서 바로 보여줄 수 있는 데모를 목표로 합니다.",
  },
];

function TeamIntroPage() {
  return (
    <main className="team-page">
      <div className="team-container">
        <div className="team-topbar">
          <div className="team-brand">
            <span className="brand-dot" />
            <span>Team 즉석의 낭만</span>
          </div>

          <Link to="/" className="team-back-link">
            메인으로 돌아가기
          </Link>
        </div>

        <section className="team-hero">
          <div className="team-hero-content">
            <span className="team-badge">캡스톤 프로젝트 팀 소개</span>

            <h1>
              민원 데이터로
              <br />
              사회문제의 조짐을 찾는 팀
            </h1>

            <p>
              우리 팀은 공공 민원 데이터를 기반으로 급증하는 이슈를 감지하고,
              사용자가 쉽게 이해할 수 있는 대시보드 서비스로 연결하는 것을 목표로
              개발하고 있습니다.
            </p>

            <div className="team-hero-actions">
              <Link to="/demo" className="team-primary-button">
                시연 흐름 보기
              </Link>
              <Link to="/stack" className="team-secondary-button">
                기술 스택 보기
              </Link>
            </div>
          </div>

          <div className="team-hero-visual">
            <div className="team-orbit-card">
              <div className="orbit-center">
                <span>TEAM</span>
                <strong>3</strong>
              </div>

              <div className="orbit-member orbit-member-1">
                <b>B1</b>
                <span>Data Pipeline</span>
              </div>

              <div className="orbit-member orbit-member-2">
                <b>B2</b>
                <span>Server API</span>
              </div>

              <div className="orbit-member orbit-member-3">
                <b>FE</b>
                <span>Web UI</span>
              </div>
            </div>
          </div>
        </section>

        <section className="team-summary-grid">
          <article>
            <span>Team Size</span>
            <strong>3명</strong>
            <p>Backend 1, Backend 2, Frontend로 역할을 분담합니다.</p>
          </article>

          <article className="active">
            <span>Main Goal</span>
            <strong>징후 탐지</strong>
            <p>민원 흐름에서 사회문제의 조짐을 빠르게 파악합니다.</p>
          </article>

          <article>
            <span>Project Type</span>
            <strong>AI Service</strong>
            <p>데이터 분석 결과를 웹 서비스 형태로 제공합니다.</p>
          </article>
        </section>

        <section className="team-member-section">
          <div className="team-section-heading">
            <span>Members</span>
            <h2>각자의 역할이 하나의 서비스로 연결됩니다</h2>
          </div>

          <div className="team-member-grid">
            {teamMembers.map((member) => (
              <article
                key={member.role}
                className={`team-member-card ${member.highlight ? "highlight" : ""}`}
              >
                <div className={`member-avatar ${member.color}`}>
                  {member.shortName}
                </div>

                <div className="member-role">{member.role}</div>
                <h3>{member.name}</h3>
                <strong>{member.title}</strong>
                <p>{member.description}</p>

                <div className="member-task-wrap">
                  {member.tasks.map((task) => (
                    <span key={task}>{task}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="team-collaboration-section">
          <div className="team-section-heading">
            <span>Collaboration</span>
            <h2>우리 팀의 개발 흐름</h2>
          </div>

          <div className="collaboration-line">
            {collaborationSteps.map((step) => (
              <article key={step.number} className="collaboration-card">
                <div className="collaboration-number">{step.number}</div>
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="team-value-section">
          <div className="team-value-left">
            <span className="team-badge">Project Identity</span>
            <h2>
              우리가 만드는 서비스의
              <br />
              핵심 방향
            </h2>
            <p>
              단순히 데이터를 보여주는 것이 아니라, 민원 속에서 반복적으로
              나타나는 문제의 신호를 발견하고 사용자가 바로 이해할 수 있게
              정리하는 것을 중요하게 생각합니다.
            </p>
          </div>

          <div className="team-value-list">
            {projectValues.map((value) => (
              <article key={value.label} className="team-value-card">
                <span>{value.label}</span>
                <h3>{value.title}</h3>
                <p>{value.description}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

export default TeamIntroPage;