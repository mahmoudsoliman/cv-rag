from typing import List, Optional, Literal
from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict

class EducationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

class ExperienceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    company: str
    title: Optional[str] = None
    start: Optional[str] = None   # "YYYY-MM" or "YYYY"
    end: Optional[str] = None     # "YYYY-MM", "YYYY", or null
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    highlights: Optional[List[str]] = None

class LinkItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Optional[Literal["linkedin","github","portfolio","other"]] = "other"
    url: str

class CertificationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    year: Optional[int] = None
    issuer: Optional[str] = None

class CandidateProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    links: List[LinkItem] = []
    summary: Optional[str] = None
    skills: List[str] = []         
    education: List[EducationItem] = []
    experience: List[ExperienceItem] = []
    certifications: Optional[List[CertificationItem]] = None