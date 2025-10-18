from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict

class QueryRoute(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Literal["sql","vector","hybrid"]
    target_sections: List[Literal["experience","education","skills","summary","certifications"]]
    skills: List[str] = None
    company: Optional[str] = None
    institution: Optional[str] = None
    candidate_name: Optional[str] = None
    need_summarization: bool = False
    # meta
    confidence: float = 0.7
    abstain: bool = False
