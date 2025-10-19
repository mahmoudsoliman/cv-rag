from langchain.schema import Document
from model.CandidateProfile import CandidateProfile

def synth_experience_text(ex):
    parts = []
    parts.append(f"{(ex.title or '').strip()} at {ex.company} ({ex.start} to {ex.end}).".strip())
    if ex.description:
        parts.append(f"Responsibilities: {ex.description}")
    if ex.skills:
        parts.append(f"Tech: {', '.join(ex.skills)}")
    return "\n".join([p for p in parts if p])

def synth_education_text(edu):
    deg = " in ".join([x for x in [edu.degree, edu.field] if x])
    main = f"{deg} at {edu.institution}" if deg else f"{edu.institution}"
    years = f" ({edu.start_year}–{edu.end_year})" if (edu.start_year or edu.end_year) else ""
    return main + years

def build_docs_from_profile(text, candidate_id, profile, pdf_path):
    docs = []
    # if profile.summary:
    #     docs.append(Document(
    #         page_content=profile.summary,
    #         metadata={"candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "summary", "source_file": pdf_path}
    #     ))
    # if profile.skills:
    #     docs.append(Document(
    #         page_content="Skills: " + ", ".join(profile.skills),
    #         metadata={"candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "skills", "skills": ", ".join(profile.skills), "source_file": pdf_path}
    #     ))
    # for ex in profile.experience:
    #     docs.append(Document(
    #         page_content=synth_experience_text(ex),
    #         metadata={
    #             "candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "experience", "company": ex.company,
    #             "title": ex.title, "start": ex.start, "end": ex.end, "source_file": pdf_path
    #         }
    #     ))
    # for edu in profile.education:
    #     docs.append(Document(
    #         page_content=synth_education_text(edu),
    #         metadata={
    #             "candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "education", "institution": edu.institution,
    #             "degree": edu.degree, "field": edu.field, "start_year": edu.start_year,
    #             "end_year": edu.end_year, "source_file": pdf_path
    #         }
    #     ))
    # for cert in profile.certifications or []:
    #     line = f"Certification: {cert.name}" + (f" ({cert.year})" if cert.year else "") + (f", issuer: {cert.issuer}" if cert.issuer else "")
    #     docs.append(Document(
    #         page_content=line,
    #         metadata={"candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "certifications", "name": cert.name, "source_file": pdf_path}
    #     ))

    # Create metadata with simple types only (Chroma requirement)
    metadata = {
        "candidate_id": candidate_id, 
        "candidate_name": profile.full_name,
        "email": profile.email or "",
        "phone": profile.phone or "",
        "location": profile.location or "",
        "summary": profile.summary or "",
        "source_file": pdf_path
    }
    
    # Add skills as a comma-separated string
    if profile.skills:
        metadata["skills"] = ", ".join(profile.skills)
    
    # Add education info (first degree if available)
    if profile.education:
        first_edu = profile.education[0]
        metadata["education_institution"] = first_edu.institution or ""
        metadata["education_degree"] = first_edu.degree or ""
        metadata["education_field"] = first_edu.field or ""
        if first_edu.start_year:
            metadata["education_start_year"] = first_edu.start_year
        if first_edu.end_year:
            metadata["education_end_year"] = first_edu.end_year
    
    # Add experience info (most recent job if available)
    if profile.experience:
        recent_exp = profile.experience[0]
        metadata["latest_company"] = recent_exp.company or ""
        metadata["latest_title"] = recent_exp.title or ""
        metadata["latest_start"] = recent_exp.start or ""
        metadata["latest_end"] = recent_exp.end or ""
    
    docs.append(Document(
        page_content=text,
        metadata=metadata
    ))
    return docs
