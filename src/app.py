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

@app.post('/upload')
async def upload_post(
        file: UploadFile = File(...),
        caption: str = Form(''),
        session: AsyncSession = Depends(get_async_session)
        ) -> PostResponse:
    post = Post(caption=caption, url='fake_url', file_type='photo', file_name='fake_name')
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return PostResponse.model_validate(post)
