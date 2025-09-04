from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import engine, Base, get_db
from models import BookDB
from schemas import Book

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

# GET all books from DB
@app.get("/books")
async def get_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookDB))
    books = result.scalars().all()
    return books

# POST a new book to DB
@app.post("/books")
async def add_book(book: Book, db: AsyncSession = Depends(get_db)):
    db_book = BookDB(title=book.title, author=book.author, status=book.status)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

# Update a book's status (or other fields)
@app.put("/books/{book_id}")
async def update_book(book_id: int, book_update: Book, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookDB).where(BookDB.id == book_id))
    db_book = result.scalars().first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Only update fields that are provided
    # if book_update.title is not None:
    #     db_book.title = book_update.title
    # if book_update.author is not None:
    #     db_book.author = book_update.author
    if book_update.status is not None:
        db_book.status = book_update.status
    
    await db.commit()
    await db.refresh(db_book)
    return db_book
