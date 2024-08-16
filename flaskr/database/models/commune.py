from .base import db, TABLENAMES
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from typing import List

TB = TABLENAMES['commune']
REGION_TB = TABLENAMES['region']


class Commune(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(40), unique=True)

    region_id: Mapped[int] = mapped_column(
        ForeignKey(f"{REGION_TB['singular']}.id"))
    region: Mapped[REGION_TB['tb']] = relationship(back_populates=TB['plural'])

    blocks: Mapped[List["Block"]] = relationship(back_populates=TB['singular'])
