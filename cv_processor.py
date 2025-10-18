import os
import glob
import asyncio
from typing import List
from pdf_parser import extract_pdf_text
from cv_extractor import extract_structured_profile_from_text
from sql_store import store_profile
from cv_chunker import build_docs_from_profile
from chroma_store import store


async def process_single_resume(pdf_path: str, db_path: str) -> str:
    """Process a single resume file and return the candidate ID."""
    try:
        print(f"Processing: {os.path.basename(pdf_path)}")
        
        # Extract text from PDF
        text = await asyncio.to_thread(extract_pdf_text, pdf_path)
        
        # Extract structured profile using LLM
        profile = await asyncio.to_thread(extract_structured_profile_from_text, text)
        
        # Store profile in database
        candidate_id = await asyncio.to_thread(store_profile, db_path, profile, source_file=pdf_path)
        
        # Build documents for vector store
        docs = await asyncio.to_thread(build_docs_from_profile, profile, candidate_id, pdf_path=pdf_path)
        
        # Add to vector store
        await asyncio.to_thread(store.add_documents, docs)
        
        print(f"Successfully processed: {os.path.basename(pdf_path)} (ID: {candidate_id})")
        return candidate_id
        
    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {str(e)}")
        raise


async def process_all_resumes(pdf_folder: str = "data/pdf", db_path: str = "data/candidates.db", max_concurrent: int = 5) -> List[str]:
    processed_candidates = []
    
    # Get all PDF files in the folder
    pdf_pattern = os.path.join(pdf_folder, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    # Create semaphore to limit concurrent operations
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_semaphore(pdf_path: str) -> str:
        async with semaphore:
            return await process_single_resume(pdf_path, db_path)
    
    # Create tasks for all PDF files
    tasks = [process_with_semaphore(pdf_path) for pdf_path in pdf_files]
    
    # Process tasks and collect results
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful results
    for result in results:
        if isinstance(result, str):  # Successful candidate ID
            processed_candidates.append(result)
        elif isinstance(result, Exception):
            # Exception was already logged in process_single_resume
            continue
    
    print(f"Completed processing {len(processed_candidates)} resumes successfully.")
    return processed_candidates


if __name__ == "__main__":
    asyncio.run(process_all_resumes())