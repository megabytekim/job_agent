# Modules Reference Guide

## Core Dependencies

### A2A SDK (`a2a-sdk>=0.2.16`)
The Agent-to-Agent protocol implementation for inter-agent communication.

**Key Classes:**
- `A2ACardResolver`: Discovers agent capabilities from endpoint
- `A2AClient`: Client for sending messages to A2A agents  
- `A2AStarletteApplication`: HTTP server implementing A2A protocol
- `DefaultRequestHandler`: Routes A2A requests to agent executors
- `AgentCard`: Metadata describing agent capabilities
- `SendMessageRequest`/`SendMessageResponse`: A2A message types
- `MessageSendParams`: Message parameters
- `Task`, `TaskArtifactUpdateEvent`, `TaskStatusUpdateEvent`: Task types

**Usage Pattern:**
```python
# Client side (purchasing agent)
resolver = A2ACardResolver(base_url=agent_url, httpx_client=client)
card = await resolver.get_agent_card()
a2a_client = A2AClient(httpx_client, card, url=card.url)
response = await a2a_client.send_message(request)

# Server side (remote agents)  
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

### LangGraph (Pizza & Job Agents)
Framework for building stateful, multi-step applications with LLMs.

**Key Components:**
- `create_react_agent`: Creates ReAct pattern agent
- `MemorySaver`: Checkpointing for conversation memory
- `ChatVertexAI`: Vertex AI LLM integration

**Usage Pattern:**
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

### CrewAI (Burger Agent)
Multi-agent orchestration framework.

**Key Components:**
- `Agent`: Individual agent with role and capabilities
- `Task`: Work to be performed by agents
- `Crew`: Collection of agents working together
- `LLM`: Language model wrapper
- `Process`: Execution strategy (sequential/hierarchical)

**Usage Pattern:**
```python
from crewai import Agent, Crew, LLM, Task, Process

model = LLM(model="vertex_ai/gemini-2.5-flash-lite")
agent = Agent(role="Specialist", goal="...", tools=[tool], llm=model)
task = Task(description="...", agent=agent, expected_output="...")
crew = Crew(tasks=[task], agents=[agent], process=Process.sequential)

response = crew.kickoff(inputs={"key": "value"})
```

### Vertex AI Integration
Google Cloud's AI platform integration.

**Components:**
- `ChatVertexAI`: LangChain Vertex AI integration
- `vertexai.agent_engines`: Agent Engine deployment
- `vertexai.preview.reasoning_engines`: ADK app wrapper
- `litellm`: Universal LLM interface (used by CrewAI)

**Usage Pattern:**
```python
# Direct Vertex AI
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET)
adk_app = reasoning_engines.AdkApp(agent=root_agent)
remote_app = agent_engines.create(agent_engine=adk_app)

# LangChain integration
from langchain_google_vertexai import ChatVertexAI
model = ChatVertexAI(model="gemini-2.5-flash-lite", project=PROJECT_ID, location=LOCATION)

# CrewAI integration  
import litellm
litellm.vertex_project = PROJECT_ID
litellm.vertex_location = LOCATION
model = LLM(model="vertex_ai/gemini-2.5-flash-lite")
```

### Gradio (`gradio>=5.38.2`)
Web UI framework for machine learning applications.

**Key Components:**
- `gr.ChatInterface`: Chat interface for conversational agents
- `gr.ChatMessage`: Individual chat message with metadata
- Streaming support for real-time responses

**Usage Pattern:**
```python
import gradio as gr

async def get_response_from_agent(message: str, history: List[Dict[str, Any]]) -> str:
    # Process message and return response
    yield gr.ChatMessage(role="assistant", content=response)

demo = gr.ChatInterface(
    get_response_from_agent,
    title="Agent Interface",
    type="messages"
)
demo.launch(server_name="0.0.0.0", server_port=8080)
```

## Project-Specific Modules

### Job Agent (Standalone)
The `job-agent/` package is a self-contained A2A-compatible service that exposes:
- A2A Agent Card for discovery
- A2A message endpoints for programmatic interaction
- A simple built-in web chat UI at the service root for human testing

Key files:
- `job-agent/__main__.py`: A2A server entrypoint and web UI routes
- `job-agent/agent.py`: LangGraph-based agent using Vertex AI `ChatVertexAI`
- `job-agent/agent_executor.py`: Bridges A2A requests to the agent

Dependencies (subset):
- `a2a-sdk[http-server]`: A2A HTTP server (Starlette)
- `langgraph`, `langchain-google-vertexai`: Agent + Gemini (Vertex AI)
- `uvicorn`, `starlette`, `sse-starlette`: Web serving + streaming

Endpoints exposed:
- `GET /.well-known/agent.json`: A2A Agent Card (well-known discovery)
- `POST /message/send`: A2A non-streaming message
- `POST /message/stream`: A2A streaming message (SSE)
- `GET /`: Minimal web chat UI (human testing)
- `POST /chat`: Simple JSON chat endpoint used by the UI

Code flow summary:
1. `__main__.py` creates `AgentCard` and `A2AStarletteApplication` with `DefaultRequestHandler(JobAgentExecutor)`, then builds the Starlette `app`.
2. The file mounts two extra routes for the web UI: `GET /` returns HTML; `POST /chat` calls the agent directly.
3. `JobAgentExecutor.execute(...)` receives the user message from A2A, calls `JobAgent.invoke(...)`, then enqueues a completed task with a text artifact.
4. `JobAgent` (LangGraph) constructs a ReAct agent with `ChatVertexAI(model="gemini-2.5-flash-lite")` and a `search_jobs` tool for career assistance. It runs, then returns the final message content.

UX flow summary (web UI):
1. User opens `GET /` (root). The page loads a minimal chat interface.
2. On send, the browser posts JSON to `POST /chat` with `{ text, contextId }`.
3. The server calls `JobAgent.invoke(text, contextId)` and returns `{ reply }`.
4. The UI appends user and agent bubbles; errors are shown inline if the call fails.

Environment variables:
- `GOOGLE_CLOUD_PROJECT` (required)
- `GOOGLE_CLOUD_LOCATION` (e.g., `us-central1`) (required)
- `HOST_OVERRIDE` (optional; used to publish external URL in the Agent Card, e.g., Cloud Run URL)

Local run pattern:
```bash
cd job-agent
uv sync
uv run . --host 0.0.0.0 --port 8080
# Open http://localhost:8080
```

Cloud Run deployment (example):
```bash
gcloud run deploy job-agent \
  --source ./job-agent \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1

