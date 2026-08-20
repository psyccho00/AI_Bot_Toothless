# 🐉 Toothless Health Assistant - Quick Start Guide

Get up and running with Toothless in 5 minutes!

## Step 1: Get Your Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in to your account
3. Copy your API key
4. Save it somewhere safe

## Step 2: Setup Python Environment

```bash
# Navigate to project directory
cd toothless-health-assistant

# Create virtual environment
python -m venv venv

# Activate it (choose one based on your OS)
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure API Key

Edit `.env` file and replace:
```
ANTHROPIC_API_KEY="your-api-key-here"
```

With your actual Claude API key.

## Step 5: Run the Server

```bash
python main.py
```

You should see:
```
✅ Database initialized
🐉 Welcome to Toothless - AI Health Assistant!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 6: Access the API

### Option A: Interactive Documentation
Open http://localhost:8000/docs in your browser

### Option B: Run Demo Script
In another terminal:
```bash
python demo.py
```

### Option C: Use cURL Commands

```bash
# Register a user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "age": 30,
    "gender": "Male"
  }'

# Chat with Toothless
curl -X POST http://localhost:8000/toothless/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "I have been feeling tired recently"
  }'
```

## Common Tasks

### 1. Create a New User

```python
import requests

response = requests.post("http://localhost:8000/users/register", json={
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "age": 30,
    "gender": "Male",
    "medical_history": "None",
    "allergies": "None"
})

user = response.json()
user_id = user['id']
print(f"User created with ID: {user_id}")
```

### 2. Chat with Toothless

```python
response = requests.post("http://localhost:8000/toothless/chat", json={
    "user_id": user_id,
    "message": "I've been having trouble sleeping"
})

ai_response = response.json()
print("Toothless:", ai_response['response'])
```

### 3. Track Health

```python
# Create a health check-in
response = requests.post(f"http://localhost:8000/health-checkins?user_id={user_id}", json={
    "symptoms": "Mild headache",
    "pain_level": 3,
    "energy_level": 5,
    "sleep_quality": 6,
    "sleep_hours": 7
})

checkin = response.json()
print("Check-in assessment:", checkin['ai_assessment'])
```

### 4. Track Mood

```python
response = requests.post(f"http://localhost:8000/mood-entries?user_id={user_id}", json={
    "mood_rating": 7,
    "mood_type": "happy",
    "stress_level": 3,
    "anxiety_level": 2,
    "depression_signs": 1
})

mood = response.json()
print("Mood recommendation:", mood['ai_recommendation'])
```

### 5. View Health Dashboard

```python
response = requests.get(f"http://localhost:8000/dashboard/{user_id}")
dashboard = response.json()

print(f"User: {dashboard['user']['full_name']}")
print(f"Mood: {dashboard['metrics']['average_mood']}/10")
print(f"Energy: {dashboard['metrics']['average_energy']}/10")
```

## API Endpoints Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/users/register` | POST | Register new user |
| `/users/login` | POST | Login user |
| `/users/{user_id}` | GET | Get user profile |
| `/health-checkins` | POST | Create health check-in |
| `/mood-entries` | POST | Log mood entry |
| `/medications` | POST | Add medication |
| `/toothless/chat` | POST | Chat with Toothless AI |
| `/dashboard/{user_id}` | GET | Get health dashboard |
| `/docs` | GET | API documentation |

## Troubleshooting

### Error: "Could not connect to API"
- Make sure the server is running: `python main.py`
- Check that you're using the correct port: http://localhost:8000

### Error: "ANTHROPIC_API_KEY not found"
- Edit `.env` file and add your Claude API key
- Make sure the key is valid and active

### Error: "Database locked"
- You may have multiple instances running
- Close other Python processes and restart

### Error: Connection refused
- Server might not be running
- Try: `python main.py`
- If port 8000 is in use, change it: `python main.py --port 8001`

## Next Steps

1. **Explore the API Documentation**: http://localhost:8000/docs
2. **Run the Demo Script**: `python demo.py`
3. **Build Your Own Integration**: Use the API in your application
4. **Deploy to Production**: See README.md for deployment instructions

## Key Features to Try

### 1. Daily Health Check-In
```bash
curl -X POST http://localhost:8000/toothless/daily-checkin \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

### 2. Mood Analysis
```bash
curl -X POST http://localhost:8000/mood-entries?user_id=1 \
  -H "Content-Type: application/json" \
  -d '{
    "mood_rating": 5,
    "mood_type": "anxious",
    "stress_level": 7,
    "anxiety_level": 6,
    "depression_signs": 2
  }'
```

### 3. Multi-Turn Conversation
```python
# First message
requests.post("http://localhost:8000/toothless/chat", json={
    "user_id": 1,
    "message": "I have been stressed lately"
})

# Follow-up (Toothless remembers context)
requests.post("http://localhost:8000/toothless/chat", json={
    "user_id": 1,
    "message": "It's mainly from work deadlines"
})
```

## Important Reminders

⚠️ **Disclaimer**: Toothless is an AI health assistant, not a replacement for professional medical advice. Always consult licensed healthcare providers for serious health concerns.

🔒 **Privacy**: Keep your API key private. Don't commit it to version control.

📝 **Development**: The included SQLite database is for development. Use PostgreSQL for production.

## Getting Help

- **API Docs**: http://localhost:8000/docs
- **README**: Open `README.md` for comprehensive documentation
- **Demo Script**: Run `python demo.py` to see examples
- **Issues**: Check error messages in the terminal

---

**Congratulations!** You now have Toothless running. Your AI Health Assistant is ready! 🐉✨
