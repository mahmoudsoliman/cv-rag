# Resumes RAG

## 1. Overview
1. **Resume Generation** with realistic but fake data and images.
2. **Resume Processing & Storage** in searchable formats.
3. **Query Answering** over the processed resumes.
4. **User Interface** for interactive exploration and evidence-backed answers.
---

- 2. System Components
### 2.1 Synthetic Resume Generation
- The user triggers generation by running a **Python command** to start the RAG system.
- The system uses **Faker** to produce personal data that is guaranteed to be fake and easy to control.
- It randomly chooses a **job title** from a hardcoded set.
- The system sends **fake personal data + chosen title + a JSON schema** to an **LLM**.
- The LLM returns the **JSON schema filled** with resume data **and** a **profile image prompt**.
- The system **stores the JSON** to a file.
- The system requests an image from an **images LLM** (**gpt-image-1**), using the profile image prompt, to generate a **headshot**. Note: gpt-image-1 generates good quality headshots. Other options may be cheaper/faster but were not examined. 
- The generated **image is stored** in a file.
- The system uses the JSON data and image to **build an HTML resume** from a stored template.
- The HTML resume is **converted to PDF** and **stored** in a file.
- **Model choice**: **gpt-4o-mini** is used as a strong-enough and cost-effective model for these queries.




![diagram-export-20-10-2025-00_43_18.png](https://eraser.imgix.net/workspaces/wyrn2YjZzGwQauNnw418/Fu8xX11Fc7Um9tPS9GS0SyP5RKA2/diagram-export-20-10-2025-00_43_18_0BekdWX2A2tdiqPOF3ghC.png?ixlib=js-3.7.0 "diagram-export-20-10-2025-00_43_18.png")



### 2.2 Resume Processing & Storage
- A **CV processor script** reads the generated **PDF resumes** and converts them to **text**.
- The script sends the text to the **LLM**, along with a **JSON schema**, to **parse** the resume.
- The LLM returns a **structured** representation covering sections such as: **summary, education, experience, skills, certifications**.
- The **structured data** is stored in a **SQL database** (**SQLite**, suitable for lightweight prototypes).
- The **raw resume text** is stored in a **vector database** (**ChromaDB**, suitable for local prototypes).
- 
![diagram-export-20-10-2025-02_00_35.png](https://eraser.imgix.net/workspaces/wyrn2YjZzGwQauNnw418/Fu8xX11Fc7Um9tPS9GS0SyP5RKA2/diagram-export-20-10-2025-02_00_35_WZxR7V-qCwq5STOl0vGiu.png?ixlib=js-3.7.0 "diagram-export-20-10-2025-02_00_35.png")



### 2.3 Query Answering (RAG)
- A **FastAPI** endpoint exposes an API that accepts a **natural-language query** from the user.
- The API forwards the query to the **RAG system**.
- The RAG system sends the query to the **LLM** with a **JSON schema** requesting a **structured form** of the query.
- The LLM returns the **structured query**, indicating:
    - the **mode** (hybrid or vector-only),
    - **target sections**,
    - **filters** (e.g., skills, company, institution, candidate name),
    - whether **summarization** is needed,
    - **confidence** and **abstain** flags.

```json
{
  "mode": "hybrid",
  "target_sections": [
    "skills",
    "experience"
  ],
  "skills": [
    "python"
  ],
  "company": null,
  "institution": null,
  "candidate_name": null,
  "need_summarization": false,
  "confidence": 0.8,
  "abstain": false
}
```
- Based on the structured query:
    - The system runs a **SQL search** (deriving the SQL from the structured fields) to produce **facts**.
    - It runs a **vector search** against ChromaDB using the **original query text**.

- The **facts** (SQL results) and **vector hits** are sent to the **LLM** to:
    - **rank** results,
    - **deduplicate** candidates,
    - select the **best 10**,
    - and produce a **human-readable answer**.

- The API returns the **final answer** along with the **documents used as evidence**.
- **Abstraction**: **LangChain** is used to abstract LLM interactions, enabling easy model swapping, standardized prompts/calls, and reliable structured output parsing.
![diagram-export-20-10-2025-00_34_03.png](https://eraser.imgix.net/workspaces/wyrn2YjZzGwQauNnw418/Fu8xX11Fc7Um9tPS9GS0SyP5RKA2/diagram-export-20-10-2025-00_34_03_CwSv-tf6OTJAqrcnWuCjC.png?ixlib=js-3.7.0 "diagram-export-20-10-2025-00_34_03.png")



### 2.4 User Interface
- A **modern React-based** interface interacts with the CV Search API.
- Users submit **natural-language queries** and receive a **clear answer** with **supporting evidence**.
- The UI maintains **in-memory conversation history**.
- The interface was **generated with bolt.new** using a prompt authored via ChatGPT.
---

![Screenshot 2025-10-20 at 02.06.14.png](https://eraser.imgix.net/workspaces/wyrn2YjZzGwQauNnw418/Fu8xX11Fc7Um9tPS9GS0SyP5RKA2/Screenshot%202025-10-20%20at%2002.06.14_hYaJRJUvX3pZMi6Lxhla1.png?ixlib=js-3.7.0 "Screenshot 2025-10-20 at 02.06.14.png")



## 3. End-to-End Flow Summary
1. **Generate Resumes**
    - User runs Python command → Faker data → random title → LLM fills JSON + image prompt → store JSON → gpt-image-1 generates headshot → store image → build HTML → convert to PDF → store artifacts.

2. **Process & Store**
    - CV processor reads PDFs → extract text → LLM parses into structured JSON → store structured data in SQLite → store raw text in ChromaDB.

3. **Answer Queries**
    - FastAPI receives query → LLM creates structured query (mode/filters/sections) → SQL search (facts) + vector search (original query) → LLM ranks/dedupes/selects top 10 and composes answer → API returns answer + evidence.

4. **Frontend**
    - React UI sends queries, displays answers with evidence, and keeps in-memory history.

---

## 4. Rationale
- **Faker**: more consistent, guaranteed-fake, and easy-to-control data.
- **gpt-4o-mini**: strong enough and cost-effective for this workload.
- **SQLite**: lightweight SQL database suitable for prototypes.
- **ChromaDB**: vector database suitable for local prototypes.
- **LangChain**: abstraction layer to swap models, standardize prompts/calls, and parse structured outputs.
- **gpt-image-1**: produces good-quality headshots for synthetic profiles (alternatives exist but were not evaluated).
- **React + bolt.new**: simple, modern UI generation and iteration path.
---

## 5. Interfaces (concise)
- **Generation Trigger**: Python CLI command (invokes the RAG system to synthesize resumes).
- **Ingestion**: CV processor script (PDF → text → LLM parse → store to SQLite & ChromaDB).
- **API (FastAPI)**:
    - **Request**: `{ "query": "natural language text" }` 
    - **Response**:
        - `answer` : human-readable result,
        - `evidence` : documents used,
        - up to **10** top results after ranking/deduplication.


- **Frontend**: React SPA consuming the API, showing answer + evidence and preserving in-memory conversation history.






