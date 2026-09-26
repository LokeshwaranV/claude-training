# Development Guide - Elation Health Chat Bot

This guide explains how to set up the project for local development without Docker.

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn
- Git

## Backend Development

### Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create data directories:**
```bash
mkdir -p data/sessions
```

5. **Set environment variables:**
```bash
export ANTHROPIC_API_KEY=your_key_here
# Or on Windows:
# set ANTHROPIC_API_KEY=your_key_here
```

6. **Start development server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

**API Documentation:** http://localhost:8000/docs (Swagger UI)

### Project Structure

```
backend/
├── services/
│   ├── __init__.py
│   └── chat_service.py           # Claude API integration
├── routes/
│   ├── __init__.py
│   └── chat.py                   # REST endpoints
├── session/
│   ├── __init__.py
│   └── manager.py                # Session management
├── models/
│   ├── __init__.py
│   └── schemas.py                # Pydantic models
├── integrations/
│   ├── __init__.py
│   └── elation_client.py         # EHR integration (future)
├── main.py                       # FastAPI application
├── requirements.txt
└── __init__.py
```

### Key Services

#### ChatService (`services/chat_service.py`)

Handles all Claude API interactions:

```python
from services.chat_service import ChatService

chat_service = ChatService()

# Process a message
response = chat_service.process_message(
    user_message="Hello",
    conversation_history=[],
    patient_context=patient_data,
    specialty=SpecialtyEnum.GENERAL_PRACTICE
)

# Generate a note
note = chat_service.generate_note(
    conversation_history=messages,
    patient_context=patient_data
)

# Validate content
validation = chat_service.validate_clinical_content(
    content="Clinical note text"
)

# Summarize chart
summary = chat_service.summarize_chart(
    chart_data="...",
    patient_context=patient_data
)
```

#### SessionManager (`session/manager.py`)

Manages conversation sessions:

```python
from session.manager import SessionManager

session_manager = SessionManager()

# Create session
session_id = session_manager.create_session(
    user_id="user123",
    patient_id="P001",
    specialty=SpecialtyEnum.GENERAL_PRACTICE
)

# Add message
session_manager.add_message(
    session_id=session_id,
    role=MessageRole.USER,
    content="Message text"
)

# Get history
messages = session_manager.get_conversation_history(session_id)

# Get session
session = session_manager.get_session(session_id)

# End session
session_manager.end_session(session_id)
```

### Testing Backend

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_chat_service.py -v

# Run with coverage
pytest --cov=services tests/
```

### Adding New Routes

1. Create handler function in appropriate route file
2. Use Pydantic models for request/response validation
3. Add docstring with endpoint description
4. Test with provided test file

Example:
```python
# In routes/chat.py
@router.post("/new-endpoint", response_model=ResponseModel)
async def new_endpoint(request: RequestModel) -> ResponseModel:
    """Description of what this endpoint does."""
    try:
        # Your logic here
        return ResponseModel(...)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Frontend Development

### Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set environment variables:**
```bash
# Create .env.local file in frontend directory
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
```

4. **Start development server:**
```bash
npm start
```

The app will open at: http://localhost:3000

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWindow.jsx        # Message display
│   │   ├── ChatWindow.css
│   │   ├── InputArea.jsx         # User input
│   │   ├── InputArea.css
│   │   ├── PatientInfo.jsx       # Patient context
│   │   └── PatientInfo.css
│   ├── App.jsx                   # Main component
│   ├── App.css
│   ├── index.jsx                 # React entry point
│   └── index.css
├── public/
│   └── index.html
├── package.json
└── Dockerfile
```

### Component Architecture

#### App Component
Main container that manages:
- Global state (messages, session, patient data)
- API communication
- Message handling

#### ChatWindow Component
Displays:
- Message list
- User/assistant messages with different styles
- Loading indicator
- Markdown rendering

#### InputArea Component
Provides:
- Text input for messages
- Submit button
- Keyboard shortcuts (Enter to send, Shift+Enter for newline)

#### PatientInfo Component
Manages:
- Patient data form
- Medical specialty selection
- Patient information display
- Form validation

### Adding New Components

1. Create component file in `src/components/`
2. Create corresponding CSS file
3. Import and use in parent component
4. Ensure responsive design

Example:
```jsx
import React, { useState } from 'react';
import './MyComponent.css';

function MyComponent({ prop1, prop2 }) {
  const [state, setState] = useState(null);
  
  return (
    <div className="my-component">
      {/* JSX */}
    </div>
  );
}

export default MyComponent;
```

### Styling Guidelines

- Use CSS files (not CSS-in-JS)
- Follow BEM naming convention
- Mobile-first responsive design
- Color palette from App.css

### API Communication

```jsx
// Making API calls
const apiUrl = process.env.REACT_APP_API_URL;

fetch(`${apiUrl}/api/chat/message`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userInput,
    session_id: sessionId,
    patient_context: patientData,
    specialty: specialty
  })
})
.then(res => res.json())
.then(data => {
  // Handle response
})
.catch(err => console.error(err));
```

### Building for Production

```bash
npm run build
```

This creates optimized production build in `build/` directory.

## Common Development Tasks

### Debugging Backend

```bash
# Enable debug mode
export DEBUG=true
uvicorn main:app --reload

# Use Python debugger
import pdb; pdb.set_trace()  # In code
```

### Debugging Frontend

1. Use Chrome DevTools (F12)
2. React DevTools extension for React debugging
3. Console for logs and errors
4. Network tab for API calls

### Adding Dependencies

**Backend:**
```bash
cd backend
pip install new_package
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install new_package
npm install  # Updates package-lock.json
```

### Database Management

Currently using SQLite for local development:
```bash
# Database location
backend/data/chat.db

# To reset
rm backend/data/chat.db
```

For production, switch to PostgreSQL.

### Running Tests

```bash
cd backend
pytest tests/test_chat_service.py -v

# With coverage report
pytest --cov=services tests/
```

### Code Formatting

```bash
# Python
pip install black
black backend/

# JavaScript
npm run format  # (if configured in package.json)
```

## Useful Commands

```bash
# Start both services in development
# Terminal 1
cd backend && uvicorn main:app --reload

# Terminal 2
cd frontend && npm start

# Stop services
Ctrl+C in each terminal

# Clean up
rm -rf backend/venv
rm -rf frontend/node_modules
rm -rf data/
```

## Tips and Best Practices

1. **Use type hints** in Python for better IDE support
2. **Component reusability** in React - create smaller components
3. **Error handling** - always handle API errors gracefully
4. **Testing** - write tests for critical functionality
5. **Git commits** - make small, meaningful commits
6. **Documentation** - document complex logic

## Troubleshooting

### Python ModuleNotFoundError
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Node modules errors
- Delete node_modules: `rm -rf node_modules`
- Reinstall: `npm install`

### API connection errors
- Check backend is running on port 8000
- Verify `REACT_APP_API_URL` environment variable
- Check browser console for CORS errors

### Port conflicts
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

## Next Steps

1. Set up local environment
2. Run both backend and frontend
3. Test basic chat functionality
4. Review code structure
5. Start contributing!

Happy coding! 🚀
