import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from .base import Base


class CategoryDataModel(Base):
    __tablename__ = "category"
    id: Mapped[int] = sa.Column(
        sa.Integer,
        primary_key=True,
        autoincrement=True
    )
    title: Mapped[str] = sa.Column(
        sa.String(length=256),
        nullable=False
    )
    description_ru = sa.Column(
        sa.Text,
        nullable=True
    )
    description_en = sa.Column(
        sa.Text,
        nullable=True
    )
    link = sa.Column(
        sa.Text,
        nullable=True
    )

    parent_id = sa.Column(
        sa.ForeignKey("category.id", ondelete="CASCADE"),
        nullable=True,
    )
    parent: Mapped["CategoryDataModel"] = relationship()


class UserDataModel(Base):
    __tablename__ = "user"
    telegram_id: Mapped[int] = sa.Column(
        sa.BigInteger(),
        primary_key=True,
    )
    full_name: Mapped[str] = sa.Column(
        sa.String(length=256),
        nullable=True
    )
    email: Mapped[str] = sa.Column(
        sa.String(length=256),
        nullable=True
    )
    is_admin: Mapped[bool] = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False
    )
    personal_data_agreement: Mapped[bool] = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False
    )

    language: Mapped[str] = sa.Column(
        sa.String(),
        nullable=False,
        default="ru",
    )
