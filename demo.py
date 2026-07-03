#!/usr/bin/env python3
"""
Toothless Health Assistant - Demo Script

This script demonstrates how to use the Toothless API programmatically.
Run the FastAPI server first: python main.py
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def register_user():
    """Register a new user"""
    print_header("🐉 Registering New User")
    
    user_data = {
        "email": "aeede.johnson@example.com",
        "username": "aceede_johnson",
        "password": "123567",
        "full_name": "Alic Johnson",
        "age": 32,
        "gender": "Female",
        "medical_history": "Type 2 Diabetes, Mild Hypertension",
        "allergies": "Shellfish, Penicillin",
        "current_medications": "Metformin 500mg twice daily, Lisinopril 10mg daily"
    }
    
    response = requests.post(f"{BASE_URL}/users/register", json=user_data)
    
    if response.status_code == 200:
        user = response.json()
        print_success(f"User registered: {user['full_name']} (ID: {user['id']})")
        print(f"  Email: {user['email']}")
        print(f"  Username: {user['username']}")
        return user['id']
    else:
        print_warning(f"Registration failed: {response.text}")
        return None


def chat_with_toothless(user_id):
    """Have a conversation with Toothless AI"""
    print_header("💬 Chat with Toothless AI")
    
    messages = [
        "Hello, I've been feeling very tired lately and my energy levels are quite low.",
        "I think it might be related to my diabetes - my blood sugar has been inconsistent.",
        "I'm also struggling with stress at work, which is affecting my sleep."
    ]
    
    for message in messages:
        print(f"{Colors.OKBLUE}You: {message}{Colors.ENDC}")
        
        request_data = {
            "user_id": user_id,
            "message": message,
            "include_recommendations": True
        }
        
        response = requests.post(f"{BASE_URL}/toothless/chat", json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"{Colors.OKGREEN}Toothless: {result['response']}{Colors.ENDC}")
            
            if result.get('health_alerts'):
                print(f"{Colors.WARNING}Health Alerts:{Colors.ENDC}")
                for alert in result['health_alerts']:
                    print(f"  - {alert}")
            
            if result.get('requires_professional_help'):
                print_warning("Toothless recommends consulting a healthcare professional.")
            
            print()


def create_health_checkin(user_id):
    """Create a health check-in"""
    print_header("📋 Health Check-In")
    
    checkin_data = {
        "symptoms": "Fatigue, increased thirst, occasional headaches",
        "pain_level": 2,
        "energy_level": 3,
        "sleep_quality": 5,
        "sleep_hours": 6.0,
        "appetite": "normal",
        "hydration_status": "low",
        "medication_compliance": True,
        "notes": "Blood sugar readings slightly elevated. Stress from work affecting sleep."
    }
    
    response = requests.post(
        f"{BASE_URL}/health-checkins?user_id={user_id}",
        json=checkin_data
    )
    
    if response.status_code == 200:
        checkin = response.json()
        print_success("Health check-in recorded")
        print(f"  ID: {checkin['id']}")
        print(f"  Symptoms: {checkin['symptoms']}")
        print(f"  Energy Level: {checkin['energy_level']}/10")
        print(f"  Sleep Quality: {checkin['sleep_quality']}/10")
        print(f"  Sleep Hours: {checkin['sleep_hours']}h")
        print()
        print(f"{Colors.BOLD}Toothless Assessment:{Colors.ENDC}")
        print(f"{checkin['ai_assessment']}")
    else:
        print_warning(f"Check-in failed: {response.text}")


def create_mood_entry(user_id):
    """Create a mood entry"""
    print_header("😊 Mood Tracking")
    
    mood_data = {
        "mood_rating": 5,
        "mood_type": "anxious",
        "stress_level": 7,
        "anxiety_level": 6,
        "depression_signs": 3,
        "triggers": "Work deadlines, health concerns, sleep issues",
        "coping_strategies": "Exercise, meditation, talking to friends",
        "notes": "Feeling overwhelmed by multiple stressors"
    }
    
    response = requests.post(
        f"{BASE_URL}/mood-entries?user_id={user_id}",
        json=mood_data
    )
    
    if response.status_code == 200:
        mood = response.json()
        print_success("Mood entry recorded")
        print(f"  Mood Rating: {mood['mood_rating']}/10 ({mood['mood_type']})")
        print(f"  Stress Level: {mood['stress_level']}/10")
        print(f"  Anxiety Level: {mood['anxiety_level']}/10")
        print(f"  Depression Signs: {mood['depression_signs']}/10")
        print()
        print(f"{Colors.BOLD}Toothless Recommendation:{Colors.ENDC}")
        print(f"{mood['ai_recommendation']}")
    else:
        print_warning(f"Mood entry failed: {response.text}")


def add_medication(user_id):
    """Add a medication to the user's list"""
    print_header("💊 Add Medication")
    
    med_data = {
        "name": "Metformin",
        "dosage": "500mg",
        "frequency": "twice daily",
        "start_date": (datetime.utcnow() - timedelta(days=365)).isoformat(),
        "reason": "Type 2 Diabetes management",
        "known_side_effects": "Mild GI upset, metallic taste",
        "interactions": "Contrast dye, some antibiotics"
    }
    
    response = requests.post(
        f"{BASE_URL}/medications?user_id={user_id}",
        json=med_data
    )
    
    if response.status_code == 200:
        med = response.json()
        print_success("Medication added")
        print(f"  Name: {med['name']}")
        print(f"  Dosage: {med['dosage']}")
        print(f"  Frequency: {med['frequency']}")
        print(f"  Reason: {med['reason']}")
    else:
        print_warning(f"Failed to add medication: {response.text}")


