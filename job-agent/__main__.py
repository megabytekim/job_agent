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

        uvicorn.run(server.build(), host=host, port=port)

        logger.info(f"Starting server on {host}:{port}")
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()


