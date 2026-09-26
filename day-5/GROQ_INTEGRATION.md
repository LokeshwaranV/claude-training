# Groq Integration Guide

## Overview

This project now integrates **Groq** for ultra-fast LLM inference using open-source models. Groq provides:

- ⚡ **Ultra-fast inference** (~50ms response time)
- 🔓 **Open-source models** (Llama, Mixtral)
- 💰 **No rate limits** for local development
- 🏥 **Healthcare-optimized** model selection
- 🚀 **Production-ready** API

## Supported Models

### Llama 3.1 (Recommended) 🌟
```
Model ID: llama-3.1-70b-versatile
Max Tokens: 8K
Best For: General tasks, clinical documentation
Speed: Ultra-fast
Quality: Highest
```

### Llama 3
```
Model ID: llama3-70b-8192
Max Tokens: 8K
Best For: Creative tasks, analysis
Speed: Very fast
Quality: High
```

### Mixtral 8x7B
```
Model ID: mixtral-8x7b-32768
Max Tokens: 32K (highest context)
Best For: Long-context analysis, summarization
Speed: Fast
Quality: High
```

## Configuration

### Step 1: Get Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Navigate to API Keys
4. Create new API key
5. Copy and save securely

⚠️ **Important**: Never commit API keys to version control!

### Step 2: Set Environment Variables

**Backend (.env)**
```env
GROQ_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE
GROQ_MODEL=llama3.1
```

**Alternative models:**
```env
GROQ_MODEL=llama3
GROQ_MODEL=mixtral
```

### Step 3: Verify Installation

```bash
# Backend dependencies already included
python -m pip show groq

# Should output groq version 0.x.x+
```

## Usage

### Python Backend

#### GroqClient Class

```python
from backend.services.groq_client import GroqClient

# Initialize with default model (llama3.1)
client = GroqClient()

# Or specify custom model
client = GroqClient(model="mixtral")

# Get model info
info = client.get_model_info()
print(info)
# {
#   "model": "llama-3.1-70b-versatile",
#   "provider": "Groq",
#   "max_tokens": 4096,
#   "type": "Open-source (Llama 3.1/Mixtral)",
#   ...
# }
```

#### Generate Response

```python
# Simple response
response = client.generate_response(
    prompt="What are the symptoms of hypertension?",
    temperature=0.7
)

# With system prompt
response = client.generate_response(
    prompt="Draft a clinical note for patient with flu symptoms",
    system_prompt="You are a clinical documentation assistant",
    temperature=0.3,
    max_tokens=1000
)
```

#### Stream Response

```python
# Real-time streaming for frontend
for chunk in client.stream_response(
    prompt="Generate discharge instructions",
    system_prompt="You are a helpful medical assistant"
):
    print(chunk, end="", flush=True)
```

#### Clinical Functions

```python
# Generate clinical summary
summary = client.generate_clinical_summary(
    patient_notes="Patient presented with fever, cough, and fatigue...",
    max_length=500
)

# Extract clinical entities
entities = client.extract_entities(
    text="Patient on Lisinopril 10mg daily for hypertension..."
)
# Returns: {
#   "medications": ["Lisinopril 10mg daily"],
#   "conditions": ["Hypertension"],
#   "vitals": [],
#   "recommendations": []
# }

# Validate content
validation = client.validate_content_fast(
    content="Patient diagnosed with pneumonia, prescribed..."
)
# Returns: {
#   "is_valid": True,
#   "confidence": 92,
#   "issues": []
# }
```

#### Switch Models

```python
# Change model at runtime
client.switch_model("mixtral")
# Output: "Switched to mixtral: mixtral-8x7b-32768"

# Available models
print(client.AVAILABLE_MODELS)
# {
#   "llama3.1": "llama-3.1-70b-versatile",
#   "llama3": "llama3-70b-8192",
#   "mixtral": "mixtral-8x7b-32768"
# }
```

### API Endpoints

#### Send Message

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the treatment options for diabetes?",
    "session_id": "session-123",
    "patient_context": {"age": 45, "conditions": ["Type 2 Diabetes"]},
    "specialty": "endocrinology"
  }'
```

Response:
```json
{
  "response": "Treatment options for Type 2 Diabetes include...",
  "session_id": "session-123",
  "timestamp": "2024-09-26T12:00:00Z",
  "model": "llama-3.1-70b-versatile",
  "tokens_used": 150
}
```

#### Generate Clinical Note

```bash
curl -X POST http://localhost:8000/api/chat/generate-note \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "patient_id": "P001",
    "encounter_type": "office_visit",
    "specialty": "internal_medicine"
  }'
```

## Performance Metrics

### Groq vs Other Providers

| Provider | Model | Latency | Cost | Quality |
|----------|-------|---------|------|---------|
| **Groq** | Llama 3.1 | ~50ms | Free | High |
| OpenAI | GPT-4 | ~2000ms | $0.03/1K | Highest |
| Anthropic | Claude 3 | ~1500ms | $0.003/1K | Very High |
| Local (CPU) | Llama 2 | ~10000ms | $0 | Medium |

### Throughput

- Single request: ~50ms (0.3s with overhead)
- Parallel requests: 100-150 RPS per API key
- Token generation: ~100-150 tokens/second

## Optimization Tips

### 1. Prompt Engineering
```python
# ❌ Bad: Vague prompt
"Give me medical advice"

