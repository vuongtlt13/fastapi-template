@router.put("/me", response_model=UserInfo)
def update_user_me(
        *,
        db: Session = Depends(common.get_db),
        password: str = Body(None),
        full_name: str = Body(None),
        email: EmailStr = Body(None),
        current_user: User = Depends(common.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdateRequest(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = user_repo.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=UserInfo)
def read_user_me(
        db: Session = Depends(common.get_db),
        current_user: User = Depends(common.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
