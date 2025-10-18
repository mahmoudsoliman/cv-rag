# CV Search API

A powerful RAG (Retrieval-Augmented Generation) system for searching and querying CV/resume data. This FastAPI-based backend provides intelligent search capabilities across candidate profiles using both SQL queries and vector similarity search.

## 🚀 Features

- **Intelligent Query Routing**: Automatically routes queries to SQL, vector search, or hybrid approaches based on query type
- **Multi-Modal Search**: Supports searches across education, experience, skills, and candidate summaries
- **Structured Data Extraction**: Extracts and stores candidate profiles with education, experience, skills, and certifications
- **Vector Similarity Search**: Uses ChromaDB for semantic search across resume content
- **SQL Filtering**: Precise filtering by specific criteria (company, institution, skills, etc.)
- **AI-Powered Answers**: Generates natural language responses using OpenAI's GPT models
- **RESTful API**: Clean FastAPI endpoints with comprehensive error handling

## 🏗️ Architecture

The system consists of several key components:

- **CV Processing**: PDF parsing and structured data extraction using AI
- **Database Layer**: SQLite for structured data + ChromaDB for vector embeddings
- **Query Processing**: Intelligent routing and execution of search queries
- **Answer Generation**: AI-powered response synthesis from search results

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository and navigate to the API directory:**
   ```bash
   cd api
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the API directory:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Initialize the database and process sample CVs:**
   ```bash
   python -c "from cv_processing.cv_processor import process_all_resumes; import asyncio; asyncio.run(process_all_resumes())"
   ```

## 🚀 Running the API

### Option 1: Using the provided script
```bash
chmod +x run_api.sh
./run_api.sh
```

### Option 2: Direct Python execution
```bash
python main.py
```

The API will start on `http://localhost:8000`

## 📚 API Endpoints

### Health Check
```http
GET /health
```

### Search CVs
```http
POST /ask
Content-Type: application/json

{
  "question": "Find candidates with React experience"
}
```

**Response:**
```json
{
  "ok": true,
  "sections": ["skills", "experience"],
  "facts": [...],
  "docs": [...],
  "answer": "Generated answer based on search results",
  "why": "Explanation of search approach"
}
```

## 🔍 Query Types Supported

- **Skills Search**: "Find candidates with Python and React skills"
- **Company Experience**: "Who worked at Google or Microsoft?"
- **Education Queries**: "Find candidates with Computer Science degrees"
- **Hybrid Searches**: "Show me software engineers with AWS experience"
- **Summarization**: "Summarize all candidates" or "Tell me about John Doe"

## 🗄️ Database Schema

The system uses two storage layers:

1. **SQLite Database** (`data/candidates.db`): Stores structured candidate profiles
2. **ChromaDB** (`data/chroma_resumes/`): Stores vector embeddings for semantic search

## 📁 Project Structure

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
- **CORS**: Enabled for all origins (configure in `main.py` for production)
- **Vector Store**: ChromaDB with default settings
- **Database**: SQLite with auto-initialization

## 🧪 Testing

Test the API using curl or any HTTP client:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Find candidates with Python skills"}'
```

## 🚨 Troubleshooting

1. **OpenAI API Key Error**: Ensure your `.env` file contains a valid OpenAI API key
2. **Database Not Found**: Run the CV processing script to initialize the database
3. **Port Already in Use**: Change the port in `main.py` or kill the process using port 8000
4. **Import Errors**: Ensure all dependencies are installed and virtual environment is activated

## 📝 Notes

- The system processes PDF resumes from the `data/pdf/` directory
- Vector embeddings are generated using OpenAI's text-embedding models
- Query routing uses GPT-4o-mini for intelligent query classification
- All AI operations require a valid OpenAI API key