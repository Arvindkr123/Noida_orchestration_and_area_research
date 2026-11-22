# Noida Area Research

A small full-stack research prototype for Noida and its sectors. It turns a
question into a structured research plan, runs the selected data tools, and
returns the plan, source results, and an execution trace.

## What it does

1. Validates the request and extracts its location and topics with a Groq-hosted
   language model.
2. Builds a plan with research questions and selected tools.
3. Runs selected tools concurrently:
   - **News:** recent news search through Tavily.
   - **Weather:** current conditions and a three-day forecast from Open-Meteo.
   - **Traffic:** Tavily web search for traffic and connectivity information.
4. Returns each tool's results and any per-tool errors. If one tool fails, the
   other successful results are still returned.

Traffic results are web-search findings, not live map traffic speeds or
turn-by-turn routing. Weather is fetched from Open-Meteo and does not require an
API key.

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer and npm
- A Groq API key
- A Tavily API key

## Run on Windows

### 1. Configure and start the backend

In PowerShell, from the project root:

```powershell
Set-Location .\backend
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `backend\.env` and set your keys. If you already have this file, keep it
and update only the values you need:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Start the API from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Using `python -m uvicorn` ensures Uvicorn runs from the active virtual
environment. The API health check is at <http://127.0.0.1:8000/health>, and
interactive API documentation is at <http://127.0.0.1:8000/docs>.

### 2. Start the frontend

Open a second PowerShell terminal from the project root:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The frontend uses `http://localhost:8000` by
default. To use another backend URL, set `VITE_API_BASE_URL` in a frontend
`.env` file.

## API example

Send a research request to `POST /api/research`:

```powershell
$body = @{
    mode = "sector"
    input = "Sector 62"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/research" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

Supported modes are `query`, `sector`, and `city`. City mode currently accepts
Noida only. The response includes the detected intent, research plan,
`tool_results`, `execution_trace`, and an `errors` list. A tool failure produces
the `completed_with_errors` status while preserving successful tool results.

## Run backend checks

From the `backend` directory with the virtual environment activated:

```powershell
python -m unittest discover -s tests -v
```

Build the frontend from the `frontend` directory:

```powershell
npm run build
```

