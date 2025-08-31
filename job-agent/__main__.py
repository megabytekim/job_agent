"""
Entry point for the A2A + LangGraph Job Agent.
"""

from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import JobAgent
from agent_executor import JobAgentExecutor
import uvicorn
from dotenv import load_dotenv
import logging
import os
import click
import uuid
from starlette.responses import HTMLResponse, JSONResponse
from starlette.requests import Request

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", "host", default="0.0.0.0")
@click.option("--port", "port", default=int(os.getenv("PORT", "8080")))
def main(host, port):
    """Start the A2A server for the Job Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="job_agent",
            name="일자리 전문가",
            description="일자리 고민이 있는 사람에게 전문가 조언을 제공합니다.",
            tags=["job_agent"],
            examples=["커리어 고민이 있어요."],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="일자리 전문가",
            description="일자리 고민이 있는 사람에게 전문가 조언을 제공합니다.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=JobAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=JobAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=JobAgentExecutor(), task_store=InMemoryTaskStore()
        )
        server = A2AStarletteApplication(agent_card=agent_card, http_handler=request_handler)

        # Build underlying Starlette app and mount a simple web UI
        app = server.build()

        # Lightweight UI agent instance (separate from executor) for direct chats
        ui_agent = JobAgent()

        async def homepage(_: Request) -> HTMLResponse:
            return HTMLResponse(
                """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Job Agent - Chat</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; background: #0b1021; color: #e6e9f5; }
      .container { max-width: 840px; margin: 0 auto; padding: 24px; }
      h1 { margin: 0 0 16px; font-size: 20px; color: #a7b1ff; }
      .chat { background: #0f1633; border: 1px solid #1f2a56; border-radius: 12px; padding: 16px; min-height: 360px; }
      .msg { padding: 10px 12px; border-radius: 8px; margin: 8px 0; max-width: 80%; white-space: pre-wrap; }
      .user { background: #1b2554; margin-left: auto; }
      .agent { background: #131a3a; }
      .input { display: flex; gap: 8px; margin-top: 12px; }
      input, button { font-size: 16px; }
      input { flex: 1; padding: 10px 12px; border-radius: 8px; border: 1px solid #1f2a56; background: #0f1633; color: #e6e9f5; }
      button { padding: 10px 14px; border-radius: 8px; border: 1px solid #2a3a7a; background: #2d3c80; color: #e6e9f5; cursor: pointer; }
      button:disabled { opacity: .6; cursor: not-allowed; }
      .hint { color: #97a0d1; font-size: 12px; margin-top: 8px; }
      a { color: #a7b1ff; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Job Agent - Chat</h1>
      <div class="chat" id="chat"></div>
      <div class="input">
        <input id="text" placeholder="Type your message..." />
        <button id="send">Send</button>
      </div>
      <div class="hint">
        This UI posts to <code>/chat</code> on this service and renders the response. The Agent Card is available at <a href="/.well-known/agent.json">/.well-known/agent.json</a>.
      </div>
    </div>
    <script>
      const chat = document.getElementById('chat');
      const input = document.getElementById('text');
      const btn = document.getElementById('send');
      function safeUUID() {
        try {
          if (typeof crypto !== 'undefined' && crypto && typeof crypto.randomUUID === 'function') {
            return crypto.randomUUID();
          }
        } catch (_) {}
        // Fallback
        const s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
        return `${Date.now().toString(16)}-${s4()}-${s4()}-${s4()}-${s4()}${s4()}${s4()}`;
      }
      let contextId = safeUUID();

      function addMsg(text, cls) {
        const div = document.createElement('div');
        div.className = 'msg ' + cls;
        div.textContent = text;
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
      }

      let isProcessing = false; // 중복 처리 방지 플래그

      async function send() {
        const text = input.value.trim();
        if (!text || isProcessing) return; // 이미 처리 중이면 무시
        
        isProcessing = true; // 처리 시작
        input.value = '';
        btn.disabled = true;
        addMsg(text, 'user');
        
        try {
          const res = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, contextId }) });
          if (!res.ok) throw new Error('Request failed');
          const data = await res.json();
          if (data && data.reply) addMsg(data.reply, 'agent'); else addMsg('[No reply]', 'agent');
        } catch (e) {
          console.error('POST /chat failed', e);
          addMsg('Error: ' + e.message, 'agent');
        } finally {
          btn.disabled = false;
          isProcessing = false; // 처리 완료
          input.focus();
        }
      }

      btn.addEventListener('click', send);
      input.addEventListener('keydown', (e) => { 
        if (e.key === 'Enter') {
          e.preventDefault(); // 기본 Enter 동작 방지
          send(); 
        }
      });
      input.focus();
    </script>
  </body>
  </html>
                """
            )

        async def chat(request: Request) -> JSONResponse:
            body = await request.json()
            user_text = (body or {}).get("text", "").strip()
            context_id = (body or {}).get("contextId") or str(uuid.uuid4())
            if not user_text:
                return JSONResponse({"error": "Missing text"}, status_code=400)
            try:
                reply = ui_agent.invoke(user_text, context_id)
                return JSONResponse({"reply": reply, "contextId": context_id})
            except Exception as e:
                return JSONResponse({"error": str(e)}, status_code=500)

        app.add_route("/", homepage, methods=["GET"])
        app.add_route("/chat", chat, methods=["POST"])

        uvicorn.run(app, host=host, port=port)

        logger.info(f"Starting server on {host}:{port}")
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()


