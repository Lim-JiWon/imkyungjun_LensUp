import axios from "axios";

const API_BASE_URL = "https://api.minwon-ai.kr";

/**
 * AI 검색 도우미 챗봇
 * POST /chat/search-assistant
 */
export async function askChatBot(message) {
  const trimmedMessage = String(message || "").trim();

  if (!trimmedMessage) {
    throw new Error("메시지를 입력해주세요.");
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/chat/search-assistant`,
      {
        message: trimmedMessage,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 60000,
      }
    );

    const data = response.data;

    console.log("[CHATBOT RAW RESPONSE]", data);

    const topics = extractTopics(data);
    const answer = extractChatAnswer(data, trimmedMessage, topics);

    return {
      success: true,
      raw: data,
      answer,
      topics,
      results: topics,
      query: data?.query || data?.normalized_query || trimmedMessage,
    };
  } catch (error) {
    console.error("[CHATBOT API ERROR]", error);

    if (error.response) {
      throw new Error(
        error.response.data?.detail ||
          error.response.data?.message ||
          "챗봇 서버에서 오류가 발생했습니다."
      );
    }

    if (error.request) {
      throw new Error("챗봇 서버에 연결할 수 없습니다.");
    }

    throw new Error(error.message || "챗봇 요청 중 오류가 발생했습니다.");
  }
}

function extractChatAnswer(data, originalMessage, topics) {
  if (!data) {
    return "챗봇 응답 데이터가 비어 있습니다.";
  }

  if (typeof data === "string") {
    return data;
  }

  const directAnswer =
    data.answer ||
    data.message ||
    data.response ||
    data.result ||
    data.reply ||
    data.content ||
    data.assistant_answer ||
    data.assistant_message ||
    data.ai_answer ||
    data.text ||
    data.data?.answer ||
    data.data?.message ||
    data.data?.response ||
    data.data?.result ||
    data.data?.reply ||
    data.data?.content ||
    data.chat?.answer ||
    data.chat?.message ||
    data.chat?.response ||
    data.chat?.reply ||
    data.choices?.[0]?.message?.content;

  if (typeof directAnswer === "string" && directAnswer.trim()) {
    return directAnswer.trim();
  }

  if (topics.length > 0) {
    return `"${originalMessage}"와 관련된 민원 주제를 찾았습니다. 아래 주제를 선택하면 상세 페이지로 이동할 수 있습니다.`;
  }

  return "관련 민원 주제를 찾지 못했습니다. 다른 키워드로 다시 질문해보세요.";
}

function extractTopics(data) {
  if (!data || typeof data !== "object") return [];

  const possibleLists = [
    data.results,
    data.topics,
    data.issues,
    data.items,
    data.recommendations,
    data.related_issues,
    data.search_results,
    data.data?.results,
    data.data?.topics,
    data.data?.issues,
    data.data?.items,
    data.data?.recommendations,
    data.data?.related_issues,
  ];

  const foundList = possibleLists.find((list) => Array.isArray(list));

  if (Array.isArray(foundList) && foundList.length > 0) {
    return foundList.map((item, index) => normalizeTopic(item, index));
  }

  if (Array.isArray(data.keywords) && data.keywords.length > 0) {
    return data.keywords.map((keyword, index) => ({
      id: null,
      title: typeof keyword === "string" ? keyword : keyword?.keyword || keyword?.label || `키워드 ${index + 1}`,
      summary: "관련 키워드입니다.",
      riskLevel: "",
      score: null,
      topKeyword: typeof keyword === "string" ? keyword : keyword?.keyword || keyword?.label || "",
    }));
  }

  return [];
}

function normalizeTopic(item, index) {
  if (typeof item === "string") {
    return {
      id: null,
      title: item,
      summary: "관련 민원 주제입니다.",
      riskLevel: "",
      score: null,
      topKeyword: item,
    };
  }

  return {
    id: item.id ?? item.issue_id ?? item.dashboard_id ?? null,
    title:
      item.title ||
      item.topic ||
      item.name ||
      item.keyword ||
      item.top_keyword ||
      `민원 주제 ${index + 1}`,
    summary:
      item.summary ||
      item.description ||
      item.reason ||
      item.forecast ||
      "요약 정보가 없습니다.",
    riskLevel: item.risk_level || item.riskLevel || item.status || "",
    score: item.score ?? item.risk_score ?? null,
    topKeyword: item.top_keyword || item.keyword || "",
    source: item.source || "",
  };
}