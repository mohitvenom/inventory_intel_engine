# Inventory Intel Agent

A full-stack, MCP-powered agentic system that autonomously monitors product prices and stock across e-commerce retailers, stores historical data, and alerts on meaningful changes.

*Note: This project is being built incrementally in phases. See `docs/ROADMAP.md` for current progress.*

## Setup Instructions

1. **Start the Database**
   Ensure Docker is running, then start the PostgreSQL service:
   ```bash
   docker-compose up -d
   ```

2. **Set up Python Environment**
   Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   # source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Run the FastAPI Server**
   Start the development server for the backend app:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Verify Setup**
   Visit [http://localhost:8000/health](http://localhost:8000/health) to confirm the environment is healthy.
