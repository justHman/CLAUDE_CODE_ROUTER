import json
import uuid
from typing import AsyncGenerator

async def convert_openai_stream_to_anthropic(stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """
    Takes OpenAI SSE string lines, parses them, and yields Anthropic SSE string lines.
    """
    message_id = f"msg_{uuid.uuid4()}"
    
    # 1. Message Start
    msg_start = {
        "type": "message_start",
        "message": {
            "id": message_id,
            "type": "message",
            "role": "assistant",
            "content": [],
            "model": "unknown",
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0}
        }
    }
    yield f"event: message_start\ndata: {json.dumps(msg_start)}\n\n"
    
    # 2. Tracks states
    content_block_index = 0
    in_text_block = False
    in_tool_block = False
    current_tool_call_id = None
    current_tool_name = None
    
    async for line in stream:
        line = line.strip()
        if not line or line.startswith(":"):
            continue
            
        if line == "data: [DONE]":
            break
            
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
            except Exception:
                continue
                
            choices = data.get("choices", [])
            if not choices:
                continue
                
            delta = choices[0].get("delta", {})
            finish_reason = choices[0].get("finish_reason")
            
            # Handle text content
            content = delta.get("content")
            if content is not None:
                if not in_text_block:
                    # start text block
                    start_block = {
                        "type": "content_block_start",
                        "index": content_block_index,
                        "content_block": {"type": "text", "text": ""}
                    }
                    yield f"event: content_block_start\ndata: {json.dumps(start_block)}\n\n"
                    in_text_block = True
                    
                delta_block = {
                    "type": "content_block_delta",
                    "index": content_block_index,
                    "delta": {"type": "text_delta", "text": content}
                }
                yield f"event: content_block_delta\ndata: {json.dumps(delta_block)}\n\n"
                
            # Handle tool calls
            tool_calls = delta.get("tool_calls")
            if tool_calls:
                for tc in tool_calls:
                    tc_index = tc.get("index", 0)
                    # In OpenAI streams, the first chunk of a tool call has the id and name
                    if tc.get("id"):
                        # If we were in a text block, we must close it
                        if in_text_block:
                            yield f"event: content_block_stop\ndata: {{\"type\": \"content_block_stop\", \"index\": {content_block_index}}}\n\n"
                            content_block_index += 1
                            in_text_block = False
                            
                        # If we were in another tool block, close it
                        if in_tool_block:
                            yield f"event: content_block_stop\ndata: {{\"type\": \"content_block_stop\", \"index\": {content_block_index}}}\n\n"
                            content_block_index += 1
                            
                        current_tool_call_id = tc["id"]
                        current_tool_name = tc["function"]["name"]
                        
                        start_block = {
                            "type": "content_block_start",
                            "index": content_block_index,
                            "content_block": {
                                "type": "tool_use",
                                "id": current_tool_call_id,
                                "name": current_tool_name,
                                "input": {}
                            }
                        }
                        yield f"event: content_block_start\ndata: {json.dumps(start_block)}\n\n"
                        in_tool_block = True
                        
                    # Arguments chunk
                    if tc.get("function") and tc["function"].get("arguments"):
                        args_chunk = tc["function"]["arguments"]
                        delta_block = {
                            "type": "content_block_delta",
                            "index": content_block_index,
                            "delta": {
                                "type": "input_json_delta",
                                "partial_json": args_chunk
                            }
                        }
                        yield f"event: content_block_delta\ndata: {json.dumps(delta_block)}\n\n"
                        
            # Handle finish
            if finish_reason:
                if in_text_block:
                    yield f"event: content_block_stop\ndata: {{\"type\": \"content_block_stop\", \"index\": {content_block_index}}}\n\n"
                elif in_tool_block:
                    yield f"event: content_block_stop\ndata: {{\"type\": \"content_block_stop\", \"index\": {content_block_index}}}\n\n"
                    
                stop_reason_map = {
                    "stop": "end_turn",
                    "tool_calls": "tool_use",
                    "length": "max_tokens"
                }
                anthropic_stop_reason = stop_reason_map.get(finish_reason, "end_turn")
                
                msg_delta = {
                    "type": "message_delta",
                    "delta": {
                        "stop_reason": anthropic_stop_reason,
                        "stop_sequence": None
                    },
                    "usage": {"output_tokens": 1} # Dummy or real if provider sends usage stream
                }
                yield f"event: message_delta\ndata: {json.dumps(msg_delta)}\n\n"
                
    # 3. Message Stop
    yield f"event: message_stop\ndata: {{\"type\": \"message_stop\"}}\n\n"
