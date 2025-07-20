"""
Resume builder Pydantic schemas for HireVision application
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from pydantic.networks import HttpUrl

from .base import BaseResponse, TaskStatus, TimestampMixin, UserBaseMixin


class EducationSchema(BaseModel):
    """Schema for education entries"""
    degree: str = Field(..., description="Degree name")
    institution: str = Field(..., description="Educational institution")
    location: Optional[str] = Field(None, description="Institution location")
    start_date: str = Field(..., description="Start date")
    end_date: Optional[str] = Field(None, description="End date (or 'Present')")
    gpa: Optional[str] = Field(None, description="GPA or grade")
    relevant_courses: List[str] = Field(default_factory=list, description="Relevant coursework")
    honors: List[str] = Field(default_factory=list, description="Academic honors")


class ExperienceSchema(BaseModel):
    """Schema for work experience entries"""
    position: str = Field(..., description="Job position/title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    start_date: str = Field(..., description="Start date")
    end_date: Optional[str] = Field(None, description="End date (or 'Present')")
    description: List[str] = Field(default_factory=list, description="Job responsibilities and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")


class ProjectSchema(BaseModel):
    """Schema for project entries"""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    duration: Optional[str] = Field(None, description="Project duration")
    url: Optional[HttpUrl] = Field(None, description="Project URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub repository URL")
    highlights: List[str] = Field(default_factory=list, description="Project highlights")
    role: Optional[str] = Field(None, description="Your role in the project")


class SkillsSchema(BaseModel):
    """Schema for skills section"""
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries")
    tools: List[str] = Field(default_factory=list, description="Tools and technologies")
    databases: List[str] = Field(default_factory=list, description="Database technologies")
    cloud_platforms: List[str] = Field(default_factory=list, description="Cloud platforms")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: List[str] = Field(default_factory=list, description="Spoken languages")


class ResearchPaperSchema(BaseModel):
    """Schema for research papers"""
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    publication: Optional[str] = Field(None, description="Publication venue")
    date: Optional[str] = Field(None, description="Publication date")
    url: Optional[HttpUrl] = Field(None, description="Paper URL")
    abstract: Optional[str] = Field(None, description="Paper abstract")


class AchievementSchema(BaseModel):
    """Schema for achievements and awards"""
    title: str = Field(..., description="Achievement title")
    description: Optional[str] = Field(None, description="Achievement description")
    date: Optional[str] = Field(None, description="Achievement date")
    issuer: Optional[str] = Field(None, description="Issuing organization")


class ContactInfoSchema(BaseModel):
    """Schema for contact information"""
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    website: Optional[HttpUrl] = Field(None, description="Personal website URL")
    location: Optional[str] = Field(None, description="Current location")


class ResumeBuilderInputSchema(BaseModel):
    """Schema for resume builder input"""
    contact_info: ContactInfoSchema = Field(..., description="Contact information")
    education: List[EducationSchema] = Field(..., min_length=1, description="Education history")
    experience: List[ExperienceSchema] = Field(default_factory=list, description="Work experience")
    projects: List[ProjectSchema] = Field(..., min_length=1, description="Project portfolio")
    skills: SkillsSchema = Field(..., description="Skills and technologies")
    research_papers: List[ResearchPaperSchema] = Field(default_factory=list, description="Research publications")
    achievements: List[AchievementSchema] = Field(default_factory=list, description="Awards and achievements")
    others: List[str] = Field(default_factory=list, description="Additional information")
    
    # Customization options
    template: Optional[str] = Field("professional", description="Resume template style")
    color_scheme: Optional[str] = Field("blue", description="Color scheme")
    font_size: Optional[int] = Field(11, ge=9, le=14, description="Font size")
    include_summary: bool = Field(True, description="Include professional summary")
    summary_text: Optional[str] = Field(None, description="Custom summary text")


class ResumeBuilderOutputSchema(BaseResponse, TimestampMixin, UserBaseMixin):
    """Schema for resume builder output"""
    id: UUID = Field(..., description="Resume ID")
    task_status: TaskStatus = Field(..., description="Processing status")
    task_error: Optional[str] = Field(None, description="Error message if failed")
    
    # Generated content
    latex_content: Optional[str] = Field(None, description="Generated LaTeX content")
    pdf_url: Optional[str] = Field(None, description="Generated PDF URL")
    preview_url: Optional[str] = Field(None, description="Preview image URL")
    
    # Metadata
    template_used: Optional[str] = Field(None, description="Template used")
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")
    word_count: Optional[int] = Field(None, description="Approximate word count")
    page_count: Optional[int] = Field(None, description="Number of pages")
    
    # Input data (for reference)
    contact_info: Optional[ContactInfoSchema] = Field(None, description="Original contact info")
    input_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of input data")


class ResumeBuilderListSchema(BaseModel):
    """Schema for list of resumes"""
    resumes: List[ResumeBuilderOutputSchema] = Field(..., description="List of resumes")
    total_count: int = Field(..., ge=0, description="Total number of resumes")


class ResumeBuilderCreateResponseSchema(BaseResponse):
    """Schema for resume builder creation response"""
    id: UUID = Field(..., description="Resume ID")
    task_id: str = Field(..., description="Background task ID")
    message: str = Field(..., description="Status message")
    status_url: Optional[str] = Field(None, description="URL to check status")


class ResumeBuilderStatusSchema(BaseModel):
    """Schema for resume builder status"""
    status: TaskStatus = Field(..., description="Current task status")
    error: Optional[str] = Field(None, description="Error message if failed")
    has_results: bool = Field(..., description="Whether results are available")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class ResumeTemplateSchema(BaseModel):
    """Schema for resume templates"""
    name: str = Field(..., description="Template name")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Template description")
    preview_url: Optional[str] = Field(None, description="Template preview image")
    category: str = Field(..., description="Template category")
    features: List[str] = Field(default_factory=list, description="Template features")
    suitable_for: List[str] = Field(default_factory=list, description="Suitable for roles/industries")


class ResumeAnalyticsSchema(BaseModel):
    """Schema for resume analytics"""
    total_resumes: int = Field(..., ge=0, description="Total resumes generated")
    popular_templates: List[Dict[str, Any]] = Field(default_factory=list, description="Most used templates")
    average_generation_time: Optional[float] = Field(None, description="Average generation time")
    success_rate: Optional[float] = Field(None, ge=0, le=100, description="Success rate percentage")
    user_satisfaction: Optional[float] = Field(None, ge=0, le=5, description="Average user rating")


class ResumeCustomizationSchema(BaseModel):
    """Schema for resume customization options"""
    template: str = Field(..., description="Template name")
    color_scheme: str = Field(..., description="Color scheme")
    font_family: str = Field(..., description="Font family")
    font_size: int = Field(..., ge=8, le=16, description="Font size")
    margins: Dict[str, float] = Field(..., description="Page margins")
    section_order: List[str] = Field(..., description="Order of resume sections")
    include_photo: bool = Field(False, description="Include profile photo")
    include_qr_code: bool = Field(False, description="Include QR code") 