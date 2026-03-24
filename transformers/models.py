from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

# -----------------
# Anthropic Schemas
# -----------------

class AnthropicSource(BaseModel):
    type: str # "base64" usually
    media_type: str
    data: str

class AnthropicMessageContent(BaseModel):
    type: str # "text", "image", "tool_use", "tool_result"
    text: Optional[str] = None
    source: Optional[AnthropicSource] = None
    id: Optional[str] = None
    name: Optional[str] = None
    input: Optional[Dict[str, Any]] = None
    content: Optional[Union[str, List[Dict[str, Any]]]] = None # For tool_result
    is_error: Optional[bool] = None

class AnthropicMessage(BaseModel):
    role: str
    content: Union[str, List[AnthropicMessageContent]]

class AnthropicTool(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any]

class AnthropicToolChoice(BaseModel):
    type: str # "auto", "any", "tool"
    name: Optional[str] = None

class AnthropicMessageRequest(BaseModel):
    model: str
    messages: List[AnthropicMessage]
    max_tokens: int = Field(default=8192)
    system: Optional[Union[str, List[Dict[str, Any]]]] = None
    temperature: Optional[float] = 1.0
    stream: Optional[bool] = False
    tools: Optional[List[AnthropicTool]] = None
    tool_choice: Optional[AnthropicToolChoice] = None
    metadata: Optional[Dict[str, Any]] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None