from fastapi import FastAPI, APIRouter, Depends, Form, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
import logging
import tempfile
from ..Services.Challenge_Service import verify_challenge as verify_challenge_service

logger = logging.getLogger('uvicorn.error')

challenge_router = APIRouter()


@challenge_router.post("/verify")
async def verify_challenge(image: UploadFile, description: str = Form()):
    try:
        image_bytes = await image.read()
        verification_result = verify_challenge_service(image_bytes, description)
        logger.info(f"Verification result: {verification_result}")

        return JSONResponse(content={"verification_result": verification_result}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error during challenge verification: {e}")
        return JSONResponse(content={"error": "An error occurred during verification."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)