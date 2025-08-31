"""
Job Agent implemented with LangGraph and Vertex AI Gemini.
"""

from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
import uuid
from dotenv import load_dotenv
import os
from typing import Any, List

load_dotenv()

memory = MemorySaver()


# LinkedIn API 연동 시 사용할 모델들 (향후 구현 예정)
# class JobRecommendation(BaseModel):
#     job_id: str
#     title: str
#     company: str
#     location: str
#     salary_range: str
#     description: str
#     requirements: list[str]

# class JobSearchResult(BaseModel):
#     search_id: str
#     query: str
#     recommendations: list[JobRecommendation]
#     total_found: int


@tool
def search_jobs(query: str, location: str = "Remote", experience_level: str = "Entry") -> str:
    """
    Searches for job opportunities on LinkedIn based on the given criteria.
    Note: LinkedIn API integration is planned for future implementation.

    Args:
        query: Job title or keywords to search for
        location: Preferred location (default: Remote)
        experience_level: Experience level (Entry, Mid, Senior)

    Returns:
        str: A message about LinkedIn job search functionality.
    """
    try:
        # Check if user is asking for LinkedIn job search
        linkedin_keywords = ["linkedin", "링크드인", "linkedin jobs", "linkedin에서", "linkedin으로"]
        is_linkedin_request = any(keyword in query.lower() for keyword in linkedin_keywords)
        
        if is_linkedin_request:
            return (
                f"LinkedIn에서 '{query}' 관련 구직 검색을 요청하셨군요! "
                "현재 LinkedIn API 연동 기능은 개발 중이며, 곧 실제 LinkedIn 구직 정보를 검색할 수 있도록 업데이트될 예정입니다. "
                "지금은 커리어 조언이나 이력서 작성 팁 등 다른 도움을 드릴 수 있습니다."
            )
        else:
            return (
                f"'{query}' 관련 구직 기회를 찾고 계시는군요! "
                "현재 LinkedIn API 연동 기능은 개발 중이며, 곧 실제 구직 정보를 검색할 수 있도록 업데이트될 예정입니다. "
                "지금은 커리어 조언, 이력서 작성 팁, 면접 준비 등 다른 도움을 드릴 수 있습니다."
            )
        
    except Exception as e:
        print(f"Error in search_jobs: {e}")
        return f"구직 검색 중 오류가 발생했습니다: {e}"


