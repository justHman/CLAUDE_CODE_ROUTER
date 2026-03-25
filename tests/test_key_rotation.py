import pytest
from core.config import ProviderConfig

def test_api_key_parsing():
    config = ProviderConfig(
        base_url="http://test.com",
        api_key="key1, key2, key3 ",
        type="test"
    )
    
    assert config.get_active_key() == "key1"
    
def test_key_rotation():
    config = ProviderConfig(
        base_url="http://test.com",
        api_key="keyA, keyB, keyC",
        type="test"
    )
    
    # State 0
    assert config.get_active_key() == "keyA"
    
    # Rotate to State 1
    assert config.rotate_key() is True
    assert config.get_active_key() == "keyB"
    
    # Rotate to State 2
    assert config.rotate_key() is True
    assert config.get_active_key() == "keyC"
    
    # Rotate exhausted
    assert config.rotate_key() is False
    assert config.get_active_key() == "keyC" # Stays on the last one
    
    # Reset
    config.reset_keys()
    assert config.get_active_key() == "keyA"
    
def test_empty_keys():
    config = ProviderConfig(
        base_url="http://test.com",
        api_key="",
        type="test"
    )
    
    assert config.get_active_key() is None
    assert config.rotate_key() is False
