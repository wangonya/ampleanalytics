from fastapi import APIRouter, Depends

from app.models.user import Token, User, UserCreate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", response_model=Token)
def login():
    return UserService().login_user(form_data)


@router.get("/me", response_model=User)
def get_current_user(
    current_user=Depends(UserService().get_current_user),
):
    return current_user


@router.post("", response_model=User)
def create_user(new_user: UserCreate):
    return UserService().create_user(new_user)
