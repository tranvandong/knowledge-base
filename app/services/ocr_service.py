# OCR Service

import logging
from typing import Any

from app.models.ocr import (
    ImageSourceType,
    OCRRequest,
    OCRResponse,
)
from app.providers.ocr_provider import (
    OCRProvider,
    MockOCRProvider,
)


logger = logging.getLogger(__name__)


class OCRService:
    """
    OCR Service - Business logic layer cho OCR operations
    """
    
    def __init__(self, provider: OCRProvider):
        self.provider = provider
    
    async def recognize(self, request: OCRRequest) -> OCRResponse:
        """
        Thực hiện OCR trên hình ảnh
        
        Args:
            request: OCRRequest chứa thông tin nguồn hình ảnh
            
        Returns:
            OCRResponse với các text blocks được nhận diện
        """
        try:
            # Validate request
            request.validate_source()
            
            logger.info(
                "OCR request | source_type=%s | url=%s | file_id=%s | base64_len=%s",
                request.source_type,
                request.url or "N/A",
                request.file_id or "N/A",
                len(request.base64_data) if request.base64_data else 0,
            )
            
            # Gọi provider để thực hiện OCR
            response = await self.provider.recognize(
                source_type=request.source_type,
                url=request.url,
                base64_data=request.base64_data,
                file_id=request.file_id,
                prompt=request.prompt,
                language=request.language,
            )
            
            logger.info(
                "OCR completed | success=%s | texts_count=%d | model=%s",
                response.success,
                len(response.texts),
                response.model,
            )
            
            return response
            
        except ValueError as e:
            logger.warning("OCR validation error: %s", str(e))
            return OCRResponse(
                success=False,
                texts=[],
                full_text="",
                model=self.provider.model,
                source_type=request.source_type,
                error=f"Lỗi validation: {str(e)}",
            )
            
        except Exception as e:
            logger.error("OCR unexpected error: %s", str(e), exc_info=True)
            return OCRResponse(
                success=False,
                texts=[],
                full_text="",
                model=self.provider.model,
                source_type=request.source_type,
                error=f"Lỗi không xác định: {str(e)}",
            )
    
    def get_provider_info(self) -> dict[str, Any]:
        """Get thông tin về provider đang sử dụng"""
        return {
            "model": self.provider.model,
            "provider_type": self.provider.__class__.__name__,
        }


class OCRServiceFactory:
    """
    Factory để tạo OCR service với different providers
    """
    
    @staticmethod
    def create(
        provider_type: str = "mock",
        **kwargs,
    ) -> OCRService:
        """
        Tạo OCR service với specified provider
        
        Args:
            provider_type: Loại provider ("mock", "meta", "local")
            **kwargs: Các arguments cho provider
                - api_key: Meta AI API key
                - model: Model name
                - base_url: API base URL
        """
        if provider_type == "mock":
            provider = MockOCRProvider(
                model=kwargs.get("model", "mock-ocr-model")
            )
            
        elif provider_type == "meta":
            provider = MetaOCRProvider(
                api_key=kwargs["api_key"],
                model=kwargs.get("model", "muse-spark-1.3"),
                base_url=kwargs.get("base_url", "https://api.meta.ai/v1"),
            )
            
        elif provider_type == "local":
            from app.providers.ocr_provider import LocalOCRProvider
            provider = LocalOCRProvider(
                engine=kwargs.get("engine", "tesseract"),
                model=kwargs.get("model", "local-tesseract"),
            )
            
        else:
            raise ValueError(f"Không hỗ trợ provider type: {provider_type}")
        
        return OCRService(provider)
    
    @staticmethod
    def create_from_config(
        provider_type: str,
        api_key: str | None = None,
        model: str = "muse-spark-1.3",
        base_url: str = "https://api.meta.ai/v1",
    ) -> OCRService:
        """Tạo OCR service từ config"""
        if provider_type == "meta":
            if not api_key:
                raise ValueError("api_key là bắt buộc cho MetaOCRProvider")
            provider = MetaOCRProvider(
                api_key=api_key,
                model=model,
                base_url=base_url,
            )
        elif provider_type == "mock":
            provider = MockOCRProvider(model=model)
        else:
            raise ValueError(f"Không hỗ trợ provider type: {provider_type}")
        
        return OCRService(provider)


# Import MetaOCRProvider for factory
from app.providers.ocr_provider import MetaOCRProvider