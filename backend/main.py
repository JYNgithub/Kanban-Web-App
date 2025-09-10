from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import engine, Base, get_db
from models import RecordsDB
from schemas import Records

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET all CRM entries
@app.get("/crm")
async def get_crm(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecordsDB))
    crm_entries = result.scalars().all()
    return crm_entries

# POST a new CRM entry
@app.post("/crm")
async def add_crm(entry: Records, db: AsyncSession = Depends(get_db)):
    db_entry = RecordsDB(**entry.model_dump())
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry

# Update a CRM entry
@app.put("/crm/{crm_id}")
async def update_crm(crm_id: int, crm_update: Records, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecordsDB).where(RecordsDB.id == crm_id))
    db_entry = result.scalars().first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="CRM entry not found")
    for field, value in crm_update.dict(exclude_unset=True).items():
        setattr(db_entry, field, value)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry

