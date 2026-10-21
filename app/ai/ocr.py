# OCR Controller

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models.ocr import (
    ImageSourceType,
    OCRRequest,
    OCRResponse,
)
from app.services.ocr_service import OCRService
from app.providers.ocr_provider import MockOCRProvider


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ocr",
    tags=["OCR"],
)


# Default OCR service (mock)
def get_default_ocr_service() -> OCRService:
    """Tạo default OCR service với Mock provider"""
    return OCRService(MockOCRProvider(model="mock-ocr-v1"))


@router.post(
    "",
    response_model=OCRResponse,
    summary="OCR từ hình ảnh",
    description="""
    Nhận diện văn bản từ hình ảnh sử dụng OCR.
    
    Hỗ trợ 3 loại nguồn hình ảnh:
    1. **URL**: Hình ảnh từ internet (http/https URL)
    2. **Base64**: Image bytes dạng Base64 data URL (`data:image/...;base64,...`)
    3. **File ID**: File đã upload lên Files API
    
    ## Ví dụ sử dụng
    
    ### Từ URL
    ```bash
    curl -X POST http://localhost:8000/ocr \\
      -H "Content-Type: application/json" \\
      -d '{
        "source_type": "url",
        "url": "https://example.com/image.png",
        "language": "vi"
      }'
    ```
    
    ### Từ Base64
    ```bash
    curl -X POST http://localhost:8000/ocr \\
      -H "Content-Type: application/json" \\
      -d '{
        "source_type": "base64",
        "base64_data": "data:image/png;base64,iVBORw0KG..."
      }'
    ```
    
    ### Từ File ID
    ```bash
    curl -X POST http://localhost:8000/ocr \\
      -H "Content-Type: application/json" \\
      -d '{
        "source_type": "file_id",
        "file_id": "file_abc123"
      }'
    ```
    """,
    responses={
        200: {
            "description": "OCR successful",
            "model": OCRResponse,
        },
        400: {
            "description": "Invalid request (missing required fields)",
        },
        500: {
            "description": "OCR processing error",
        },
    },
)
async def ocr_image(
    request: OCRRequest,
    service: Annotated[OCRService, Depends(get_default_ocr_service)],
) -> OCRResponse:
    """
    Nhận diện văn bản từ hình ảnh (OCR endpoint)
    
    Args:
        request: OCRRequest chứa thông tin nguồn hình ảnh và các tùy chọn
        service: OCRService được inject qua dependency
    
    Returns:
        OCRResponse với các đoạn text được nhận diện
        
    Raises:
        HTTPException: 400 nếu request không hợp lệ
        HTTPException: 500 nếu có lỗi khi xử lý OCR
    """
    try:
        # Validate source
        try:
            request.validate_source()
        except ValueError as e:
            logger.warning("OCR validation error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        
        # Process OCR
        response = await service.recognize(request)
        
        if not response.success:
            logger.error("OCR failed: %s", response.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error or "OCR processing failed",
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("OCR unexpected error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi không xác định: {str(e)}",
        )


@router.post(
    "/stream",
    summary="OCR với streaming response",
    description="""
    Nhận diện văn bản từ hình ảnh với streaming response.
    Trả về từng text block ngay khi được nhận diện.
    
    Response format: Server-Sent Events (SSE)
    ```
    data: {"status": "processing", "texts_count": 0}\n\n
    data: {"status": "text_found", "text": "...", "index": 0}\n\n
    data: {"status": "completed", "full_text": "...", "language": "vi"}\n\n
    ```
    """,
)
async def ocr_image_stream(
    request: OCRRequest,
    service: Annotated[OCRService, Depends(get_default_ocr_service)],
) -> StreamingResponse:
    """
    OCR với streaming - trả về từng text block ngay khi được nhận diện
    
    Args:
        request: OCRRequest
        service: OCRService
    
    Returns:
        StreamingResponse (SSE)
    """
    async def generate():
        try:
            # Validate source
            request.validate_source()
            
            # Send processing status
            yield "data: {\"status\": \"processing\", \"message\": \"Bắt đầu nhận diện văn bản\"}\n\n"
            
            # Process OCR
            response = await service.recognize(request)
            
            if response.success:
                # Send each text found
                for index, item in enumerate(response.texts):
                    import json
                    yield f"data: {json.dumps({'status': 'text_found', 'text': item.text, 'index': index, 'confidence': item.confidence})}\n\n"
                
                # Send completion
                import json
                completion_data = {
                    "status": "completed",
                    "full_text": response.full_text,
                    "texts_count": len(response.texts),
                    "language_detected": response.language_detected,
                    "model": response.model,
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            else:
                import json
                yield f"data: {json.dumps({'status': 'error', 'error': response.error})}\n\n"
                
        except Exception as e:
            import json
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get(
    "/providers",
    summary="Lấy thông tin OCR providers",
    description="Trả về danh sách các OCR providers được hỗ trợ và thông tin model",
)
async def get_ocr_providers(
    service: Annotated[OCRService, Depends(get_default_ocr_service)],
) -> dict:
    """
    Lấy thông tin về OCR provider đang được sử dụng
    
    Returns:
        Dict chứa thông tin provider và model
    """
    info = service.get_provider_info()
    
    return {
        "available_providers": ["mock", "meta", "local"],
        "current_provider": info,
        "supported_source_types": [
            {"type": "url", "description": "Hình ảnh từ internet", "required_field": "url"},
            {"type": "base64", "description": "Image bytes dạng Base64", "required_field": "base64_data"},
            {"type": "file_id", "description": "File đã upload lên Files API", "required_field": "file_id"},
        ],
        "supported_languages": [
            {"code": "vi", "name": "Vietnamese"},
            {"code": "en", "name": "English"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"},
        ],
    }


@router.get(
    "/health",
    summary="OCR health check",
    description="Kiểm tra OCR service có đang hoạt động không",
)
async def ocr_health(
    service: Annotated[OCRService, Depends(get_default_ocr_service)],
) -> dict:
    """
    OCR health check
    
    Returns:
        Dict với status OK nếu service hoạt động
    """
    info = service.get_provider_info()
    
    return {
        "status": "ok",
        "service": "ocr",
        "provider": info["provider_type"],
        "model": info["model"],
    }
