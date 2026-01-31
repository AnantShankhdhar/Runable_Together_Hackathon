# Industrial Maintenance Intelligence API

**Transform unstructured maintenance documents into decision-ready reliability intelligence.**

> "Factories don't lack maintenance data — they lack the ability to learn from it."

## Problem Statement

Industrial plants generate thousands of maintenance work orders, failure reports, and equipment manuals every year. These documents contain critical information about equipment failures, root causes, fixes, and downtime — but they exist as unstructured PDFs, scanned logs, and free-text technician notes.

Because this data is not structured or connected across documents, teams cannot learn from past failures. As a result, the same equipment issues recur, downtime increases, and maintenance decisions rely on tribal knowledge rather than data.

## Solution

This API provides:
- **AI-powered extraction** using Claude Sonnet to parse unstructured documents
- **Vector embeddings** via OpenAI for semantic similarity search
- **Structured failure database** to query historical maintenance intelligence
- **Pattern detection** to identify recurring issues before they cause downtime

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MAINTENANCE INTELLIGENCE API                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐   │
│  │   Documents  │───▶│   Claude     │───▶│  Structured Extraction   │   │
│  │   (PDF/Text) │    │   Sonnet     │    │  - Work Orders           │   │
│  └──────────────┘    └──────────────┘    │  - Failure Events        │   │
│                                           │  - Equipment Links       │   │
│                                           └───────────┬──────────────┘   │
│                                                       │                  │
│                                                       ▼                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐   │
│  │   Similar    │◀───│   OpenAI     │◀───│   PostgreSQL + pgvector  │   │
│  │   Failure    │    │   Embeddings │    │   - Documents            │   │
│  │   Search     │    └──────────────┘    │   - Work Orders          │   │
│  └──────────────┘                        │   - Failure Events       │   │
│                                           │   - Equipment Registry   │   │
│                                           │   - Embeddings (vector)  │   │
│                                           └──────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Cost Optimization Strategies

At scale (100K+ documents), AI processing costs can become significant. This system implements:

### 1. Extraction Caching
```python
# Documents are hashed; identical content reuses cached extractions
content_hash = sha256(document_text)
if cache.exists(content_hash):
    return cache.get(content_hash)  # Zero API cost
```

### 2. Batch Embedding
```python
# Instead of embedding one at a time (100 API calls for 100 items):
# Batch them (1 API call for 100 items)
EMBEDDING_BATCH_SIZE = 100
embeddings = openai.embed(batch_of_texts)
```

### 3. Smart Text Filtering
```python
# Skip embedding very short texts (unlikely to provide value)
MIN_TEXT_LENGTH_FOR_EMBEDDING = 50
```

### 4. Tiered Processing
```
Priority 1: New failure reports (process immediately)
Priority 2: Historical data (batch process overnight)
Priority 3: Low-value documents (skip or defer)
```

### Cost Estimates (Jan 2025)
| Operation | Cost per 1K tokens | 10K Documents Est. |
|-----------|-------------------|-------------------|
| Claude Sonnet (input) | $0.003 | ~$30-50 |
| Claude Sonnet (output) | $0.015 | ~$15-25 |
| OpenAI ada-002 embeddings | $0.0001 | ~$1-2 |

## Quick Start

### 1. Start PostgreSQL with pgvector

```bash
# Using Docker
docker-compose up -d db

# Or use a managed PostgreSQL with pgvector support
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
# - DATABASE_URL
```

### 3. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python scripts/load_sample_data.py
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

### 6. Access Documentation

Open http://localhost:8000/docs for interactive API documentation.

## API Endpoints

### Documents
- `POST /documents/upload` - Upload a document
- `POST /documents/upload/text` - Upload raw text
- `GET /documents/` - List documents
- `GET /documents/{id}` - Get document details
- `POST /documents/{id}/process` - Trigger AI extraction
- `POST /documents/batch` - Batch upload

### Failure Intelligence
- `GET /failures/` - List failures
- `POST /failures/search` - Semantic search for similar failures
- `GET /failures/search/quick?q=...` - Quick similarity search
- `GET /failures/analytics/summary` - Failure analytics
- `GET /failures/patterns/recurring` - Find recurring patterns
- `POST /failures/embed` - Generate embeddings batch

### Equipment
- `POST /equipment/` - Register equipment
- `GET /equipment/` - List equipment
- `GET /equipment/{id}` - Get equipment details
- `GET /equipment/{id}/stats` - Equipment reliability stats
- `GET /equipment/{id}/history` - Maintenance history

## Example Usage

### Upload a Work Order

```bash
curl -X POST "http://localhost:8000/documents/upload/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Machine A71 - Date: 04/03/2024 - Issue: Pump making grinding noise. Gina Moore noted: Replaced worn bearings, root cause was lack of lubrication.",
    "filename": "work_order_001.txt",
    "plant_id": "PLANT-001"
  }'
```

### Search for Similar Failures

```bash
curl -X POST "http://localhost:8000/failures/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pump bearing noise grinding",
    "limit": 5
  }'
```

### Get Failure Analytics

```bash
curl "http://localhost:8000/failures/analytics/summary?days=90"
```

## Database Schema

### Core Tables
- **documents** - Raw uploaded documents with status tracking
- **equipment** - Equipment registry with aggregated stats
- **work_orders** - Extracted work order data
- **failure_events** - Structured failure records with embeddings

### Cost Optimization Tables
- **extraction_cache** - Cache for document extractions
- **embedding_batches** - Batch job tracking

### Analytics Tables
- **failure_patterns** - Discovered recurring patterns

## Technology Stack

- **FastAPI** - Async Python web framework
- **PostgreSQL** - Relational database
- **pgvector** - Vector similarity search extension
- **Claude Sonnet** - AI extraction (Anthropic)
- **OpenAI ada-002** - Text embeddings
- **SQLAlchemy** - Async ORM

## Production Considerations

1. **API Keys**: Use secret management (AWS Secrets Manager, etc.)
2. **Rate Limiting**: Implement per-client rate limits
3. **Queuing**: Use Celery/Redis for background processing
4. **Monitoring**: Add Prometheus metrics for cost tracking
5. **Backup**: Regular PostgreSQL backups including vector data

## License

MIT
