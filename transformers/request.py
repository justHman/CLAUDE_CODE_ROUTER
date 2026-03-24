import json
from typing import Dict, Any, List
from transformers.models import AnthropicMessageRequest, AnthropicMessage, AnthropicMessageContent, AnthropicTool

def convert_tools_to_openai(tools: List[AnthropicTool]) -> List[Dict[str, Any]]:
    if not tools:
        return []
    
    openai_tools = []
    for t in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.input_schema
            }
        })
    return openai_tools


def convert_messages_to_openai(messages: List[AnthropicMessage]) -> List[Dict[str, Any]]:
    openai_messages = []
    
    for msg in messages:
        role = msg.role
        if isinstance(msg.content, str):
            openai_messages.append({"role": role, "content": msg.content})
        else:
            # Complex content array
            content_str = ""
            tool_calls = []
            tool_call_id = None
            for block in msg.content:
                if block.type == "text":
                    content_str += (block.text or "")
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "type": "function",
                        "function": {
                            "name": block.name,
                            "arguments": json.dumps(block.input)
                        }
                    })
                elif block.type == "tool_result":
                    # For OpenAI, tool results are separate messages with role "tool"
                    # But Claude sends them in the next 'user' message with type 'tool_result'
                    tool_call_id = block.tool_use_id if hasattr(block, 'tool_use_id') else None
                    # Fallback if id is stored in block.id (which in our model it usually isn't standard, Anthropic uses tool_use_id)
                    # For safety, let's extract tool_use_id from dict if possible
                    # Note: We need to update our model to include tool_use_id
                    
            if tool_calls:
                openai_msg = {"role": role, "content": content_str or None, "tool_calls": tool_calls}
                openai_messages.append(openai_msg)
            elif role == "user" and any(b.type == "tool_result" for b in msg.content):
                # Claude bundles tool results into the user message.
                # OpenAI requires a separate message per tool result.
                for block in msg.content:
                    if block.type == "text":
                        if block.text:
                            openai_messages.append({"role": "user", "content": block.text})
                    elif block.type == "tool_result":
                        tool_use_id = getattr(block, "tool_use_id", block.id)
                        # The content could be string or list
                        content_res = block.content
                        if isinstance(content_res, list):
                            content_res = json.dumps([c.dict() for c in content_res])
                        openai_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_use_id,
                            "content": str(content_res)
                        })
            else:
                openai_messages.append({"role": role, "content": content_str})
                
    return openai_messages

def convert_request(req: AnthropicMessageRequest) -> dict:
    openai_req = {
        "model": req.model,
        "messages": convert_messages_to_openai(req.messages),
        "temperature": req.temperature,
        "max_tokens": req.max_tokens,
        "stream": req.stream,
    }
    
    if req.system:
        # System prompt prepended
        if isinstance(req.system, str):
            openai_req["messages"].insert(0, {"role": "system", "content": req.system})
        elif isinstance(req.system, list):
            # If it's a list of blocks
            sys_content = "".join([b.get("text", "") for b in req.system if isinstance(b, dict) and b.get("type") == "text"])
            openai_req["messages"].insert(0, {"role": "system", "content": sys_content})
            
    if req.tools:
        openai_req["tools"] = convert_tools_to_openai(req.tools)
        if req.tool_choice:
            # map tool_choice
            if req.tool_choice.type == "auto":
                openai_req["tool_choice"] = "auto"
            elif req.tool_choice.type == "any":
                openai_req["tool_choice"] = "required"
            elif req.tool_choice.type == "tool":
                openai_req["tool_choice"] = {
                    "type": "function",
                    "function": {"name": req.tool_choice.name}
                }
                
    if req.top_p is not None:
        openai_req["top_p"] = req.top_p
        
    return openai_req