# ✅ Good: Clear, specific prompt
"List 5 evidence-based treatment options for hypertension in a 65-year-old patient with chronic kidney disease, with contraindications"
```

### 2. Temperature Setting
```python
# Creative tasks
temperature=0.7-1.0

# Clinical documentation (be accurate!)
temperature=0.3-0.5

# Analysis tasks
temperature=0.5-0.7
```

### 3. Context Trimming
```python
# ❌ Bad: Send full conversation history
messages = all_messages  # Could be 10k+ tokens

# ✅ Good: Summarize old context
messages = [
    {"role": "system", "content": "Prior context: ..."},
    *recent_messages[-10:]  # Keep recent context
]
```

### 4. Batch Requests
```python
# ❌ Bad: Sequential requests
for item in items:
    response = client.generate_response(item)  # Slow!

# ✅ Good: Batch when possible
responses = [client.generate_response(item) for item in items]
# Can parallelize with asyncio
```

## Error Handling

```python
from groq import APIError, RateLimitError

try:
    response = client.generate_response(prompt)
except RateLimitError:
    print("Rate limited - wait and retry")
except APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Security Considerations

### API Key Protection

```python
# ✅ Good: Use environment variables
api_key = os.getenv("GROQ_API_KEY")

# ❌ Bad: Hardcode keys
api_key = "gsk_..."  # Never do this!
```

### Data Privacy

- ✅ Patient data stays within your infrastructure
- ✅ Groq doesn't store your requests
- ✅ No model training on your data
- ✅ HIPAA-compatible (verify in enterprise terms)

### Rate Limiting

```python
# Implement rate limiting
from functools import wraps
import time

def rate_limit(max_calls=10, time_window=60):
    def decorator(func):
        calls = []
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - time_window]
            if len(calls) >= max_calls:
                raise RateLimitError("Rate limit exceeded")
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Monitoring & Logging

### Request Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("groq_client")

# Logs all Groq requests
logger.info(f"Groq request: {prompt[:100]}...")
logger.info(f"Response tokens: {token_count}")
```

### Metrics Collection

```python
metrics = {
    "total_requests": 0,
    "total_tokens": 0,
    "avg_latency": 0,
    "error_count": 0
}

def track_request(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            metrics["total_requests"] += 1
            return result
        except Exception:
            metrics["error_count"] += 1
            raise
        finally:
            metrics["avg_latency"] = (
                (metrics["avg_latency"] * (metrics["total_requests"]-1) +
                 (time.time() - start)) / metrics["total_requests"]
            )
    return wrapper
```

## Troubleshooting

### Issue: Invalid API Key

```
groq.error.AuthenticationError: Invalid API key
```

**Solution:**
1. Verify key in console.groq.com
2. Check `.env` file for typos
3. Restart backend after changing key

### Issue: Rate Limited

```
groq.error.RateLimitError: Rate limit exceeded
```

**Solution:**
1. Wait 60 seconds before retrying
2. Implement exponential backoff
3. Check API dashboard for quota

### Issue: Model Not Found

```
groq.error.NotFoundError: model not found
```

**Solution:**
1. Check model name in `AVAILABLE_MODELS`
2. Use default model: `llama-3.1-70b-versatile`
3. Verify model ID on Groq console

### Issue: Timeout

```
groq.error.APITimeoutError: Request timed out
```

**Solution:**
1. Reduce `max_tokens` parameter
2. Check internet connection
3. Increase timeout threshold
4. Use shorter prompts

## Cost Analysis

### Groq (Free Tier)
- 0 API calls/month
- 0 cost
- Perfect for development/testing

### Groq (Enterprise)
- Volume pricing available
- Custom rate limits
- Dedicated support

### vs Alternative Providers
```
OpenAI GPT-4:
- $0.03 per 1K tokens (input)
- $0.06 per 1K tokens (output)
- ~100K tokens = $4.50

Groq Llama 3.1:
- $0 (free tier)
- ~100K tokens = $0
```

## Next Steps

1. ✅ Set up Groq API key
2. ✅ Configure environment variables
3. ✅ Test with example prompts
4. ✅ Integrate with chat endpoints
5. ✅ Monitor performance metrics
6. 🔜 Scale to production

## Resources

- [Groq Console](https://console.groq.com)
- [Groq API Docs](https://console.groq.com/docs)
- [Llama Model Cards](https://llama.meta.com/)
- [LLM Best Practices](https://openai.com/research/practices)

## Support

For Groq-specific issues:
- Check [Groq Status Page](https://status.groq.com)
- Contact Groq support via console
- Review API documentation

For integration questions:
- Review code examples in this guide
- Check backend error logs
- Open project issue with details
