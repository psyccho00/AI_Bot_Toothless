import sys
import os
import logging

# Ensure logging is visible
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from config import settings
from providers import ai_router

def test_single_provider(provider_name: str):
    print(f"\n==========================================")
    print(f"Testing forced provider: {provider_name}")
    print(f"==========================================")
    
    # Temporarily override settings
    original_provider = settings.AI_PROVIDER
    settings.AI_PROVIDER = provider_name
    
    system_prompt = "You are a helpful test assistant. Keep your response extremely brief, under 5 words."
    messages = [{"role": "user", "content": "Hello, who are you?"}]
    
    try:
        response, provider = ai_router.generate_chat_response(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=20
        )
        print(f"SUCCESS: Response from {provider_name}: '{response.strip()}' (Resolved Provider: {provider})")
    except Exception as e:
        print(f"FAILURE: Failed to query {provider_name}: {e}")
    finally:
        # Restore settings
        settings.AI_PROVIDER = original_provider

def test_auto_fallback():
    print(f"\n==========================================")
    print(f"Testing automatic fallback sequence (auto)")
    print(f"==========================================")
    
    original_provider = settings.AI_PROVIDER
    settings.AI_PROVIDER = "auto"
    
    system_prompt = "You are a helpful test assistant. Keep your response extremely brief, under 5 words."
    messages = [{"role": "user", "content": "Reply with 'Fallback test successful'."}]
    
    try:
        response, provider = ai_router.generate_chat_response(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=20
        )
        print(f"SUCCESS: Response in 'auto' mode: '{response.strip()}' (Resolved Provider: {provider})")
    except Exception as e:
        print(f"FAILURE: Failed in 'auto' mode: {e}")
    finally:
        settings.AI_PROVIDER = original_provider

def test_timeout_and_fallback():
    print(f"\n==========================================")
    print(f"Testing fallback on invalid keys / simulated failure")
    print(f"==========================================")
    
    original_provider = settings.AI_PROVIDER
    original_anthropic_key = settings.ANTHROPIC_API_KEY
    
    # Set AI provider to auto
    settings.AI_PROVIDER = "auto"
    # Break Anthropic key to force fallback to next provider (Gemini or Groq)
    settings.ANTHROPIC_API_KEY = "sk-ant-invalidkey-123456789"
    
    # Re-initialize the clients with these new overridden keys
    from providers import MultiProviderClient
    temp_router = MultiProviderClient()
    
    system_prompt = "You are a helpful test assistant. Keep your response extremely brief, under 5 words."
    messages = [{"role": "user", "content": "Reply with 'Fallback simulated'."}]
    
    try:
        response, provider = temp_router.generate_chat_response(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=20
        )
        print(f"SUCCESS: Fallback successfully bypassed Anthropic and used: '{response.strip()}' (Resolved Provider: {provider})")
    except Exception as e:
        print(f"FAILURE: Failed during fallback test: {e}")
    finally:
        settings.AI_PROVIDER = original_provider
        settings.ANTHROPIC_API_KEY = original_anthropic_key

def test_forced_demo_mode():
    print(f"\n==========================================")
    print(f"Testing forced demo provider setting (demo)")
    print(f"==========================================")
    
    original_provider = settings.AI_PROVIDER
    settings.AI_PROVIDER = "demo"
    
    system_prompt = "You are a helpful test assistant."
    messages = [{"role": "user", "content": "Hello."}]
    
    try:
        ai_router.generate_chat_response(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=20
        )
        print("FAILURE: generate_chat_response succeeded in forced demo mode (should have raised exception to trigger fallback)")
    except Exception as e:
        print(f"SUCCESS: generate_chat_response raised exception as expected: {e}")
    finally:
        settings.AI_PROVIDER = original_provider

if __name__ == "__main__":
    print("Starting Multi-Provider AI verification tests...")
    print(f"Configured Keys Status:")
    print(f"- ANTHROPIC_API_KEY: {'Configured' if settings.ANTHROPIC_API_KEY else 'Missing'}")
    print(f"- GEMINI_API_KEY: {'Configured' if settings.GEMINI_API_KEY else 'Missing'}")
    print(f"- GROQ_API_KEY: {'Configured' if settings.GROQ_API_KEY else 'Missing'}")
    print(f"- Current AI_PROVIDER: {settings.AI_PROVIDER}")
    
    # Test each forced mode
    if settings.ANTHROPIC_API_KEY:
        test_single_provider("anthropic")
    if settings.GEMINI_API_KEY:
        test_single_provider("gemini")
    if settings.GROQ_API_KEY:
        test_single_provider("groq")
        
    # Test auto fallback sequence
    test_auto_fallback()
    
    # Test invalid keys fallback simulation
    test_timeout_and_fallback()
    
    # Test forced demo mode
    test_forced_demo_mode()
