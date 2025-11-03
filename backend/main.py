from contextlib import asynccontextmanager
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import os

from database import engine, Base, get_db
from models import RecordsDB, UserDB
from schemas import Records, User, Token

#--------------------------------------------------------
# Configuration & Initialization
#--------------------------------------------------------

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup encryption and authentication
load_dotenv()
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)  # Don't auto error for optional auth

# Lifespan event to create tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    yield

# Initialize FastAPI app
app = FastAPI(title="CRM Kanban API", version="1.0.0", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#--------------------------------------------------------
# Utility functions
#--------------------------------------------------------

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ENCRYPTION_KEY, algorithm=ALGORITHM)

# Dependency to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(credentials.credentials, ENCRYPTION_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"email": email, "user_id": user_id}
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

#--------------------------------------------------------
# API Endpoints
#--------------------------------------------------------

# Register a new user
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: User, db: AsyncSession = Depends(get_db)):
    logger.info(f"Registration attempt for email: {user.email}")
    
    try:
        # Check if user exists
        result = await db.execute(select(UserDB).where(UserDB.email == user.email))
        existing_user = result.scalars().first()
        
        if existing_user:
            logger.warning(f"Registration failed: Email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = pwd_context.hash(user.password)
        db_user = UserDB(email=user.email, password_hash=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"User registered successfully: {user.email}")
        return {"message": "User created successfully", "email": user.email}
        
    except IntegrityError as e:
        logger.error(f"Database integrity error during registration: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Login for user
@app.post("/login", response_model=Token)
async def login(user: User, db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt for email: {user.email}")
    
    try:
        result = await db.execute(select(UserDB).where(UserDB.email == user.email))
        db_user = result.scalars().first()
        
        if not db_user:
            logger.warning(f"Login failed: User {user.email} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not pwd_context.verify(user.password, db_user.password_hash):
            logger.warning(f"Login failed: Invalid password for {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        access_token = create_access_token(
            data={"sub": db_user.email, "user_id": db_user.user_id}
        )
        
        logger.info(f"Login successful for: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Get all CRM records
@app.get("/crm")
async def get_crm(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        result = await db.execute(select(RecordsDB).where(RecordsDB.user_id == user_id))
        crm_entries = result.scalars().all()
        return crm_entries
    except Exception as e:
        logger.error(f"Error fetching CRM entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch records"
        )

# Add a new CRM record
@app.post("/crm")
async def add_crm(entry: Records, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        entry_data = entry.model_dump() # Override the user_id from token (don't trust frontend)
        entry_data["user_id"] = user_id
        db_entry = RecordsDB(**entry_data)
        db.add(db_entry)
        await db.commit()
        await db.refresh(db_entry)
        return db_entry
    except Exception as e:
        logger.error(f"Error adding CRM entry: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create record"
        )

# Update a CRM record
@app.put("/crm/{record_id}")
async def update_crm(record_id: int, crm_update: Records, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        # Only allow users to update their own records
        result = await db.execute(select(RecordsDB).where(RecordsDB.id == record_id, RecordsDB.user_id == user_id))
        db_entry = result.scalars().first()
        
        if not db_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CRM entry not found")
        
        for field, value in crm_update.model_dump(exclude_unset=True).items():
            if field != "user_id":  # Don't allow changing user_id
                setattr(db_entry, field, value)
        
        await db.commit()
        await db.refresh(db_entry)
        return db_entry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating CRM entry: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update record"
        )

# Delete a CRM record
@app.delete("/crm/{record_id}")
async def delete_crm(record_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        stmt = select(RecordsDB).where(
            RecordsDB.id == record_id,
            RecordsDB.user_id == user_id
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        await db.delete(record)
        await db.commit()
    except Exception as e:
        logger.error(f"Error deleting CRM entry: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete record"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    