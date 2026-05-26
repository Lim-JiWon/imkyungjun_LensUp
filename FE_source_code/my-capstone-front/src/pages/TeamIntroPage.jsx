import { Link } from "react-router-dom";

const teamMembers = [
  {
    role: "Backend 1",
    name: "팀원 1",
    description:
      "공공 민원 데이터 수집, 전처리, 분석 결과 생성 파이프라인을 담당합니다.",
    tasks: ["데이터 수집", "전처리", "분석 결과 생성"],
  },
  {
    role: "Backend 2",
    name: "팀원 2",
    description:
      "서버, DB, API, 배포 환경을 구축하고 프론트와의 데이터 연동을 담당합니다.",
    tasks: ["FastAPI 서버", "DB 설계", "API 연동", "배포"],
    highlight: true,
  },
  {
    role: "Frontend",
    name: "팀원 3",
    description:
      "메인 화면, 대시보드 UI, 사용자 흐름과 시각화 화면 구현을 담당합니다.",
    tasks: ["React UI", "대시보드", "시각화"],
  },
];

const sectionStyle = {
  minHeight: "100vh",
  background: "linear-gradient(180deg, #eef5ff 0%, #f8fbff 100%)",
  padding: "110px 24px 80px",
  color: "#111827",
};

const containerStyle = {
  maxWidth: "1200px",
  margin: "0 auto",
};

const topNavStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "24px",
};

const linkStyle = {
  color: "#2573c2",
  fontWeight: 700,
  textDecoration: "none",
  fontSize: "15px",
};

const badgeStyle = {
  display: "inline-block",
  padding: "10px 18px",
  borderRadius: "999px",
  background: "rgba(255,255,255,0.78)",
  border: "1px solid rgba(255,255,255,0.9)",
  boxShadow: "0 10px 24px rgba(89, 130, 200, 0.08)",
  fontSize: "14px",
  fontWeight: 700,
  color: "#4b5563",
};

const titleStyle = {
  fontSize: "clamp(42px, 7vw, 78px)",
  lineHeight: 1.15,
  fontWeight: 900,
  letterSpacing: "-0.04em",
  margin: "24px 0 18px",
  color: "#0f172a",
};

const subtitleStyle = {
  fontSize: "clamp(17px, 2vw, 22px)",
  lineHeight: 1.8,
  color: "#5b6473",
  maxWidth: "880px",
  margin: "0 auto",
};

const heroCardStyle = {
  marginTop: "42px",
  background: "rgba(255,255,255,0.58)",
  border: "1px solid rgba(255,255,255,0.85)",
  backdropFilter: "blur(12px)",
  borderRadius: "34px",
  padding: "24px",
  boxShadow: "0 20px 60px rgba(71, 133, 255, 0.12)",
};

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  gap: "20px",
  marginTop: "10px",
};

const getMemberCardStyle = (highlight) => ({
  background: highlight
    ? "linear-gradient(135deg, #f8fbff 0%, #ffffff 45%, #eaf3ff 100%)"
    : "rgba(255,255,255,0.86)",
  border: highlight
    ? "1px solid rgba(86, 168, 255, 0.28)"
    : "1px solid rgba(255,255,255,0.9)",
  borderRadius: "28px",
  padding: "24px",
  boxShadow: highlight
    ? "0 18px 40px rgba(71, 133, 255, 0.14)"
    : "0 10px 24px rgba(89, 130, 200, 0.08)",
});

const roleStyle = {
  fontSize: "14px",
  fontWeight: 700,
  color: "#6b7280",
  marginBottom: "10px",
};

const nameStyle = {
  fontSize: "30px",
  fontWeight: 800,
  color: "#0f172a",
  marginBottom: "12px",
};

const descStyle = {
  fontSize: "15px",
  lineHeight: 1.8,
  color: "#475569",
  minHeight: "84px",
};

const chipWrapStyle = {
  display: "flex",
  flexWrap: "wrap",
  gap: "10px",
  marginTop: "18px",
};

const chipStyle = {
  padding: "9px 14px",
  borderRadius: "999px",
  background: "#eef5ff",
  color: "#2573c2",
  fontSize: "14px",
  fontWeight: 700,
};

const bottomBoxStyle = {
  marginTop: "26px",
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  gap: "18px",
};

const infoCardStyle = {
  background: "rgba(255,255,255,0.82)",
  borderRadius: "26px",
  padding: "24px",
  boxShadow: "0 10px 24px rgba(89, 130, 200, 0.08)",
};

function TeamIntroPage() {
  return (
    <section style={sectionStyle}>
      <div style={containerStyle}>
        <div style={topNavStyle}>
          <div></div>
          <Link to="/" style={linkStyle}>
            ← 메인으로 돌아가기
          </Link>
        </div>

        <div style={{ textAlign: "center" }}>
          <div style={badgeStyle}>캡스톤 프로젝트 팀 소개</div>
          <h1 style={titleStyle}>
            우리 팀이 만드는
            <br />
            사회문제 징후 탐지 시스템
          </h1>
          <p style={subtitleStyle}>
            공공 민원 데이터 기반 AI 사회문제 징후 탐지 시스템을 구현하는 팀입니다.
            각 팀원은 데이터 분석, 서버·DB·API, 프론트엔드 영역을 분담하여
            하나의 완성도 있는 서비스 데모를 목표로 개발하고 있습니다.
          </p>
        </div>

        <div style={heroCardStyle}>
          <div style={gridStyle}>
            {teamMembers.map((member) => (
              <div
                key={member.name + member.role}
                style={getMemberCardStyle(member.highlight)}
              >
                <div style={roleStyle}>{member.role}</div>
                <div style={nameStyle}>{member.name}</div>
                <div style={descStyle}>{member.description}</div>
                <div style={chipWrapStyle}>
                  {member.tasks.map((task) => (
                    <span key={task} style={chipStyle}>
                      {task}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div style={bottomBoxStyle}>
            <div style={infoCardStyle}>
              <div style={roleStyle}>프로젝트 목표</div>
              <div style={{ ...nameStyle, fontSize: "24px", marginBottom: "10px" }}>
                문제의 조짐을 더 빠르게 파악
              </div>
              <div style={descStyle}>
                급증 키워드, 기관·지역별 민원 흐름, AI 브리핑을 통해 사회문제의
                징후를 직관적으로 파악할 수 있는 데모 서비스를 구현합니다.
              </div>
            </div>

            <div style={infoCardStyle}>
              <div style={roleStyle}>개발 스택</div>
              <div style={{ ...nameStyle, fontSize: "24px", marginBottom: "10px" }}>
                React · FastAPI · PostgreSQL
              </div>
              <div style={descStyle}>
                프론트는 React, 백엔드는 FastAPI, 데이터 저장은 PostgreSQL을
                중심으로 구성하여 실제 캡스톤 데모에 맞는 구조로 개발합니다.
              </div>
            </div>

            <div style={infoCardStyle}>
              <div style={roleStyle}>협업 방식</div>
              <div style={{ ...nameStyle, fontSize: "24px", marginBottom: "10px" }}>
                역할 분담 + API 연동 중심
              </div>
              <div style={descStyle}>
                데이터 분석, 서버, 프론트가 각각 역할을 나누고 최종적으로
                API를 기준으로 연결하여 하나의 흐름으로 시연할 수 있게 맞춥니다.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default TeamIntroPage;