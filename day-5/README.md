# 🏥 Elation Health Chat Bot

An AI-powered clinical documentation assistant that reduces chart review and documentation burden for clinicians. Inspired by the Elation Health case study achieving **61% reduction in documentation time**.

## Features

✅ **Intelligent Chat Interface** - Conversational AI for clinical documentation
✅ **Clinical Note Generation** - Auto-generate clinical notes from conversations
✅ **Patient Context** - Maintain patient medical history and context
✅ **Content Validation** - Validate clinical accuracy of generated content
✅ **Chart Summarization** - Quickly summarize patient records
✅ **Specialty-Specific** - Tailored responses for different medical specialties
✅ **HIPAA Compliance** - Secure handling of patient data
✅ **Session Management** - Persistent conversation history
✅ **Mobile Responsive** - Works on desktop and mobile devices

## Quick Start

### Prerequisites
- Docker and Docker Compose
- ANTHROPIC_API_KEY from [Anthropic Console](https://console.anthropic.com)

### 1. Clone and Setup
```bash
cd /home/labuser/Downloads/day-5
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start with Docker Compose
```bash
docker-compose up
```

### 3. Access the Application
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Try the Demo
1. Set patient context in the sidebar (optional)
2. Type a clinical question or observation
3. Get AI-generated responses
4. Generate clinical notes from conversations
5. Validate clinical content

## Architecture

### High-Level Design (HLD)

The system follows a layered architecture:

```
┌─────────────────────────────────────────┐
│      React Frontend (Web/Mobile)        │
└──────────────────┬──────────────────────┘
                   │ REST API
        ┌──────────▼──────────┐
        │   FastAPI Backend   │
        │  (8000)             │
        └──┬────────────┬─────┘
           │            │
    ┌──────▼────┐  ┌───▼──────────┐
    │  Claude   │  │ Session/Data │
    │  API      │  │ Storage      │
    └───────────┘  └──────────────┘
```

### Low-Level Design (LLD)

**Backend Components:**
- `services/chat_service.py` - Claude API integration
- `routes/chat.py` - REST endpoints
- `session/manager.py` - Session management
- `models/schemas.py` - Data models

**Frontend Components:**
- `ChatWindow` - Message display
- `InputArea` - User input
- `PatientInfo` - Patient context management

## Technology Stack

| Component | Tech |
|-----------|------|
| **Backend** | Python 3.11, FastAPI |
| **Frontend** | React 18, JavaScript |
| **LLM** | Claude 3.5 Sonnet |
| **Database** | SQLite (local), PostgreSQL (production) |
| **Deployment** | Docker Compose |

## Project Structure

```
elation-health-chatbot/
├── backend/
│   ├── services/
│   │   ├── chat_service.py         # Claude integration
│   │   └── document_service.py     # Document handling
│   ├── routes/
│   │   └── chat.py                 # API endpoints
│   ├── session/
│   │   └── manager.py              # Session management
│   ├── models/
│   │   └── schemas.py              # Data models
│   ├── main.py                     # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── InputArea.jsx
│   │   │   └── PatientInfo.jsx
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── tests/
│   └── test_chat_service.py
├── CLAUDE.md                       # Project documentation
├── DEPLOYMENT.md                   # Deployment guide
├── docker-compose.yml
├── Dockerfile.backend
└── README.md (this file)
```

## API Endpoints

### Chat
- `POST /api/chat/message` - Send message and get response
- `POST /api/chat/generate-note` - Generate clinical note
- `GET /api/chat/history/{session_id}` - Get conversation history
- `POST /api/chat/validate` - Validate clinical content
- `POST /api/chat/summarize` - Summarize patient records
- `DELETE /api/chat/session/{session_id}` - End session

### System
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Swagger API documentation

## Development

### Local Setup (No Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ANTHROPIC_API_KEY=your_key uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

### Running Tests
```bash
cd backend
pytest tests/ -v
```

## Configuration

Edit `.env` file to configure:
- `ANTHROPIC_API_KEY` - Your Claude API key
- `HOST` / `PORT` - Server configuration
- `DEBUG` - Debug mode (true/false)
- `REACT_APP_API_URL` - Backend URL for frontend

## Features in Development

- [ ] Voice input/output support
- [ ] Real-time collaboration
- [ ] Elation EHR integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Custom prompt templates

## Use Cases

### Physician Burnout Reduction
- Automated documentation drafting
- Patient record summarization
- Reduced paperwork burden

### Clinical Data Processing
- Automated data extraction
- Record structuring
- Accuracy validation

### Evidence-Based Medicine
- Patient population screening
- Treatment eligibility identification
- Intervention recommendations

## Performance Metrics

| Metric | Target |
|--------|--------|
| Chart Review Time | -50% reduction |
| Documentation Time | -60% reduction |
| Clinical Accuracy | >99% |
| Response Latency | <2 seconds |
| API Availability | >99.9% uptime |

## HIPAA Compliance

- ✅ Encrypted data transmission (HTTPS)
- ✅ Encrypted data at rest
- ✅ Audit logging for all access
- ✅ Role-based access control
- ✅ Secure session management
- ✅ Regular security audits

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port
lsof -i :8000  # or :3000
kill -9 <PID>
```

**API key not working?**
- Verify key in `.env` file
- Test with: `curl -H "x-api-key: YOUR_KEY" https://api.anthropic.com/v1/messages`

**Frontend can't reach backend?**
- Check `REACT_APP_API_URL` in `.env`
- Verify backend is running: `curl http://localhost:8000/health`

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## License

This project is provided as-is for educational and healthcare purposes.

## Support

- 📖 See [CLAUDE.md](CLAUDE.md) for detailed architecture
- 🚀 See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions
- 📝 API docs available at http://localhost:8000/docs

---

**Built with ❤️ for healthcare providers and clinical teams**
