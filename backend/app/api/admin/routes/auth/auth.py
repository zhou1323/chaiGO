from typing import Annotated, Any

from app.api.admin.model.user import UserPublic, UserRegister, ResetPassword
from app.api.admin.service.user_service import user_service
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.common.response.response_schema import ResponseModel, response_base
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


# Use the OAuth2 mechanism provided by fastapi
@router.post("/sign-in")
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> ResponseModel:
    data = await user_service.login(
        session=session, email=form_data.username, password=form_data.password
    )
    return await response_base.success(data=data)


@router.get("/verification-code")
async def send_verification_code(email: str, session: SessionDep) -> ResponseModel:
    verification_code = await user_service.generate_verification_code(email)
    await user_service.send_verification_email(session, email, verification_code)
    return await response_base.success()


@router.post("/sign-up")
async def sign_up(session: SessionDep, user_in: UserRegister) -> ResponseModel:
    await user_service.register_user_with_verification(session, user_in)
    return await response_base.success()


@router.post("/sign-out")
async def logout(user: CurrentUser) -> ResponseModel:
    await user_service.logout(id=user.id)
    return await response_base.success()


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.get("/recover-password")
async def recover_password(email: str, session: SessionDep) -> ResponseModel:
    await user_service.recover_password(session, email)
    return await response_base.success()


@router.post("/reset-password/")
async def reset_password(session: SessionDep, body: ResetPassword) -> ResponseModel:
    user_service.reset_password(
        session=session, token=body.token, new_password=body.new_password
    )
    return await response_base.success()


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    return user_service.reset_password_html_content(session, email)
