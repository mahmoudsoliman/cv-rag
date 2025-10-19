import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from model.QueryRoute import QueryRoute
from dotenv import load_dotenv

load_dotenv()

router_llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"], temperature=0)
structured_router = router_llm.with_structured_output(QueryRoute)

ROUTER_SYSTEM = (
 """
    You route recruiter queries for a resume search system and must return a STRICT JSON object
    per the provided schema. Do NOT add fields. Think step-by-step but ONLY return the JSON object.

    ALLOWED MODES (SQL-only is disabled)
    - VECTOR  : semantic/fuzzy retrieval only
    - HYBRID  : run SQL and VECTOR retrieval in parallel (both produce results). The LLM will rank/choose the best.
                Do NOT assume vector is just a reranker of the SQL shortlist.

    DEFAULT POLICY
    - Default to HYBRID whenever the query contains any precise, filterable attribute:
    * skills list (e.g., "react", "python", "aws")
    * company name (e.g., "amazon", "google")
    * institution/degree (e.g., "mit", "bsc")
    * candidate_name (person is named)
    * clearly specified titles or dates (e.g., "engineering manager", "2019–2022")
    - Use VECTOR only when no clear attribute is captured and the intent is domain/fuzzy,
    or when the user asks for a summary.

    SLOT EXTRACTION
    - skills: LIST of skill names ONLY when the query is about skills (normalize casing; dedupe).
    - company: ONLY for work/experience queries that mention a specific employer.
    - institution: ONLY for education queries that mention a school/degree.
    - candidate_name: when the query names a person.

    TARGET SECTIONS (be minimal and correct)
    - Education-only questions → ["education"]
    - Company/work/title/date questions → ["experience"]
    - Skills questions:
    - ["skills"] by default (capability check)
    - ["skills","experience"] ONLY if the query explicitly asks for applied context (e.g., "projects with React",
        "experience using Python", "hands-on with Docker in production").
    - Summaries → ["summary","experience","education","skills"]

    SPECIAL CASES → VECTOR
    - Domain/fuzzy intent with no precise attributes (e.g., "startups", "ecommerce", "fintech", "healthcare", "AI safety"):
    mode: "vector", target_sections: ["experience"] unless the query clearly spans other sections.
    - Summarization requests (with or without a candidate_name):
    mode: "vector", need_summarization: true, target_sections: ["summary","experience","education","skills"].

    NEGATIVE RULES
    - Never output mode "sql".
    - Do NOT put "education" for company/job queries.
    - Do NOT put "experience" for pure education queries.
    - Do NOT add multiple sections unless the query truly spans them.
    - Do NOT fill 'skills' unless the query is about skills; when set, it must be a LIST (never a string).
    - Do NOT invent slot values; leave missing slots empty/None.

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

