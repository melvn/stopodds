from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class AgeBracket(str, Enum):
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_PLUS = "45+"

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    NONBINARY = "Nonbinary"
    PREFER_NOT = "PreferNot"

class Ethnicity(str, Enum):
    # TODO: Define AUS-relevant groups based on requirements
    ANGLO_AUSTRALIAN = "Anglo Australian"
    INDIGENOUS = "Indigenous"
    SOUTH_ASIAN = "South Asian"
    EAST_ASIAN = "East Asian"
    SOUTHEAST_ASIAN = "Southeast Asian"
    MIDDLE_EASTERN = "Middle Eastern"
    AFRICAN = "African"
    EUROPEAN = "European"
    LATIN_AMERICAN = "Latin American"
    OTHER = "Other"
    PREFER_NOT = "PreferNot"

class SkinTone(str, Enum):
    LIGHT = "Light"
    MEDIUM = "Medium"
    DARK = "Dark"
    PREFER_NOT = "PreferNot"

class HeightBracket(str, Enum):
    UNDER_160 = "<160"
    HEIGHT_160_175 = "160-175"
    HEIGHT_175_190 = "175-190"
    OVER_190 = ">190"
    PREFER_NOT = "PreferNot"

class ModelType(str, Enum):
    POISSON = "poisson"
    NEGBIN = "negbin"
    LIGHTGBM = "lightgbm"
    BASELINE = "baseline"

# Pydantic models for API
class SubmissionCreate(BaseModel):
    age_bracket: Optional[AgeBracket] = None
    gender: Optional[Gender] = None
    ethnicity: Optional[Ethnicity] = None
    skin_tone: Optional[SkinTone] = None
    height_bracket: Optional[HeightBracket] = None
    visible_disability: Optional[bool] = None
    concession: Optional[bool] = None
    trips: int = Field(..., ge=1, le=200, description="Number of trips in last 30 days")
    stops: int = Field(..., ge=0, description="Number of times stopped in last 30 days")
    
    @validator('stops')
    def stops_must_not_exceed_trips(cls, v, values):
        if 'trips' in values and v > values['trips']:
            raise ValueError('stops cannot exceed trips')
        return v

class GroupData(BaseModel):
    group_key: str
    n_people: int
    n_trips: int
    n_stops: int
    rate_per_100: float
    irr_vs_ref: Optional[float] = None
    confidence_interval: Optional[List[float]] = None

class OverviewResponse(BaseModel):
    total_submissions: int
    total_trips: int
    total_stops: int
    groups: List[GroupData]

class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    probability: float
    confidence_interval: List[float]
    model_run_id: str
    explanation: List[str]

class MethodsResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    model_type: ModelType
    last_trained: str
    sample_size: int
    metrics: Dict[str, Any]

# Database models (SQLAlchemy)
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid as uuid_lib

Base = declarative_base()

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    age_bracket = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    ethnicity = Column(String, nullable=True)
    skin_tone = Column(String, nullable=True)
    height_bracket = Column(String, nullable=True)
    visible_disability = Column(Boolean, nullable=True)
    concession = Column(Boolean, nullable=True)
    trips = Column(Integer, nullable=False)
    stops = Column(Integer, nullable=False)
    user_agent_hash = Column(Text, nullable=True)

class ModelRun(Base):
    __tablename__ = "model_runs"
    
    run_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model_type = Column(String, nullable=False)
    train_rows = Column(Integer, nullable=False)
    metrics = Column(JSON, nullable=True)
    coeffs = Column(JSON, nullable=True)
    public_snapshot = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

class AggregatePublic(Base):
    __tablename__ = "aggregates_public"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    group_key = Column(String, nullable=False)
    n_people = Column(Integer, nullable=False)
    n_trips = Column(Integer, nullable=False)
    n_stops = Column(Integer, nullable=False)
    rate_per_100 = Column(Float, nullable=False)
    irr_vs_ref = Column(Float, nullable=True)
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    model_run_id = Column(UUID(as_uuid=True), nullable=False)