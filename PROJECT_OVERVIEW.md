# Toothless Health Assistant - Project Structure & Overview

## 📁 Complete File Structure

```
toothless-health-assistant/
├── requirements.txt           # Python package dependencies
├── config.py                 # Application configuration
├── models.py                 # SQLAlchemy database models
├── schemas.py                # Pydantic validation schemas
├── database.py               # Database setup and connection
├── toothless_ai.py          # Toothless AI Engine (Claude API integration)
├── main.py                  # FastAPI application with all endpoints
├── demo.py                  # Demo script showing API usage
├── .env                     # Environment variables (API keys)
├── README.md                # Comprehensive documentation
├── QUICKSTART.md            # Quick start guide
└── toothless.db            # SQLite database (created on first run)
```

## 📋 File Descriptions

### Core Application Files

#### `main.py` (Main Application)
- FastAPI application with all REST API endpoints
- Database initialization on startup
- CORS middleware configuration
- Organized into logical endpoint groups:
  - User Management (registration, login, profiles)
  - Health Check-Ins
  - Mood Tracking
  - Medication Management
  - Medical Information
  - Toothless AI Chat
  - Health Dashboard

**Key Endpoints:**
- POST `/users/register` - Register new user
- GET `/users/{user_id}` - Get user profile
- POST `/health-checkins` - Create health check-in
- POST `/mood-entries` - Log mood entry
- POST `/toothless/chat` - Chat with Toothless AI
- GET `/dashboard/{user_id}` - View health dashboard
- GET `/docs` - Interactive API documentation

#### `toothless_ai.py` (AI Engine)
- Toothless AI class that wraps Claude API
- System prompt defining Toothless personality and capabilities
- Core methods:
  - `chat()` - Process user messages with AI
  - `daily_health_checkin()` - Initiate structured check-in
  - `analyze_mood()` - Analyze mood data and provide insights
  - `check_medication_interactions()` - Check for drug interactions
  - `generate_health_summary()` - Create comprehensive health summary

**Features:**
- Maintains conversation history per user
- Extracts health alerts from conversations
- Identifies follow-up questions
- Detects when professional help is needed

#### `models.py` (Database Models)
SQLAlchemy ORM models for all data entities:
- **User** - User profiles with health info
- **HealthCheckIn** - Daily health records
- **MoodEntry** - Mood tracking entries
- **Medication** - Medication management
- **MedicalInfo** - Medical condition information
- **Conversation** - Chat history with Toothless

#### `schemas.py` (Data Validation)
Pydantic models for request/response validation:
- User management schemas
- Health check-in schemas
- Mood entry schemas
- Medication schemas
- Medical info schemas
- Toothless request/response schemas
- Authentication and dashboard schemas

#### `database.py` (Database Setup)
- SQLAlchemy engine and session factory
- Database initialization function
- Dependency injection for FastAPI sessions
- Support for both SQLite and PostgreSQL

#### `config.py` (Configuration)
- Centralized configuration management
- Environment variable loading
- Settings for:
  - Application metadata
  - Database connection
  - Claude API integration
  - JWT authentication
  - CORS settings

### Configuration Files

#### `.env` (Environment Variables)
- `ANTHROPIC_API_KEY` - Claude API key (REQUIRED)
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret for authentication
- `DEBUG` - Debug mode toggle

#### `requirements.txt` (Dependencies)
Python packages needed:
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - ORM
- Pydantic - Data validation
- Anthropic - Claude API client
- psycopg2 - PostgreSQL adapter
- Alembic - Database migrations
- python-jose - JWT handling

### Documentation Files

#### `README.md`
Comprehensive documentation including:
- Feature overview
- Installation instructions
- API endpoint reference with examples
- Security and privacy information
- Database model descriptions
- Configuration options
- Deployment guidelines
- Development notes

#### `QUICKSTART.md`
Fast setup guide with:
- Step-by-step installation
- API key setup
- Running the server
- Common tasks and examples
- Troubleshooting guide

### Utility Files

#### `demo.py`
Interactive demo script showing:
- User registration
- Conversation with Toothless
- Health check-in creation
- Mood tracking
- Medication management
- Health dashboard viewing
- Colored terminal output for clarity

## 🏗️ Architecture Overview

### Technology Stack

```
Frontend (Optional)
    ↓
FastAPI Application
    ├── Authentication & Users
    ├── Health Endpoints
    ├── Mood Tracking
    ├── Medication Management
    └── Toothless AI Integration
    ↓
Toothless AI Engine
    ↓
Claude API (chat.anthropic.com)
    ↓
SQLAlchemy ORM
    ↓
Database (SQLite/PostgreSQL)
```

### Data Flow

1. **User Registration**
   ```
   User API Request → FastAPI → Database → User Created
   ```

2. **Health Check-In with AI**
   ```
   Health Data → FastAPI → Toothless AI → Claude API → Assessment → Database
   ```

3. **Conversation**
   ```
   User Message → FastAPI → Toothless AI → Claude API → Response → Database
   ```

