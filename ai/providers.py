import logging
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from groq import Groq
import google.generativeai as genai
from config import settings

logger = logging.getLogger("toothless_ai_providers")

class MultiProviderClient:
    """
    Client router that coordinates requests to Anthropic Claude, Google Gemini,
    and Groq (Llama), with automatic fallback and 10-second timeouts.
    """
    def __init__(self):
        self.anthropic_client = None
        self.groq_client = None
        self.gemini_configured = False
        
        # Initialize Anthropic if key is set
        if settings.ANTHROPIC_API_KEY:
            try:
                # Set default timeout to 10.0 seconds
                self.anthropic_client = Anthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    timeout=10.0
                )
                logger.info("Anthropic client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

        # Initialize Groq if key is set
        if settings.GROQ_API_KEY:
            try:
                # Set default timeout to 10.0 seconds
                self.groq_client = Groq(
                    api_key=settings.GROQ_API_KEY,
                    timeout=10.0
                )
                logger.info("Groq client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")

        # Configure Google Gemini if key is set
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_configured = True
                logger.info("Gemini SDK configured.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini SDK: {e}")

    def generate_chat_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024
    ) -> tuple[str, str]:
        """
        Send chat prompt to the primary provider and fall back to the next one
        if the call fails or exceeds 10 seconds. Returns a tuple of (response_text, provider_name).
        """
        # Determine fallback order
        provider_mode = settings.AI_PROVIDER.lower()
        if provider_mode == "auto":
            queue = ["anthropic", "gemini", "groq"]
        elif provider_mode in ["anthropic", "claude"]:
            queue = ["anthropic"]
        elif provider_mode == "gemini":
            queue = ["gemini"]
        elif provider_mode == "groq":
            queue = ["groq"]
        elif provider_mode == "demo":
            queue = []
        else:
            logger.warning(f"Unknown AI_PROVIDER value '{provider_mode}'. Falling back to 'auto'.")
            queue = ["anthropic", "gemini", "groq"]

        last_error = None

        for provider in queue:
            try:
                if provider == "anthropic":
                    if not self.anthropic_client:
                        raise ValueError("Anthropic API key is not configured or client failed to initialize.")
                    
                    logger.info(f"Attempting response generation using Anthropic ({settings.CLAUDE_MODEL})...")
                    # We also explicitly specify timeout on the request to ensure 10s enforcement
                    response = self.anthropic_client.messages.create(
                        model=settings.CLAUDE_MODEL,
                        max_tokens=max_tokens,
                        system=system_prompt,
                        messages=messages,
                        timeout=10.0
                    )
                    logger.info("Successfully received response from Anthropic.")
                    return response.content[0].text, "Claude"

                elif provider == "gemini":
                    if not self.gemini_configured:
                        raise ValueError("Gemini API key is not configured or client failed to initialize.")
                    
                    logger.info(f"Attempting response generation using Gemini ({settings.GEMINI_MODEL})...")
                    
                    # Convert conversation history to Gemini format
                    # Roles must be "user" or "model" (corresponds to "assistant")
                    gemini_messages = []
                    for msg in messages:
                        role = "user" if msg["role"] == "user" else "model"
                        gemini_messages.append({
                            "role": role,
                            "parts": [msg["content"]]
                        })
                    
                    # Create the model instance with system prompt instruction
                    model = genai.GenerativeModel(
                        model_name=settings.GEMINI_MODEL,
                        system_instruction=system_prompt
                    )
                    
                    # Call Gemini API with 10-second timeout configuration
                    response = model.generate_content(
                        contents=gemini_messages,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=max_tokens
                        ),
                        request_options={"timeout": 10.0}
                    )
                    logger.info("Successfully received response from Gemini.")
                    
                    try:
                        return response.text, "Gemini"
                    except Exception as exc:
                        try:
                            # Safely extract text even if finish_reason indicates token limit or other non-severe exit
                            if response.candidates and response.candidates[0].content.parts:
                                text = response.candidates[0].content.parts[0].text
                                if text:
                                    return text, "Gemini"
                        except Exception:
                            pass
                        raise exc

                elif provider == "groq":
                    if not self.groq_client:
                        raise ValueError("Groq API key is not configured or client failed to initialize.")
                    
                    logger.info(f"Attempting response generation using Groq ({settings.GROQ_MODEL})...")
                    
                    # Prepare messages including system prompt as first message
                    groq_messages = [{"role": "system", "content": system_prompt}] + messages
                    
                    # Call Groq API with 10-second timeout configuration
                    response = self.groq_client.chat.completions.create(
                        model=settings.GROQ_MODEL,
                        messages=groq_messages,
                        max_tokens=max_tokens,
                        timeout=10.0
                    )
                    logger.info("Successfully received response from Groq.")
                    return response.choices[0].message.content, "Groq"

            except Exception as e:
                logger.warning(f"Provider '{provider}' failed or timed out: {e}. Trying next available provider...")
                last_error = e

        # If all configured/available options failed
        raise RuntimeError(f"All attempted AI providers failed or timed out. Last error: {last_error}")

# Global instance of multi-provider client
ai_router = MultiProviderClient()
