import json
import base64
from typing import List, Tuple, Any, Dict
from transformers.models import AnthropicMessageRequest, AnthropicMessage, AnthropicMessageContent, AnthropicTool
from google.genai import types

def convert_request_to_gemini(req: AnthropicMessageRequest) -> Tuple[list, Any, list]:
    def dict_to_schema(schema: dict) -> types.Schema:
        if not isinstance(schema, dict):
            return types.Schema(type="STRING")
            
        t = schema.get("type", "STRING")
        if isinstance(t, list):
            t = [x for x in t if x != "null"]
            t = t[0] if t else "STRING"
            
        t = t.upper()
        if t not in ["STRING", "NUMBER", "INTEGER", "BOOLEAN", "ARRAY", "OBJECT"]:
            t = "STRING"
            
        props = None
        if "properties" in schema and isinstance(schema["properties"], dict):
            props = {k: dict_to_schema(v) for k, v in schema["properties"].items()}
                
        items = None
        if "items" in schema and isinstance(schema["items"], dict):
            items = dict_to_schema(schema["items"])
            
        return types.Schema(
            type=t,
            format=schema.get("format"),
            description=schema.get("description"),
            enum=schema.get("enum"),
            properties=props,
            required=schema.get("required"),
            items=items
        )

    contents = []
    
    for msg in req.messages:
        role = "user" if msg.role == "user" else "model"
        parts = []
        
        if isinstance(msg.content, str):
            parts.append(types.Part.from_text(text=msg.content))
        else:
            for block in msg.content:
                if block.type == "text" and block.text:
                    parts.append(types.Part.from_text(text=block.text))
                elif block.type == "image" and block.source:
                    img_bytes = base64.b64decode(block.source.data)
                    parts.append(types.Part.from_bytes(data=img_bytes, mime_type=block.source.media_type))
                elif block.type == "tool_use":
                    # Google GenAI requires FunctionCall objects
                    # For MVP, we will assume Anthropic Claude CLI doesn't heavily rely on complex tool calls for vision,
                    # but we'll try to map it.
                    parts.append(types.Part.from_function_call(
                        name=block.name,
                        args=block.input
                    ))
                elif block.type == "tool_result":
                    content_str = str(block.content) if not isinstance(block.content, list) else json.dumps([c.dict() for c in block.content])
                    # Ensure name exists, if not, put a dummy
                    name = getattr(block, 'name', 'unknown_tool') 
                    parts.append(types.Part.from_function_response(
                        name=name,
                        response={"result": content_str}
                    ))
        
        if parts:
            contents.append(types.Content(role=role, parts=parts))
            
    system_instruction = None
    if req.system:
        sys_str = req.system if isinstance(req.system, str) else "".join([b.get("text", "") for b in req.system if b.get("type") == "text"])
        system_instruction = sys_str
        
    # Mapping tools is complex in SDK, fallback to None if not strict
    # We will try passing dicts as function declarations if needed
    gemini_tools = None
    if req.tools:
        funcs = []
        for t in req.tools:
            params = dict_to_schema(t.input_schema) if t.input_schema else types.Schema(type="OBJECT", properties={})
            if params.type != "OBJECT":
                params.type = "OBJECT"
                
            funcs.append(types.FunctionDeclaration(
                name=t.name,
                description=t.description or "",
                parameters=params
            ))
        gemini_tools = [types.Tool(function_declarations=funcs)]
        
    return contents, system_instruction, gemini_tools
