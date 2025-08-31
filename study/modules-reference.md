# 모듈 참조 가이드

## 핵심 의존성

### A2A SDK (`a2a-sdk>=0.2.16`)
에이전트 간 통신을 위한 Agent-to-Agent 프로토콜 구현체입니다.

**주요 클래스:**
- `A2ACardResolver`: 엔드포인트에서 에이전트 기능을 발견합니다
- `A2AClient`: A2A 에이전트에 메시지를 보내는 클라이언트
- `A2AStarletteApplication`: A2A 프로토콜을 구현하는 HTTP 서버
- `DefaultRequestHandler`: A2A 요청을 에이전트 실행자로 라우팅합니다
- `AgentCard`: 에이전트 기능을 설명하는 메타데이터
- `SendMessageRequest`/`SendMessageResponse`: A2A 메시지 타입
- `MessageSendParams`: 메시지 매개변수
- `Task`, `TaskArtifactUpdateEvent`, `TaskStatusUpdateEvent`: 작업 타입

**사용 패턴:**
```python
# 클라이언트 측 (purchasing agent)
resolver = A2ACardResolver(base_url=agent_url, httpx_client=client)
card = await resolver.get_agent_card()
a2a_client = A2AClient(httpx_client, card, url=card.url)
response = await a2a_client.send_message(request)

# 서버 측 (remote agents)  
server = A2AStarletteApplication(agent_card=card, http_handler=handler)
uvicorn.run(server.build(), host=host, port=port)
```

### Google ADK (`google-adk>=1.8.0`)
Google's Agent Development Kit for building AI agents.

**Key Classes:**
- `Agent`: Main agent class with tools and callbacks
- `AgentExecutor`: Interface between A2A and agent logic
- `get_fast_api_app`: Creates FastAPI app for agents
- `InMemoryTaskStore`: Stores task state

**Usage Pattern:**
```python
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

agent = Agent(
    model="gemini-2.5-flash-lite",
    name="agent_name", 
    instruction=instruction_function,
    before_model_callback=callback_function,
    tools=[tool_function]
)
```

### LangGraph (Job Agent)
LLM과 함께 상태 유지, 다단계 애플리케이션을 구축하기 위한 프레임워크입니다.

**주요 구성 요소:**
- `create_react_agent`: ReAct 패턴 에이전트를 생성합니다
- `MemorySaver`: 대화 메모리를 위한 체크포인팅
- `ChatVertexAI`: Vertex AI LLM 통합

**사용 패턴:**
```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_vertexai import ChatVertexAI

memory = MemorySaver()
model = ChatVertexAI(model="gemini-2.5-flash-lite")
graph = create_react_agent(model, tools=[tool], checkpointer=memory, prompt=system_prompt)

config = {"configurable": {"thread_id": session_id}}
graph.invoke({"messages": [("user", query)]}, config)
```

### FastMCP (MCP 서버)
Model Context Protocol (MCP) 서버와 클라이언트를 구축하기 위한 Python 프레임워크입니다.

**주요 구성 요소:**
- `FastMCP`: MCP 서버 클래스
- `@server.tool()`: 도구 등록 데코레이터
- `server.run()`: 서버 실행 메서드
- `stdio` transport: 표준 입출력을 통한 통신

**사용 패턴:**
```python
from mcp.server import FastMCP

server = FastMCP(name="web-search-server")

@server.tool()
def web_search(query: str, count: int = 5) -> str:
    """웹 검색을 수행합니다."""
    # 검색 로직 구현
    return search_results

if __name__ == "__main__":
    server.run(transport="stdio")
```

### Vertex AI 통합
Google Cloud의 AI 플랫폼 통합입니다.

**구성 요소:**
- `ChatVertexAI`: LangChain Vertex AI 통합
- `vertexai.agent_engines`: Agent Engine 배포
- `vertexai.preview.reasoning_engines`: ADK 앱 래퍼

**사용 패턴:**
```python
# 직접 Vertex AI
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET)
adk_app = reasoning_engines.AdkApp(agent=root_agent)
remote_app = agent_engines.create(agent_engine=adk_app)

# LangChain 통합
from langchain_google_vertexai import ChatVertexAI
model = ChatVertexAI(model="gemini-2.5-flash-lite", project=PROJECT_ID, location=LOCATION)
```

