"""
FastAPI route module for hands-free Voice & Chat assistant interaction.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends

from commons.logger import logger
from core.apis.routes.auth_routes import get_current_user_claims
from core.apis.schemas.requests.wms_schemas import VoiceAssistantRequest
from core.apis.schemas.responses.wms_schemas import VoiceAssistantResponse
from core.controllers.wms_controllers import WMSController

assistant_router = APIRouter()
logging = logger(__name__)


@assistant_router.post(
    "/v1/assistant/chat",
    status_code=status.HTTP_200_OK,
    response_model=VoiceAssistantResponse,
)
async def query_assistant(
    request: VoiceAssistantRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    Process natural language transcribed voice command or text query.

    Args:
        request (VoiceAssistantRequest): Natural language query payload.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        VoiceAssistantResponse: Assistant answer with spoken text response.
    """
    try:
        logging.info("Calling POST /v1/assistant/chat endpoint")
        result = WMSController().query_assistant(
            user_info=user_claims,
            user_query=request.user_query,
            warehouse_id=request.warehouse_id,
        )
        return VoiceAssistantResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in POST /v1/assistant/chat endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing voice request",
        )
