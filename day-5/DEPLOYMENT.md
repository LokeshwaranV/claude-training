# Elation Health Chat Bot - Local Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for non-Docker setup)
- Node.js 18+ (for frontend development)
- ANTHROPIC_API_KEY environment variable set

## Quick Start with Docker Compose

### 1. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
nano .env
```

### 2. Start the Application

```bash
docker-compose up -d
```

The application will start on:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Stop the Application

```bash
docker-compose down
```

---

## Local Development Setup (Without Docker)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_key_here

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on: http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variable
export REACT_APP_API_URL=http://localhost:8000

# Start development server
npm start
```

Frontend runs on: http://localhost:3000

---

## API Endpoints

### Chat Endpoints

**POST /api/chat/message**
- Send a message to the chat assistant
- Request body:
  ```json
  {
    "message": "Your clinical question",
    "session_id": "optional-session-id",
    "patient_context": {
      "patient_id": "P001",
      "name": "John Doe",
      "age": 45,
      "conditions": ["Hypertension"],
      "medications": ["Lisinopril 10mg"],
      "allergies": ["Penicillin"]
    },
    "specialty": "general_practice"
  }
  ```

**POST /api/chat/generate-note**
- Generate clinical note from conversation
- Request body:
  ```json
  {
    "session_id": "session-id",
    "patient_id": "P001",
    "encounter_type": "office_visit",
    "specialty": "general_practice"
  }
  ```

**GET /api/chat/history/{session_id}**
- Get conversation history
- Query params: `limit=50` (optional)

**POST /api/chat/validate**
- Validate clinical content
- Request body: `{"content": "clinical text", "specialty": "general_practice"}`

**POST /api/chat/summarize**
- Summarize patient chart data
- Request body: `{"chart_data": "...", "patient_id": "P001", "specialty": "general_practice"}`

**DELETE /api/chat/session/{session_id}**
- End a session

---

## Testing

### Run Backend Tests

```bash
cd backend
pytest tests/test_chat_service.py -v
```

### API Testing with cURL

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat message
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how can I help with documentation?",
    "specialty": "general_practice"
  }'
```

---

## Troubleshooting

### API Key Not Found
- Ensure `ANTHROPIC_API_KEY` is set in `.env` file
- Verify the key is valid and has API permissions

### Port Already in Use
- Backend (8000): `lsof -i :8000` and kill the process
- Frontend (3000): `lsof -i :3000` and kill the process
- Or change the ports in `docker-compose.yml`

### Docker Build Issues
```bash
# Clean up old images
docker-compose down -v
docker system prune

# Rebuild images
docker-compose build --no-cache
docker-compose up
```

### Frontend Not Connecting to Backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check `.env` file for correct `REACT_APP_API_URL`
- Check browser console for CORS errors

---

## Production Considerations

1. **Security**
   - Use HTTPS with proper SSL certificates
   - Implement authentication and authorization
   - Validate all user inputs
   - Implement rate limiting

2. **Scalability**
   - Use a production database (PostgreSQL)
   - Implement caching layer (Redis)
   - Use a proper reverse proxy (Nginx)
   - Consider load balancing

3. **Monitoring**
   - Set up logging aggregation
   - Implement performance monitoring
   - Set up alerts for critical issues
   - Track API usage and costs

4. **HIPAA Compliance**
   - Ensure data encryption at rest and in transit
   - Implement comprehensive audit logging
   - Use encryption for sensitive data
   - Regular security audits

---

## Performance Optimization

### Backend
- Implement request caching
- Use connection pooling for database
- Optimize Claude API calls
- Implement rate limiting

### Frontend
- Code splitting for faster initial load
- Optimize bundle size
- Implement virtual scrolling for large chat histories
- Use lazy loading for components

---

## Support and Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **CLAUDE.md**: See project documentation for architecture details
- **GitHub Issues**: Report bugs and feature requests
