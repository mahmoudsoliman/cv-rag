from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import sys

# Add the current directory to Python path to import modules
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_processing.query_executor import execute_query
from query_processing.answer_generator import synthesize_answer_from_docs
from db.sql_store import init_db
from db.chroma_store import store
from model.CandidateProfile import CandidateProfile, EducationItem as Education, ExperienceItem as Experience, LinkItem as Link, CertificationItem as Certification

# Initialize FastAPI app
app = FastAPI(
    title="CV Search API",
    description="API for searching and querying CV/resume data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class AskRequest(BaseModel):
    question: str
    
class SnippetMetadata(BaseModel):
    section: Optional[str] = None
    candidate_id: Optional[str] = None
    candidate_name: Optional[str] = None
    company: Optional[str] = None
    institution: Optional[str] = None
    source_file: Optional[str] = None

class SnippetScore(BaseModel):
    distance: Optional[float] = None
    similarity: Optional[float] = None

class Snippet(BaseModel):
    text: str
    metadata: SnippetMetadata
    score: Optional[SnippetScore] = None

class AskResponse(BaseModel):
    ok: bool
    sections: List[str]
    facts: List[CandidateProfile]
    docs: List[Snippet]
    answer: Optional[str] = None
    why: Optional[str] = None

# Initialize database and vector store
con = init_db("data/candidates.db")
vs = store

@app.get("/")
async def root():
    return {"message": "CV Search API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Execute a query against the CV database and return structured results
    """
    try:
        # Execute the query using the existing query executor
        result = execute_query(con, vs, request.question)
        
        # Generate answer using the answer generator
        answer = synthesize_answer_from_docs(result, request.question)
        
        # Add the answer to the result
        result["answer"] = answer
        
        # Convert the result to the expected format
        # Transform docs from tuples to Snippet objects
        docs = []
        for doc_tuple in result.get("docs", []):
            if isinstance(doc_tuple, tuple) and len(doc_tuple) == 2:
                doc, score = doc_tuple
                snippet = Snippet(
                    text=doc.page_content,
                    metadata=SnippetMetadata(
                        section=doc.metadata.get("section"),
                        candidate_id=doc.metadata.get("candidate_id"),
                        candidate_name=doc.metadata.get("candidate_name"),
                        company=doc.metadata.get("company"),
                        institution=doc.metadata.get("institution"),
                        source_file=doc.metadata.get("source_file")
                    ),
                    score=SnippetScore(
                        distance=score,
                        similarity=1 - score if score is not None else None
                    )
                )
                docs.append(snippet)
        
        # Convert CandidateProfile objects to dictionaries
        facts = []
        for fact in result.get("facts", []):
            if hasattr(fact, 'model_dump'):
                # Convert Pydantic model to dictionary
                fact_dict = fact.model_dump()
                facts.append(fact_dict)
            elif hasattr(fact, '__dict__'):
                # Convert regular object to dictionary
                fact_dict = {
                    "full_name": getattr(fact, 'full_name', None),
                    "email": getattr(fact, 'email', None),
                    "phone": getattr(fact, 'phone', None),
                    "location": getattr(fact, 'location', None),
                    "links": [{"type": getattr(link, 'type', None), "url": getattr(link, 'url', None)} for link in getattr(fact, 'links', [])],
                    "summary": getattr(fact, 'summary', None),
                    "skills": getattr(fact, 'skills', []),
                    "education": [{"institution": getattr(edu, 'institution', None), "degree": getattr(edu, 'degree', None), "field": getattr(edu, 'field', None), "start_year": getattr(edu, 'start_year', None), "end_year": getattr(edu, 'end_year', None)} for edu in getattr(fact, 'education', [])],
                    "experience": [{"company": getattr(exp, 'company', None), "title": getattr(exp, 'title', None), "start": getattr(exp, 'start', None), "end": getattr(exp, 'end', None), "description": getattr(exp, 'description', None)} for exp in getattr(fact, 'experience', [])],
                    "certifications": [{"name": getattr(cert, 'name', None), "year": getattr(cert, 'year', None), "issuer": getattr(cert, 'issuer', None)} for cert in getattr(fact, 'certifications', [])] if getattr(fact, 'certifications', None) else None
                }
                facts.append(fact_dict)
            else:
                facts.append(fact)
        
        response = AskResponse(
            ok=result.get("ok", False),
            sections=result.get("sections", []),
            facts=facts,
            docs=docs,
            answer=result.get("answer"),
            why=result.get("why")
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
