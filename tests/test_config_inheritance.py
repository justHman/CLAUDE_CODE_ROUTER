import pytest
from core.routing import Router
from core.config import RoutingConfig, ProviderConfig, ModelParams

def test_resolve_config_inheritance():
    cfg = RoutingConfig(
        default_provider="fallback",
        global_config=ModelParams(
            temperature=0.7,
            max_tokens=4096,
            top_p=1.0,
            system_prompt_suffix=" (Global)"
        ),
        providers={
            "nvidia": ProviderConfig(
                type="openai_compatible", 
                base_url="http://nvidia", 
                api_key="123",
                # Priority 2: Provider level
                config=ModelParams(temperature=0.5, system_prompt_prefix="[Provider] ")
            ),
            "fallback": ProviderConfig(type="openai_compatible", base_url="http://fallback", api_key="456")
        },
        profiles={
            "coding": ModelParams(
                # Priority 3: Profile level
                temperature=0.0,
                top_k=1,
                system_prompt_prefix="[Profile] "
            )
        },
        model_mapping={
            "simple-model": "nvidia", # Uses Global & Provider
            "profile-model": {
                "provider": "nvidia",
                "profile": "coding" # Merges Global, Provider, Profile
            },
            "override-model": {
                "provider": "nvidia",
                "profile": "coding",
                # Priority 4: Model Specific
                "config": {
                    "temperature": 1.2,
                    "max_tokens": 8192,
                    "system_prompt_suffix": " (Model)"
                }
            }
        }
    )
    
    router = Router(config=cfg)
    
    # CASE 1: Simple Model (Global + Provider)
    res1 = router._resolve_model_config(cfg.model_mapping["simple-model"], "nvidia")
    assert res1.temperature == 0.5  # Provider wins over Global (0.7)
    assert res1.max_tokens == 4096  # From Global
    assert res1.top_p == 1.0        # From Global
    assert res1.system_prompt_prefix == "[Provider] "
    assert res1.system_prompt_suffix == " (Global)"

    # CASE 2: Profile Model (Global + Provider + Profile)
    res2 = router._resolve_model_config(cfg.model_mapping["profile-model"], "nvidia")
    assert res2.temperature == 0.0  # Profile (0.0) wins over Provider (0.5)
    assert res2.top_k == 1          # From Profile
    assert res2.system_prompt_prefix == "[Profile] " # Profile wins over Provider ([Provider])
    assert res2.system_prompt_suffix == " (Global)"  # From Global
    
    # CASE 3: Override Model (Global + Provider + Profile + Model)
    res3 = router._resolve_model_config(cfg.model_mapping["override-model"], "nvidia")
    assert res3.temperature == 1.2   # Model (1.2) wins over Profile (0.0)
    assert res3.max_tokens == 8192   # Model wins over Global (4096)
    assert res3.top_k == 1           # From Profile
    assert res3.system_prompt_suffix == " (Model)" # Model wins over Global ( (Global))
    assert res3.system_prompt_prefix == "[Profile] " # From Profile

    print("Config inheritance tests passed!")

if __name__ == "__main__":
    # If run directly instead of pytest
    test_resolve_config_inheritance()