### Starlette (`starlette>=0.27.0`)
ASGI 웹 프레임워크로, A2A 프로토콜 서버와 웹 UI를 구현하는 데 사용됩니다.

**주요 구성 요소:**
- `Starlette`: ASGI 애플리케이션 클래스
- `Route`: URL 라우팅
- `JSONResponse`: JSON 응답
- `HTMLResponse`: HTML 응답

**사용 패턴:**
```python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, HTMLResponse

async def chat_endpoint(request):
    data = await request.json()
    # 메시지 처리 로직
    return JSONResponse({"reply": response})

routes = [
    Route("/chat", chat_endpoint, methods=["POST"]),
    Route("/", lambda r: HTMLResponse(html_content))
]

app = Starlette(routes=routes)
```

## 프로젝트별 모듈

### Job Agent (독립 실행형)
`job-agent/` 패키지는 A2A 호환 서비스로 다음을 노출합니다:
- A2A Agent Card (발견용)
- 프로그래밍 방식 상호작용을 위한 A2A 메시지 엔드포인트
- 사람이 테스트할 수 있는 서비스 루트의 간단한 내장 웹 채팅 UI

주요 파일:
- `job-agent/__main__.py`: A2A 서버 진입점 및 웹 UI 라우트
- `job-agent/agent.py`: Vertex AI `ChatVertexAI`를 사용하는 LangGraph 기반 에이전트
- `job-agent/agent_executor.py`: A2A 요청을 에이전트로 연결
- `job-agent/web_search_server.py`: MCP 웹 검색 서버

의존성 (일부):
- `a2a-sdk[http-server]`: A2A HTTP 서버 (Starlette)
- `langgraph`, `langchain-google-vertexai`: 에이전트 + Gemini (Vertex AI)
- `uvicorn`, `starlette`, `sse-starlette`: 웹 서빙 + 스트리밍
- `mcp`, `ddgs`: MCP 서버 및 웹 검색

노출된 엔드포인트:
- `GET /.well-known/agent.json`: A2A Agent Card (well-known discovery)
- `POST /message/send`: A2A 비스트리밍 메시지
- `POST /message/stream`: A2A 스트리밍 메시지 (SSE)
- `GET /`: 최소한의 웹 채팅 UI (사람 테스트용)
- `POST /chat`: UI에서 사용하는 간단한 JSON 채팅 엔드포인트

코드 흐름 요약:
1. `__main__.py`는 `AgentCard`와 `DefaultRequestHandler(JobAgentExecutor)`를 사용하여 `A2AStarletteApplication`을 생성한 후 Starlette `app`을 빌드합니다.
2. 파일은 웹 UI를 위한 두 개의 추가 라우트를 마운트합니다: `GET /`는 HTML을 반환하고, `POST /chat`은 에이전트를 직접 호출합니다.
3. `JobAgentExecutor.execute(...)`는 A2A에서 사용자 메시지를 받아 `JobAgent.invoke(...)`를 호출한 후 텍스트 아티팩트가 포함된 완료된 작업을 큐에 넣습니다.
4. `JobAgent` (LangGraph)는 `ChatVertexAI(model="gemini-2.5-flash-lite")`와 커리어 지원을 위한 `search_jobs` 및 `web_search` 도구를 사용하여 ReAct 에이전트를 구성합니다. 실행 후 최종 메시지 내용을 반환합니다.

UX 흐름 요약 (웹 UI):
1. 사용자가 `GET /` (루트)를 엽니다. 페이지는 최소한의 채팅 인터페이스를 로드합니다.
2. 전송 시 브라우저는 `{ text, contextId }`와 함께 `POST /chat`에 JSON을 게시합니다.
3. 서버는 `JobAgent.invoke(text, contextId)`를 호출하고 `{ reply }`를 반환합니다.
4. UI는 사용자 및 에이전트 버블을 추가합니다. 호출이 실패하면 오류가 인라인으로 표시됩니다.

