from typing import Any

from fastapi import Depends, APIRouter, Response
from sqlalchemy.orm import Session

from app.core.datatable import UseDatatable
from app.core.logger import LOGGER
from app.core.response import success_response, error_response, SuccessResponseSchema
from app.datatables.user import UserDataTable
from app.dependency import common
from app.repositories.user import user_repo
from app.schemas.user import UserUpdateRequest, UserCreateRequest, UserResponse, UserDatatableResponse

router = APIRouter()


@router.get("/", response_model=UserDatatableResponse)
async def get_users(
        *,
        db: Session = Depends(common.get_db),
        response: Response,
        user_datatable: UserDataTable = Depends(UseDatatable(UserDataTable, logger=LOGGER))
) -> Any:
    """
    Retrieve users.
    """
    return await user_datatable.render(db, response)


@router.post("/", response_model=UserResponse)
async def create_user(
        *,
        db: Session = Depends(common.get_db),
        response: Response,
        user_in: UserCreateRequest,
) -> Any:
    """
    Create new user.
    """
    user = user_repo.create(db, obj_in=user_in)
    return success_response(
        message="Create new user successfully!",
        data=user,
        response=response,
    )


@router.get("/{id}", response_model=UserResponse)
async def read_user_by_id(
        *,
        db: Session = Depends(common.get_db),
        response: Response,
        id: int,
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_repo.find(db, id=id)
    if not user:
        return error_response(
            response=response,
            message="User not found!",
        )
    return success_response(
        response=response,
        message="",
        data=user
    )


@router.put("/{id}", response_model=UserResponse)
async def update_user(
        *,
        db: Session = Depends(common.get_db),
        response: Response,
        id: int,
        user_in: UserUpdateRequest,
) -> Any:
    """
    Update a user.
    """
    user = user_repo.find(db, id=id)
    if not user:
        return error_response(
            response=response,
            message="User not found!",
        )

    user = user_repo.update(db, db_obj=user, obj_in=user_in)
    return success_response(
        message="Update user successfully!",
        data=user,
        response=response,
    )


@router.delete("/{id}", response_model=SuccessResponseSchema)
async def remove_user(
        *,
        db: Session = Depends(common.get_db),
        response: Response,
        id: int,
) -> Any:
    """
    Update a user.
    """
    user = user_repo.find(db, id=id)
    if not user:
        return error_response(
            response=response,
            message="User not found!",
        )

    user_repo.remove(db, id=id, model=user)
    return success_response(
        message="Remove user successfully!",
        data=None,
        response=response,
    )
