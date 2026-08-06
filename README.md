# ✈️ TripMate AI — Multi-Agent Travel Planner

<div align="center">

### Powered by LangGraph · PostgreSQL Checkpointing · AviationStack · Tavily · Groq LLaMA

[![Live App](https://img.shields.io/badge/🌐_Live_App-Open_TripMate_AI-4f46e5?style=for-the-badge&logo=render&logoColor=white)](https://trip-planner-ai-multi-agent-travel.onrender.com)

| 🌐 **Live Website** | [trip-planner-ai-multi-agent-travel.onrender.com](https://trip-planner-ai-multi-agent-travel.onrender.com) |
|---|---|

<br/>

![Python](https://img.shields.io/badge/Python_3.12+-3776AB?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-blueviolet?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Checkpointer-336791?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F55036?style=flat-square)

</div>

---
![Architecture Diagram](diagram.png)
## 🧠 What Is This?

**TripMate AI** is a fully deployed **multi-agent travel planning system** built with LangGraph. You type a natural language travel request — *"Plan a complete 7-day Japan trip from Bangladesh under 2 lakhs"* — and four specialised AI agents execute in sequence: one searches **live flights**, one searches **hotels**, one drafts a **day-by-day itinerary**, and one compiles everything into a **beautifully formatted travel plan** with budget estimates.

Every conversation is persisted in **PostgreSQL via LangGraph's `PostgresSaver` checkpointer** — so the system remembers your session and you can continue planning across multiple requests.

---

## 🤖 The Four-Agent Pipeline

```mermaid
flowchart LR
    S(["✍️ User Query"])

    F["✈️ flight_agent\nAviationStack live API\nIATA resolver · route parser"]
    H["🏨 hotel_agent\nTavily web search\nTop 3 hotel results"]
    I["🗓️ itinerary_agent\nllama-3.3-70b\nDay-by-day plan"]
    R["📋 final_agent\nllama-3.3-70b\n6-section travel report"]

    E(["📬 Final Travel Plan"])

    S --> F --> H --> I --> R --> E

    classDef entry  fill:#7c3aed,stroke:#5b21b6,color:#fff
    classDef flight fill:#0369a1,stroke:#075985,color:#fff
    classDef hotel  fill:#0f766e,stroke:#059669,color:#fff
    classDef itin   fill:#b45309,stroke:#92400e,color:#fff
    classDef final  fill:#7e22ce,stroke:#6b21a8,color:#fff
    classDef done   fill:#059669,stroke:#047857,color:#fff

    class S entry
    class F flight
    class H hotel
    class I itin
    class R final
    class E done
```

Each agent writes its output into the shared `TravelState` — the next agent reads it automatically. No manual data passing needed.

---

## ✨ Features

| | |
|---|---|
| ✈️ **Live Flight Search** | Queries AviationStack API for real-time flight data — airline, flight number, terminal, gate, scheduled time, delay |
| 🌍 **Smart IATA Resolver** | Parses natural language queries like *"from Bangladesh to Japan"* into IATA codes (`DAC → NRT`) using `airportsdata` + `pycountry` + custom city/country maps |
| 🏨 **Hotel Discovery** | Tavily web search returns top 3 hotel results with title, URL, and snippet for the destination |
| 🗓️ **Day-by-Day Itinerary** | LLM generates a practical, budget-aware day-by-day plan from combined flight + hotel context |
| 📋 **Formatted Travel Report** | Final agent structures the response into 6 clear sections: summary, flights, hotels, itinerary, budget, recommendations |
| 💾 **PostgreSQL Memory** | `PostgresSaver` checkpointer persists every conversation thread — resume where you left off across sessions |
| ⚡ **LLM Call Counter** | `llm_calls` tracked in state — the system reports exactly how many LLM invocations were made per request |
| 🖥️ **Custom Web UI** | Vanilla HTML/CSS/JS frontend served via Jinja2 templates — no Streamlit, clean and fast |
| 🐳 **Docker Ready** | Single `Dockerfile` — build and run anywhere |
| 🔢 **Quick Prompts** | Pre-built buttons: Japan trip, Dubai trip, Thailand trip, Global flights |

---

## 🏗️ Project Structure

```
Trip-Planner-AI/
│
├── 🐍 backend.py               # LangGraph agent graph — 4 nodes, state, PostgreSQL checkpointer
├── 🐍 app.py                   # FastAPI app — serves UI + POST /api/travel endpoint
├── 🐍 main.py                  # Root entry point
│
├── 📂 tools/
│   ├── 🐍 flight_tool.py       # AviationStack API + smart IATA resolver + route parser
│   └── 🐍 tavily_tool.py       # Tavily web search — hotel results
│
├── 📂 templates/
│   └── 🌐 index.html           # TripMate AI web UI (Jinja2 template)
│
├── 📂 static/
│   ├── 🎨 style.css            # Custom dark UI with gradient blobs
│   └── ⚡ script.js            # Fetch API, streaming result display, quick prompts
│
├── 🐳 Dockerfile               # Python 3.12-slim, uvicorn entry
├── 📋 requirements.txt
└── 🔬 test.py                  # Manual test runner
```

---

## 🔀 How The Agent Graph Works

### State Definition

Every piece of data flows through `TravelState` — a `TypedDict` with `Annotated[list, operator.add]` for message accumulation:

```python
class TravelState(TypedDict):
    messages       : Annotated[list[AnyMessage], operator.add]  # accumulates across all agents
    user_query     : str        # original user question
    flight_results : str        # AviationStack output
    hotel_results  : str        # Tavily output
    itinerary      : str        # LLM-generated day plan
    llm_calls      : int        # how many LLM calls this request made
```

### Agent 1 — `flight_agent`

Calls `search_flights(query)` which:
1. Strips stopwords from the query (`flight`, `trip`, `hotel`, `budget`, etc.)
2. Parses the route using regex patterns: `from X to Y`, `to Y from X`, `flights from X`, `flights to X`
3. Resolves location names to IATA codes (city → airport → IATA via lookup tables + `pycountry`)
4. Calls AviationStack REST API with `dep_iata` and `arr_iata` params
5. Formats up to 10 flights with airline, status, terminal, gate, scheduled time, delay

```
"7-day Japan trip from Bangladesh" 
    → dep: "Bangladesh" → "IN" → fallback → "DAC" (Dhaka)
    → arr: "Japan"      → "JP" → "NRT"   (Narita)
    → AviationStack: dep_iata=DAC, arr_iata=NRT
```

### Agent 2 — `hotel_agent`

Prepends `"Best hotels for "` to the user query and calls `tavily_search()`, which returns the top 3 results as formatted strings with title, URL, and a 300-character snippet.

### Agent 3 — `itinerary_agent`

Passes `user_query + flight_results + hotel_results` to `llama-3.3-70b-versatile` via Groq with a prompt asking for a practical, budget-aware day-by-day plan.

### Agent 4 — `final_agent`

Combines all state fields and asks the LLM to produce a final report formatted into 6 sections:

```
1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations
```

### Graph Wiring

```python
graph.add_edge(START,           "flight_agent")
graph.add_edge("flight_agent",  "hotel_agent")
graph.add_edge("hotel_agent",   "itinerary_agent")
graph.add_edge("itinerary_agent","final_agent")
graph.add_edge("final_agent",    END)
```

---

## 💾 PostgreSQL Checkpointing — Persistent Memory

Every request is tied to a `thread_id`. If you send a follow-up question with the same `thread_id`, LangGraph loads your previous conversation from PostgreSQL and continues from where you left off.

```python
checkpointer = PostgresSaver(conn=psycopg.connect(DATABASE_URL, autocommit=True))
checkpointer.setup()   # auto-creates the checkpoint tables

travel_graph = graph.compile(checkpointer=checkpointer)

# Each request gets a config with thread_id
config = {"configurable": {"thread_id": thread_id}}
result = travel_graph.invoke(inputs, config=config)
```

If no `thread_id` is provided, a new one is generated (`user_{uuid4().hex}`) and returned in the response so the frontend can reuse it on subsequent turns.

---

## ✈️ Smart IATA Resolver — How It Works

The flight tool can resolve nearly any location string into an IATA airport code:

| Input | Resolution path | Output |
|---|---|---|
| `"NRT"` | Direct IATA match | `NRT` |
| `"Tokyo"` | `CITY_MAIN_AIRPORT` lookup | `NRT` |
| `"Japan"` | `country_name_to_code` → `JP` → `COUNTRY_MAIN_AIRPORT` | `NRT` |
| `"United States"` | `pycountry.countries.lookup` → `US` → main airport | `JFK` |
| `"England"` | `COUNTRY_ALIASES["england"]` → `GB` → main airport | `LHR` |
| `"Bangkok"` | `CITY_MAIN_AIRPORT` lookup | `BKK` |

**Fallback scoring** — if city/country lookup fails, it scans all IATA airports and scores them:
- +100 if the city matches exactly
- +70 if the query is in the city name
- +50 if "international" is in the airport name
- Returns the highest-scoring match

---

## 🌐 API Reference

### `GET /`

Serves the TripMate AI web UI (Jinja2 `index.html`).

---

### `POST /api/travel`

Run the full 4-agent travel planning pipeline.

**Request:**
```json
{
  "message": "Plan a complete 7 days Japan trip from Bangladesh under 2 lakhs",
  "thread_id": null
}
```

**Response:**
```json
{
  "success": true,
  "thread_id": "user_a1b2c3d4...",
  "answer": "## 🌍 Your Complete Japan Travel Plan\n\n### 1. Trip Summary\n...",
  "flight_results": "Live flights from DAC to NRT\n\nAirline: Biman...",
  "hotel_results": "1. **Park Hyatt Tokyo**\n  https://...",
  "itinerary": "Day 1: Arrive at Narita...",
  "llm_calls": 2
}
```

Pass the returned `thread_id` in subsequent requests to continue the same session.

---

### `GET /health`

```json
{ "status": "ok", "message": "AI Travel Planner API is running" }
```

---

## 📦 Installation & Local Setup

### Prerequisites

- Python 3.12+
- PostgreSQL database (local or [Render](https://render.com) / [Supabase](https://supabase.com))
- [Groq API key](https://console.groq.com) (free)
- [Tavily API key](https://tavily.com) (free tier)
- [AviationStack API key](https://aviationstack.com) (free tier — live flight data)

### 1. Clone

```bash
git clone https://github.com/paras160500/Trip-Planner-AI--Multi-Agent-Travel-Planner-with-Langgraph-PostgreSQL.git
cd Trip-Planner-AI--Multi-Agent-Travel-Planner-with-Langgraph-PostgreSQL
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Configure `.env`

```env
# LLM
GROQ_API_KEY=your_groq_api_key

# Web Search
TAVILY_API_KEY=your_tavily_api_key

# Live Flight Data
AVIATIONSTACK_API_KEY=your_aviationstack_api_key

# Default departure airport (IATA) — used when no origin is specified
DEFAULT_ORIGIN_DATA=BOM

# PostgreSQL — LangGraph checkpointing
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

> **SSL note:** the code automatically appends `?sslmode=require` to `DATABASE_URL` if not already present — required for Render/Supabase hosted databases.

### 4. Run

```bash
uvicorn app:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000)

---

## 🐳 Docker

```bash
# Build
docker build -t tripmate-ai .

# Run
docker run -p 8000:8000 --env-file .env tripmate-ai
```

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| **Agent Framework** | LangGraph `StateGraph` — sequential 4-node pipeline |
| **LLM** | Groq `llama-3.3-70b-versatile` (itinerary + final report) |
| **Flight Data** | AviationStack REST API (live flight status, not ticket prices) |
| **Hotel Search** | Tavily `TavilyClient` — web search, max 3 results |
| **IATA Resolution** | `airportsdata` + `pycountry` + custom city/country lookup tables |
| **Memory / Checkpointing** | LangGraph `PostgresSaver` (`langgraph-checkpoint-postgres`) |
| **Database** | PostgreSQL via `psycopg` (v3) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Jinja2 templates + vanilla HTML/CSS/JS |
| **Containerisation** | Docker (`python:3.12-slim`) |

---

## 🧠 Key Design Decisions

- **Sequential graph (not parallel)** — flight and hotel agents run one after the other so their outputs are available to the itinerary agent in state. A parallel fan-out would require a merge step to combine results, adding complexity for no real latency gain since all three calls are fast API/web requests.

- **`operator.add` on messages** — using `Annotated[list, operator.add]` as the reducer means each agent simply returns `[AIMessage(...)]` and LangGraph appends it to the running conversation list automatically. No manual list management needed.

- **`PostgresSaver` over `MemorySaver`** — `MemorySaver` is process-local and resets on restart. `PostgresSaver` persists checkpoints to disk, survives server restarts, and works across multiple Uvicorn workers.

- **`thread_id` returned to client** — the frontend stores the `thread_id` from the first response and sends it back on every subsequent message. This is the key to multi-turn conversations — the LangGraph graph picks up from the last checkpoint.

- **Stop-word stripping before IATA resolution** — words like `flight`, `hotel`, `trip`, `under`, `budget` would confuse the location extractor. Stripping them first means `"7-day Japan trip from Bangladesh"` cleanly resolves to `DAC → NRT`.

- **AviationStack gives status, not prices** — this is explicitly documented in the final agent prompt and in the API response. The assistant tells users that for ticket prices they need a pricing API like Amadeus.

---

## 💬 Example Query & Output

**Input:**
> "Plan a complete 7 days Japan trip from Bangladesh under 2 lakhs including flights, hotels and sightseeing"

**The system does:**
1. `flight_agent` → resolves `Bangladesh→DAC`, `Japan→NRT`, queries AviationStack
2. `hotel_agent` → Tavily search for "Best hotels for 7 days Japan trip..."
3. `itinerary_agent` → LLaMA builds a day-by-day plan from flights + hotels
4. `final_agent` → compiles the 6-section travel report

**Output sections:**
```
## 🌍 Your Complete Japan Travel Plan

### 1. Trip Summary
7-day Japan trip from Dhaka (DAC) to Tokyo (NRT)...

### 2. Flight Information
Biman Bangladesh Airlines · BG-319 · Status: active
Departure: Dhaka Hazrat Shahjalal Int'l · Gate A3 ...

### 3. Hotel Suggestions
- Park Hotel Tokyo – Shinjuku area, from ¥15,000/night
- APA Hotel Shinjuku ...

### 4. Day-by-Day Itinerary
Day 1: Arrive NRT → Shinjuku check-in → Shibuya crossing...
Day 2: Asakusa temple → Akihabara → teamLab Planets...
...

### 5. Estimated Budget
Flights: ~₹50,000 | Hotels: ~₹70,000 | Food: ~₹30,000 ...

### 6. Final Recommendations
Book 3+ months ahead for best fares. JR Pass recommended...
```

---

## 🔮 Future Improvements

- [ ] Add parallel fan-out for flight + hotel agents (faster for independent lookups)
- [ ] Integrate Amadeus API for actual ticket prices alongside AviationStack status data
- [ ] Add a `follow_up_agent` so users can refine plans mid-conversation
- [ ] Stream the LangGraph response token-by-token to the UI
- [ ] Deploy to Render with a Render PostgreSQL database (external connection string)
- [ ] Add hotel booking links via direct integration with Booking.com or Agoda

---

## 👨‍💻 Author

Built by **[paras160500](https://github.com/paras160500)**

Multi-Agent Travel Planner · LangGraph · FastAPI · PostgreSQL · Groq · AviationStack · Tavily
