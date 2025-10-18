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
# TODO: check prompt caching
    user_prompt = f"""
You are a synthetic CV generator for testing data. Produce a single JSON object that matches this schema:
{json.dumps(schema, indent=2)}

Constraints:
- Be internally consistent (dates, durations, ages).
- Use realistic but fictional company names and accomplishments.
- Do NOT reference real people or real private data.
- The "synthetic" field must be true.
- The "image_prompt" must be a short photorealistic prompt describing a headshot that matches the candidate (age, gender, attire professional), with no real person names.

Base candidate data (from Faker):
{json.dumps(basic_fields)}

Role hint: {role_hint}

Return ONLY the JSON object, no extra text.
"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Use Responses API (preferred). We'll call the responses endpoint.
    payload = {
        "model": "gpt-4o-mini",
        "input": user_prompt,
        "temperature": temperature,
        # Optionally you can ask for a JSON schema object via structured outputs if your client supports it.
    }

    print("generatinf cv data from open ai ...")

    async with session.post(f"{API_BASE}/responses", headers=headers, json=payload) as resp:
        resp.raise_for_status()
        result = await resp.json()

    # resp = requests.post(f"{API_BASE}/responses", headers=headers, json=payload)
    # resp.raise_for_status()
    # result = resp.json()

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
        # Last resort: try to find JSON substring
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
    """Generate a single CV with the given role hint."""
    if role_hint is None:
        role_hint = "Senior Backend Engineer"
    
    print(f"Generating CV for role: {role_hint} (image: {generate_image})")
    
    # Ensure directories exist
    os.makedirs("data/json", exist_ok=True)
    os.makedirs("data/images", exist_ok=True)
    os.makedirs("data/pdf", exist_ok=True)
    
    cv_id = str(uuid.uuid4())
    basic_info = generate_person_basic()
    cv = await request_structured_cv(session, basic_info, role_hint=role_hint, temperature=0.7)
    cv["id"] = cv_id
    
    # Save JSON data
    json_path = f"data/json/{cv_id}.json"
    print("Storing CV json data...")
    async with aiofiles.open(json_path, "w", encoding="utf-8") as fh:
        await fh.write(json.dumps(cv, indent=2, ensure_ascii=False))
    
    # Conditionally generate and save portrait image
    image_path = None
    if generate_image:
        image_path = f"data/images/{cv_id}.png"
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
        "Tech Lead"
    ]
    
    print(f"Generating {n} CVs with randomized titles...")
    

    async with aiohttp.ClientSession() as session:
        tasks = [
            generate_single_cv(
                session, 
                random.choice(job_titles),
                generate_image=random.random() < 0.10  # 10% chance for images
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
    asyncio.run(generate_multiple_cvs(10))  # This will generate 10 CVs with random titles
    
    # Default: generate one CV
    #generate_single_cv("Senior Backend Engineer")


