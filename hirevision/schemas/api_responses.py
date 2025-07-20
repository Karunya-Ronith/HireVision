"""
API response schemas for HireVision application
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .base import BaseResponse, TaskStatus, ValidationError


class SuccessResponse(BaseResponse):
    """Generic success response"""
    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class ErrorResponse(BaseResponse):
    """Generic error response"""
    success: bool = Field(False, description="Success indicator")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    validation_errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")


class TaskStatusResponse(BaseResponse):
    """Task status response"""
    task_id: str = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Current task status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")
    result_url: Optional[str] = Field(None, description="URL to get results")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class ListResponse(BaseResponse):
    """Generic list response with pagination"""
    items: List[Dict[str, Any]] = Field(..., description="List items")
    total_count: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_previous: bool = Field(..., description="Whether there's a previous page")


class HealthCheckResponse(BaseResponse):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Response timestamp")
    version: Optional[str] = Field(None, description="Application version")
    database: str = Field(..., description="Database status")
    redis: Optional[str] = Field(None, description="Redis status")
    openai: Optional[str] = Field(None, description="OpenAI API status")


class AuthenticationResponse(BaseResponse):
    """Authentication response"""
    access_token: Optional[str] = Field(None, description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    user_id: Optional[UUID] = Field(None, description="User ID")
    username: Optional[str] = Field(None, description="Username")
    email: Optional[str] = Field(None, description="Email address")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")


class FileUploadResponse(BaseResponse):
    """File upload response"""
    file_id: str = Field(..., description="Uploaded file ID")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="File content type")
    upload_url: Optional[str] = Field(None, description="File access URL")
    checksum: Optional[str] = Field(None, description="File checksum")


class ValidationResponse(BaseResponse):
    """Validation response"""
    is_valid: bool = Field(..., description="Whether the data is valid")
    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class BatchOperationResponse(BaseResponse):
    """Batch operation response"""
    total_items: int = Field(..., ge=0, description="Total items processed")
    successful_items: int = Field(..., ge=0, description="Successfully processed items")
    failed_items: int = Field(..., ge=0, description="Failed items")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errors for failed items")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Results for successful items")


class SearchResponse(BaseResponse):
    """Search response"""
    query: str = Field(..., description="Search query")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_count: int = Field(..., ge=0, description="Total number of results")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    search_time: Optional[float] = Field(None, description="Search time in seconds")
    suggestions: List[str] = Field(default_factory=list, description="Search suggestions")


class ConfigResponse(BaseResponse):
    """Configuration response"""
    settings: Dict[str, Any] = Field(..., description="Configuration settings")
    features: Dict[str, bool] = Field(..., description="Feature flags")
    limits: Dict[str, int] = Field(..., description="System limits")
    version: str = Field(..., description="Configuration version")


class SystemInfoResponse(BaseResponse):
    """System information response"""
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment (dev/staging/prod)")
    uptime: str = Field(..., description="System uptime")
    memory_usage: Optional[Dict[str, Any]] = Field(None, description="Memory usage statistics")
    database_info: Optional[Dict[str, Any]] = Field(None, description="Database information")


class NotificationResponse(BaseResponse):
    """Notification response"""
    notification_id: str = Field(..., description="Notification ID")
    type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    priority: str = Field(..., description="Notification priority")
    read: bool = Field(False, description="Whether notification is read")
    created_at: str = Field(..., description="Creation timestamp")


class StatisticsResponse(BaseResponse):
    """Statistics response"""
    metric_name: str = Field(..., description="Metric name")
    value: Union[int, float] = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    timestamp: str = Field(..., description="Metric timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ExportResponse(BaseResponse):
    """Export response"""
    export_id: str = Field(..., description="Export job ID")
    format: str = Field(..., description="Export format")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    created_at: str = Field(..., description="Export creation time")
    expires_at: Optional[str] = Field(None, description="Download expiration time")


class WebhookResponse(BaseResponse):
    """Webhook response"""
    webhook_id: str = Field(..., description="Webhook ID")
    event_type: str = Field(..., description="Event type")
    payload: Dict[str, Any] = Field(..., description="Webhook payload")
    timestamp: str = Field(..., description="Event timestamp")
    signature: Optional[str] = Field(None, description="Webhook signature")


# Response type unions for different scenarios
APIResponse = Union[SuccessResponse, ErrorResponse]
TaskResponse = Union[TaskStatusResponse, ErrorResponse]
ListResponseType = Union[ListResponse, ErrorResponse]
AuthResponse = Union[AuthenticationResponse, ErrorResponse] 