from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class RecordsDB(Base):
    __tablename__ = "records"
    __table_args__ = {'schema': 'my_schema'}  
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    
class UserDB(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'my_schema'}
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    
