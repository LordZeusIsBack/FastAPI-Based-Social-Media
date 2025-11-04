import os
from uuid import UUID
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy, BearerTransport
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.db import User, get_user_db

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f'User {user.id} has been created!')

    async def on_after_forgot_password(self, user: models.UP, token: str, request: Request | None = None) -> None:
        print(f'User {user.id} has been forgotten! Reset Token: {token}')

    async def on_after_request_verify(self, user: models.UP, token: str, request: Request | None = None) -> None:
        print(f'Verification requested for User {user.id}. Verification Token: {token}')


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    return UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')

def get_jwt_strategy():
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name='jwt',
    transport = bearer_transport,
    get_strategy=get_jwt_strategy
)

fastapi_user = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_user.current_user(active=True)
