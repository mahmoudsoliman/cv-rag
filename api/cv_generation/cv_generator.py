import os
import json
import base64
import random
from time import time
from dotenv import load_dotenv
from faker import Faker
import uuid
from pdf_generator import render_pdf
from secrets import randbits
import asyncio
import aiohttp
import aiofiles

load_dotenv()
API_KEY = os.environ["OPENAI_API_KEY"]
API_BASE = "https://api.openai.com/v1"



def make_cv_schema():
    """Define the CV schema we want back from the model."""
    schema = {
        "full_name": "string",
        "email": "string",
        "phone": "string",
        "location": "string",         # city, country
        "title": "string",            # e.g. Senior Backend Engineer
        "summary": "string",
        "skills": ["string"],
        "experience": [
            {
                "company": "string",
                "title": "string",
                "start_date": "YYYY-MM",
                "end_date": "YYYY-MM|null",
                "summary": "string",
                "highlights": ["string"]
            }
        ],
        "education": [
            {
                "institution": "string",
                "degree": "string",
                "start_year": "integer",
                "end_year": "integer"
            }
        ],
        "languages": [{"language": "string", "level": "string"}],
        "certifications": ["string"],
        "public_profile": {"linkedin": "string|null", "portfolio": "string|null"},
        "synthetic": True,            # always true for traceability
        "image_prompt": "string"      # store the prompt used for the portrait
    }
    return schema


def generate_person_basic():
    print("generating personal data...")
    fake = Faker()
    fake.seed_instance(randbits(64))

    name = fake.name()
    email = fake.ascii_email()
    phone = fake.phone_number()
    city = fake.city()
    country = fake.country()
    return {
        "full_name": name,
        "email": email,
        "phone": phone,
        "location": f"{city}, {country}"
    }



