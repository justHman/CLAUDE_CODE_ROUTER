import pytest
from core.routing import Router
from core.config import RoutingConfig, ProviderConfig

def test_router_model_mapping():
    cfg = RoutingConfig(
        default_provider="fallback",
        providers={
            "nvidia": ProviderConfig(type="openai_compatible", base_url="http://nvidia", api_key="123"),
            "fallback": ProviderConfig(type="openai_compatible", base_url="http://fallback", api_key="456")
        },
        model_mapping={"test-model": "nvidia"}
    )
    
    router = Router(config=cfg)
    
    # Matches mapping
    p1 = router.get_provider_for_model("test-model")
    assert p1.base_url == "http://nvidia"
    
    # Uses fallback
    p2 = router.get_provider_for_model("unknown-model")
    assert p2.base_url == "http://fallback"
