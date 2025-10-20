# CV Search API

A powerful RAG (Retrieval-Augmented Generation) system for searching and querying CV/resume data using intelligent query routing, multi-modal search capabilities, and AI-powered answer generation.

## 📖 Documentation

For comprehensive system details, architecture, and design rationale, see: [**README.md**](../README.md)

## 🛠️ Installation Guide

### Prerequisites
- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Quick Setup
```bash
cd api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Usage Guide

### 1. Generate Resumes
To generate synthetic resumes, run from the api folder:
```bash
python cv_generation/cv_generator.py
```
*Note: You can configure how many CVs to generate and the percentage of CVs that have images from within the script.*

### 2. Process CVs and Store in Database
To process the CVs and store them in the database:
```bash
python cv_processing/cv_processor.py
```
*This will process all PDF resumes in the `data/pdf` folder and store the data in the database.*

Now the API is ready to answer user queries.

### 3. Starting the API
```bash
chmod +x run_api.sh
./run_api.sh
```
Or run directly: `python main.py`

The API will be available at `http://localhost:8000`

### API Endpoints
- **Health Check**: `GET /health`
- **Search CVs**: `POST /ask` with JSON body: `{"question": "Your query here"}`

### Supported Query Types
- Skills search: "Find candidates with Python and React skills"
- Company experience: "Who worked at Google or Microsoft?"
- Education queries: "Find candidates with Computer Science degrees"
- Hybrid searches: "Show me software engineers with AWS experience"

##  Project Structure

```
api/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── run_api.sh             # Startup script
├── cv_processing/         # PDF parsing and data extraction
├── cv_generation/         # CV generation utilities
├── query_processing/      # Query routing and execution
├── db/                    # Database and vector store management
├── model/                 # Pydantic models
└── data/                  # Database files and processed CVs
```

## 🔧 Configuration

- **API Port**: 8000 (configurable in `main.py`)
- **CORS**: Enabled for all origins (configure for production use)
- **Vector Store**: ChromaDB with default settings
- **Database**: SQLite with auto-initialization
- **Storage Layers**:
  - SQLite Database (`data/candidates.db`): Structured candidate profiles
  - ChromaDB (`data/chroma_resumes/`): Vector embeddings for semantic search