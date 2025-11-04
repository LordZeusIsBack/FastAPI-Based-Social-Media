from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from src.schemas import PostResponse, UserRead, UserCreate, UserUpdate
from src.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from src.multipart_files import image_kit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
from uuid import UUID
import tempfile
from src.users import auth_backend, current_active_user, fastapi_user


@asynccontextmanager
async def life_span(fast_api_app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=life_span)
app.include_router(fastapi_user.get_auth_router(auth_backend), prefix='/auth/jwt', tags=['auth'])
app.include_router(fastapi_user.get_register_router(UserRead, UserCreate), prefix='/auth/jwt', tags=['auth'])
app.include_router(fastapi_user.get_reset_password_router(), prefix='/auth', tags=['auth'])
app.include_router(fastapi_user.get_verify_router(UserRead), prefix='/auth', tags=['auth'])
app.include_router(fastapi_user.get_users_router(UserRead, UserUpdate), prefix='/auth', tags=['auth'])

@app.post('/upload')
async def upload_post(
        file: UploadFile = File(...),
        caption: str = Form(''),
        user: User = Depends(current_active_user),
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
                user_id=user.id,
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
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
        ) -> dict:
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}
    post_data = [
        {
            'id': str(post.id),
            'user_id': str(post.user_id),
            'caption': post.caption,
            'url': post.url,
            'file_type': post.file_type,
            'file_name': post.file_name,
            'created_at': post.created_at.isoformat(),
            'is_owner': post.user_id == user.id,
            "email": user_dict.get(post.user_id, "Unknown")
        }
        for post in posts
    ]
    return {'posts': post_data}

@app.delete('/post/{post_id}')
async def delete_post(
        post_id: str,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
    ) -> dict[str, bool]:
    try:
        post_uuid = UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        if not post: raise HTTPException(status_code=404, detail='Post ID wrong!')
        if post.user_id != user.id: raise HTTPException(status_code=403, detail="You don't have permission!")
        await session.delete(post)
        await session.commit()
        return {'success': True}
    except Exception as error: raise HTTPException(status_code=500, detail=str(error))