def get_health_dashboard(user_id):
    """Get the comprehensive health dashboard"""
    print_header("📊 Health Dashboard")
    
    response = requests.get(f"{BASE_URL}/dashboard/{user_id}?days=7")
    
    if response.status_code == 200:
        dashboard = response.json()
        
        print(f"{Colors.BOLD}User Profile:{Colors.ENDC}")
        print(f"  Name: {dashboard['user']['full_name']}")
        print(f"  Age: {dashboard['user']['age']}")
        print(f"  Email: {dashboard['user']['email']}")
        
        print(f"\n{Colors.BOLD}Health Metrics (Last 7 Days):{Colors.ENDC}")
        metrics = dashboard['metrics']
        print(f"  Average Mood: {metrics['average_mood']}/10")
        print(f"  Average Energy: {metrics['average_energy']}/10")
        print(f"  Average Sleep: {metrics['average_sleep']}h")
        print(f"  Medication Compliance: {metrics['medication_compliance_rate']}%")
        print(f"  Check-ins This Week: {metrics['entries_this_week']}")
        
        if dashboard['recent_checkings']:
            print(f"\n{Colors.BOLD}Recent Check-Ins:{Colors.ENDC}")
            for checkin in dashboard['recent_checkings'][:3]:
                print(f"  • {checkin['check_in_date'][:10]} - Energy: {checkin['energy_level']}/10, Sleep: {checkin['sleep_hours']}h")
        
        if dashboard['recent_mood_entries']:
            print(f"\n{Colors.BOLD}Recent Mood Entries:{Colors.ENDC}")
            for mood in dashboard['recent_mood_entries'][:3]:
                print(f"  • {mood['entry_date'][:10]} - Mood: {mood['mood_rating']}/10 ({mood['mood_type']}), Stress: {mood['stress_level']}/10")
        
        if dashboard['active_medications']:
            print(f"\n{Colors.BOLD}Active Medications:{Colors.ENDC}")
            for med in dashboard['active_medications']:
                print(f"  • {med['name']} {med['dosage']} - {med['frequency']}")
        
        if dashboard['health_alerts']:
            print(f"\n{Colors.WARNING}{Colors.BOLD}Health Alerts:{Colors.ENDC}")
            for alert in dashboard['health_alerts']:
                print(f"  {alert}")
    else:
        print_warning(f"Failed to get dashboard: {response.text}")


def daily_checkin(user_id):
    """Start a daily check-in"""
    print_header("🌅 Daily Check-In with Toothless")
    
    # response = requests.post(f"{BASE_URL}/toothless/daily-checkin", json={"user_id": user_id})
    response = requests.post(f"{BASE_URL}/toothless/daily-checkin?user_id={user_id}")

    if response.status_code == 200:
        checkin = response.json()
        print(f"{Colors.OKGREEN}Toothless: {checkin['greeting']}{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Expected Questions:{Colors.ENDC}")
        for q in checkin['expected_questions']:
            print(f"  • {q}")
    else:
        print_warning(f"Failed to start check-in: {response.text}")


def main():
    """Run the complete demo"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "🐉 TOOTHLESS HEALTH ASSISTANT DEMO 🐉" + " "*10 + "║")
    print("║" + " "*15 + "Your AI Health Companion" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.ENDC}")
    
    print_info("Make sure the Toothless server is running: python main.py")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print_warning("Server is not responding correctly")
            return
        
        print_success("Connected to Toothless server")
        
        # Run the demo
        user_id = register_user()
        
        if user_id:
            daily_checkin(user_id)
            chat_with_toothless(user_id)
            create_health_checkin(user_id)
            create_mood_entry(user_id)
            add_medication(user_id)
            get_health_dashboard(user_id)
            
            print_header("✨ Demo Complete!")
            print_success("You can now access your data through the API")
            print_info(f"Dashboard: GET /dashboard/{user_id}")
            print_info(f"Chat: POST /toothless/chat")
            print_info(f"API Docs: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print_warning(f"Cannot connect to server at {BASE_URL}")
        print_info("Make sure to run: python main.py")
    except Exception as e:
        print_warning(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
