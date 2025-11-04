from datetime import datetime
from zoneinfo import ZoneInfo
import os
from collections.abc import AsyncGenerator
from uuid import uuid4
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv('DATABASE_URL')

class Post(DeclarativeBase):
    __tablename__ = 'posts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(ZoneInfo('Asia/Kolkata')))
