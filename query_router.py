import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from QueryRoute import QueryRoute
from dotenv import load_dotenv

load_dotenv()

router_llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"], temperature=0)
structured_router = router_llm.with_structured_output(QueryRoute)

ROUTER_SYSTEM = (
   """
    You route recruiter queries for a resume search system and must return a STRICT JSON object
    per the provided schema. Do NOT add fields. Think step-by-step but ONLY return the JSON object.

    ROUTING GOAL
    - Choose: SQL (exact filters), VECTOR (semantic/fuzzy), or HYBRID (SQL shortlist → vector rank).
    - Extract slots:
    - skills: LIST of skill names ONLY when the query is about skills (normalize casing; dedupe).
    - company: ONLY for work experience queries.
    - institution: ONLY for education queries.
    - candidate_name: when the query names a person.
    - Choose the minimal, correct target_sections: include ONLY what’s needed.

    STRICT MAPPING (apply exactly)
    - If the query targets education (university/college/institution/degree):
        mode: "sql" (or "hybrid" if semantic phrasing),
        target_sections: ["education"] ONLY.
    - If the query targets company / job / title / dates of employment:
        mode: "sql" (or "hybrid"),
        target_sections: ["experience"] ONLY.
    - If the query targets skills (e.g., "who has X", "experienced in Y"):
        - If exact skill lookup is possible → mode: "hybrid" (SQL shortlist by skills → vector rank).
        - Put all extracted skills into the 'skills' LIST.
        - target_sections:
            * ["skills"] by default (pure capability).
            * ["skills","experience"] ONLY if the query explicitly asks for applied context (e.g., "projects with React", "experience using Python", "hands-on with Docker in production").
    - If the query asks to summarize:
        mode: "vector", need_summarization: true,
        target_sections: ["summary","experience","education","skills"].
    - If candidate_name is provided and the query asks to summarize that person:
        restrict to that candidate; same sections as above.

    NEGATIVE RULES
    - Do NOT put "education" for company/job queries.
    - Do NOT put "experience" for pure education queries.
    - Do NOT add multiple sections unless the query truly spans them.
    - Do NOT fill 'skills' unless the query is about skills. When set, it must be a LIST (possibly empty, never a string).
    - Do NOT invent slot values; leave them empty/None if absent.

    CONFIDENCE & ABSTAIN
    - If unsure, set abstain=true and confidence<0.5.
    - Otherwise set confidence in [0.5,1.0].

    Return ONLY the JSON object.
    """
)

def route_query_llm(user_query: str) -> QueryRoute:
    msgs = [
        SystemMessage(content=ROUTER_SYSTEM),
        HumanMessage(content=f"Query: {user_query}\nReturn the JSON object only."),
    ]
    res = structured_router.invoke(msgs)
    print("Routed query:", res.model_dump())
    return res

