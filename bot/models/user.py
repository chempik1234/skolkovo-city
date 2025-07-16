from pydantic import EmailStr, BaseModel


class UserModel(BaseModel):
    telegram_id: int
    # full_name: str | None
    # email: EmailStr | None
    # personal_data_agreement: bool
    is_admin: bool
    is_banned: bool
    language: str
