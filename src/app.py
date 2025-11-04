from fastapi import FastAPI, File, UploadFile, Form, Depends
from src.schemas import PostResponse
from src.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select


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

@app.get('/feed')
async def get_feed(
        session: AsyncSession = Depends(get_async_session)
        ) -> dict:
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = result.scalars().all()
    print(posts)
    post_data = [
        {
            'id': str(post.id),
            'caption': post.caption,
            'url': post.url,
            'file_type': post.file_type,
            'file_name': post.file_name,
            'created_at': post.created_at.isoformat()
        }
        for post in posts
    ]
    return {'posts': post_data}
