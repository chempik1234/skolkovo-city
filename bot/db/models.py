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
    title_ru: Mapped[str] = sa.Column(
        sa.String(length=256),
        nullable=False
    )
    title_en: Mapped[str] = sa.Column(
        sa.String(length=256),
        nullable=True
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
    order_num = sa.Column(
        sa.Integer,
        nullable=False,
        unique=False
    )

    images_urls = sa.Column(
        sa.ARRAY(sa.Text),
        nullable=True
    )
    videos_urls = sa.Column(
        sa.ARRAY(sa.Text),
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
    # full_name: Mapped[str] = sa.Column(
    #     sa.String(length=256),
    #     nullable=True
    # )
    # email: Mapped[str] = sa.Column(
    #     sa.String(length=256),
    #     nullable=True
    # )
    is_admin: Mapped[bool] = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False
    )
    is_banned: Mapped[bool] = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
    )
    # personal_data_agreement: Mapped[bool] = sa.Column(
    #     sa.Boolean(),
    #     nullable=False,
    #     default=False
    # )

    language: Mapped[str] = sa.Column(
        sa.String(),
        nullable=False,
        default="ru",
    )


class QuestionDataModel(Base):
    __tablename__ = "question"
    id: Mapped[int] = sa.Column(
        sa.Integer,
        primary_key=True,
        autoincrement=True
    )
    question: Mapped[str] = sa.Column(
        sa.Text,
        nullable=False,
    )
    answer_ru: Mapped[str] = sa.Column(
        sa.Text,
        nullable=True,
    )
    answer_en: Mapped[str] = sa.Column(
        sa.Text,
        nullable=True,
    )
    embedding = sa.Column(
        sa.LargeBinary,
        nullable=True,
    )

    category_id = sa.Column(
        sa.ForeignKey("category.id", ondelete="SET_NULL"),
        nullable=True,
    )
    category: Mapped["CategoryDataModel"] = relationship()
