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
    description = sa.Column(
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
