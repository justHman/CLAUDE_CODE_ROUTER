from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import time

from transformers.models import AnthropicMessageRequest
from core.routing import Router
from api.deps import get_router
from core.logger import logger
from core.db import log_request

router = APIRouter()

@router.post("/v1/messages")
async def create_message(
    request: AnthropicMessageRequest,
    router_svc: Router = Depends(get_router)
):
    logger.debug(f"Received request for model {request.model}, stream={request.stream}")
    try:
        provider = router_svc.get_provider_for_model(request.model)
        target_model = getattr(provider, 'model', request.model)
        provider_name = type(provider).__name__
        start_time = time.time()
        
        if request.stream:
            async def stream_wrapper():
                tokens_out = 0
                status = 200
                try:
                    async for chunk in provider.generate_stream(request):
                        tokens_out += 1
                        yield chunk
                except Exception as e:
                    status = 500
                    raise e
                finally:
                    latency_ms = int((time.time() - start_time) * 1000)
                    log_request(
                        requested_model=request.model,
                        target_model=target_model,
                        provider=provider_name,
                        latency_ms=latency_ms,
                        status_code=status,
                        tokens_in=0,
                        tokens_out=tokens_out
                    )
            return StreamingResponse(
                stream_wrapper(),
                media_type="text/event-stream"
            )
        else:
            resp = await provider.generate_message(request)
            latency_ms = int((time.time() - start_time) * 1000)
            log_request(request.model, target_model, provider_name, latency_ms, 200)
            return resp
            
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        latency_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        log_request(request.model, request.model, "Unknown", latency_ms, 500)
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
