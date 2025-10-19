import sqlite3, uuid
from rapidfuzz import process, fuzz
from typing import Optional, Tuple, Iterable, List, Dict
from model.CandidateProfile import CandidateProfile, EducationItem, ExperienceItem, LinkItem, CertificationItem

def init_db(db_path="./data/candidates.db"):
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys=ON;")
    return con

def upsert_candidate(con, candidate_id: str, profile, source_file: str | None):
    con.execute("""
      INSERT INTO candidates (id, full_name, email, phone, location, summary, source_file)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET
        full_name=excluded.full_name,
        email=excluded.email,
        phone=excluded.phone,
        location=excluded.location,
        summary=excluded.summary,
        source_file=COALESCE(excluded.source_file, candidates.source_file)
    """, (
        candidate_id,
        profile.full_name,
        profile.email,
        profile.phone,
        profile.location,
        profile.summary,
        source_file
    ))

def insert_links(con, candidate_id: str, links):
    for link in links or []:
        con.execute("INSERT OR IGNORE INTO links(candidate_id, type, url) VALUES (?,?,?)",
                    (candidate_id, link.type or "other", link.url))

def insert_education(con, candidate_id: str, items):
    for ed in items or []:
        con.execute("""
          INSERT OR IGNORE INTO education(candidate_id, institution, degree, field, start_year, end_year)
          VALUES (?,?,?,?,?,?)
        """, (candidate_id, ed.institution, ed.degree, ed.field, ed.start_year, ed.end_year))

def insert_experience(con, candidate_id: str, items):
    for ex in items or []:
        con.execute("""
          INSERT OR IGNORE INTO experience(candidate_id, company, title, start, end, description)
          VALUES (?,?,?,?,?,?)
        """, (candidate_id, ex.company, ex.title, ex.start, ex.end, ex.description))

def insert_skills(con, candidate_id: str, skills: list[str]):
    for s in skills or []:
        con.execute("INSERT OR IGNORE INTO skills(candidate_id, skill) VALUES (?,?)",
                    (candidate_id, s))

def insert_certifications(con, candidate_id: str, certs):
    for c in certs or []:
        con.execute("""
          INSERT OR IGNORE INTO certifications(candidate_id, name, year, issuer)
          VALUES (?,?,?,?)
        """, (candidate_id, c.name, c.year, c.issuer))

def store_profile(db_path: str, profile, source_file: str | None = None, candidate_id: str | None = None) -> str:
    candidate_id = candidate_id or str(uuid.uuid4())
    con = init_db(db_path)
    try:
        with con:
            upsert_candidate(con, candidate_id, profile, source_file)
            insert_links(con, candidate_id, profile.links)
            insert_education(con, candidate_id, profile.education)
            insert_experience(con, candidate_id, profile.experience)
            insert_skills(con, candidate_id, profile.skills)
            insert_certifications(con, candidate_id, profile.certifications)
    finally:
        con.close()
    return candidate_id

