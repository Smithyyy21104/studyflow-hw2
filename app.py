from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path
import os
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent


def db_path() -> Path:
    return Path(os.getenv("TASKS_DB_PATH", str(ROOT / "studyflow.sqlite3")))


def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize():
    with connect() as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        total = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if total == 0 and os.getenv("SEED_DEMO", "1") == "1":
            sample = [
                ("Review DevOps lecture slides", "Study", "high", str(date.today() + timedelta(days=1)), 0),
                ("Test the application in a browser", "Project", "normal", str(date.today() + timedelta(days=2)), 0),
                ("Prepare the one-page HW2 report", "Assignment", "normal", str(date.today() + timedelta(days=3)), 1),
            ]
            connection.executemany("INSERT INTO tasks(title,category,priority,due_date,completed) VALUES(?,?,?,?,?)", sample)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    yield


app = FastAPI(title="StudyFlow - HW2 DevOps Demo", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(default="Study", min_length=1, max_length=40)
    priority: Literal["low", "normal", "high"] = "normal"
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=40)
    priority: Literal["low", "normal", "high"] | None = None
    due_date: date | None = None
    completed: bool | None = None


def encode(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["completed"] = bool(item["completed"])
    return item


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "app": "StudyFlow", "version": app.version}


@app.get("/api/tasks")
def list_tasks(status: Literal["all", "pending", "done"] = Query(default="all")):
    where = {"all": "", "pending": "WHERE completed=0", "done": "WHERE completed=1"}[status]
    with connect() as connection:
        rows = connection.execute(f"SELECT * FROM tasks {where} ORDER BY completed ASC, due_date IS NULL, due_date ASC, id DESC").fetchall()
    return [encode(row) for row in rows]


@app.get("/api/stats")
def stats():
    with connect() as connection:
        row = connection.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) AS done, SUM(CASE WHEN completed=0 THEN 1 ELSE 0 END) AS pending FROM tasks").fetchone()
    return {"total": row["total"], "done": row["done"] or 0, "pending": row["pending"] or 0}


@app.post("/api/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip() or not task.category.strip():
        raise HTTPException(status_code=422, detail="Task title and category cannot be blank")
    with connect() as connection:
        cursor = connection.execute("INSERT INTO tasks(title,category,priority,due_date) VALUES(?,?,?,?)", (task.title.strip(), task.category.strip(), task.priority, str(task.due_date) if task.due_date else None))
        row = connection.execute("SELECT * FROM tasks WHERE id=?", (cursor.lastrowid,)).fetchone()
    return encode(row)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    changes = update.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No changes supplied")
    if any(changes.get(key) is None for key in ("title", "category", "priority", "completed") if key in changes):
        raise HTTPException(status_code=422, detail="Required task fields cannot be null")
    if "title" in changes and changes["title"] is not None:
        changes["title"] = changes["title"].strip()
        if not changes["title"]:
            raise HTTPException(status_code=422, detail="Title is required")
    if "category" in changes and changes["category"] is not None:
        changes["category"] = changes["category"].strip()
        if not changes["category"]:
            raise HTTPException(status_code=422, detail="Category is required")
    if "due_date" in changes and changes["due_date"] is not None:
        changes["due_date"] = str(changes["due_date"])
    if "completed" in changes:
        changes["completed"] = int(changes["completed"])
    with connect() as connection:
        if connection.execute("SELECT id FROM tasks WHERE id=?", (task_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Task not found")
        setters = ", ".join(f"{field}=?" for field in changes)
        connection.execute(f"UPDATE tasks SET {setters} WHERE id=?", (*changes.values(), task_id))
        row = connection.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    return encode(row)


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with connect() as connection:
        result = connection.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
