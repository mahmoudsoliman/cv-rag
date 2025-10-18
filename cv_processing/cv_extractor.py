import os
from typing import List, Optional, Literal
from dotenv import load_dotenv
from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict
from model.CandidateProfile import (EducationItem, ExperienceItem, LinkItem, CertificationItem, CandidateProfile)



from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()

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


def make_extraction_prompt():
    return f"""You are a precise information extraction assistant for résumés.

        Extract only facts explicitly present in the text. Do not invent.

        Return strictly valid JSON matching the target schema.

        If a field is unknown, omit it or use null.
        """

def build_llm():
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, api_key=os.environ["OPENAI_API_KEY"], temperature=0)

def extract_structured_profile_from_text(resume_text: str) -> CandidateProfile:
    llm = build_llm()

    structured_llm = llm.with_structured_output(CandidateProfile)
    messages = [
        SystemMessage(content=make_extraction_prompt()),
        HumanMessage(f"""Extract the résumé information as a JSON object matching the schema.
            Résumé text:
            {resume_text}
            """)
    ]

    result: CandidateProfile = structured_llm.invoke(messages)
    return result



