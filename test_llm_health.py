"""
LLM Health Check - Test the NVIDIA API configuration
Run this script to verify the LLM is working correctly
"""

import httpx
import asyncio
import json
from datetime import datetime

# Configuration
NVIDIA_API_KEY = "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "meta/llama-3.1-8b-instruct"

# Test message
TEST_MESSAGE = "What should I eat during pregnancy?"

async def test_llm():
    """Test NVIDIA LLM API connectivity and response"""
    
    print("=" * 70)
    print("🤖 NVIDIA LLM Health Check")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Model: {MODEL}")
    print(f"Endpoint: {NVIDIA_BASE_URL}/chat/completions")
    print(f"Test Message: {TEST_MESSAGE}")
    print("-" * 70)
    
    request_body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a warm, patient-first medical companion for pregnancy care. Answer directly and naturally."
            },
            {
                "role": "user",
                "content": TEST_MESSAGE
            }
        ],
        "temperature": 0.4,
        "max_tokens": 220,
    }
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(base_url=NVIDIA_BASE_URL, timeout=30.0) as client:
            print("\n📡 Sending request to NVIDIA API...")
            response = await client.post(
                "/chat/completions",
                headers=headers,
                json=request_body
            )
            
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCCESS! LLM is active and responding!")
                print("\n📝 Response:")
                print("-" * 70)
                
                if data.get("choices"):
                    reply = data["choices"][0].get("message", {}).get("content", "No content")
                    print(reply)
                else:
                    print("No choices in response")
                
                print("\n" + "-" * 70)
                print("📊 Response Metadata:")
                print(f"  - Model: {data.get('model')}")
                print(f"  - Usage - Input tokens: {data.get('usage', {}).get('prompt_tokens')}")
                print(f"  - Usage - Output tokens: {data.get('usage', {}).get('completion_tokens')}")
                print(f"  - Created: {data.get('created')}")
                
                print("\n✨ LLM Configuration is CORRECT and WORKING! ✨")
                return True
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except httpx.ConnectError as e:
        print(f"❌ Connection Error: {e}")
        print("   - Check internet connection")
        print("   - Verify NVIDIA API endpoint is accessible")
        return False
    except httpx.TimeoutException as e:
        print(f"⏱️  Timeout: {e}")
        print("   - API is taking too long to respond")
        print("   - Try again in a few moments")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

def main():
    print("\n🚀 Starting LLM Health Check...\n")
    
    try:
        result = asyncio.run(test_llm())
        
        print("\n" + "=" * 70)
        if result:
            print("✅ LLM is READY TO USE! Start the backend with:")
            print("   cd backend")
            print("   python -m uvicorn app.main:app --reload")
            print("=" * 70)
        else:
            print("❌ LLM Setup Failed. Check the errors above.")
            print("=" * 70)
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")

if __name__ == "__main__":
    main()
