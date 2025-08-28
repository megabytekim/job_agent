# Job Agent Documentation

This document provides an overview of the Job Agent's code structure and execution flow.

## Project Structure

The project is organized into the following key files:

-   `__main__.py`: The main entry point for the application. It initializes and runs the web server.
-   `agent.py`: Defines the core logic of the Job Agent using LangGraph and Google Vertex AI.
-   `agent_executor.py`: Connects the Job Agent to the A2A server framework.
-   `pyproject.toml`: Lists the project's dependencies.

## Execution Flow

1.  **Application Startup**: The application is started by running `__main__.py`. This file uses `uvicorn` to launch a web server.

2.  **A2A Server Initialization**: The `__main__.py` script sets up an `A2AStarletteApplication`, which creates a web server that adheres to the A2A (Agent-to-Agent) communication protocol. It also defines the agent's capabilities and metadata, such as its name, description, and skills.

3.  **User Interaction**: The application provides a simple web interface for users to interact with the agent. When a user sends a message, the web server receives it at the `/chat` endpoint.

4.  **Agent Invocation**: The `/chat` endpoint calls the `JobAgent`'s `invoke` method to process the user's query.

5.  **Core Agent Logic**: The `JobAgent` in `agent.py` uses a ReAct (Reasoning and Acting) agent created with `langgraph`. This agent is powered by Google's Gemini model and is provided with a system prompt that instructs it to act as a pizza store assistant. The agent can use the `create_pizza_order` tool to create pizza orders.

6.  **A2A Framework Integration**: The `JobAgentExecutor` in `agent_executor.py` integrates the `JobAgent` with the A2A server. It receives requests from the A2A server, passes them to the `JobAgent`, and sends the agent's response back to the server.

## Key Technologies

-   **FastAPI**: The web framework used to build the A2A server (via `A2AStarletteApplication`).
-   **LangChain & LangGraph**: The frameworks used to build the core agent logic.
-   **Google Vertex AI**: The platform that provides the Gemini large language model.
-   **A2A SDK**: A library for building agents that can communicate with each other.
