from langchain.schema import Document

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

def build_docs_from_profile(profile, candidate_id, pdf_path):
    docs = []
    if profile.summary:
        docs.append(Document(
            page_content=profile.summary,
            metadata={"candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "summary", "source_file": pdf_path}
        ))
    if profile.skills:
        docs.append(Document(
            page_content="Skills: " + ", ".join(profile.skills),
            metadata={"candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "skills", "skills": ", ".join(profile.skills), "source_file": pdf_path}
        ))
    for ex in profile.experience:
        docs.append(Document(
            page_content=synth_experience_text(ex),
            metadata={
                "candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "experience", "company": ex.company,
                "title": ex.title, "start": ex.start, "end": ex.end, "source_file": pdf_path
            }
        ))
    for edu in profile.education:
        docs.append(Document(
            page_content=synth_education_text(edu),
            metadata={
                "candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "education", "institution": edu.institution,
                "degree": edu.degree, "field": edu.field, "start_year": edu.start_year,
                "end_year": edu.end_year, "source_file": pdf_path
            }
        ))
    for cert in profile.certifications or []:
        line = f"Certification: {cert.name}" + (f" ({cert.year})" if cert.year else "") + (f", issuer: {cert.issuer}" if cert.issuer else "")
        docs.append(Document(
            page_content=line,
            metadata={"candidate_id": candidate_id, "candidate_name": profile.full_name, "section": "certifications", "name": cert.name, "source_file": pdf_path}
        ))
    return docs