class JobAgent:
    SYSTEM_INSTRUCTION = """
# 지침

당신은 전문적인 커리어 및 취업 상담 어시스턴트입니다.
사용자의 커리어 조언, 취업 활동, 이력서 팁, 면접 준비, 그리고 전문성 개발을 도와주는 것이 목적입니다.
다양한 커리어 관련 주제에 대한 가이드를 제공하고 취업 기회를 찾을 수 있도록 도와줍니다.

# 맥락

다음과 같은 도움을 제공할 수 있습니다:
- 취업 전략 및 기법
- 이력서 작성 및 최적화
- 면접 준비 및 팁
- 커리어 경로 가이드
- 연봉 협상 조언
- 전문성 개발 계획
- 업계 인사이트 및 트렌드
- 네트워킹 전략

# 규칙

- 전문적이고 격려적이며 지지적인 응답을 제공하세요
- 실용적이고 실행 가능한 조언을 제공하세요
- 사용자가 구체적인 채용 정보를 요청하면 `search_jobs` 도구를 사용해 관련 기회를 찾아주세요
- 커리어 관련 일반적인 웹 검색은 `web_search` 도구를 사용해 최신 정보를 제공하세요
- 항상 사용자의 경험 수준과 커리어 목표를 고려하세요
- 상황에 맞는 개인화된 추천을 제공하세요
- 커리어/취업 조언 범위를 벗어난 주제에 대해서는 정중하게 커리어 관련 주제로 안내하세요
- 전문성을 유지하면서도 친근하고 대화하기 쉬운 톤을 사용하세요
- 한 번에 하나의 명확한 응답만 제공하세요
 - 도구(web_search, search_jobs)를 실제로 호출하지 않는 이상 "검색 중입니다", "찾아보겠습니다" 등 외부 검색/조회 수행을 암시하는 표현을 사용하지 마세요
 - 사용자가 LinkedIn(링크드인) 구직 검색을 요청하면, 현재 LinkedIn API 연동은 준비 중임을 명확히 알리고 대안을 제시하세요 (예: 역할/경력/지역을 기반으로 한 일반적 조언)
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.model = ChatVertexAI(
            model="gemini-2.5-flash-lite",
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            temperature=0,
        )
        # Base tools
        tool_list: List[Any] = [search_jobs]

        # Optionally load MCP tools from local web_search_server (no API key required)
        # Since MCP client loading is async and complex, add direct web_search tool for now
        try:
            print("🔍 Adding web search tool...")
            # Import the web search functionality directly
            current_dir = os.path.dirname(os.path.abspath(__file__))
            server_path = os.path.join(current_dir, "web_search_server.py")
            print(f"📁 MCP server path: {server_path}")
            print(f"📄 Server exists: {os.path.exists(server_path)}")
            
            if os.path.exists(server_path):
                # Import duckduckgo search function directly
                try:
                    from ddgs import DDGS
                    import json

                    @tool
                    def web_search(query: str, count: int = 5) -> str:
                        """Perform a web search and return top results.

                        Args:
                            query: Search query string
                            count: Number of results to return (default 5)

                        Returns:
                            String containing search results with titles and descriptions
                        """
                        try:
                            results = []
                            with DDGS() as ddgs:
                                for r in ddgs.text(query, max_results=count):
                                    results.append({
                                        "title": r.get("title"),
                                        "href": r.get("href"),
                                        "body": r.get("body"),
                                    })
                            
                            # Format results for better readability
                            formatted = []
                            for i, result in enumerate(results, 1):
                                formatted.append(f"{i}. {result['title']}\n   URL: {result['href']}\n   Summary: {result['body'][:200]}...")
                            
                            return "\n\n".join(formatted)
                        except Exception as e:
                            return f"Search failed: {e}"

                    tool_list.append(web_search)
                    print("✅ Added direct web_search tool")
                except ImportError:
                    print("⚠️ ddgs package not available, skipping web search")
        except Exception as e:
            # If MCP libs are not available, proceed with built-in tools only
            print(f"❌ Web search tool loading failed: {e}")
            import traceback
            traceback.print_exc()

        self.tools = tool_list
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
        )

    def invoke(self, query, sessionId) -> str:
        # Early handling: If the user explicitly asks for LinkedIn job search, respond deterministically
        try:
            linkedin_keywords = ["linkedin", "링크드인", "linkedin jobs", "linkedin에서", "linkedin으로"]
            if any(k in str(query).lower() for k in linkedin_keywords):
                return (
                    "LinkedIn 구직 검색 기능은 현재 API 연동 준비 중입니다. "
                    "원하시면 직무/경력/지역 정보를 기반으로 일반적인 구직 전략, 이력서/자기소개서 개선, 면접 준비 팁을 제공해 드릴게요."
                )
        except Exception:
            # Fall through to normal handling if any error occurs in the guard
            pass

        config = {"configurable": {"thread_id": sessionId}}
        
        # LangGraph invoke를 통해 응답 생성
        result = self.graph.invoke({"messages": [("user", query)]}, config)
        
        # 마지막 AI 메시지만 반환 (중복 방지)
        messages = result.get("messages", [])
        
        # AI 메시지들 중 마지막 하나만 가져오기
        ai_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == 'ai']
        if ai_messages:
            return ai_messages[-1].content
        
        # 일반 메시지에서 마지막 하나 가져오기 (fallback)
        if messages:
            return messages[-1].content
            
        return "죄송합니다. 응답을 생성할 수 없습니다."