4. **Health Dashboard**
   ```
   API Request → FastAPI → Database Query → Analytics → Response
   ```

## 🔄 Request/Response Flow

### Example: Chat with Toothless

**Request:**
```json
{
  "user_id": 1,
  "message": "I've been feeling tired",
  "include_recommendations": true
}
```

**Processing:**
1. Validate request in FastAPI
2. Load user context from database
3. Send to Toothless AI
4. Toothless calls Claude API with system prompt
5. Extract health insights and alerts
6. Save conversation to database
7. Return response

**Response:**
```json
{
  "response": "I understand you're feeling tired. This could be related to sleep, stress, or health conditions...",
  "recommendations": ["How is your sleep quality?"],
  "health_alerts": [],
  "requires_professional_help": false
}
```

## 🌟 Key Features Implementation

### 1. Daily Health Check-In
- Initiated by `/toothless/daily-checkin` endpoint
- Toothless asks about symptoms, sleep, energy, mood
- Records data in `HealthCheckIn` table
- Generates AI assessment

### 2. Mood Tracking
- Collects mood rating, stress level, anxiety, depression signs
- Stores triggers and coping strategies
- Toothless analyzes mood patterns
- Provides mental health recommendations

### 3. Medication Management
- Track medication name, dosage, frequency
- Toothless can check for drug interactions
- Monitor compliance
- Track side effects

### 4. AI Conversations
- Multi-turn conversation support
- Context-aware responses
- Health alert detection
- Professional help recommendations

### 5. Health Dashboard
- Aggregated health metrics
- Mood and energy trends
- Recent entries summary
- Medication list
- Health alerts

## 🔐 Security Features

- **CORS Protection** - Configured origins
- **Password Hashing** - Ready for bcrypt integration
- **JWT Support** - Token-based authentication
- **HIPAA Ready** - Structured for compliance
- **Secure API Keys** - Environment variable management
- **Data Validation** - Pydantic schemas

## 📊 Database Schema

### User Table
- Stores user profile and medical history
- Relationships to health check-ins, mood entries, medications

### HealthCheckIn Table
- Daily health metrics
- AI assessment from Toothless
- Timestamps for tracking

### MoodEntry Table
- Mood ratings and emotional state
- Stress and anxiety levels
- AI recommendations

### Medication Table
- Active medications
- Dosage and frequency
- Side effects and interactions

### Conversation Table
- Chat history in JSON format
- Topic classification
- AI summaries and alerts

## 🚀 Running the Application

### Development
```bash
python main.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Docker
```bash
docker build -t toothless .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your-key toothless
```

## 📡 API Response Codes

- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## 🔧 Configuration Options

### Database
- SQLite (development): `sqlite:///./toothless.db`
- PostgreSQL (production): `postgresql://user:pass@host/db`

### Claude Model
- Current: `claude-opus-4-20250805`
- Can be changed in `config.py`

### Debug Mode
- Set `DEBUG=True` in `.env` for development
- Set `DEBUG=False` for production

## 📈 Performance Considerations

- Conversation history stored in-memory for speed
- Database queries optimized with indexing
- CORS caching enabled
- Connection pooling for database

## 🧪 Testing the Application

### Using Swagger UI
1. Navigate to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Enter parameters and execute

### Using Demo Script
```bash
python demo.py
```

### Using cURL
See QUICKSTART.md and README.md for examples

## 🛠️ Development Workflow

### Adding New Features
1. Define database model in `models.py`
2. Create Pydantic schema in `schemas.py`
3. Add API endpoints in `main.py`
4. Test using Swagger UI or demo script

### Updating Toothless AI
- Edit system prompt in `toothless_ai.py`
- Add new analysis methods as needed
- Update corresponding API endpoints

## 📚 Dependencies Breakdown

| Package | Purpose |
|---------|---------|
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| SQLAlchemy | Database ORM |
| Pydantic | Data validation |
| Anthropic | Claude API client |
| Python-Jose | JWT tokens |
| Passlib | Password hashing |

## 🎯 Project Completion Status

✅ **Core Infrastructure**
- FastAPI setup with CORS
- Database models and schemas
- User management endpoints
- Database initialization

✅ **Health Features**
- Health check-in creation and retrieval
- Mood tracking with analysis
- Medication management
- Medical information storage

✅ **AI Integration**
- Toothless AI engine
- Claude API integration
- Conversation management
- Health assessment and recommendations

✅ **Dashboard & Analytics**
- Comprehensive health dashboard
- Metrics calculation
- Trend analysis
- Alert generation

✅ **Documentation**
- README with full API documentation
- Quick start guide
- Demo script with examples
- Code comments and docstrings

## 🎓 Learning Resources

The codebase demonstrates:
- FastAPI best practices
- SQLAlchemy ORM patterns
- Pydantic validation
- Claude API integration
- REST API design
- Database modeling
- Authentication concepts

---

**Toothless Health Assistant is ready to use!** 🐉✨

Start with the QUICKSTART.md for immediate setup, or read README.md for comprehensive documentation.
