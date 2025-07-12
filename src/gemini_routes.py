"""
Gemini Chat Routes - Handles native Gemini chat interfaces.
This module provides native Gemini chat interfaces that connect directly to Google's Assistant
without any format transformations.
"""
import json
import logging
from fastapi import APIRouter, Request, Response, Depends
from typing import Optional

from .auth import authenticate_user
from .google_chat_interface import send_gemini_request, build_gemini_payload_from_native
from .config import SUPPORTED_MODELS

router = APIRouter()


@router.get("/v1beta/models")
async def gemini_list_models(request: Request, username: str = Depends(authenticate_user)):
    """
    Native Gemini models interface.
    Returns available models in Gemini format, matching the official Gemini Assistant.
    """
    try:
        logging.info("Gemini models list requested")
        models_response = {
            "models": SUPPORTED_MODELS
        }
        logging.info(f"Returning {len(SUPPORTED_MODELS)} Gemini models")
        return Response(
            content=json.dumps(models_response),
            status_code=200,
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logging.error(f"Failed to list Gemini models: {str(e)}")
        return Response(
            content=json.dumps({
                "error": {
                    "message": f"Failed to list models: {str(e)}",
                    "code": 500
                }
            }),
            status_code=500,
            media_type="application/json"
        )


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gemini_chat_handler(request: Request, full_path: str, username: str = Depends(authenticate_user)):
    """
    Native Gemini chat handler interface.
    Handles all native Gemini chat calls by connecting directly to Google's Assistant.
    
    This handler manages paths like:
    - /v1beta/models/{model}/generateContent
    - /v1beta/models/{model}/streamGenerateContent
    - /v1/models/{model}/generateContent
    - etc.
    """
    try:
        # Get the request body
        post_data = await request.body()
        # Determine if this is a streaming request
        is_streaming = "stream" in full_path.lower()
        # Extract model name from the path
        model_name = _extract_model_from_path(full_path)
        logging.info(f"Gemini chat handler request: path={full_path}, model={model_name}, stream={is_streaming}")
        if not model_name:
            logging.error(f"Could not extract model name from path: {full_path}")
            return Response(
                content=json.dumps({
                    "error": {
                        "message": f"Could not extract model name from path: {full_path}",
                        "code": 400
                    }
                }),
                status_code=400,
                media_type="application/json"
            )
        # Parse the incoming request
        try:
            if post_data:
                incoming_request = json.loads(post_data)
            else:
                incoming_request = {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in request body: {str(e)}")
            return Response(
                content=json.dumps({
                    "error": {
                        "message": "Invalid JSON in request body",
                        "code": 400
                    }
                }),
                status_code=400,
                media_type="application/json"
            )
        # Build the payload for Google Assistant
        gemini_payload = build_gemini_payload_from_native(incoming_request, model_name)
        # Send the request to Google Assistant
        response = send_gemini_request(gemini_payload, is_streaming=is_streaming)
        # Log the response status
        if hasattr(response, 'status_code'):
            if response.status_code != 200:
                logging.error(f"Gemini Assistant returned error: status={response.status_code}")
            else:
                logging.info(f"Successfully processed Gemini chat for model: {model_name}")
        return response
    except Exception as e:
        logging.error(f"Gemini chat handler error: {str(e)}")
        return Response(
            content=json.dumps({
                "error": {
                    "message": f"Handler error: {str(e)}",
                    "code": 500
                }
            }),
            status_code=500,
            media_type="application/json"
        )

def _extract_model_from_path(path: str) -> Optional[str]:
    """
    Extract the model name from a Gemini chat path.
    
    Examples:
    - "v1beta/models/gemini-1.5-pro/generateContent" -> "gemini-1.5-pro"
    - "v1/models/gemini-2.0-flash/streamGenerateContent" -> "gemini-2.0-flash"
    
    Args:
        path: The chat path
    Returns:
        Model name (just the model name, not prefixed with "models/") or None if not found
    """
    parts = path.split('/')
    # Look for the pattern: .../models/{model_name}/...
    try:
        models_index = parts.index('models')
        if models_index + 1 < len(parts):
            model_name = parts[models_index + 1]
            # Remove any action suffix like ":streamGenerateContent" or ":generateContent"
            if ':' in model_name:
                model_name = model_name.split(':')[0]
            # Return just the model name without "models/" prefix
            return model_name
    except ValueError:
        pass
    # If we can't find the pattern, return None
    return None

@router.get("/v1/models")
async def gemini_list_models_v1(request: Request, username: str = Depends(authenticate_user)):
    """
    Alternative models interface for v1 version.
    Some clients might use /v1/models instead of /v1beta/models.
    """
    return await gemini_list_models(request, username)

# Health check interface
@router.get("/health")
async def health_check():
    """
    Simple health check interface.
    """
    return {"status": "healthy", "service": "gemini-chat-playground"}