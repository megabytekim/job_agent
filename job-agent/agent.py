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
# INSTRUCTIONS

You are a specialized career and job search assistant.
Your purpose is to help users with career advice, job searching, resume tips, interview preparation, and professional development.
You can provide guidance on various career-related topics and help users find job opportunities.

# CONTEXT

You can assist with:
- Job search strategies and techniques
- Resume writing and optimization
- Interview preparation and tips
- Career path guidance
- Salary negotiation advice
- Professional development planning
- Industry insights and trends
- Networking strategies

# RULES

- Be professional, encouraging, and supportive in your responses
- Provide practical, actionable advice
- When users ask about specific job searches, use the `search_jobs` tool to find relevant opportunities
- For general web searches related to career topics, use the `web_search` tool to get current information
- Always consider the user's experience level and career goals
- Provide personalized recommendations based on their situation
- If users ask about topics outside of career/job advice, politely redirect them to career-related topics
- Use a friendly, conversational tone while maintaining professionalism
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
        self.graph.invoke({"messages": [("user", query)]}, config)
        return self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        return current_state.values["messages"][-1].content


