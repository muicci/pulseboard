import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import datetime
import asyncio

app = FastAPI()

# Database connection details
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Pydantic models for data validation
class Signal(BaseModel):
    timestamp: datetime.datetime
    type: str
    source: str
    data: dict

class Event(BaseModel):
    timestamp: datetime.datetime
    name: str
    description: Optional[str]
    source: str
    data: dict

class Email(BaseModel):
    timestamp: datetime.datetime
    sender: str
    subject: str
    body_snippet: Optional[str]
    is_read: bool
    data: dict

# Database connection pool
pool = None

@app.on_event("startup")
async def startup():
    global pool
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        await create_tables()
        print("Database connection pool created and tables checked/created.")
    except Exception as e:
        print(f"Failed to connect to database or create tables: {e}")
        # Depending on requirements, you might want to exit or retry
        # For now, let's just log and let FastAPI continue if possible

@app.on_event("shutdown")
async def shutdown():
    global pool
    if pool:
        await pool.close()
        print("Database connection pool closed.")

async def create_tables():
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS pulseboard_signals (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                type VARCHAR(255) NOT NULL,
                source VARCHAR(255) NOT NULL,
                data JSONB
            );
            CREATE TABLE IF NOT EXISTS pulseboard_events (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                source VARCHAR(255) NOT NULL,
                data JSONB
            );
            CREATE TABLE IF NOT EXISTS pulseboard_emails (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                sender VARCHAR(255) NOT NULL,
                subject VARCHAR(255) NOT NULL,
                body_snippet TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                data JSONB
            );
        """)
    print("Tables checked/created successfully.")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    if not pool:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database pool not initialized.")
    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database connection error: {e}")

@app.post("/api/signals", status_code=status.HTTP_201_CREATED)
async def create_signal(signal: Signal):
    """Create a new signal."""
    if not pool:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database pool not initialized.")
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO pulseboard_signals (timestamp, type, source, data) VALUES ($1, $2, $3, $4)",
            signal.timestamp, signal.type, signal.source, signal.data
        )
    return {"message": "Signal created successfully", "signal": signal.dict()}

@app.get("/api/signals", response_model=List[Signal])
async def get_signals():
    """Retrieve all signals."""
    if not pool:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database pool not initialized.")
    async with pool.acquire() as conn:
        # Note: asyncpg.Record objects can be directly unpacked into Pydantic models
        # if the column names match the model's field names.
        rows = await conn.fetch("SELECT timestamp, type, source, data FROM pulseboard_signals ORDER BY timestamp DESC")
    return [Signal(**row) for row in rows]

@app.get("/api/events", response_model=List[Event])
async def get_events():
    """Retrieve all events."""
    if not pool:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database pool not initialized.")
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT timestamp, name, description, source, data FROM pulseboard_events ORDER BY timestamp DESC")
    return [Event(**row) for row in rows]

@app.get("/api/emails", response_model=List[Email])
async def get_emails():
    """Retrieve all emails."""
    if not pool:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database pool not initialized.")
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT timestamp, sender, subject, body_snippet, is_read, data FROM pulseboard_emails ORDER BY timestamp DESC")
    return [Email(**row) for row in rows]

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Retrieve combined data for the dashboard."""
    if not pool:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database pool not initialized.")
    async with pool.acquire() as conn:
        signals_raw = await conn.fetch("SELECT timestamp, type, source, data FROM pulseboard_signals ORDER BY timestamp DESC LIMIT 10")
        events_raw = await conn.fetch("SELECT timestamp, name, description, source, data FROM pulseboard_events ORDER BY timestamp DESC LIMIT 10")
        emails_raw = await conn.fetch("SELECT timestamp, sender, subject, body_snippet, is_read, data FROM pulseboard_emails ORDER BY timestamp DESC LIMIT 10")

    return {
        "signals": [Signal(**row) for row in signals_raw],
        "events": [Event(**row) for row in events_raw],
        "emails": [Email(**row) for row in emails_raw]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18880)
