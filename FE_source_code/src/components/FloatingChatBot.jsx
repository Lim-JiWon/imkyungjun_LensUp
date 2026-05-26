import { useEffect, useRef, useState } from "react";
import { MessageCircle, X, Send } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { askChatBot } from "../api/chat";
import "./FloatingChatBot.css";

function FloatingChatBot() {
  const navigate = useNavigate();

  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const bodyRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      role: "ai",
      text: "안녕하세요! 민원 이슈나 급등 키워드에 대해 궁금한 점을 물어보세요.",
      topics: [],
    },
  ]);

  useEffect(() => {
    if (!bodyRef.current) return;

    bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [messages, isOpen]);

  const getTopicId = (topic) => {
    const directId =
      topic?.id ??
      topic?.issue_id ??
      topic?.issueId ??
      topic?.dashboard_id ??
      topic?.dashboardId ??
      null;

    if (directId) return directId;

    const detailApi = topic?.detailApi || topic?.detail_api;

    if (detailApi) {
      try {
        const path = detailApi.startsWith("http")
          ? new URL(detailApi).pathname
          : detailApi;

        const parts = path.split("/").filter(Boolean);
        return parts[parts.length - 1] || null;
      } catch {
        return null;
      }
    }

    return null;
  };

  const normalizeTopic = (topic) => {
    return {
      ...topic,
      id: getTopicId(topic),
      title:
        topic?.title ||
        topic?.issue_title ||
        topic?.issueTitle ||
        "제목 없음",
      summary: topic?.summary || topic?.description || "",
      topKeyword:
        topic?.topKeyword ||
        topic?.top_keyword ||
        topic?.keyword ||
        topic?.matched_keyword ||
        "",
      riskLevel: topic?.riskLevel || topic?.risk_level || "",
      score: topic?.score ?? topic?.match_score ?? null,
    };
  };

  const handleSend = async () => {
    const userInput = input.trim();

    if (!userInput || isSending) return;

    const userMessage = {
      role: "user",
      text: userInput,
      topics: [],
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsSending(true);

    const loadingMessage = {
      role: "ai",
      text: "답변을 생성하는 중입니다...",
      topics: [],
      isLoading: true,
    };

    setMessages((prev) => [...prev, loadingMessage]);

    try {
      const botResponse = await askChatBot(userInput);

      const rawTopics = Array.isArray(botResponse.topics)
        ? botResponse.topics
        : Array.isArray(botResponse.results)
        ? botResponse.results
        : [];

      const topics = rawTopics.map(normalizeTopic);

      const aiMessage = {
        role: "ai",
        text: botResponse.answer || "응답 내용이 없습니다.",
        topics,
      };

      setMessages((prev) => {
        const removedLoading = prev.filter((message) => !message.isLoading);
        return [...removedLoading, aiMessage];
      });
    } catch (error) {
      console.error("[CHATBOT ERROR]", error);

      const errorMessage = {
        role: "ai",
        text:
          error.message ||
          "챗봇 응답을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
        topics: [],
      };

      setMessages((prev) => {
        const removedLoading = prev.filter((message) => !message.isLoading);
        return [...removedLoading, errorMessage];
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !isSending) {
      handleSend();
    }
  };

  const handleTopicClick = (topic) => {
    const topicId = getTopicId(topic);

    if (!topicId) {
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: "이 주제는 상세 페이지로 이동할 수 있는 ID가 없습니다.",
          topics: [],
        },
      ]);
      return;
    }

    setIsOpen(false);
    navigate(`/issues/${topicId}`);
  };

  function getRiskText(riskLevel) {
    const value = String(riskLevel || "").toLowerCase();

    if (value === "critical") return "매우 높음";
    if (value === "high") return "높음";
    if (value === "medium") return "보통";
    if (value === "low") return "낮음";
    if (value === "watch") return "관찰 필요";

    return riskLevel || "";
  }

  function getScoreText(score) {
    if (score === null || score === undefined || score === "") return null;

    const numberScore = Number(score);

    if (Number.isNaN(numberScore)) return null;

    return Math.round(numberScore);
  }

  return (
    <div className="floating-chatbot">
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div>
              <p className="chatbot-title">AI 민원 도우미</p>
              <span className="chatbot-status">
                {isSending ? "답변 생성 중" : "실시간 이슈 분석 보조"}
              </span>
            </div>

            <button
              className="chatbot-close-btn"
              onClick={() => setIsOpen(false)}
              aria-label="챗봇 닫기"
            >
              <X size={18} />
            </button>
          </div>

          <div className="chatbot-body" ref={bodyRef}>
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`chatbot-message-wrap ${
                  message.role === "user" ? "user" : "ai"
                }`}
              >
                <div
                  className={`chatbot-message ${
                    message.role === "user" ? "user" : "ai"
                  } ${message.isLoading ? "loading" : ""}`}
                >
                  {message.text}
                </div>

                {message.role === "ai" &&
                  Array.isArray(message.topics) &&
                  message.topics.length > 0 && (
                    <div
                      style={{
                        display: "grid",
                        gap: "10px",
                        marginTop: "10px",
                      }}
                    >
                      {message.topics.slice(0, 3).map((topic, topicIndex) => {
                        const scoreText = getScoreText(topic.score);

                        return (
                          <button
                            key={`${topic.id || topic.title}-${topicIndex}`}
                            type="button"
                            onClick={() => handleTopicClick(topic)}
                            style={{
                              width: "100%",
                              textAlign: "left",
                              border: "1px solid rgba(37, 99, 235, 0.16)",
                              background: "#ffffff",
                              borderRadius: "16px",
                              padding: "12px 14px",
                              cursor: "pointer",
                              boxShadow: "0 8px 20px rgba(15, 23, 42, 0.06)",
                            }}
                          >
                            <div
                              style={{
                                fontSize: "13px",
                                fontWeight: 800,
                                color: "#2563eb",
                                marginBottom: "6px",
                              }}
                            >
                              {topic.topKeyword
                                ? `#${topic.topKeyword}`
                                : `추천 주제 ${topicIndex + 1}`}
                            </div>

                            <div
                              style={{
                                fontSize: "14px",
                                fontWeight: 800,
                                color: "#111827",
                                lineHeight: 1.4,
                                marginBottom: "6px",
                              }}
                            >
                              {topic.title}
                            </div>

                            <div
                              style={{
                                fontSize: "13px",
                                color: "#64748b",
                                lineHeight: 1.45,
                              }}
                            >
                              {topic.summary}
                            </div>

                            {(topic.riskLevel || scoreText !== null) && (
                              <div
                                style={{
                                  display: "flex",
                                  gap: "8px",
                                  flexWrap: "wrap",
                                  marginTop: "10px",
                                }}
                              >
                                {topic.riskLevel && (
                                  <span
                                    style={{
                                      padding: "5px 8px",
                                      borderRadius: "999px",
                                      background: "#eff6ff",
                                      color: "#2563eb",
                                      fontSize: "12px",
                                      fontWeight: 700,
                                    }}
                                  >
                                    위험도 {getRiskText(topic.riskLevel)}
                                  </span>
                                )}

                                {scoreText !== null && (
                                  <span
                                    style={{
                                      padding: "5px 8px",
                                      borderRadius: "999px",
                                      background: "#f8fafc",
                                      color: "#334155",
                                      fontSize: "12px",
                                      fontWeight: 700,
                                    }}
                                  >
                                    점수 {scoreText}
                                  </span>
                                )}
                              </div>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
              </div>
            ))}
          </div>

          <div className="chatbot-input-area">
            <input
              type="text"
              placeholder={
                isSending ? "답변을 기다리는 중입니다..." : "궁금한 내용을 입력하세요"
              }
              value={input}
              disabled={isSending}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
            />

            <button
              onClick={handleSend}
              disabled={isSending}
              aria-label="메시지 보내기"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      )}

      <button
        className="chatbot-floating-btn"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="AI 챗봇 열기"
      >
        {isOpen ? <X size={28} /> : <MessageCircle size={30} />}
      </button>
    </div>
  );
}

export default FloatingChatBot;