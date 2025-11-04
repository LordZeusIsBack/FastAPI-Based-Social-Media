from fastapi import FastAPI, HTTPException
from src.schemas import PostCreate
from src.db import create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager


@asynccontextmanager
async def life_span(fast_api_app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=life_span)
