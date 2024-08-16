from .base import db, TABLENAMES
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from typing import List

TB = TABLENAMES['cne']
FORM_TB = TABLENAMES['form']


class Cne(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(50), unique=True)

    forms: Mapped[List[FORM_TB['tb']]] = relationship(
        back_populates=TB['singular'])