async def request_structured_cv(session, basic_fields, role_hint="software engineer", temperature=0.7):
    schema = make_cv_schema()
    user_prompt = f"""
        You are a synthetic CV generator for testing data. Produce a single JSON object that matches the schema below.

        STRICT OUTPUT
        - Return ONLY the JSON object. No prose, no Markdown, no comments.
        - The JSON MUST validate against the provided schema exactly (correct keys, types, and nesting).

        GLOBAL CONSTRAINTS
        - Be internally consistent (dates, durations, ages, seniority).
        - Use real company names and real universities that plausibly match the candidate’s location/region in the base data.
        - Companies and universities MUST be diverse: do not repeat the same company or university more than once in the entire CV, unless representing multiple roles at the SAME employer (then titles/dates must be distinct and contiguous, with no overlaps or gaps larger than 3 months).
        - Skills MUST be relevant to the role hint and the actual experience described. Do not list skills the experience does not justify.
        - Use a professional tone suitable for CVs.
        - Do NOT reference real people or private data.
        - The "synthetic" field must be true.
        - The "image_prompt" must be a short photorealistic headshot description (age, gender expression if implied by base data, neutral background, professional attire). No real person names, no copyrighted styles.

        ANTI-REPETITION & DIVERSITY RULES
        - Companies: choose well-known or regionally plausible real companies across different sizes (startup, mid-size, enterprise); do not reuse the same company name unless modeling a promotion at the same employer.
        - Universities: choose real, regionally plausible institutions; do not reuse the same university.
        - Projects/Accomplishments: write distinct, non-template bullets. Vary verbs and outcomes. Include concrete metrics (e.g., latency ↓35%, revenue ↑$1.2M, NPS +12, cycle time ↓25%) where credible.
        - Skills: deduplicate and normalize (e.g., "Python" not ["py","python","Python3"]). Keep 10–16 unique skills max. Group them implicitly in bullets (core languages/frameworks, tools, cloud, data/DB, testing/CI/CD).

        ROLE ALIGNMENT (based on Role hint)
        - Include skills and achievements that are typical for the role level and function.
        - If role is backend: emphasize languages (e.g., Python/Go/Java), frameworks (Django/FastAPI/Spring), databases (PostgreSQL/MySQL), cloud (AWS/Azure/GCP), CI/CD, observability, scalability, security.
        - If frontend: emphasize JS/TS, React/Vue, state mgmt, accessibility, performance (LCP/CLS), testing (Jest/RTL), design systems.
        - If data/ML: emphasize Python, pandas, SQL, Spark, ML frameworks, feature stores, MLOps.
        - If mobile: platform language + tooling, store releases, performance, accessibility.
        (Adapt similarly for DevOps/SRE, Product, Design, etc.)

        DATE & SENIORITY CONSISTENCY
        - Total experience years must match the roles’ dates.
        - No overlapping full-time roles unless clearly marked as part-time/consulting.
        - Internships and part-time must be labeled.

        STRUCTURE RULES
        - Experience: 3–6 roles; each role 3–6 bullets; results-oriented and metric-driven where possible.
        - Education: 1–2 entries that match location/discipline; plausible years for the candidate’s age.
        - Certifications (optional): use real cert names relevant to role; no duplicates.
        - Links: 1–3 links (e.g., GitHub, portfolio, LinkedIn) if plausible.
        - Summary: 2–4 sentences tailored to the role; avoid generic boilerplate.

        VALIDATION & SELF-CHECK (silent)
        - Before returning JSON, silently verify:
        * No duplicated company names across different employers.
        * No duplicated university names.
        * Skills list is deduplicated, normalized (title case for products, uppercase for acronyms).
        * Skills present are evidenced by at least one experience bullet or project.
        * Dates are chronological and plausible with no large unexplained gaps.
        - If any check fails, regenerate the problematic parts and re-validate, then output the final JSON.

        Base candidate data (from Faker):
        {json.dumps(basic_fields)}

        schema:
        {json.dumps(schema, indent=2)}

        Role hint: {role_hint}
"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Use Responses API (preferred). We'll call the responses endpoint.
    payload = {
        "model": "gpt-4o-mini",
        "input": user_prompt,
        "temperature": temperature
    }

    print("generating cv data from open ai ...")

    async with session.post(f"{API_BASE}/responses", headers=headers, json=payload) as resp:
        resp.raise_for_status()
        result = await resp.json()

    text = ""
    for part in result.get("output", []):
        if isinstance(part, dict):
            if part.get("type") == "message":
                contents = part.get("content")
                if isinstance(contents, list):
                    for c in contents:
                        if c.get("type") == "output_text":
                            text += c.get("text", "")
        elif isinstance(part, str):
            text += part


    try:
        cv_json = json.loads(text.strip())
    except Exception as e:
        import re
        m = re.search(r"(\{.*\})", text, flags=re.DOTALL)
        if m:
            cv_json = json.loads(m.group(1))
        else:
            raise RuntimeError("Failed to parse JSON from model response:\n" + text) from e

    return cv_json


async def generate_portrait_image(session, image_prompt, fname="portrait.png", size="1024x1024"):
    print("Generating portrait image...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-image-1",
        "prompt": image_prompt,
        "size": size
    }

    _image_sem = asyncio.Semaphore(4)

    async with _image_sem:
        async with session.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as r:

            if r.status != 200:
                print("Status:", r.status)
                try:
                    print("Body:",  await r.json())
                except Exception:
                    print("Body (raw):", await r.text())
                raise SystemExit()
            json_data = await r.json()
    
    b64 = json_data["data"][0]["b64_json"]
    async with aiofiles.open(fname, "wb") as f:
            await f.write(base64.b64decode(b64))
    print(f"saved {fname}")


async def generate_single_cv(session, role_hint=None, generate_image=True):
    if role_hint is None:
        role_hint = "Senior Backend Engineer"
    
    print(f"Generating CV for role: {role_hint} (image: {generate_image})")
    
    # Ensure directories exist
    os.makedirs("./data/json", exist_ok=True)
    os.makedirs("./data/images", exist_ok=True)
    os.makedirs("./data/pdf", exist_ok=True)
    
    cv_id = str(uuid.uuid4())
    basic_info = generate_person_basic()
    cv = await request_structured_cv(session, basic_info, role_hint=role_hint, temperature=0.7)
    cv["id"] = cv_id
    
    # Save JSON data
    json_path = f"./data/json/{cv_id}.json"
    print("Storing CV json data...")
    async with aiofiles.open(json_path, "w", encoding="utf-8") as fh:
        await fh.write(json.dumps(cv, indent=2, ensure_ascii=False))
    
    # Conditionally generate and save portrait image
    image_path = None
    if generate_image:
        image_path = f"./data/images/{cv_id}.png"
        await generate_portrait_image(session, cv["image_prompt"], fname=image_path)
    
    # Generate PDF
    pdf_path = f"data/pdf/{cv['full_name'].replace(' ', '_')}.pdf"
    await asyncio.to_thread(render_pdf, cv, image_path, pdf_path)
    
    print(f"Generated CV for {cv['full_name']} ({role_hint})")


async def generate_multiple_cvs(n):
    t1 = time()
    """Generate n CVs with randomized job titles."""
    job_titles = [
        "Junior Software Engineer",
        "Software Engineer",
        "Senior Software Engineer", 
        "Full Stack Engineer",
        "Data Engineer",
        "Data Scientist",
        "Engineering Manager",
        "Tech Lead",
        "VP of Engineering",
        "Software Engineer in Test",
        "DevOps Engineer",
        "Data Analyst"
    ]
    
    print(f"Generating {n} CVs with randomized titles...")
    

    async with aiohttp.ClientSession() as session:
        tasks = [
            generate_single_cv(
                session, 
                random.choice(job_titles),
                generate_image=random.random() < 0.2  # 20% chance for images
            ) 
            for _ in range(n)
        ]
        await asyncio.gather(*tasks)
    
    print(f"\nCompleted generating {n} CVs!")
    t2 = time();
    print(f"Time taken: {t2 - t1:.2f} seconds")


# Generate a single CV (original behavior)
if __name__ == "__main__":
    # Example usage:
    # For a single CV:
    # generate_single_cv("Senior Backend Engineer")
    
    # For multiple CVs with random titles:
    asyncio.run(generate_multiple_cvs(10))  # This will generate 20 CVs with random titles
    
    # Default: generate one CV
    #generate_single_cv("Senior Backend Engineer")


