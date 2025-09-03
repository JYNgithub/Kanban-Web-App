from sqlalchemy import Column, Integer, String
from database import Base

class BookDB(Base):
    __tablename__ = "books"
    __table_args__ = {'schema': 'my_schema'}  
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    status = Column(String, nullable=False)
