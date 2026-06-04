import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .chunk import main as chunk_main
from .ingest import main as ingest_main
from .vector_db import upsert_chunks_into_chroma

IST_ZONE = ZoneInfo("Asia/Kolkata")
SCHEDULE_HOUR = int(os.environ.get("SCHEDULER_HOUR_IST", "10"))
SCHEDULE_MINUTE = int(os.environ.get("SCHEDULER_MINUTE_IST", "0"))
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "mutual_fund_chunks")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
LOG_DIR = Path("data/logs")
LOG_FILE = LOG_DIR / "refresh.log"


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _log(message: str) -> None:
    now = datetime.now(IST_ZONE).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"[scheduler {now}] {message}")


def _log_to_file(message: str) -> None:
    _ensure_log_dir()
    timestamp = datetime.now(IST_ZONE).strftime("%Y-%m-%d %H:%M:%S %Z")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def refresh_corpus() -> None:
    start_time = datetime.now(IST_ZONE)
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    _log("Starting scheduled corpus refresh.")
    _log_to_file(f"REFRESH_START: {start_time_str}")
    
    try:
        ingest_main()
        chunk_main()
        upsert_chunks_into_chroma(collection_name=COLLECTION_NAME, model_name=EMBEDDING_MODEL, force_refresh=True)
        
        completion_time = datetime.now(IST_ZONE)
        completion_time_str = completion_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        elapsed_seconds = (completion_time - start_time).total_seconds()
        
        summary = f"Completed successfully in {elapsed_seconds:.2f}s (ingestion + chunking + vector upsert)"
        _log("Scheduled corpus refresh completed successfully.")
        _log_to_file(f"REFRESH_COMPLETION: {completion_time_str}")
        _log_to_file(f"STATUS: SUCCESS")
        _log_to_file(f"SUMMARY: {summary}")
        _log_to_file("---")
    except Exception as exc:
        completion_time = datetime.now(IST_ZONE)
        completion_time_str = completion_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        elapsed_seconds = (completion_time - start_time).total_seconds()
        
        error_msg = str(exc)
        _log(f"Scheduled corpus refresh failed: {error_msg}")
        _log_to_file(f"REFRESH_COMPLETION: {completion_time_str}")
        _log_to_file(f"STATUS: FAILURE")
        _log_to_file(f"SUMMARY: Refresh failed after {elapsed_seconds:.2f}s - {error_msg}")
        _log_to_file("---")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=IST_ZONE)

    trigger = CronTrigger(
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        timezone=IST_ZONE,
    )

    scheduler.add_job(
        refresh_corpus,
        trigger=trigger,
        id="daily_corpus_refresh",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()

    _log(
        f"Scheduler started for daily refresh at {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} IST."
    )

    return scheduler


if __name__ == "__main__":
    start_scheduler()
    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped.")
