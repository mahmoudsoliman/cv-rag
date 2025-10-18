import fitz

def extract_pdf_text(pdf_path: str, *, strip_whitespace: bool = True) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        text = page.get_text("text")
        if text:
            parts.append(text)
    return "\n".join(parts)


