# Quick Start - Elation Health Chat Bot v2.0

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- API Keys: Claude + Groq

---

## Option 1: Docker Compose (Easiest)

```bash
# 1. Navigate to project
cd /home/labuser/Downloads/day-5

# 2. Set up environment
cp .env.example .env
# Edit .env and add:
# ANTHROPIC_API_KEY=sk_ant_...
# GROQ_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE

# 3. Start services
docker-compose up -d

# 4. Wait 30 seconds for startup

# 5. Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Option 2: Local Development (5 min)

### Backend (Terminal 1)
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export ANTHROPIC_API_KEY=sk_ant_...
export GROQ_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE

# Start server
uvicorn main:app --reload

# Backend ready at http://localhost:8000
```

### Frontend (Terminal 2)
```bash
cd frontend

# Install dependencies
npm install

# Set environment
export REACT_APP_API_URL=http://localhost:8000

# Start development
npm start

# Frontend opens at http://localhost:3000
```

---

## Try It Out

### 1. Open Chat
Go to `http://localhost:3000`

### 2. Add Patient Context (Optional)
Click "✏️ Edit Patient" in sidebar:
- Name: John Doe
- Age: 45
- Conditions: Hypertension, Type 2 Diabetes
- Medications: Lisinopril 10mg, Metformin 500mg
- Allergies: Penicillin

### 3. Start Chatting
Send: "Patient presenting with persistent headaches for 2 weeks"

### 4. Generate Note
Click "📝 Generate Note"

### 5. View Guidelines
Visit: `http://localhost:8000/api/rag/guidelines`
POST: `{"condition": "hypertension"}`

---

## New Features in v2.0

### 1. Groq Fast Responses
- Real-time AI responses
- 10x faster than Claude alone
- Automatic fallback to Claude

### 2. Multi-Agent System
- Frontend Agent: UI optimization
- Backend Agent: API development
- RAG Agent: Clinical knowledge
- Triage Agent: Quality review

### 3. Clinical Knowledge Base
- Hypertension guidelines
- Diabetes protocols
- Drug interactions
- Medication appropriateness
- COPD management
- Depression screening

### 4. Observability
```bash
# View metrics
curl http://localhost:8000/api/metrics

# Output:
# {
#   "total_api_calls": 42,
#   "error_rate": 2.38,
#   "avg_response_time_ms": 1200,
#   ...
# }
```

### 5. Load Testing
```bash
# Run load test
k6 run load_tests/load_test.js

# Generates report:
# - Response times (p50, p95, p99)
# - Error rates
# - Throughput
```

---

## API Endpoints

### Health
```bash
curl http://localhost:8000/health
```

### Chat
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Clinical note text",
    "specialty": "general_practice"
  }'
```

### RAG - Get Guidelines
```bash
curl -X POST http://localhost:8000/api/rag/guidelines \
  -H "Content-Type: application/json" \
  -d '{"condition": "hypertension"}'
```

### RAG - Retrieve Documents
```bash
curl "http://localhost:8000/api/rag/retrieve?query=blood%20pressure&top_k=3"
```

### Orchestration Status
```bash
curl http://localhost:8000/api/orchestration/status
```

### Metrics
```bash
curl http://localhost:8000/api/metrics
```

---

## Configuration

### Environment Variables
Edit `.env`:
```bash
# Required
ANTHROPIC_API_KEY=your_key
GROQ_API_KEY=your_key

# Optional features
RAG_ENABLED=true
OTEL_ENABLED=true
ENABLE_ORCHESTRATION=true
```

### Agent Configuration
Edit `.claude/settings.json` for:
- Agent models & capabilities
- Tool access levels
- Context limits
- Observability settings

---

## Documentation

- **CLAUDE.md** - Architecture & HLD/LLD
- **README.md** - Project overview
- **SKILLS.md** - Agent capabilities
- **AIDLC_PLAN.md** - Implementation plan
- **AIDLC_DEPLOYMENT.md** - Full deployment guide
- **DEVELOPMENT.md** - Developer guide

---

## Troubleshooting

### "API key not found"
```bash
# Check .env file
cat .env | grep ANTHROPIC_API_KEY

# Or set directly
export ANTHROPIC_API_KEY=sk_ant_...
```

### "Port 8000 already in use"
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### "Frontend can't reach backend"
```bash
# Check backend running
curl http://localhost:8000/health

# Check .env in frontend
echo $REACT_APP_API_URL
```

---

## What's New in v2.0

| Feature | Status |
|---------|--------|
| Groq Integration | ✅ Live |
| Multi-Agent Orchestration | ✅ Ready |
| Clinical RAG Engine | ✅ Active |
| OpenTelemetry | ✅ Configured |
| Load Testing | ✅ Included |
| MCP Framework | ✅ Prepared |
| Context Trimming | ✅ Enabled |
| Advanced Settings | ✅ Added |

---

## Next Steps

1. **Run locally** to test features
2. **Read documentation** in AIDLC_DEPLOYMENT.md
3. **Set up monitoring** with OpenTelemetry
4. **Run load tests** to benchmark performance
5. **Explore RAG** knowledge base
6. **Configure agents** for your needs

---

## Performance Expectations

### Response Times
- Chat message: 300ms (Groq) - 2000ms (Claude)
- RAG retrieval: 150ms
- Note generation: 2500ms
- P95 latency: <1 second

### Reliability
- Success rate: >99%
- Error rate: <1%
- Uptime: 99.9%

---

## Key Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health & info |
| `/health` | GET | System health |
| `/api/chat/message` | POST | Send message |
| `/api/chat/generate-note` | POST | Generate note |
| `/api/rag/knowledge` | GET | Knowledge base info |
| `/api/rag/retrieve` | GET | Retrieve documents |
| `/api/rag/guidelines` | POST | Get guidelines |
| `/api/orchestration/status` | GET | Agent status |
| `/api/metrics` | GET | System metrics |
| `/docs` | GET | API documentation |

---

## Support

- 📖 See AIDLC_DEPLOYMENT.md for detailed setup
- 🔍 Check logs: `docker-compose logs backend`
- 🐛 Report issues with full error messages
- 💬 Ask questions in documentation

---

**Ready to go!** 🚀  
Start with Option 1 (Docker) for fastest setup.

Questions? See AIDLC_DEPLOYMENT.md for detailed troubleshooting.
