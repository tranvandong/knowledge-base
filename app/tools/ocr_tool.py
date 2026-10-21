# OCR Tool

from typing import Any

from app.models.ocr import OCRToolInput, ImageSourceType
from app.tools.base import BaseTool


class OCRTool(BaseTool[OCRToolInput]):
    """
    OCR Tool - cho phép agent nhận diện văn bản từ hình ảnh
    
    Tool này hỗ trợ 3 loại nguồn hình ảnh:
    - URL: Hình ảnh từ internet (http/https)
    - Base64: Image bytes dạng Base64 data URL
    - File ID: File đã upload lên Files API
    """
    
    def __init__(self, ocr_service: Any):
        """
        Args:
            ocr_service: OCRService instance để xử lý OCR
        """
        self.ocr_service = ocr_service
    
    @property
    def name(self) -> str:
        return "ocr_image"
    
    @property
    def description(self) -> str:
        return (
            "Nhận diện văn bản từ hình ảnh (OCR - Optical Character Recognition). "
            "Hỗ trợ 3 loại nguồn: "
            "1) url - Hình ảnh từ internet (http/https URL) "
            "2) base64 - Image bytes dạng Base64 data URL "
            "3) file_id - File đã upload lên hệ thống. "
            "Trả về văn bản được nhận diện cùng với ngôn ngữ phát hiện được."
        )
    
    @property
    def input_model(self) -> type[OCRToolInput]:
        return OCRToolInput
    
    def execute(self, arguments: OCRToolInput) -> dict[str, Any]:
        """
        Thực hiện OCR trên hình ảnh
        
        Args:
            arguments: OCRToolInput chứa thông tin nguồn hình ảnh
            
        Returns:
            Dict chứa kết quả OCR:
            {
                "success": bool,
                "full_text": str,
                "texts": [{"text": str, "confidence": float}],
                "language_detected": str,
                "model": str,
                "error": str | None
            }
        """
        import asyncio
        from app.models.ocr import OCRRequest
        
        # Convert tool input to service request
        ocr_request = OCRRequest(
            source_type=ImageSourceType(arguments.source_type),
            url=arguments.url,
            base64_data=arguments.base64_data,
            file_id=arguments.file_id,
            prompt=arguments.prompt,
        )
        
        # Run async OCR service trong sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(
            self.ocr_service.recognize(ocr_request)
        )
        
        return {
            "success": response.success,
            "full_text": response.full_text,
            "texts": [
                {
                    "text": item.text,
                    "confidence": item.confidence,
                    "bounding_box": item.bounding_box,
                }
                for item in response.texts
            ],
            "language_detected": response.language_detected,
            "model": response.model,
            "source_type": response.source_type.value,
            "error": response.error,
        }
    
    def validate_arguments(self, arguments: dict[str, Any]) -> OCRToolInput:
        """Validate và parse arguments"""
        return OCRToolInput(**arguments)


class OCRToolDefinition:
    """
    Tool definition cho LLM function calling
    """
    
    @staticmethod
    def get_definition() -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "ocr_image",
                "description": (
                    "Nhận diện văn bản từ hình ảnh (OCR). "
                    "Hỗ trợ hình ảnh từ URL, Base64 data, hoặc file đã upload."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_type": {
                            "type": "string",
                            "enum": ["url", "base64", "file_id"],
                            "description": "Loại nguồn hình ảnh",
                        },
                        "url": {
                            "type": "string",
                            "description": "URL đầy đủ của hình ảnh (bắt buộc nếu source_type=url)",
                        },
                        "base64_data": {
                            "type": "string",
                            "description": "Image bytes dạng Base64 data URL (bắt buộc nếu source_type=base64)",
                        },
                        "file_id": {
                            "type": "string",
                            "description": "File ID từ Files API (bắt buộc nếu source_type=file_id)",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Prompt bổ sung để hướng dẫn OCR",
                        },
                    },
                    "required": ["source_type"],
                    "allOf": [
                        {
                            "if": {"properties": {"source_type": {"const": "url"}}},
                            "then": {"required": ["url"]},
                        },
                        {
                            "if": {"properties": {"source_type": {"const": "base64"}}},
                            "then": {"required": ["base64_data"]},
                        },
                        {
                            "if": {"properties": {"source_type": {"const": "file_id"}}},
                            "then": {"required": ["file_id"]},
                        },
                    ],
                },
            },
        }
