from anthropic import Anthropic
from config import settings
import json
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

class ToothlessAI:
    """
    Toothless AI Health Assistant
    
    Named after the friendly dragon from How to Train Your Dragon,
    Toothless is an intelligent, responsive, and caring AI health companion.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.model = settings.CLAUDE_MODEL
        self.system_prompt = self._get_system_prompt()
        self.conversation_history = {}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Toothless AI"""
        return """You are Toothless, an AI Health Assistant - a caring, intelligent, and empathetic digital health companion.

Your personality:
- You are warm, friendly, and non-judgmental like the dragon Toothless from How to Train Your Dragon
- You listen carefully and show genuine concern for the user's wellbeing
- You are intelligent and knowledgeable about health topics
- You balance being helpful with professional responsibility

Your responsibilities:
1. Conduct daily health check-ins about physical symptoms, energy, sleep, and mood
2. Track mood and emotional wellbeing with psychological insights
3. Provide evidence-based medical information and guidance
4. Help users track medications and health goals
5. Identify potential health risks and recommend professional care when needed

Important guidelines:
- ALWAYS remind users that you are not a replacement for professional medical advice
- When symptoms seem serious or emergency-related, IMMEDIATELY recommend seeking professional help
- Base medical advice on established, reliable sources
- Ask clarifying questions to better understand the user's situation
- Be empathetic and supportive, especially when discussing mental health or serious conditions
- Never diagnose - suggest possible conditions and recommend professional evaluation
- Maintain patient confidentiality and privacy

When conducting a health check-in, ask about:
- Current symptoms or pain
- Sleep quality and hours
- Energy levels and mood
- Appetite and hydration
- Medication compliance
- Any concerning changes in health

Format your responses to be clear, compassionate, and actionable.

CRITICAL: Always include a disclaimer that users should consult licensed healthcare professionals for diagnosis and treatment."""

    def start_conversation(self, user_id: int, topic: str = "general") -> Dict[str, Any]:
        """Start a new conversation with a greeting"""
        greeting = self._get_greeting_by_topic(topic)
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        return {
            "greeting": greeting,
            "topic": topic,
            "conversation_id": user_id
        }
    
    def _get_greeting_by_topic(self, topic: str) -> str:
        """Get an appropriate greeting based on the topic"""
        greetings = {
            "health_checkin": "Hello! I'm Toothless, your AI health companion. Let's do a quick health check-in. How are you feeling today? Any symptoms, aches, or concerns I should know about?",
            "mood_tracking": "Hi there! I'm here to help you understand your emotional wellbeing. How are you feeling emotionally right now? I'd love to hear about your mood and what's on your mind.",
            "medical_info": "Welcome! I'm Toothless. I'm here to help you understand health conditions and medical information. What would you like to know about?",
            "medication": "Hello! Let's talk about your medications. Are you taking all your medications as prescribed? Any side effects or concerns?",
            "general": "Hi! I'm Toothless, your AI health assistant. I'm here to help with any health-related questions or concerns. What can I help you with today?"
        }
        return greetings.get(topic, greetings["general"])

    def chat(self, user_id: int, user_message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user message and generate AI response
        
        Args:
            user_id: User ID for conversation tracking
            user_message: The user's message
            context: Additional context (user profile info, previous conditions, etc.)
        
        Returns:
            Dictionary with AI response and extracted health data
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Build the full system prompt with user context if provided
        system = self.system_prompt
        if context:
            system += f"\n\nUser Context:\n{context}"
        
        # Add user message to history
        self.conversation_history[user_id].append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=self.conversation_history[user_id]
            )
            
            assistant_message = response.content[0].text
            
            # Add assistant response to history
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Extract health insights and recommendations
            health_alerts = self._extract_health_alerts(assistant_message, user_message)
            follow_ups = self._extract_follow_up_questions(assistant_message)
        except Exception as e:
            import logging
            logging.error(f"Anthropic API Error during chat: {e}. Falling back to demo mode.")
            assistant_message = self._get_fallback_response(user_message)
            health_alerts = []
            follow_ups = []
        
        return {
            "response": assistant_message,
            "health_alerts": health_alerts,
            "follow_up_questions": follow_ups,
            "requires_professional_help": "emergency" in assistant_message.lower() or "seek professional" in assistant_message.lower()
        }

    def daily_health_checkin(self, user_id: int, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct a structured daily health check-in
        
        Args:
            user_id: User ID
            user_profile: User profile data (name, age, conditions, medications, etc.)
        
        Returns:
            Health check-in data and assessment
        """
        context = self._build_user_context(user_profile)
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # First message: start the check-in
        greeting = f"Hi {user_profile.get('full_name', 'there')}! Let's do your daily health check-in. How are you feeling today?"
        
        return {
            "greeting": greeting,
            "expected_questions": [
                "How are your current symptoms or pain levels?",
                "How was your sleep last night?",
                "What's your energy level like today?",
                "How's your mood?",
                "Have you taken your medications?"
            ]
        }

    def analyze_mood(self, user_id: int, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze mood data and provide psychological insights
        
        Args:
            user_id: User ID
            mood_data: Mood metrics and entries
        
        Returns:
            Analysis and recommendations
        """
        mood_context = f"""
        Recent mood data:
        - Current mood rating: {mood_data.get('mood_rating', 'N/A')}/10
        - Mood type: {mood_data.get('mood_type', 'Not specified')}
        - Stress level: {mood_data.get('stress_level', 'N/A')}/10
        - Anxiety level: {mood_data.get('anxiety_level', 'N/A')}/10
        - Depression indicators: {mood_data.get('depression_signs', 'N/A')}/10
        - Triggers: {mood_data.get('triggers', 'Not specified')}
        """
        
        analysis_prompt = f"""Based on this mood data, provide:
        1. An assessment of the user's emotional state
        2. Identified mood patterns or concerns
        3. Coping strategies and resources
        4. Recommendations for mental health support if needed
        5. When they should seek professional help
        
        {mood_context}"""
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": "user",
            "content": analysis_prompt
        })
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.conversation_history[user_id]
            )
            
            analysis = response.content[0].text
            
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": analysis
            })
            
            return {
                "mood_analysis": analysis,
                "requires_professional_help": "professional help" in analysis.lower() or "mental health" in analysis.lower()
            }
        except Exception as e:
            import logging
            logging.error(f"Anthropic API Error during mood analysis: {e}. Falling back to demo mode.")
            return {
                "mood_analysis": "[Demo mode response, not medical advice]\n\nYour mood data has been saved. Please consult a mental health professional if you need support.",
                "requires_professional_help": False
            }

    def check_medication_interactions(self, medications: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Check for potential drug interactions
        
        Args:
            medications: List of medications with name and dosage
        
        Returns:
            Interaction analysis and warnings
        """
        med_list = "\n".join([f"- {med['name']} ({med['dosage']})" for med in medications])
        
        query = f"""Please analyze these medications for potential interactions:
        {med_list}
        
        For each medication:
        1. List known side effects
        2. Identify any dangerous interactions with other medications in the list
        3. Note important precautions
        4. Recommend when to contact a pharmacist
        
        Remember: This is informational only. Users should always consult with their pharmacist."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[{"role": "user", "content": query}]
            )
            
            return {
                "interaction_analysis": response.content[0].text,
                "medications_reviewed": len(medications)
            }
        except Exception as e:
            import logging
            logging.error(f"Anthropic API Error during medication check: {e}")
            return {
                "interaction_analysis": "[Demo mode response, not medical advice]\n\nUnable to check interactions at this time. Always consult your pharmacist or doctor before taking new medications.",
                "medications_reviewed": len(medications)
            }

    def generate_health_summary(self, user_id: int, health_data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive health summary
        
        Args:
            user_id: User ID
            health_data: Dictionary with recent health metrics
        
        Returns:
            Health summary string
        """
        summary_prompt = f"""Generate a brief, compassionate health summary for a user based on this data:

        Health Metrics:
        {json.dumps(health_data, indent=2)}
        
        Provide:
        1. Overall health assessment
        2. Key observations
        3. Trends (improving/declining/stable)
        4. Recommendations for next steps
        5. When professional care is needed
        
        Keep it concise and supportive."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                system=self.system_prompt,
                messages=[{"role": "user", "content": summary_prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            import logging
            logging.error(f"Anthropic API Error during health summary: {e}")
            return "[Demo mode response, not medical advice]\n\nHealth summary unavailable in demo mode. Please keep monitoring your health."

    def _extract_health_alerts(self, ai_response: str, user_message: str) -> List[str]:
        """Extract health alerts from the conversation"""
        alerts = []
        
        alert_keywords = [
            "severe", "emergency", "hospitalize", "call 911", "poison control",
            "chest pain", "difficulty breathing", "loss of consciousness",
            "bleeding", "severe", "immediate care", "urgent"
        ]
        
        combined_text = (ai_response + " " + user_message).lower()
        
        for keyword in alert_keywords:
            if keyword in combined_text:
                alerts.append(f"⚠️ Potential {keyword} detected - seek professional help immediately")
                break
        
        return alerts

    def _extract_follow_up_questions(self, ai_response: str) -> List[str]:
        """Extract follow-up questions from AI response"""
        questions = []
        
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.endswith('?') and len(line) > 10:
                questions.append(line)
        
        return questions[:3]  # Return top 3 questions

    def _build_user_context(self, user_profile: Dict[str, Any]) -> str:
        """Build user context string for the AI"""
        context = f"""
        User Profile:
        - Name: {user_profile.get('full_name', 'User')}
        - Age: {user_profile.get('age', 'N/A')}
        - Gender: {user_profile.get('gender', 'N/A')}
        
        Medical History:
        {user_profile.get('medical_history', 'None reported')}
        
        Allergies:
        {user_profile.get('allergies', 'None reported')}
        
        Current Medications:
        {user_profile.get('current_medications', 'None reported')}
        """
        
        return context

    def reset_conversation(self, user_id: int):
        """Reset conversation history for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

    def _get_fallback_response(self, message: str) -> str:
        """Provide a safe rule-based response when API is unavailable"""
        msg = message.lower()
        
        # Define symptom groups with keywords and general advice
        symptom_groups = [
            {
                "category": "General Symptoms",
                "keywords": ["headache", "dizziness", "dizzy", "fatigue", "weakness", "body pain", "body ache"],
                "advice": "Rest in a quiet room, stay hydrated, and ensure you're getting enough sleep."
            },
            {
                "category": "Fever Symptoms",
                "keywords": ["fever", "chills", "sweating"],
                "advice": "Monitor your temperature, drink plenty of fluids, and get plenty of rest."
            },
            {
                "category": "Respiratory Symptoms",
                "keywords": ["cold", "cough", "sore throat", "runny nose", "blocked nose", "sneezing"],
                "advice": "Drink warm fluids, rest your voice, and consider using a humidifier."
            },
            {
                "category": "Digestive Issues",
                "keywords": ["vomiting", "nausea", "vomit", "stomach pain", "stomach ache", "diarrhea", "constipation", "bloating", "acidity"],
                "advice": "Eat bland, easily digestible foods and stay hydrated with clear liquids."
            },
            {
                "category": "Mental & Sleep",
                "keywords": ["anxiety", "stress", "insomnia", "anxious", "stressed"],
                "advice": "Try deep breathing exercises, mindfulness, and limit caffeine/screen time."
            },
            {
                "category": "Other Concerns",
                "keywords": ["back pain", "joint pain", "rash", "itching", "swelling", "dehydration"],
                "advice": "Rest affected areas, drink more water, and avoid irritating any skin issues."
            }
        ]
        
        serious_keywords = ["chest pain", "shortness of breath", "breathing difficulty", "palpitations"]
        
        detected_categories = []
        is_serious = False
        
        # 1. Check for serious symptoms
        for word in serious_keywords:
            if word in msg:
                is_serious = True
                break
                
        # 2. Check regular symptom groups
        for group in symptom_groups:
            # Check if any keyword from this group is in the message
            if any(keyword in msg for keyword in group["keywords"]):
                detected_categories.append(group)
                
        # 3. Format the response
        response = "[Demo mode response, not medical advice]\n\n"
        
        if is_serious:
            response += "🚨 **WARNING: You have mentioned potentially serious symptoms.**\n"
            response += "Please seek immediate medical attention or call emergency services.\n\n"
            
        if detected_categories:
            response += "Based on your message, I've noted the following concerns:\n\n"
            for group in detected_categories:
                response += f"- **{group['category']}**: {group['advice']}\n"
            
            response += "\n*If your symptoms persist, worsen, or cause you severe discomfort, please consult a healthcare professional.*"
        else:
            if not is_serious:
                response += "I'm currently operating in demo mode and my full AI capabilities are offline. "
                response += "I've noted your check-in. Please take care of yourself, and consult a doctor if you feel unwell."
                
        return response


# Global instance of Toothless
toothless = ToothlessAI()
