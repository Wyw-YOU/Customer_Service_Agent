from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt import create_access_token, get_current_user
from app.config.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db=Depends(get_db)):
    import bcrypt

    repo = UserRepository(db)
    user = await repo.get_by_username(request.username)
    if not user or not bcrypt.checkpw(request.password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token)


@router.get("/users/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user), db=Depends(get_db)):
    repo = UserRepository(db)
    u = await repo.get_by_id(int(user["sub"]))
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=u.id, username=u.username, email=u.email, phone=u.phone, role=u.role)
