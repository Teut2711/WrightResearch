import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.run_reconciliation import run_reconciliation
from app.enums import ReportType
import sqlite3
import uuid
from contextlib import asynccontextmanager

from app.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.getLogger("uvicorn.errors").info(
        "=============== Db created ================="
    )
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Trade Reconciliation System"}


@app.get("/run-reconciliation/")
async def run_reconciliation_endpoint(background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(run_reconciliation, task_id)
    return {"task_id": task_id}


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    db_path = Path("data") / "trades.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT status, reason FROM tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"task_id": task_id, "status": row[0], "reason": row[1]}
    else:
        raise HTTPException(status_code=404, detail="Task not found")


@app.get("/download-report/{report_type}")
async def download_report(report_type: ReportType):
    report_path = Path(__file__).parent / "data" / report_type.value
    if report_path.exists():
        return FileResponse(
            report_path,
            media_type="application/octet-stream",
            filename=report_type.value,
        )
    else:
        raise HTTPException(status_code=404, detail="Report not found")
