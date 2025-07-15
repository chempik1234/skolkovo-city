from pydantic import EmailStr, BaseModel


class UserModel(BaseModel):
    telegram_id: int
    full_name: str | None
    email: EmailStr | None
    is_admin: bool
    personal_data_agreement: bool
    language: str
