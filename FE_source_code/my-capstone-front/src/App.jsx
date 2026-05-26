import { Routes, Route } from "react-router-dom";

import TopNav from "./components/TopNav";
import FloatingChatBot from "./components/FloatingChatBot";

import DemoLanding from "./pages/DemoLanding";
import FeaturePage from "./pages/FeaturePage";
import DashboardPage from "./pages/DashboardPage";
import DemoFlowPage from "./pages/DemoFlowPage";
import TechStackPage from "./pages/TechStackPage";
import TeamIntroPage from "./pages/TeamIntroPage";
import SearchPage from "./pages/SearchPage";
import TopicComplaintPage from "./pages/TopicComplaintPage";

import "./styles/App.css";

function App() {
  return (
    <>
      <TopNav />

      <Routes>
        <Route path="/" element={<DemoLanding />} />

        {/* 민원 보기 페이지 */}
        <Route path="/complaints" element={<TopicComplaintPage />} />
        <Route path="/topics" element={<TopicComplaintPage />} />

        <Route path="/features" element={<FeaturePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/demo" element={<DemoFlowPage />} />
        <Route path="/stack" element={<TechStackPage />} />
        <Route path="/team" element={<TeamIntroPage />} />
        <Route path="/search" element={<SearchPage />} />
      </Routes>

      <FloatingChatBot />
    </>
  );
}

export default App;