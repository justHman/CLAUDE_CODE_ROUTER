import json
import httpx
from typing import AsyncGenerator, Dict, Any
from providers.base import BaseProvider
from transformers.models import AnthropicMessageRequest
from transformers.request import convert_request
from transformers.response import convert_openai_stream_to_anthropic
from core.logger import logger

class OpenAICompatibleProvider(BaseProvider):
    async def _post_request(self, payload: dict, stream: bool = False) -> httpx.Response:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8082",
            "X-Title": "Claude Code Router"
        }
        
        url = self.base_url.rstrip("/") + "/chat/completions"
        logger.debug(f"Sending request to {url} format: {self.base_url}")
        
        client = httpx.AsyncClient(timeout=180.0)
        
        if stream:
            request = client.build_request("POST", url, headers=headers, json=payload)
            # Yielding the stream response object requires careful caller handling
            return await client.send(request, stream=True)
        else:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            await client.aclose()
            return response

    async def generate_message(self, request: AnthropicMessageRequest) -> Dict[str, Any]:
        """Not often used by Claude CLI, heavily reliant on stream."""
        openai_req = convert_request(request)
        if self.model:
            openai_req["model"] = self.model
            
        response = await self._post_request(openai_req, stream=False)
        data = response.json()
        
        # Super simple conversion - we really only care about streams for Claude Code
        # But let's build a stub
        content_blocks = []
        if "choices" in data and data["choices"]:
            msg = data["choices"][0]["message"]
            if msg.get("content") is not None:
                content_blocks.append({"type": "text", "text": msg["content"]})
            if msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "input": json.loads(tc["function"]["arguments"])
                    })
                    
        return {
            "id": data.get("id", "msg_1"),
            "type": "message",
            "role": "assistant",
            "model": self.model,
            "content": content_blocks,
            "stop_reason": data["choices"][0].get("finish_reason") if data.get("choices") else "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": data.get("usage", {}).get("completion_tokens", 0)
            }
        }

    async def generate_stream(self, request: AnthropicMessageRequest) -> AsyncGenerator[str, None]:
        openai_req = convert_request(request)
        if self.model:
            openai_req["model"] = self.model
            
        openai_req["stream"] = True
        
        response = await self._post_request(openai_req, stream=True)
        
        async def raw_sse_stream():
            async for line in response.aiter_lines():
                yield line
                
        # Pipe it through the transformer
        try:
            async for anthropic_line in convert_openai_stream_to_anthropic(raw_sse_stream()):
                yield anthropic_line
        finally:
            await response.aclose()
