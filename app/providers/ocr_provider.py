# OCR Provider

import base64
import json
import httpx
from abc import ABC, abstractmethod
from typing import Any

from app.models.ocr import (
    ImageSourceType,
    OCRRequest,
    OCRResponse,
    OCRResultItem,
)


class OCRProvider(ABC):
    """Abstract base class cho OCR providers"""
    
    @property
    @abstractmethod
    def model(self) -> str:
        """Tên model OCR"""
        pass
    
    @abstractmethod
    async def recognize(
        self,
        source_type: ImageSourceType,
        url: str | None = None,
        base64_data: str | None = None,
        file_id: str | None = None,
        prompt: str | None = None,
        language: str | None = None,
    ) -> OCRResponse:
        """
        Thực hiện OCR trên hình ảnh
        
        Args:
            source_type: Loại nguồn hình ảnh
            url: URL của hình ảnh (cho source_type=URL)
            base64_data: Base64 data URL (cho source_type=BASE64)
            file_id: File ID (cho source_type=FILE_ID)
            prompt: Prompt bổ sung
            language: Ngôn ngữ văn bản
            
        Returns:
            OCRResponse với các text blocks được nhận diện
        """
        pass
    
    def _build_image_content(
        self,
        source_type: ImageSourceType,
        url: str | None = None,
        base64_data: str | None = None,
        file_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Build image content format cho Meta AI API
        """
        if source_type == ImageSourceType.URL and url:
            return [{"type": "input_image", "image_url": url}]
        
        elif source_type == ImageSourceType.BASE64 and base64_data:
            # base64_data đã có format: data:image/...;base64,...
            return [{"type": "input_image", "image_url": base64_data}]
        
        elif source_type == ImageSourceType.FILE_ID and file_id:
            return [{"type": "input_image", "image_url": f"file://{file_id}"}]
        
        raise ValueError(f"Không hỗ trợ source_type: {source_type}")
    
    def _build_content_text(
        self,
        prompt: str | None = None,
        language: str | None = None,
    ) -> str:
        """Build text content với optional prompt và language"""
        parts = []
        
        if language:
            parts.append(f"Hãy nhận diện văn bản tiếng {language} trong hình ảnh này.")
        
        if prompt:
            parts.append(prompt)
        else:
            if not language:
                parts.append("Hãy nhận diện tất cả văn bản có trong hình ảnh này.")
        
        parts.append("Trả về văn bản chính xác nhất có thể.")
        
        return " ".join(parts)


class MetaOCRProvider(OCRProvider):
    """
    Meta AI OCR Provider - sử dụng Meta AI API
    Compatible với curl example đã cung cấp
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "muse-spark-1.3",
        base_url: str = "https://api.meta.ai/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    @property
    def model(self) -> str:
        return self.model
    
    async def recognize(
        self,
        source_type: ImageSourceType,
        url: str | None = None,
        base64_data: str | None = None,
        file_id: str | None = None,
        prompt: str | None = None,
        language: str | None = None,
    ) -> OCRResponse:
        """
        Gọi Meta AI API để thực hiện OCR
        """
        try:
            # Build image content
            image_content = self._build_image_content(
                source_type, url, base64_data, file_id
            )
            
            # Build text prompt
            text_content = self._build_content_text(prompt, language)
            
            # Prepare request payload theo Meta AI API format
            payload = {
                "model": self.model,
                "input": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": text_content
                            },
                            *image_content
                        ]
                    }
                ]
            }
            
            # Make API call
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/responses",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                
                response.raise_for_status()
                data = response.json()
                
                return self._parse_response(data, source_type)
                
        except httpx.HTTPStatusError as e:
            return OCRResponse(
                success=False,
                texts=[],
                full_text="",
                model=self.model,
                source_type=source_type,
                error=f"HTTP Error: {e.response.status_code} - {e.response.text}",
            )
        except Exception as e:
            return OCRResponse(
                success=False,
                texts=[],
                full_text="",
                model=self.model,
                source_type=source_type,
                error=f"Lỗi không xác định: {str(e)}",
            )
    
    def _parse_response(
        self,
        data: dict[str, Any],
        source_type: ImageSourceType,
    ) -> OCRResponse:
        """
        Parse Meta AI API response thành OCRResponse
        
        Meta AI response format:
        {
            "id": "...",
            "model": "muse-spark-1.3",
            "choices": [...],
            "output": {
                "content": [...]
            }
        }
        """
        try:
            # Extract output content
            output = data.get("output", {})
            contents = output.get("content", [])
            
            texts = []
            full_text_parts = []
            language_detected = None
            
            for content in contents:
                if content.get("type") == "text":
                    text = content.get("text", "").strip()
                    if text:
                        full_text_parts.append(text)
                        
                        # Create result item
                        result_item = OCRResultItem(
                            text=text,
                            confidence=0.9,  # Meta AI không cung cấp confidence
                            bounding_box=None,
                        )
                        texts.append(result_item)
                        
                        # Try to detect language from first result
                        if language_detected is None and text:
                            language_detected = self._detect_language(text)
            
            return OCRResponse(
                success=True,
                texts=texts,
                full_text="\n\n".join(full_text_parts),
                language_detected=language_detected,
                model=self.model,
                source_type=source_type,
                error=None,
            )
            
        except Exception as e:
            return OCRResponse(
                success=False,
                texts=[],
                full_text="",
                model=self.model,
                source_type=source_type,
                error=f"Lỗi parse response: {str(e)}",
            )
    
    def _detect_language(self, text: str) -> str | None:
        """Simple language detection based on character patterns"""
        # Check for Vietnamese diacritics
        vietnamese_chars = set("ăâđêôơưạảấềỏắằệốớủửợẩẫậểổ"
                              "áàảãạăằắẳẵặâầấẩẫậéèẻẽẹêềếểễệíìỉĩị"
                              "óòỏõọôồốổỗộướờởỡợúùủũụưừứửữựýỳỷỹỵ")
        
        # Check for Japanese characters
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FFF),  # CJK
        ]
        
        # Check for Korean
        korean_range = (0xAC00, 0xD7AF)
        
        text_set = set(text.lower())
        
        # Vietnamese detection
        if text_set & vietnamese_chars:
            return "vi"
        
        # Japanese detection
        for char in text:
            code = ord(char)
            for start, end in japanese_ranges:
                if start <= code <= end:
                    return "ja"
        
        # Korean detection
        for char in text:
            code = ord(char)
            if korean_range[0] <= code <= korean_range[1]:
                return "ko"
        
        # Default to English if mostly ASCII
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        if ascii_chars / len(text) > 0.9:
            return "en"
        
        return None


