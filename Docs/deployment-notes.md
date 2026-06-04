# Local Deployment Notes

## Start Application

Activate environment:

```powershell
.venv\Scripts\activate
```

Run backend:

```powershell
uvicorn src.app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Rebuild Corpus

```powershell
python -m src.ingest
python -m src.chunk
python -m src.embed
```

Refresh Chroma:

```powershell
python -c "from src.vector_db import upsert_chunks_into_chroma; upsert_chunks_into_chroma(force_refresh=True)"
```

## Run Tests

```powershell
python -m pytest -v
```

## Scheduler

Enable:

```env
ENABLE_SCHEDULER=1
```

Runs daily refresh at 10:00 AM.
