from typing import Optional
from query_processing.query_router import route_query_llm
from model.QueryRoute import QueryRoute
from db.chroma_store import store
from db.sql_store import init_db, resolve_candidate, load_candidate_profiles, ids_by_company, ids_by_institution, ids_by_skills, id_by_name, companies_for, institutions_for

# ---- Helpers ----

def vsearch(vs, query: str, k=8, cand_ids: Optional[list[str]] = None):
    clauses = []
    if cand_ids:
        clauses.append({"candidate_id": {"$in": cand_ids}})

    filter = None
    if len(clauses) == 1:
        filter = clauses[0]
    elif len(clauses) > 1:
        filter = {"$and": clauses}
    return vs.similarity_search_with_score(query, k=k, filter=filter or None)

def experience_text_blocks(vs, candidate_id: str, k: int = 8):
    return vsearch(vs, "summarize the candidate's work experience", k=k,
                   cand_ids=[candidate_id])

def profile_summary_blocks(vs, candidate_id: str, k: int = 8):
    return vsearch(vs, "overall resume summary", k=k,
                   cand_ids=[candidate_id])

# ---- Executor ----

def execute_candidate_query(con, vs, route: QueryRoute, user_query: str):

    cid_name = None
    if route.candidate_name:
        cid_name = resolve_candidate(con, route.candidate_name)

    if not cid_name:
        return {"facts": [], "docs": [], "why": "candidate_not_found", "message": "Could not resolve candidate name. Check spelling."}

    candidate_id, canonical_name = cid_name
    
    default_sections = ["experience","summary","education","skills"]
    sections = route.target_sections or default_sections
    
    profiles = load_candidate_profiles(con, [candidate_id])

    result = {
        "sections": [],
        "facts": [],
        "docs": []
    }

    if route.need_summarization:
        docs = profile_summary_blocks(vs, candidate_id, k=8)
        result["facts"].extend(profiles)
        result["docs"].extend(docs)
        result["sections"] = default_sections
        return result

    if "experience" in sections:
        comps = companies_for(con, candidate_id)
        result["facts"].extend(profiles)
        result["companies"] = comps
        result["sections"].append("experience")

    if "education" in sections:
        insts = institutions_for(con, candidate_id)
        result["institutions"] = insts
        result["sections"].append("education")
        result["facts"].extend(profiles)

    if "skills" in sections:
        result["sections"].append("skills")
        result["facts"].extend(profiles)

    return result

def execute_query(con, vs, q: str):
    route = route_query_llm(q)

    # fallback if router abstains or low confidence
    if route.abstain or route.confidence < 0.5:
        route.mode = "vector"
        route.target_sections = ["experience", "summary", "skills", "education"]

    sections = route.target_sections or ["experience", "summary", "skills", "education"]

    if route.candidate_name:
        return execute_candidate_query(con, vs, route, q)

    if route.mode == "vector":
        docs = vsearch(vs, q, k=8)
        result = {"sections": sections, "facts": [], "docs": docs}
        return result

    if route.mode == "hybrid":
        # Build shortlist from precise slots (only those provided)
        ids = set()
        if getattr(route, "skills", None):
            ids |= set(ids_by_skills(con, route.skills))
        if route.company:
            ids |= set(ids_by_company(con, route.company))
        if route.institution:
            ids |= set(ids_by_institution(con, route.institution))
        if route.candidate_name:
            cid = id_by_name(con, route.candidate_name)
            if cid:
                ids.add(cid)

        profiles = load_candidate_profiles(con, list(ids)) if ids else []
        docs = vsearch(vs, q, k=8)
        result = {"sections": sections, "facts": profiles, "docs": docs}
        return result