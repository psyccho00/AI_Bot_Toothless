# 🐉 Toothless – AI Health Assistant (Chat-Based)

A modern **chat-based AI health assistant** built using **FastAPI + JavaScript**, designed to simulate real-world conversational healthcare support.

Toothless provides intelligent health guidance through a **ChatGPT-style interface**, with both:
- 🤖 AI-powered responses (when API is available)
- 🧠 Smart rule-based fallback (when API is unavailable)

---

## 🚀 Features

### 💬 Chat-Based Interface
- Real-time chat UI (ChatGPT-style)
- User messages → right side  
- AI responses → left side  
- Smooth scrolling chat experience  
- “Analyzing...” loading indicator  

---

### 🧠 Smart Demo Mode (No API Required)
- Detects multiple symptoms  
- Supports combinations (e.g., fever + cough)  
- Provides structured health advice  
- Handles unknown inputs safely  

---

### 🩺 Supported Symptoms

**General:** headache, dizziness, fatigue, weakness, body pain  
**Fever:** fever, chills, sweating  
**Respiratory:** cough, cold, sore throat, runny nose, congestion  
**Digestive:** vomiting, nausea, stomach pain, diarrhea, acidity  
**Mental:** stress, anxiety, insomnia  
**Serious:** chest pain, shortness of breath  

---

### 🤖 AI Mode (Optional)
- Uses Anthropic Claude API
- Automatically falls back to demo mode if API fails

---

## 🛠️ Tech Stack

- Backend: FastAPI (Python)
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (SQLAlchemy)
- AI Integration: Anthropic Claude API

---

## 📂 Project Structure

├── main.py  
├── toothless_ai.py  
├── models.py  
├── schemas.py  
├── database.py  
├── config.py  
├── frontend/  
│   ├── index.html  
│   ├── style.css  
│   └── app.js  
├── .env  

---

## ⚙️ Setup Instructions

### 1. Create Virtual Environment
python -m venv .venv

Activate:
.venv\Scripts\activate

---

### 2. Install Dependencies
pip install -r requirements.txt

---

### 3. Configure Environment Variables

Create `.env` file:

ANTHROPIC_API_KEY=your_api_key_here  
DATABASE_URL=sqlite:///./toothless.db  

---

## ▶️ Run the App

.venv\Scripts\python.exe -m uvicorn main:app --reload

---

## 🌐 Open in Browser

http://localhost:8000/app

API Docs:
http://localhost:8000/docs

---

## 💬 Example

Input:
I have fever and vomiting

Output:
[Demo mode response, not medical advice]

Detected: fever, vomiting  
Advice:
- Stay hydrated  
- Eat light food  
- Monitor symptoms  

---

## 🧠 Key Highlights

- Chat-based UI from scratch  
- Frontend ↔ backend API integration  
- AI + fallback system  
- Multi-symptom detection  
- Graceful degradation  

---