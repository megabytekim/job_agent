# Job Agent

A smart AI-powered job application assistant built using the Agent-to-Agent (A2A) protocol to streamline your job search process through intelligent automation and multi-agent collaboration.

## Description

Job Agent is an advanced tool designed to help job seekers manage their applications, track their progress, and optimize their job search strategy using AI agents that can communicate and collaborate with each other. Built on the [Agent-to-Agent (A2A) protocol](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge?hl=ko#1), this system enables multiple specialized AI agents to work together to provide comprehensive job search assistance.

Whether you're actively looking for new opportunities or just keeping your options open, this tool provides the structure, automation, and insights you need to stay organized and focused through intelligent agent collaboration.

## Features

- **Multi-Agent Architecture**: Specialized AI agents working together using A2A protocol
- **Application Tracking**: Keep track of all your job applications in one place with intelligent status updates
- **Status Management**: Monitor the progress of each application through different stages with automated notifications
- **Company Research**: AI agents automatically gather and organize information about potential employers
- **Interview Preparation**: Prepare for interviews with structured notes and AI-powered reminders
- **Analytics**: Get insights into your job search performance and patterns through intelligent analysis
- **Automated Communication**: Agents can communicate with job boards, company systems, and other services
- **Real-time Updates**: Receive instant updates on application status changes and new opportunities

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with billing enabled
- Google Cloud CLI (gcloud) installed
- Docker (for containerized deployment)
- Knowledge of HTTP services and full-stack architecture

### Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd job_agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or using uv (recommended)
   uv sync
   ```

3. Set up Google Cloud configuration:
   ```bash
   # Authenticate with Google Cloud
   gcloud auth login
   
   # Set your project ID
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable required APIs
   gcloud services enable run.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```

4. Configure environment variables:
   ```bash
   # Copy and edit the environment template
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

## Usage

### Architecture Overview

Job Agent implements a multi-agent architecture using the A2A protocol:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Job Seeker    │    │  Job Agent      │    │  Company        │
│   (User)        │◄──►│  (A2A Client)   │◄──►│  Agents         │
│                 │    │                 │    │  (A2A Servers)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Google Cloud   │
                       │  Run Services   │
                       └─────────────────┘
```

### Agent Types

- **Application Tracker Agent**: Manages job application status and progress
- **Company Research Agent**: Gathers information about potential employers
- **Interview Scheduler Agent**: Handles interview coordination and reminders
- **Job Board Agent**: Monitors and applies to job postings automatically

### Basic Commands

```bash
# Start the main job agent interface
python main.py

# Deploy agents to Cloud Run
gcloud run deploy job-agent --source .

# View agent logs
gcloud logs read --service=job-agent

# Test agent communication
python test_a2a_communication.py
```

### A2A Protocol Implementation

The system uses the A2A protocol for agent communication:

1. **Agent Discovery**: A2A client searches for available A2A server agent cards
2. **Connection Building**: Client builds connections based on agent capabilities
3. **Message Exchange**: Agents communicate using standardized payload formats
4. **Status Updates**: Real-time progress updates through push notifications
5. **Artifact Delivery**: Completed tasks deliver results to requesting agents

## Project Structure

```
job_agent/
├── README.md
├── requirements.txt              # Python dependencies
├── main.py                      # Main application entry point
├── agents/                      # A2A agent implementations
│   ├── application_tracker.py   # Application tracking agent
│   ├── company_researcher.py    # Company research agent
│   ├── interview_scheduler.py   # Interview coordination agent
│   └── job_board_monitor.py     # Job board monitoring agent
├── a2a/                         # A2A protocol implementation
│   ├── client.py               # A2A client implementation
│   ├── server.py               # A2A server implementation
│   └── models.py               # Data models and schemas
├── cloud_run/                   # Cloud Run deployment files
│   ├── Dockerfile              # Container configuration
│   └── service.yaml            # Service deployment config
├── tests/                       # Test files
│   ├── test_a2a_communication.py
│   └── test_agents.py
├── .env.example                # Environment variables template
└── .gitignore                  # Git ignore file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the [LICENSE NAME] - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

- Project Link: [https://github.com/yourusername/job_agent](https://github.com/yourusername/job_agent)
- Email: [your-email@example.com]

## Acknowledgments

- **Google Codelabs**: This project is inspired by the [Agent-to-Agent (A2A) Protocol tutorial](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge?hl=ko#1) which demonstrates multi-agent communication using Google Cloud services
- **Google Cloud Platform**: For providing the infrastructure and services that enable this multi-agent architecture
- **A2A Protocol**: For establishing the standard for agent-to-agent communication and collaboration
- **Agent Development Kit (ADK)**: For the framework that enables building intelligent agent systems

## Technical References

- [Agent-to-Agent (A2A) Protocol Documentation](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge?hl=ko#1)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Cloud Agent Engine Documentation](https://cloud.google.com/agent-engine/docs)
- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/)

---

**Note**: This is a work in progress. Features and documentation will be updated as the project develops. The A2A protocol is currently in development, so implementation details may change as the protocol evolves.