URL=$(gcloud run services describe job-agent --region us-central1 --format='value(status.url)')
gcloud run services update job-agent --region us-central1 --update-env-vars HOST_OVERRIDE=$URL
```

### `purchasing_concierge/purchasing_agent.py`
Main orchestrating agent that coordinates remote seller agents.

**Key Methods:**
- `create_agent()`: Creates ADK agent with tools and callbacks
- `before_agent_callback()`: Initializes A2A connections to remote agents
- `send_task()`: Sends tasks to specific remote agents via A2A
- `list_remote_agents()`: Discovers available remote agents

**Dependencies:**
```python
from google.adk import Agent
from a2a.client import A2ACardResolver
from a2a.types import AgentCard, SendMessageRequest, MessageSendParams
```

### `purchasing_concierge/remote_agent_connection.py`  
Wrapper for A2A client connections to remote agents.

**Key Class:**
```python
class RemoteAgentConnections:
    def __init__(self, agent_card: AgentCard, agent_url: str)
    async def send_message(self, message_request: SendMessageRequest) -> SendMessageResponse
```

### Remote Agent Executors
Each remote agent has an executor that bridges A2A protocol with agent logic.

**Pattern:**
```python
class [Agent]Executor(AgentExecutor):
    def __init__(self):
        self.agent = [SpecificAgent]()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        result = self.agent.invoke(query, context.context_id)
        
        parts = [Part(root=TextPart(text=str(result)))]
        await event_queue.enqueue_event(completed_task(...))
```

### Agent Implementations

#### `pizza_agent/agent.py` - LangGraph Implementation
- Uses `create_react_agent` with `create_pizza_order` tool
- Maintains conversation memory with `MemorySaver`
- Structured system instructions for pizza ordering

#### `burger_agent/agent.py` - CrewAI Implementation  
- Uses CrewAI's `Agent`, `Task`, `Crew` pattern
- Single agent with `create_burger_order` tool
- Template-based task instructions

#### `job_agent/agent.py` - Misconfigured Implementation
- **Issue**: Contains pizza agent logic instead of job logic
- **Problem**: Uses `create_pizza_order` tool for job agent
- **Fix Needed**: Should implement job-specific functionality

## Tool Patterns

### Order Creation Tools
All agents follow similar tool patterns for order creation:

```python
from pydantic import BaseModel
from langchain_core.tools import tool  # LangGraph
from crewai.tools import tool          # CrewAI

class OrderItem(BaseModel):
    name: str
    quantity: int 
    price: int

class Order(BaseModel):
    order_id: str
    status: str
    order_items: list[OrderItem]

@tool
def create_[product]_order(order_items: list[OrderItem]) -> str:
    order_id = str(uuid.uuid4())
    order = Order(order_id=order_id, status="created", order_items=order_items)
    return f"Order {order.model_dump()} has been created"
```

## HTTP/API Layers

### A2A Protocol Endpoints
Each remote agent exposes A2A protocol endpoints via `A2AStarletteApplication`:

- `GET /`: Returns agent card (capabilities, skills, metadata)
- `POST /send_message`: Accepts A2A message requests
- WebSocket support for streaming responses

### Gradio Interface  
The main UI exposes a chat interface that:
- Connects to deployed Agent Engine
- Streams responses from purchasing agent
- Formats tool calls and responses with metadata

### Cloud Run Deployment
Each component runs as a containerized service:
- Remote agents: Individual Cloud Run services
- Purchasing agent: Deployed to Vertex AI Agent Engine
- UI: Can run locally or be deployed separately

## Configuration Patterns

### Environment Variables
```python
# Common across all components
GOOGLE_CLOUD_PROJECT=project-id
GOOGLE_CLOUD_LOCATION=us-central1  
GOOGLE_GENAI_USE_VERTEXAI=True

# Purchasing agent specific
PIZZA_SELLER_AGENT_URL=https://pizza-agent-url
BURGER_SELLER_AGENT_URL=https://burger-agent-url
AGENT_ENGINE_RESOURCE_NAME=projects/.../reasoningEngines/...

# Remote agents
HOST_OVERRIDE=https://external-url  # For agent card URL
PORT=8080                           # Cloud Run default
```

### Docker Configuration
All remote agents use similar Dockerfile patterns:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
ENTRYPOINT ["uv", "run", ".", "--host", "0.0.0.0", "--port", "8080"]
```

This modular architecture allows for independent development, testing, and deployment of each agent while maintaining standardized communication protocols.
