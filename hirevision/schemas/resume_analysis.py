"""
Resume analysis Pydantic schemas for HireVision application
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .base import BaseResponse, TaskStatus, TimestampMixin, UserBaseMixin, FileSchema


class ResumeFileSchema(FileSchema):
    """Schema for resume file uploads"""
    content_type: str = Field(..., description="File content type")
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validate file content type"""
        allowed_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/msword',  # .doc
        ]
        if v not in allowed_types:
            raise ValueError("File must be PDF, DOCX, or DOC format")
        return v


class ResumeAnalysisInputSchema(BaseModel):
    """Schema for resume analysis input"""
    job_description: str = Field(..., min_length=10, max_length=10000, description="Job description text")
    resume_file: Optional[ResumeFileSchema] = Field(None, description="Resume file information")
    
    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v: str) -> str:
        """Validate job description"""
        v = v.strip()
        if not v:
            raise ValueError("Job description cannot be empty")
        return v


class SkillGapSchema(BaseModel):
    """Schema for skill gap information"""
    skill: str = Field(..., description="Missing skill")
    importance: str = Field(..., description="Importance level (high/medium/low)")
    description: Optional[str] = Field(None, description="Description of the skill gap")


class RecommendationSchema(BaseModel):
    """Schema for improvement recommendations"""
    category: str = Field(..., description="Recommendation category")
    recommendation: str = Field(..., description="Specific recommendation")
    priority: str = Field(..., description="Priority level (high/medium/low)")


class ResumeAnalysisOutputSchema(BaseResponse, TimestampMixin, UserBaseMixin):
    """Schema for resume analysis output"""
    id: UUID = Field(..., description="Analysis ID")
    task_status: TaskStatus = Field(..., description="Processing status")
    task_error: Optional[str] = Field(None, description="Error message if failed")
    
    # Analysis results
    ats_score: Optional[int] = Field(None, ge=0, le=100, description="ATS compatibility score")
    score_explanation: Optional[str] = Field(None, description="Explanation of the score")
    strengths: List[str] = Field(default_factory=list, description="Resume strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Resume weaknesses")
    recommendations: List[RecommendationSchema] = Field(default_factory=list, description="Improvement recommendations")
    skills_gap: List[SkillGapSchema] = Field(default_factory=list, description="Missing skills")
    upskilling_suggestions: List[str] = Field(default_factory=list, description="Learning suggestions")
    overall_assessment: Optional[str] = Field(None, description="Overall assessment")
    
    # Input data (for reference)
    job_description: Optional[str] = Field(None, description="Original job description")
    resume_filename: Optional[str] = Field(None, description="Original resume filename")


class ResumeAnalysisListSchema(BaseModel):
    """Schema for list of resume analyses"""
    analyses: List[ResumeAnalysisOutputSchema] = Field(..., description="List of analyses")
    total_count: int = Field(..., ge=0, description="Total number of analyses")


class ResumeAnalysisCreateResponseSchema(BaseResponse):
    """Schema for resume analysis creation response"""
    id: UUID = Field(..., description="Analysis ID")
    task_id: str = Field(..., description="Background task ID")
    message: str = Field(..., description="Status message")
    status_url: Optional[str] = Field(None, description="URL to check status")


class ResumeAnalysisStatusSchema(BaseModel):
    """Schema for resume analysis status"""
    status: TaskStatus = Field(..., description="Current task status")
    error: Optional[str] = Field(None, description="Error message if failed")
    has_results: bool = Field(..., description="Whether results are available")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class ResumeTextExtractionSchema(BaseModel):
    """Schema for extracted resume text"""
    text: str = Field(..., description="Extracted text content")
    page_count: int = Field(..., ge=1, description="Number of pages")
    word_count: int = Field(..., ge=0, description="Word count")
    extraction_method: str = Field(..., description="Method used for extraction")
    warnings: List[str] = Field(default_factory=list, description="Extraction warnings")


class JobDescriptionAnalysisSchema(BaseModel):
    """Schema for job description analysis"""
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    experience_level: Optional[str] = Field(None, description="Required experience level")
    education_requirements: List[str] = Field(default_factory=list, description="Education requirements")
    key_responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    industry: Optional[str] = Field(None, description="Industry sector")
    job_type: Optional[str] = Field(None, description="Job type (full-time, part-time, etc.)")


class ResumeComparisonSchema(BaseModel):
    """Schema for comparing multiple resumes"""
    resume_ids: List[UUID] = Field(..., min_length=2, max_length=10, description="Resume IDs to compare")
    job_description: str = Field(..., min_length=10, description="Job description for comparison")
    comparison_criteria: List[str] = Field(default_factory=list, description="Specific criteria to focus on")


class ResumeComparisonResultSchema(BaseModel):
    """Schema for resume comparison results"""
    comparison_id: UUID = Field(..., description="Comparison ID")
    rankings: List[Dict[str, Any]] = Field(..., description="Ranked resumes with scores")
    detailed_comparison: Dict[str, Any] = Field(..., description="Detailed comparison data")
    recommendations: List[str] = Field(default_factory=list, description="Comparison insights") 