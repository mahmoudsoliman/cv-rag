import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)

def synthesize_answer_from_docs(result: dict, user_query: str):
    
    sections = result.get("sections") or ["experience","education","skills","summary"]
    facts = result.get("facts") or []
    docs = result.get("docs") or []

    system = SystemMessage(content=(
        "You are a recruiter assistant. Answer the user's question using ONLY the provided context.\n"
        "- Treat 'facts' (structured profiles from the database) as authoritative for names, companies, schools, dates, skills.\n"
        "- Treat 'snippets' (free text from vector search) as supporting evidence. Each snippet includes a score:\n"
        "    • score.distance: cosine distance (lower is better)\n"
        "    • score.similarity: derived ≈ 1 - distance (higher is better)\n"
        "- Prefer the facts when there is any disagreement.\n"
        "- Be concise, factual, and do not fabricate missing information.\n"
        "- If the answer is not present, say so briefly."
    ))

    human = HumanMessage(content=(
        f"Question: {user_query}\n\n"
        f"Sections searched: {sections}\n\n"
        f"facts (JSON array of CandidateProfile objects):\n{facts}\n\n"
        f"snippets (JSON array with text, metadata, score):\n{docs}\n"
    ))

    return llm.invoke([system, human]).content
