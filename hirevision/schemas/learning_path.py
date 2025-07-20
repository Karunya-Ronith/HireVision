"""
Learning path analysis Pydantic schemas for HireVision application
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .base import BaseResponse, TaskStatus, TimestampMixin, UserBaseMixin


class LearningResourceSchema(BaseModel):
    """Schema for learning resources"""
    type: str = Field(..., description="Resource type (course/book/project/tool)")
    name: str = Field(..., description="Resource name")
    url: Optional[str] = Field(None, description="Resource URL or placeholder")
    description: str = Field(..., description="Why this resource is recommended")
    difficulty: str = Field(..., description="Difficulty level (beginner/intermediate/advanced)")
    verified: bool = Field(False, description="Whether the resource is verified to exist")
    duration: Optional[str] = Field(None, description="Estimated time to complete")
    cost: Optional[str] = Field(None, description="Cost information (free/paid/$$)")


class LearningProjectSchema(BaseModel):
    """Schema for learning projects"""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    skills_practiced: List[str] = Field(default_factory=list, description="Skills practiced in project")
    github_template: Optional[str] = Field(None, description="GitHub template URL if available")
    difficulty: str = Field(..., description="Project difficulty level")
    estimated_duration: Optional[str] = Field(None, description="Time to complete")


class LearningPhaseSchema(BaseModel):
    """Schema for learning phases"""
    phase: str = Field(..., description="Phase name (e.g., Phase 1: Foundation)")
    duration: str = Field(..., description="Estimated phase duration")
    description: str = Field(..., description="Detailed phase description")
    skills_to_learn: List[str] = Field(default_factory=list, description="Skills to learn in this phase")
    resources: List[LearningResourceSchema] = Field(default_factory=list, description="Learning resources")
    projects: List[LearningProjectSchema] = Field(default_factory=list, description="Practical projects")
    milestones: List[str] = Field(default_factory=list, description="Phase milestones")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for this phase")


class LearningPathInputSchema(BaseModel):
    """Schema for learning path analysis input"""
    current_skills: str = Field(..., min_length=10, max_length=5000, description="Current skills and experience")
    dream_role: str = Field(..., min_length=5, max_length=200, description="Target dream role")
    experience_level: Optional[str] = Field(None, description="Current experience level")
    preferred_learning_style: Optional[str] = Field(None, description="Preferred learning style")
    time_commitment: Optional[str] = Field(None, description="Available time per week")
    budget: Optional[str] = Field(None, description="Budget for learning resources")


class LearningPathOutputSchema(BaseResponse, TimestampMixin, UserBaseMixin):
    """Schema for learning path analysis output"""
    id: UUID = Field(..., description="Learning path ID")
    task_status: TaskStatus = Field(..., description="Processing status")
    task_error: Optional[str] = Field(None, description="Error message if failed")
    
    # Analysis results
    role_analysis: Optional[str] = Field(None, description="Analysis of the dream role")
    skills_gap: List[str] = Field(default_factory=list, description="Missing skills")
    learning_path_data: List[LearningPhaseSchema] = Field(default_factory=list, description="Structured learning path")
    timeline: Optional[str] = Field(None, description="Overall timeline and roadmap")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics and goals")
    career_advice: Optional[str] = Field(None, description="General career advice")
    networking_tips: List[str] = Field(default_factory=list, description="Networking and community tips")
    
    # Metadata
    total_estimated_duration: Optional[str] = Field(None, description="Total estimated time")
    difficulty_level: Optional[str] = Field(None, description="Overall difficulty assessment")
    confidence_score: Optional[int] = Field(None, ge=0, le=100, description="Confidence in recommendations")
    
    # Input data (for reference)
    current_skills: Optional[str] = Field(None, description="Original skills input")
    dream_role: Optional[str] = Field(None, description="Original dream role")


class LearningPathListSchema(BaseModel):
    """Schema for list of learning paths"""
    learning_paths: List[LearningPathOutputSchema] = Field(..., description="List of learning paths")
    total_count: int = Field(..., ge=0, description="Total number of learning paths")


class LearningPathCreateResponseSchema(BaseResponse):
    """Schema for learning path creation response"""
    id: UUID = Field(..., description="Learning path ID")
    task_id: str = Field(..., description="Background task ID")
    message: str = Field(..., description="Status message")
    status_url: Optional[str] = Field(None, description="URL to check status")


class LearningPathStatusSchema(BaseModel):
    """Schema for learning path analysis status"""
    status: TaskStatus = Field(..., description="Current task status")
    error: Optional[str] = Field(None, description="Error message if failed")
    has_results: bool = Field(..., description="Whether results are available")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class SkillAssessmentSchema(BaseModel):
    """Schema for individual skill assessment"""
    skill: str = Field(..., description="Skill name")
    current_level: str = Field(..., description="Current proficiency level")
    target_level: str = Field(..., description="Target proficiency level")
    gap_analysis: str = Field(..., description="Analysis of the skill gap")
    priority: str = Field(..., description="Learning priority (high/medium/low)")
    recommended_resources: List[LearningResourceSchema] = Field(default_factory=list, description="Skill-specific resources")


class CareerPathRecommendationSchema(BaseModel):
    """Schema for career path recommendations"""
    alternative_roles: List[str] = Field(default_factory=list, description="Alternative career roles to consider")
    stepping_stone_roles: List[str] = Field(default_factory=list, description="Intermediate roles toward dream role")
    industry_insights: List[str] = Field(default_factory=list, description="Industry-specific insights")
    salary_expectations: Optional[Dict[str, Any]] = Field(None, description="Salary range information")
    job_market_analysis: Optional[str] = Field(None, description="Current job market analysis")


class LearningPathUpdateSchema(BaseModel):
    """Schema for updating learning path progress"""
    completed_phases: List[str] = Field(default_factory=list, description="Completed learning phases")
    current_phase: Optional[str] = Field(None, description="Currently active phase")
    skills_acquired: List[str] = Field(default_factory=list, description="Newly acquired skills")
    feedback: Optional[str] = Field(None, description="User feedback on the learning path")
    adjustment_requests: List[str] = Field(default_factory=list, description="Requested adjustments")


class LearningPathAnalyticsSchema(BaseModel):
    """Schema for learning path analytics"""
    total_users: int = Field(..., ge=0, description="Total users with learning paths")
    popular_roles: List[Dict[str, Any]] = Field(default_factory=list, description="Most popular dream roles")
    common_skills_gaps: List[Dict[str, Any]] = Field(default_factory=list, description="Most common skill gaps")
    average_completion_time: Optional[str] = Field(None, description="Average path completion time")
    success_rate: Optional[float] = Field(None, ge=0, le=100, description="Success rate percentage") 