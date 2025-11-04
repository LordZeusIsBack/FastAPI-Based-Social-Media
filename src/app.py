from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from src.schemas import PostResponse
from src.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from src.multipart_files import image_kit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
from uuid import uuid4
import tempfile


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
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        upload_result = image_kit.upload(
            file=open(temp_file_path , 'rb'),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=['backend-upload']
            )
        )
        if upload_result.response_metadata.http_status_code == 200:
            post = Post(
                caption=caption,
                url=upload_result.url,
                file_type='video' if file.content_type.startswith('video') else 'image',
                file_name=upload_result.name
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return PostResponse.model_validate(post)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

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
