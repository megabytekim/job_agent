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


class JobRecommendation(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    salary_range: str
    description: str
    requirements: list[str]


class JobSearchResult(BaseModel):
    search_id: str
    query: str
    recommendations: list[JobRecommendation]
    total_found: int


@tool
def search_jobs(query: str, location: str = "Remote", experience_level: str = "Entry") -> str:
    """
    Searches for job opportunities based on the given criteria.

    Args:
        query: Job title or keywords to search for
        location: Preferred location (default: Remote)
        experience_level: Experience level (Entry, Mid, Senior)

    Returns:
        str: A message with job search results and recommendations.
    """
    try:
        search_id = str(uuid.uuid4())
        
        # Mock job recommendations based on query
        mock_jobs = [
            JobRecommendation(
                job_id=str(uuid.uuid4()),
                title=f"{query} Developer",
                company="Tech Corp",
                location=location,
                salary_range="$60K - $80K",
                description=f"Looking for a {query} developer to join our team",
                requirements=["Python", "JavaScript", "2+ years experience"]
            ),
            JobRecommendation(
                job_id=str(uuid.uuid4()),
                title=f"Senior {query} Engineer",
                company="Innovation Inc",
                location=location,
                salary_range="$100K - $130K",
                description=f"Senior role in {query} development",
                requirements=["5+ years experience", "Leadership skills", "Advanced programming"]
            )
        ]
        
        result = JobSearchResult(
            search_id=search_id,
            query=query,
            recommendations=mock_jobs,
            total_found=len(mock_jobs)
        )
        
        print("===")
        print(f"Job search completed: {result}")
        print("===")
        
        return f"Found {result.total_found} jobs for '{query}' in {location}. Search ID: {search_id}"
        
    except Exception as e:
        print(f"Error searching jobs: {e}")
        return f"Error searching jobs: {e}"


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
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.model = ChatVertexAI(
            model="gemini-2.5-flash-lite",
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
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