환경 변수:
- `GOOGLE_CLOUD_PROJECT` (필수)
- `GOOGLE_CLOUD_LOCATION` (예: `us-central1`) (필수)
- `HOST_OVERRIDE` (선택사항; Agent Card에서 외부 URL을 게시하는 데 사용, 예: Cloud Run URL)

로컬 실행 패턴:
```bash
cd job-agent
uv sync
uv run . --host 0.0.0.0 --port 8080
# http://localhost:8080 열기
```

Cloud Run 배포 (예시):
```bash
gcloud run deploy job-agent \
  --source ./job-agent \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1

URL=$(gcloud run services describe job-agent --region us-central1 --format='value(status.url)')
gcloud run services update job-agent --region us-central1 --update-env-vars HOST_OVERRIDE=$URL
```

### `job-agent/agent_executor.py`
A2A 프로토콜 요청을 JobAgent로 연결하는 브리지 역할을 합니다.

**주요 메서드:**
- `execute()`: A2A 요청을 받아 JobAgent를 호출하고 결과를 반환합니다
- `__init__()`: JobAgent 인스턴스를 초기화합니다

**패턴:**
```python
class JobAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = JobAgent()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        result = self.agent.invoke(query, context.context_id)
        
        parts = [Part(root=TextPart(text=str(result)))]
        await event_queue.enqueue_event(completed_task(...))
```

### 에이전트 구현

#### `job-agent/agent.py` - LangGraph 구현
- `create_react_agent`와 `search_jobs`, `web_search` 도구를 사용합니다
- `MemorySaver`로 대화 메모리를 유지합니다
- 커리어 및 구직 지원을 위한 구조화된 시스템 지침을 포함합니다
- 한국어 시스템 프롬프트로 현지화되어 있습니다

## 도구 패턴

### 구직 및 웹 검색 도구
Job Agent는 구직 지원과 웹 검색을 위한 도구 패턴을 따릅니다:

```python
from pydantic import BaseModel
from langchain_core.tools import tool

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
    """주어진 기준에 따라 구직 기회를 검색합니다."""
    # 구직 검색 로직 구현
    return f"'{query}'에 대한 {total_found}개의 구직 기회를 찾았습니다."

@tool
def web_search(query: str, count: int = 5) -> str:
    """웹 검색을 수행하고 상위 결과를 반환합니다."""
    # DuckDuckGo를 사용한 웹 검색 구현
    return formatted_search_results
```

## HTTP/API 레이어

### A2A 프로토콜 엔드포인트
Job Agent는 `A2AStarletteApplication`을 통해 A2A 프로토콜 엔드포인트를 노출합니다:

- `GET /.well-known/agent.json`: 에이전트 카드 반환 (기능, 기술, 메타데이터)
- `POST /message/send`: A2A 메시지 요청 수락
- `POST /message/stream`: 스트리밍 응답을 위한 SSE 지원

### 웹 채팅 인터페이스
내장된 웹 UI는 다음 기능을 제공합니다:
- 루트 `/`에서 간단한 채팅 인터페이스 제공
- `POST /chat` 엔드포인트를 통한 JSON 기반 메시지 처리
- 실시간 응답 및 오류 처리

### Cloud Run 배포
Job Agent는 컨테이너화된 서비스로 실행됩니다:
- 독립 실행형 Cloud Run 서비스
- CI/CD 파이프라인을 통한 자동 배포
- 환경 변수를 통한 설정 관리

## 설정 패턴

### 환경 변수
```python
# 모든 구성 요소에 공통
GOOGLE_CLOUD_PROJECT=project-id
GOOGLE_CLOUD_LOCATION=us-central1  
GOOGLE_GENAI_USE_VERTEXAI=True

# Job Agent 특정
HOST_OVERRIDE=https://external-url  # Agent Card URL용
PORT=8080                           # Cloud Run 기본값
```

### Docker 설정
Job Agent는 다음과 같은 Dockerfile 패턴을 사용합니다:
```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
ADD . /app
WORKDIR /app
RUN uv sync --frozen
EXPOSE 8080
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["uv", "run", ".", "--host", "0.0.0.0", "--port", "8080"]
```

이 모듈형 아키텍처는 표준화된 통신 프로토콜을 유지하면서 각 에이전트의 독립적인 개발, 테스트 및 배포를 가능하게 합니다.
