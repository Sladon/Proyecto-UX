from .base import db, TABLENAMES, NUMBER_VAL_MSG
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates
from sqlalchemy import ForeignKey

from typing import List, Optional

TB = TABLENAMES['prty']
BLOCK_TB = TABLENAMES['block']
FORM_TB = TABLENAMES['form']
MULTI_PRTY_TB = TABLENAMES['multi_prty']


class Property(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int]

    block_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"{BLOCK_TB['singular']}.id"))
    block: Mapped[Optional[BLOCK_TB['tb']]] = relationship(
        back_populates=TB['plural'])

    forms: Mapped[List[FORM_TB['tb']]] = relationship(
        back_populates=TB['singular'])
    multi_properties: Mapped[List[MULTI_PRTY_TB['tb']]
                             ] = relationship(back_populates=TB['singular'])

    @validates('number')
    def validate_number(self, key, value):
        try:
            int(value)
        except Exception:
            raise ValueError(NUMBER_VAL_MSG.format(key))
        return value
