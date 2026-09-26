# Quick Start Guide - Elation Health Chat Bot

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.11+
- Git (optional)

---

## Step 1: Backend Setup

### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Configure Environment

Update `.env` with your Groq API key:

```env
GROQ_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE
GROQ_MODEL=llama3.1
```

### Start Backend Server

```bash
python main.py
```

You should see:
```
🚀 Starting Elation Health Chat Bot v2.0...
⚡ Running with Groq + Open-Source LLMs (Llama 3.1/Mixtral)
✅ GROQ_API_KEY configured - using Groq for fast inference
...
🏥 Elation Health Chat Bot ready!
   Frontend: http://localhost:3000
   API Docs: http://localhost:8000/docs
```

---

## Step 2: Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Configure Environment

Create `.env` in frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

### Start Development Server

```bash
npm start
```

The app will open automatically at `http://localhost:3000` 🎉

---

## Step 3: Test the Application

### 1. Try a Simple Message

Type in the chat: 
```
What are the symptoms of hypertension?
```

You should get a response within 1-2 seconds!

### 2. Load Patient Context

1. Click "✏️ Edit Patient" in sidebar
2. Fill in sample patient data:
   - **Name**: John Smith
   - **Age**: 65
   - **Gender**: Male
   - **Conditions**: Hypertension, Type 2 Diabetes
   - **Medications**: Lisinopril 10mg daily, Metformin 500mg BID
   - **Allergies**: Penicillin
3. Click "💾 Save Patient"

### 3. Generate a Clinical Note

1. Send a message about the patient
2. Click "📝 Generate Note" button
3. Watch the system create a clinical note!

### 4. Switch Medical Specialties

Select a specialty from the dropdown:
- 👨‍⚕️ General Practice
- ❤️ Cardiology  
- 🧠 Neurology
- 🩹 Dermatology
- 👶 Pediatrics
- 💭 Psychiatry

### 5. Toggle Theme

Click the sun/moon icon to switch between dark and light themes.

---

## Architecture Overview

```
┌─────────────────────────┐
│   React Frontend        │
│   (Port 3000)           │
└──────────┬──────────────┘
           │ HTTP
           ▼
┌─────────────────────────┐
│   FastAPI Backend       │
│   (Port 8000)           │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│   Groq API              │
│   (Llama 3.1)           │
└─────────────────────────┘
```

---

## Key Features Showcase

### 🎨 Modern UI
- Professional healthcare color palette
- Dark/Light theme support
- Smooth animations and transitions
- Responsive design

### ⚡ Fast Inference
- Ultra-fast responses (~50ms)
- Open-source Llama 3.1 model
- No API rate limits
- Production-ready

### 🏥 Clinical Features
- Patient context management
- Medical specialty selection
- Clinical note generation
- Entity extraction

### 📱 Responsive
- Desktop: Full sidebar + chat
- Tablet: Collapsible sidebar
- Mobile: Bottom slide-up sidebar

---

## Common Tasks

### Change Backend Port

Edit `backend/main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Change here
        reload=True
    )
```

### Change Frontend URL

Edit `frontend/.env`:
```env
REACT_APP_API_URL=http://your-api-server:8000
```

### Switch Groq Model

Edit `.env`:
```env
GROQ_MODEL=mixtral  # or llama3
```

Then restart backend.

### Enable Logging

Edit `backend/.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Deploy to Production

```bash
# Build frontend
cd frontend
npm run build

# Serve with production backend
cd ../backend
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

---

## Troubleshooting

### "Failed to connect to backend"

1. Check backend is running: `http://localhost:8000/health`
2. Verify API URL in frontend `.env`
3. Check CORS is enabled in backend

### "Invalid Groq API Key"

1. Get new key from [console.groq.com](https://console.groq.com)
2. Update `.env` file
3. Restart backend: Press `Ctrl+C`, then run `python main.py`

### "Frontend won't load"

1. Clear browser cache: `Ctrl+Shift+Delete`
2. Hard refresh: `Ctrl+F5`
3. Check console for errors: `F12`

### "Slow responses"

1. Verify internet connection
2. Check Groq status: [status.groq.com](https://status.groq.com)
3. Try reducing `max_tokens` in `.env`

### "Syntax error in CSS"

1. Verify CSS variable names in `App.css`
2. Check for unclosed braces `{}`
3. Restart frontend: `Ctrl+C`, then `npm start`

---

## API Documentation

### Interactive Docs

Visit **http://localhost:8000/docs** for interactive Swagger UI

### Key Endpoints

```bash
# Send message
POST /api/chat/message
{
  "message": "What is diabetes?",
  "session_id": "session-123",
  "patient_context": {...},
  "specialty": "endocrinology"
}

# Generate note
POST /api/chat/generate-note
{
  "session_id": "session-123",
  "patient_id": "P001",
  "encounter_type": "office_visit",
  "specialty": "general_practice"
}

# Health check
GET /health
```

---

## Performance Tips

### Frontend
- Use production build: `npm run build`
- Clear browser cache regularly
- Close unused browser tabs

### Backend
- Monitor with `htop` or Task Manager
- Use production WSGI server (gunicorn)
- Enable Redis caching for sessions

### Groq
- Use Llama 3.1 for best performance
- Keep prompts focused
- Batch requests when possible

---

## Security Checklist

- [ ] Never commit `.env` files with real API keys
- [ ] Use HTTPS in production
- [ ] Rotate API keys monthly
- [ ] Enable audit logging
- [ ] Implement authentication
- [ ] Encrypt patient data
- [ ] Review HIPAA compliance

---

## Next Steps

1. ✅ Get app running (you are here!)
2. 🔗 Integrate with real patient data
3. 🔐 Add authentication/authorization
4. 📊 Set up monitoring and logging
5. 🚀 Deploy to production

---

## Documentation

- [Frontend Update](./FRONTEND_UPDATE.md) - UI/UX details
- [Groq Integration](./GROQ_INTEGRATION.md) - LLM setup guide
- [CLAUDE.md](./CLAUDE.md) - Project overview
- [API Docs](http://localhost:8000/docs) - Interactive docs

---

## Getting Help

### Issues?

1. Check [Troubleshooting](#troubleshooting) section
2. Review error logs in console
3. Check [GitHub Issues](https://github.com) (if applicable)

### Want to contribute?

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

### Have questions?

- Read the documentation
- Check existing issues
- Ask in project discussions

---

## What's New in This Update? ✨

### Frontend Improvements
- ✅ Modern aesthetic design with professional color palette
- ✅ Smooth animations and transitions
- ✅ Dark/Light theme support
- ✅ Improved responsive design
- ✅ Better accessibility

### Groq Integration
- ✅ Updated to Llama 3.1 (recommended model)
- ✅ Support for multiple OSS models
- ✅ Ultra-fast inference
- ✅ Model switching capability

### Documentation
- ✅ Comprehensive Groq guide
- ✅ Frontend update details
- ✅ Quick start guide
- ✅ Best practices

---

## Version Info

- **Frontend**: React 18
- **Backend**: FastAPI 0.104+
- **LLM**: Groq with Llama 3.1
- **Node**: 16+
- **Python**: 3.11+

---

**Ready to build amazing clinical AI? Let's go! 🏥**
