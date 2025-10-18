import json, os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES = os.path.join(BASE_DIR, "templates")

def to_file_uri(p: str | None) -> str | None:
    if not p:
        return None
    path = Path(p).resolve()
    return path.as_uri() if path.is_file() else None

def render_pdf(cv_data, portrait_path, pdf_path):
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"])
    )
    tmpl = env.get_template("cv-template-1.html")

    id = cv_data.get("id", "unknown")

    # Handle case where portrait_path is None (no image)
    portrait_src = to_file_uri(portrait_path) if portrait_path else None
    print("Portrait path:", portrait_path, "->", portrait_src)

    # WeasyPrint resolves relative URLs from base_url. Pass absolute for images.
    html_str = tmpl.render(**cv_data, portrait_path=portrait_src)
    HTML(string=html_str, base_url=BASE_DIR).write_pdf(pdf_path)

    out_pdf = os.path.join(BASE_DIR, pdf_path)
    print("Saved ->", out_pdf)
