from transformers.request import convert_request
from transformers.models import AnthropicMessageRequest, AnthropicMessage, AnthropicMessageContent

def test_convert_simple_message():
    req = AnthropicMessageRequest(
        model="sonnet[3m]",
        messages=[
            AnthropicMessage(role="user", content="Hello world")
        ],
        temperature=0.5
    )
    
    openai_req = convert_request(req)
    
    assert openai_req["temperature"] == 0.5
    assert openai_req["messages"][0]["role"] == "user"
    assert openai_req["messages"][0]["content"] == "Hello world"
    assert "tools" not in openai_req

def test_convert_system_prompt():
    req = AnthropicMessageRequest(
        model="opus",
        system="You are an AI",
        messages=[AnthropicMessage(role="user", content="Hi")]
    )
    openai_req = convert_request(req)
    assert openai_req["messages"][0]["role"] == "system"
    assert openai_req["messages"][0]["content"] == "You are an AI"
    assert openai_req["messages"][1]["role"] == "user"
