from .base import db, TABLENAMES
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from typing import List

TB = TABLENAMES['region']
COMMUNE_TB = TABLENAMES['commune']
REGION_TB = TABLENAMES['region']


class Region(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(50), unique=True)
    order: Mapped[int]
    short_desc: Mapped[str] = mapped_column(String(40))

    communes: Mapped[List[COMMUNE_TB['tb']]] = relationship(
        back_populates=REGION_TB['singular'])
