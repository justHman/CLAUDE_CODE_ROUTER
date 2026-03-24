from typing import AsyncGenerator, Dict, Any
from providers.base import BaseProvider
from transformers.models import AnthropicMessageRequest
from transformers.gemini import convert_request_to_gemini
from google import genai
from google.genai import types
import json
import uuid

class GeminiProvider(BaseProvider):
    def __init__(self, base_url: str, api_key: str | None = None, model: str | None = None, model_config: Any = None):
        super().__init__(base_url=base_url, api_key=api_key, model=model, model_config=model_config)
        # GenAI client
        self.client = genai.Client(api_key=self.api_key)

    async def generate_message(self, request: AnthropicMessageRequest) -> Dict[str, Any]:
        contents, system_instruction, tools = convert_request_to_gemini(request)
        
        # Merge system prompt injection
        if self.model_config:
            prefix = self.model_config.system_prompt_prefix or ""
            suffix = self.model_config.system_prompt_suffix or ""
            if prefix or suffix:
                system_instruction = f"{prefix}{system_instruction or ''}{suffix}"

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            temperature=self.model_config.temperature if self.model_config else None,
            top_p=self.model_config.top_p if self.model_config else None,
            top_k=self.model_config.top_k if self.model_config else None,
            max_output_tokens=self.model_config.max_tokens if self.model_config else None,
        )
        
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )
        
        # Translate to Anthropic non-stream response
        text = response.text if response.text else ""
        return {
            "id": f"msg_{uuid.uuid4().hex}",
            "type": "message",
            "role": "assistant",
            "model": self.model,
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                "output_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0
            }
        }

    async def generate_stream(self, request: AnthropicMessageRequest) -> AsyncGenerator[str, None]:
        contents, system_instruction, tools = convert_request_to_gemini(request)
        
        # Merge system prompt injection
        if self.model_config:
            prefix = self.model_config.system_prompt_prefix or ""
            suffix = self.model_config.system_prompt_suffix or ""
            if prefix or suffix:
                system_instruction = f"{prefix}{system_instruction or ''}{suffix}"

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            temperature=self.model_config.temperature if self.model_config else None,
            top_p=self.model_config.top_p if self.model_config else None,
            top_k=self.model_config.top_k if self.model_config else None,
            max_output_tokens=self.model_config.max_tokens if self.model_config else None,
        )
        
        msg_id = f"msg_{uuid.uuid4().hex}"
        
        # 1. message_start
        yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'id': msg_id, 'type': 'message', 'role': 'assistant', 'model': self.model, 'content': [], 'usage': {'input_tokens': 0, 'output_tokens': 0}}})}\n\n"
        
        # 2. content_block_start
        yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"
        
        input_tokens = 0
        output_tokens = 0

        async for chunk in await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config
        ):
            if chunk.usage_metadata:
                input_tokens = chunk.usage_metadata.prompt_token_count
                output_tokens = chunk.usage_metadata.candidates_token_count
                
            if chunk.text:
                yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': chunk.text}})}\n\n"
                
        # 3. content_block_stop
        yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"
        
        # 4. message_delta (stop reason)
        yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': output_tokens}})}\n\n"
        
        # 5. message_stop
        yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"