def resolve_candidate(con: sqlite3.Connection, name_query: str, max_candidates: int = 20) -> Optional[Tuple[str, str]]:
    q = name_query.strip().lower()

    # 1) LIKE shortlist
    rows = con.execute(
        """
        SELECT id, full_name
        FROM candidates
        WHERE lower(full_name) LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (f"%{q}%", max_candidates)
    ).fetchall()
    
    if not rows:
        return None
    
    
    if process and fuzz:
        choices = [r[1] for r in rows]
        best = process.extractOne(name_query, choices, scorer=fuzz.token_set_ratio)
        if best:
            best_name, _score, idx = best
            return rows[idx][0], best_name

    return rows[0][0], rows[0][1]


def _ph(n: int) -> str:
    return ",".join("?" for _ in range(n))

def _norm(s: Optional[str]) -> Optional[str]:
    return s.lower().strip() if isinstance(s, str) else None

def load_candidate_profiles(con: sqlite3.Connection, candidate_ids: List[str]) -> List[CandidateProfile]:
    """
    Batch load complete CandidateProfile objects for the given candidate_ids.
    Runs one SELECT per table and assembles Pydantic objects.
    """
    if not candidate_ids:
        return []

    ph = _ph(len(candidate_ids))

    # --- Base candidates ---
    base_rows = con.execute(
        f"""
        SELECT id, full_name, email, phone, location, summary, source_file
        FROM candidates
        WHERE id IN ({ph})
        """,
        candidate_ids,
    ).fetchall()
    # id -> CandidateProfile (partially filled)
    by_id: Dict[str, CandidateProfile] = {}
    for cid, full_name, email, phone, location, summary, source_file in base_rows:
        by_id[cid] = CandidateProfile(
            full_name=full_name,
            email=email,
            phone=phone,
            location=location,
            links=[],
            summary=summary,
            skills=[],
            education=[],
            experience=[],
            certifications=[]
        )
    if not by_id:
        return []

    # --- Links ---
    rows = con.execute(
        f"""
        SELECT candidate_id, COALESCE(type,'other') as type, url
        FROM links
        WHERE candidate_id IN ({ph})
        ORDER BY id
        """,
        candidate_ids,
    ).fetchall()
    for cid, typ, url in rows:
        if cid in by_id:
            by_id[cid].links.append(LinkItem(type=typ, url=url))

    # --- Education (most recent first) ---
    rows = con.execute(
        f"""
        SELECT candidate_id, institution, degree, field, start_year, end_year
        FROM education
        WHERE candidate_id IN ({ph})
        ORDER BY COALESCE(end_year, start_year) DESC, institution
        """,
        candidate_ids,
    ).fetchall()
    for cid, inst, degree, field, sy, ey in rows:
        if cid in by_id:
            by_id[cid].education.append(EducationItem(
                institution=inst, degree=degree, field=field,
                start_year=sy, end_year=ey
            ))

    # --- Experience (most recent end/start first) ---
    rows = con.execute(
        f"""
        SELECT candidate_id, company, title, start, "end", description
        FROM experience
        WHERE candidate_id IN ({ph})
        ORDER BY COALESCE(substr("end",1,4),'9999') DESC,
                 COALESCE(substr(start,1,4),'0000') DESC,
                 company
        """,
        candidate_ids,
    ).fetchall()
    for cid, company, title, start, end, desc in rows:
        if cid in by_id:
            by_id[cid].experience.append(ExperienceItem(
                company=company, title=title, start=start, end=end, description=desc,
                skills=None, highlights=None  # not stored in SQL per your simplified schema
            ))

    # --- Skills (sorted) ---
    rows = con.execute(
        f"""
        SELECT candidate_id, skill
        FROM skills
        WHERE candidate_id IN ({ph})
        ORDER BY lower(skill)
        """,
        candidate_ids,
    ).fetchall()
    for cid, skill in rows:
        if cid in by_id and skill:
            by_id[cid].skills.append(skill)

    # --- Certifications (recent first, then name) ---
    rows = con.execute(
        f"""
        SELECT candidate_id, name, year, issuer
        FROM certifications
        WHERE candidate_id IN ({ph})
        ORDER BY COALESCE(year, 0) DESC, lower(name)
        """,
        candidate_ids,
    ).fetchall()
    for cid, name, year, issuer in rows:
        if cid in by_id:
            by_id[cid].certifications.append(CertificationItem(
                name=name, year=year, issuer=issuer
            ))

    # Preserve input order
    return [by_id[cid] for cid in candidate_ids if cid in by_id]


def companies_for(con: sqlite3.Connection, candidate_id: str) -> List[str]:
    rows = con.execute(
        "SELECT DISTINCT company FROM experience WHERE candidate_id=? AND company IS NOT NULL AND company<>'' ORDER BY company",
        (candidate_id,)
    ).fetchall()
    return [r[0] for r in rows]

def institutions_for(con: sqlite3.Connection, candidate_id: str) -> List[str]:
    rows = con.execute(
        "SELECT DISTINCT institution FROM education WHERE candidate_id=? AND institution IS NOT NULL AND institution<>'' ORDER BY end_year DESC NULLS LAST",
        (candidate_id,)
    ).fetchall()
    return [r[0] for r in rows]

def ids_by_skill(con, skill: str) -> list[str]:
    """Single skill (case-insensitive)."""
    return [r[0] for r in con.execute(
        """
        SELECT DISTINCT c.id
        FROM candidates c
        JOIN skills s ON s.candidate_id = c.id
        WHERE lower(s.skill) = lower(?)
        """,
        (skill,)
    ).fetchall()]

def ids_by_skills(con, skills: Iterable[str], mode: str = "and") -> list[str]:
    skills = [s for s in {_norm(s) for s in skills} if s] 
    if not skills:
        return []
    if mode.lower() == "or":
        qmarks = ",".join("?" for _ in skills)
        rows = con.execute(
            f"""
            SELECT DISTINCT c.id
            FROM candidates c
            JOIN skills s ON s.candidate_id = c.id
            WHERE lower(s.skill) IN ({qmarks})
            """,
            skills
        ).fetchall()
        return [r[0] for r in rows]
    else:
        # AND semantics: count distinct matched skills == len(skills)
        qmarks = ",".join("?" for _ in skills)
        rows = con.execute(
            f"""
            SELECT c.id
            FROM candidates c
            JOIN skills s ON s.candidate_id = c.id
            WHERE lower(s.skill) IN ({qmarks})
            GROUP BY c.id
            HAVING COUNT(DISTINCT lower(s.skill)) = ?
            """,
            skills + [len(skills)]
        ).fetchall()
        return [r[0] for r in rows]

def ids_by_company(con, comp_like: str) -> list[str]:
    return [r[0] for r in con.execute(
        """
        SELECT DISTINCT c.id
        FROM candidates c
        JOIN experience e ON e.candidate_id = c.id
        WHERE lower(e.company) LIKE lower(?)
        """,
        (f"%{comp_like}%",)
    ).fetchall()]

def ids_by_institution(con, inst_like: str) -> list[str]:
    return [r[0] for r in con.execute(
        """
        SELECT DISTINCT c.id
        FROM candidates c
        JOIN education e ON e.candidate_id = c.id
        WHERE lower(e.institution) LIKE lower(?)
        """,
        (f"%{inst_like}%",)
    ).fetchall()]

def id_by_name(con, name_like: str) -> Optional[str]:
    row = con.execute(
        """
        SELECT id FROM candidates
        WHERE lower(full_name) LIKE lower(?)
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (f"%{name_like}%",)
    ).fetchone()
    return row[0] if row else None