from .base import db, TABLENAMES, ID_VAL_MSG, NUMBER_VAL_MSG
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates
from sqlalchemy import ForeignKey

from typing import List

TB = TABLENAMES['block']
COMMUNE_TB = TABLENAMES['commune']
PRTY_TB = TABLENAMES['prty']


class Block(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int]
    commune_id: Mapped[int] = mapped_column(ForeignKey(
        f"{COMMUNE_TB['singular']}.id"))
    commune: Mapped[COMMUNE_TB['tb']] = relationship(
        back_populates=TB['plural'], uselist=False)

    properties: Mapped[List[PRTY_TB['tb']]] = relationship(
        back_populates=TB['singular'])

    @validates('number')
    def validate_number(self, key, value):
        try:
            int(value)
        except Exception:
            raise ValueError(NUMBER_VAL_MSG.format(key))
        return value

    @validates('commune_id')
    def validate_cne(self, key, value):
        try:
            int(value)
        except Exception:
            raise ValueError(ID_VAL_MSG)
        return value
