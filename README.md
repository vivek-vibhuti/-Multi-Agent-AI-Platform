# Multi AI Agent Workflow

An enterprise-grade AI agent orchestration platform built with FastAPI backend, Streamlit frontend, and LangGraph for multi-agent workflows. Leverages Groq for fast LLM inference and Tavily for web search capabilities.

## Features

- **Multi-Agent Orchestration**: Uses LangGraph to create sophisticated agent workflows with tool integration
- **FastAPI Backend**: High-performance async API for agent communication
- **Streamlit Frontend**: Professional, enterprise-grade UI with real-time telemetry and monitoring
- **Web Search Integration**: Tavily API for real-time information retrieval
- **Multiple LLM Support**: Configurable Groq models (Llama 3.3 70B, Llama 3.1 8B, etc.)
- **Observability**: Built-in metrics, latency tracking, and token usage monitoring
- **Extensible Tool System**: Pluggable tools for code execution, vector databases, and more
- **Production Ready**: Docker-ready structure with environment configuration

## Architecture

```
├── app/
│   ├── backend/          # FastAPI application
│   │   └── app.py        # Main API endpoints
│   ├── core/             # AI agent logic
│   │   └── ai_agent.py   # LangGraph agent implementation
│   ├── frontend/         # Streamlit UI
│   │   └── ui.py         # Professional dashboard interface
│   ├── config/           # Configuration management
│   │   └── settings.py   # Environment variable handling
│   └── common/           # Shared utilities (logging, exceptions)
├── requirements.txt      # Python dependencies
├── setup.py              # Package configuration
└── .env                  # Environment variables (API keys)
```

### Core Components

1. **Backend API** (`app/backend/app.py`)
   - RESTful endpoint (`/chat`) for agent interactions
   - Model validation and error handling
   - Integration with AI agent service

2. **AI Agent** (`app/core/ai_agent.py`)
   - LangGraph-based agent creation
   - Tool integration (web search, code execution, etc.)
   - Message processing and response generation

3. **Frontend UI** (`app/frontend/ui.py`)
   - Streamlit-based professional dashboard
   - Real-time telemetry and metrics display
   - Interactive prompt composer and execution controls
   - Workflow visualization and debugging tools

## Installation

### Prerequisites
- Python 3.8+
- API keys for:
  - Groq (for LLM inference)
  - Tavily (for web search)
  - Optional: Google API keys for additional services

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Multiagent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env` (if exists) or create a new `.env` file
   - Add your API keys:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
     TAVILY_API_KEY=your_tavily_api_key_here
     # Optional: Google APIs
     GOOGLE_API_KEY=your_google_api_key_here
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     ```

## Usage

### Starting the Application

1. Start the backend API server:
   ```bash
   python -m app.main
   ```
   The API will be available at `http://127.0.0.1:9999`

2. In a separate terminal, launch the Streamlit frontend:
   ```bash
   streamlit run app/frontend/ui.py
   ```
   The UI will be available at `http://localhost:8501`

### Using the API

The backend exposes a single POST endpoint:

```
POST /chat
Content-Type: application/json

{
    "model_name": "llama-3.3-70b-versatile",
    "system_prompt": "You are a helpful AI assistant",
    "messages": ["Your query here"],
    "allow_search": true
}
```

Response:
```json
{
    "response": "AI agent response text"
}
```

### Frontend Features

The Streamlit UI provides:

- **Agent Control**: Model selection, temperature, token limits, and system prompts
- **Tool Integrations**: Toggle web search, code sandbox, vector DB, and other tools
- **Execution Tabs**: 
  - Response: View and export agent outputs
  - Workflow Graph: Visualize the LangGraph execution flow
  - Reasoning Trace: Step-by-step chain-of-thought visualization
  - Memory & State: Inspect LangGraph state and checkpoints
  - Tool Pipeline: Monitor tool execution logs
  - Metrics: Latency, token usage, and cost estimates
  - Raw Payload: Inspect HTTP requests/responses
- **System Telemetry**: Real-time CPU, memory, GPU, and API quota monitoring
- **Prompt Composer**: With presets for common tasks (quantum computing, security audits, etc.)

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | API key for Groq LLM inference | Yes |
| `TAVILY_API_KEY` | API key for Tavily web search | Yes (for search functionality) |
| `GOOGLE_API_KEY` | API key for Google services | Optional |
| `OPENROUTER_API_KEY` | API key for OpenRouter | Optional |

### Model Configuration

Available models are defined in `app/config/settings.py`:
- `llama-3.3-70b-versatile`
- `llama-3.1-8b-instant`

Additional models can be added to the `ALLOWED_MODEL_NAMES` list.

## API Endpoints

### POST `/chat`
Send a message to the AI agent and get a response.

**Parameters:**
- `model_name` (string): LLM model to use (must be in `ALLOWED_MODEL_NAMES`)
- `system_prompt` (string): Instructions for the agent's behavior
- `messages` (array): User messages (single string or array of strings)
- `allow_search` (boolean): Enable/disable web search tool

**Returns:**
- `response` (string): Agent's generated response

**Error Responses:**
- `400`: Invalid model name
- `500`: Internal server error during agent processing

## Development

### Project Structure
- `app/backend/`: FastAPI application
- `app/core/`: Agent logic and LangGraph integration
- `app/frontend/`: Streamlit dashboard
- `app/config/`: Settings and environment management
- `app/common/`: Shared utilities (logging, custom exceptions)

### Running Tests
*(Add testing instructions if tests exist)*

### Code Style
*(Add linting/formatting guidelines if applicable)*

## Deployment

### Docker
*(Add Dockerfile and docker-compose instructions if available)*

### Cloud Deployment
The application can be deployed to any platform supporting Python/FastAPI and Streamlit:
- AWS (ECS, EKS, Elastic Beanstalk)
- Google Cloud (Cloud Run, App Engine)
- Azure (App Service, Container Instances)
- Vercel (for frontend) + any backend host

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- [LangGraph](https://langchain-ai.github.io/langgraph/) for agent orchestration
- [Groq](https://groq.com/) for fast LLM inference
- [Tavily](https://tavily.com/) for AI-optimized search
- [Streamlit](https://streamlit.io/) for rapid UI development
- [FastAPI](https://fastapi.tiangolo.com/) for high-performance API

---

**Note**: This README was generated based on the project structure and code analysis. For the most accurate and up-to-date information, please refer to the source code and any existing documentation in the repository.