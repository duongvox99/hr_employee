# TODO: In production, use proper OAuth2 with JWT tokens, just use simple base64 encoding for demo purposes.

import base64
import json

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer()


def decode_token(token: str) -> dict:
    """
    Decode a simple base64 token.

    In production, use proper JWT library like python-jose.
    For this demo, we use a simple base64 encoded JSON.
    """
    try:
        token_data = base64.b64decode(token.encode()).decode()
        return json.loads(token_data)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from the token.

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    token_data = decode_token(token)

    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    return user


def create_access_token(user_id: int) -> str:
    """
    Create a simple access token for a user.

    In production, use proper JWT with expiration, signing, etc.
    """
    token_data = {"user_id": user_id}
    token_json = json.dumps(token_data)
    return base64.b64encode(token_json.encode()).decode()