class MockOCRProvider(OCRProvider):
    """
    Mock OCR Provider cho testing
    """
    
    def __init__(self, model: str = "mock-ocr-model"):
        self._model = model
    
    @property
    def model(self) -> str:
        return self._model
    
    async def recognize(
        self,
        source_type: ImageSourceType,
        url: str | None = None,
        base64_data: str | None = None,
        file_id: str | None = None,
        prompt: str | None = None,
        language: str | None = None,
    ) -> OCRResponse:
        """Mock OCR - trả về kết quả fake"""
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(0.5)
        
        mock_texts = [
            OCRResultItem(
                text="Hóa đơn GTGT",
                confidence=0.95,
                bounding_box={"x": 10, "y": 10, "width": 200, "height": 30},
            ),
            OCRResultItem(
                text="Công ty TNHH ABC",
                confidence=0.92,
                bounding_box={"x": 10, "y": 50, "width": 150, "height": 20},
            ),
            OCRResultItem(
                text="Địa chỉ: 123 Nguyễn Trãi, Q1, TP.HCM",
                confidence=0.88,
                bounding_box={"x": 10, "y": 80, "width": 300, "height": 20},
            ),
        ]
        
        full_text = "\n".join([item.text for item in mock_texts])
        
        detected_lang = language or "vi"
        
        return OCRResponse(
            success=True,
            texts=mock_texts,
            full_text=full_text,
            language_detected=detected_lang,
            model=self.model,
            source_type=source_type,
            error=None,
        )


class LocalOCRProvider(OCRProvider):
    """
    Local OCR Provider - sử dụng Tesseract hoặc các OCR engine khác
    Có thể implement sau nếu cần
    """
    
    def __init__(
        self,
        engine: str = "tesseract",
        model: str = "local-tesseract",
    ):
        self._model = model
        self._engine = engine
    
    @property
    def model(self) -> str:
        return self._model
    
    async def recognize(
        self,
        source_type: ImageSourceType,
        url: str | None = None,
        base64_data: str | None = None,
        file_id: str | None = None,
        prompt: str | None = None,
        language: str | None = None,
    ) -> OCRResponse:
        """Local OCR - placeholder cho implementation sau"""
        
        # TODO: Implement local OCR using Tesseract, EasyOCR, etc.
        raise NotImplementedError(
            "LocalOCRProvider chưa được implement. "
            "Sử dụng MockOCRProvider hoặc MetaOCRProvider."
        )
