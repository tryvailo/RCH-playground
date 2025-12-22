#!/usr/bin/env python3
"""
Test script to check if Perplexity and OpenAI API keys are working
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_api_keys():
    """Test Perplexity and OpenAI API keys"""
    print("=" * 70)
    print("🔍 API KEYS TEST - Perplexity & OpenAI")
    print("=" * 70)
    
    from config_manager import get_credentials
    from utils.auth import credentials_store
    
    creds = get_credentials()
    credentials_store['default'] = creds
    
    print("\n📋 Checking API Keys Configuration:")
    print("-" * 70)
    
    # Check Perplexity
    perplexity_key = None
    perplexity_status = "❌ Not configured"
    if creds.perplexity and creds.perplexity.api_key:
        perplexity_key = creds.perplexity.api_key
        if perplexity_key.lower() in ["your-perplexity-api-key", "your-perplexity-key", "placeholder", "example", "test"] or perplexity_key.startswith("your-"):
            perplexity_status = "❌ Placeholder value (not a real key)"
        else:
            perplexity_status = f"✅ Configured (key: {perplexity_key[:20]}...{perplexity_key[-10:] if len(perplexity_key) > 30 else ''})"
    
    print(f"Perplexity: {perplexity_status}")
    
    # Check OpenAI
    openai_key = None
    openai_status = "❌ Not configured"
    if creds.openai and creds.openai.api_key:
        openai_key = creds.openai.api_key
        if openai_key.lower() in ["your-openai-api-key", "your-openai-key", "sk-placeholder", "placeholder", "example", "test"] or openai_key.startswith("your-") or openai_key.startswith("sk-placeholder"):
            openai_status = "❌ Placeholder value (not a real key)"
        else:
            openai_status = f"✅ Configured (key: {openai_key[:20]}...{openai_key[-10:] if len(openai_key) > 30 else ''})"
    
    print(f"OpenAI: {openai_status}")
    
    print("\n🧪 Testing API Keys:")
    print("-" * 70)
    
    # Test Perplexity
    if perplexity_key and perplexity_status.startswith("✅"):
        print("\n1. Testing Perplexity API...")
        try:
            from utils.client_factory import get_perplexity_client
            client = get_perplexity_client()
            result = await client.search("What is a care home?", model="sonar-pro", max_tokens=100)
            if result.get("content"):
                print("   ✅ Perplexity API: WORKING")
                print(f"   Response length: {len(result.get('content', ''))} characters")
            else:
                print("   ⚠️  Perplexity API: Responded but no content")
        except ValueError as e:
            if "not configured" in str(e).lower() or "placeholder" in str(e).lower():
                print(f"   ❌ Perplexity API: {e}")
            else:
                print(f"   ❌ Perplexity API: Configuration error - {e}")
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"   ❌ Perplexity API: INVALID KEY - {error_msg}")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"   ⚠️  Perplexity API: Rate limit - {error_msg}")
            else:
                print(f"   ❌ Perplexity API: ERROR - {error_msg}")
    else:
        print("\n1. Perplexity API: ⏭️  Skipped (not configured or placeholder)")
    
    # Test OpenAI
    if openai_key and openai_status.startswith("✅"):
        print("\n2. Testing OpenAI API...")
        try:
            from utils.client_factory import get_openai_client
            import httpx
            
            client = get_openai_client()
            # Simple test - make a minimal API call
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say 'test' if you can read this."}
                    ],
                    "max_tokens": 10
                }
                
                response = await http_client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print("   ✅ OpenAI API: WORKING")
                    print(f"   Response: {content}")
                elif response.status_code == 401:
                    print("   ❌ OpenAI API: INVALID KEY - Authentication failed")
                elif response.status_code == 429:
                    print("   ⚠️  OpenAI API: Rate limit exceeded")
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = error_data.get("error", {}).get("message", response.text)
                    print(f"   ❌ OpenAI API: ERROR ({response.status_code}) - {error_msg}")
        except ValueError as e:
            if "not configured" in str(e).lower() or "placeholder" in str(e).lower():
                print(f"   ❌ OpenAI API: {e}")
            else:
                print(f"   ❌ OpenAI API: Configuration error - {e}")
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"   ❌ OpenAI API: INVALID KEY - {error_msg}")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"   ⚠️  OpenAI API: Rate limit - {error_msg}")
            elif "insufficient_quota" in error_msg.lower() or "quota" in error_msg.lower():
                print(f"   ❌ OpenAI API: QUOTA EXCEEDED - {error_msg}")
            else:
                print(f"   ❌ OpenAI API: ERROR - {error_msg}")
    else:
        print("\n2. OpenAI API: ⏭️  Skipped (not configured or placeholder)")
    
    print("\n" + "=" * 70)
    print("✅ Test complete")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_api_keys())

