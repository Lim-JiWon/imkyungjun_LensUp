import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Search } from "lucide-react";

function TopNav() {
  const navigate = useNavigate();
  const [searchKeyword, setSearchKeyword] = useState("");

  const menus = [
    { label: "서비스 소개", path: "/" },
    { label: "민원 보기", path: "/complaints" },
    { label: "핵심 기능", path: "/features" },
    { label: "분석 대시보드", path: "/dashboard" },
    { label: "시연 흐름", path: "/demo" },
    { label: "기술 스택", path: "/stack" },
    { label: "팀 소개", path: "/team" },
  ];

  function handleSearchSubmit(event) {
    event.preventDefault();

    const trimmed = searchKeyword.trim();

    if (!trimmed) return;

    navigate(`/search?query=${encodeURIComponent(trimmed)}`);
    setSearchKeyword("");
  }

  return (
    <header className="navbar">
      <nav className="nav-inner">
        <div className="nav-menu">
          {menus.map((menu) => (
            <NavLink
              key={menu.path}
              to={menu.path}
              end={menu.path === "/"}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {menu.label}
            </NavLink>
          ))}
        </div>

        <form className="nav-search" onSubmit={handleSearchSubmit}>
          <button
            type="submit"
            className="nav-search-button"
            aria-label="검색"
          >
            <Search size={16} className="nav-search-icon" />
          </button>

          <input
            type="text"
            placeholder="검색"
            className="nav-search-input"
            value={searchKeyword}
            onChange={(event) => setSearchKeyword(event.target.value)}
          />
        </form>
      </nav>
    </header>
  );
}

export default TopNav;