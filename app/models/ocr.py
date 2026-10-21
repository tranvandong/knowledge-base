# OCR Models

from enum import Enum
from typing import Literal, Any

from pydantic import BaseModel, Field, field_validator


class ImageSourceType(str, Enum):
    """Loại nguồn hình ảnh OCR"""
    URL = "url"           # Public URL (http/https)
    BASE64 = "base64"     # Base64 data URL
    FILE_ID = "file_id"   # Uploaded file ID


class OCRImageSource(BaseModel):
    """Nguồn hình ảnh cho OCR - hỗ trợ 3 loại"""
    
    source_type: ImageSourceType = Field(
        description="Loại nguồn hình ảnh: url, base64, hoặc file_id"
    )
    
    # Một trong các trường sau sẽ được sử dụng tùy thuộc vào source_type
    url: str | None = Field(
        default=None,
        description="URL đầy đủ của hình ảnh (http/https)"
    )
    
    base64_data: str | None = Field(
        default=None,
        description="Image bytes dạng Base64 (data:image/...;base64,...)"
    )
    
    file_id: str | None = Field(
        default=None,
        description="File ID từ Files API"
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str | None, info) -> str | None:
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError("URL phải bắt đầu bằng http:// hoặc https://")
        return v

    @field_validator('base64_data')
    @classmethod
    def validate_base64(cls, v: str | None, info) -> str | None:
        if v is not None:
            # Kiểm tra format data URL
            if not v.startswith('data:image/'):
                raise ValueError("Base64 data phải bắt đầu bằng 'data:image/'")
        return v


class OCRRequest(BaseModel):
    """Request body cho OCR endpoint"""
    
    source_type: ImageSourceType = Field(
        description="Loại nguồn hình ảnh: url, base64, hoặc file_id"
    )
    
    # Các trường option tùy thuộc source_type
    url: str | None = Field(
        default=None,
        description="URL đầy đủ của hình ảnh"
    )
    
    base64_data: str | None = Field(
        default=None,
        description="Image bytes dạng Base64 (data:image/...;base64,...)"
    )
    
    file_id: str | None = Field(
        default=None,
        description="File ID từ Files API"
    )
    
    language: str | None = Field(
        default=None,
        description="Ngôn ngữ của văn bản (ví dụ: 'vi', 'en', 'ja')"
    )
    
    prompt: str | None = Field(
        default=None,
        description="Prompt bổ sung để hướng dẫn OCR"
    )

    def validate_source(self) -> None:
        """Validate rằng đã cung cấp đúng trường cho source_type"""
        if self.source_type == ImageSourceType.URL and not self.url:
            raise ValueError("URL là bắt buộc khi source_type là 'url'")
        
        if self.source_type == ImageSourceType.BASE64 and not self.base64_data:
            raise ValueError("base64_data là bắt buộc khi source_type là 'base64'")
        
        if self.source_type == ImageSourceType.FILE_ID and not self.file_id:
            raise ValueError("file_id là bắt buộc khi source_type là 'file_id'")


class OCRResultItem(BaseModel):
    """Một kết quả OCR (có thể có nhiều text blocks)"""
    
    text: str = Field(description="Văn bản được nhận diện")
    confidence: float | None = Field(
        default=None,
        description="Độ tin cậy của kết quả (0-1)",
        ge=0,
        le=1
    )
    bounding_box: dict[str, int] | None = Field(
        default=None,
        description="Vị trí bounding box (x, y, width, height)"
    )


class OCRResponse(BaseModel):
    """Response body cho OCR endpoint"""
    
    success: bool = Field(description="Trạng thái thành công")
    texts: list[OCRResultItem] = Field(
        default_factory=list,
        description="Danh sách các đoạn văn bản nhận diện được"
    )
    full_text: str = Field(
        description="Toàn bộ văn bản nối lại"
    )
    language_detected: str | None = Field(
        default=None,
        description="Ngôn ngữ được phát hiện trong ảnh"
    )
    model: str = Field(
        description="Model OCR được sử dụng"
    )
    source_type: ImageSourceType = Field(
        description="Loại nguồn hình ảnh đã sử dụng"
    )
    error: str | None = Field(
        default=None,
        description="Thông báo lỗi nếu có"
    )


class OCRToolInput(BaseModel):
    """Input model cho OCR tool"""
    
    source_type: Literal["url", "base64", "file_id"] = Field(
        description="Loại nguồn hình ảnh: url, base64, hoặc file_id"
    )
    
    url: str | None = Field(
        default=None,
        description="URL đầy đủ của hình ảnh"
    )
    
    base64_data: str | None = Field(
        default=None,
        description="Image bytes dạng Base64"
    )
    
    file_id: str | None = Field(
        default=None,
        description="File ID từ Files API"
    )
    
    prompt: str | None = Field(
        default=None,
        description="Prompt bổ sung để hướng dẫn OCR"
    )
