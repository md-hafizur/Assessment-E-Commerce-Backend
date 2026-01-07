import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTPBearer scheme for token authentication
bearer_scheme = HTTPBearer()


def get_user_from_token(
    credential: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decode JWT token, and get user from database.
    
    This dependency is intended to be used by other dependencies.
    """
    logger.info(f"Received credentials: {credential.credentials}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credential.credentials
    
    # It seems that in some cases, the scheme is still present in the credentials.
    # We will manually remove it to be safe.
    if token.lower().startswith("bearer "):
        token = token[7:]
    
    logger.info(f"Token after stripping 'bearer ': {token}")
    
    payload = decode_access_token(token)
    logger.info(f"Decoded payload: {payload}")
    
    if payload is None:
        # The decode_access_token function now raises an HTTPException,
        # so this check might be redundant, but we keep it for safety.
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    logger.info(f"User ID from token: {user_id}")
    
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    logger.info(f"User from database: {user}")
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_user(
    user: User = Depends(get_user_from_token)
) -> User:
    """
    Get the current user, and check if they are active.
    """
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges. Admin access required."
        )
    return current_user
