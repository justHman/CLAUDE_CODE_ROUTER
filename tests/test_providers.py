import asyncio
import base64
from core.routing import router
from transformers.models import AnthropicMessageRequest, AnthropicMessage, AnthropicMessageContent, AnthropicSource

async def test_model(model_name):
    print(f"\n--- Testing Model: {model_name} ---")
    req = AnthropicMessageRequest(
        model=model_name,
        messages=[AnthropicMessage(role="user", content="Say exactly 'TEST_OK' and nothing else.")],
        max_tokens=100
    )
    provider = router.get_provider_for_model(model_name)
    print(f"Provider resolved: {type(provider).__name__} (Target: {getattr(provider, 'model', model_name)})")
    
    try:
        resp = await provider.generate_message(req)
        try:
            text = resp['content'][0]['text']
            print(f"✅ Success! Response: {text}")
        except (KeyError, IndexError):
            print(f"⚠️ Warning: Response format issue: {resp}")
    except Exception as e:
        print(f"🔥 Exception: {e}")

async def test_gemini_vision():
    print(f"\n--- Testing Gemini Vision ---")
    # Base64 for a tiny 1x1 pixel PNG
    base64_img = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    content_blocks = [
        AnthropicMessageContent(type="text", text="What is in this image? Reply with 'IT_IS_A_PIXEL'"),
        AnthropicMessageContent(type="image", source=AnthropicSource(type="base64", media_type="image/png", data=base64_img))
    ]
    
    req = AnthropicMessageRequest(
        model="gemini-2.5-flash-image",
        messages=[AnthropicMessage(role="user", content=content_blocks)],
        max_tokens=100
    )
    
    provider = router.get_provider_for_model("gemini-2.5-flash-image")
    print(f"Provider resolved: {type(provider).__name__}")
    
    try:
        resp = await provider.generate_message(req)
        try:
            text = resp['content'][0]['text']
            print(f"✅ Vision Success! Response: {text}")
        except (KeyError, IndexError):
            print(f"⚠️ Warning: Response format issue: {resp}")
    except Exception as e:
        print(f"🔥 Exception: {e}")

async def main():
    await test_gemini_vision()
    await test_model("gemini-2.5-flash")
    await test_model("claude-3-5-sonnet-20241022")
    await test_model("claude-3-opus-20240229")

if __name__ == "__main__":
    asyncio.run(main())
