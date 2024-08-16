from .base import db, TABLENAMES, ID_VAL_MSG, NUMBER_VAL_MSG
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from datetime import date

from typing import List

TB = TABLENAMES['form']
CNE_TB = TABLENAMES['cne']
PRPTY_TB = TABLENAMES['prty']
MULT_PRTY_TB = TABLENAMES['multi_prty']


class Form(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    attention_number: Mapped[UUID]
    cne_id: Mapped[int] = mapped_column(ForeignKey(f"{CNE_TB['singular']}.id"))
    cne: Mapped[CNE_TB['tb']] = relationship(back_populates=TB['plural'])
    property_id: Mapped[int] = mapped_column(ForeignKey("property.id"))
    property: Mapped[PRPTY_TB['tb']] = relationship(
        back_populates=TB['plural'])
    pages: Mapped[int]
    inscription_date: Mapped[date]
    inscription_number: Mapped[int]
    
    multi_properties: Mapped[List[MULT_PRTY_TB['tb']]
                         ] = relationship(back_populates=TB['singular'])
    

    transactions: Mapped[List["Transaction"]
                         ] = relationship(back_populates=TB['singular'])

    def __init__(self, **kwargs):
        if 'attention_number' not in kwargs:
            kwargs['attention_number'] = uuid4()
        super().__init__(**kwargs)

    @validates('pages')
    def validate_number(self, key, value):
        try:
            int(value)
        except Exception:
            raise ValueError(NUMBER_VAL_MSG.format(key))
        return value

    @validates('inscription_number')
    def validate_number(self, key, value):
        try:
            int(value)
        except Exception:
            raise ValueError(NUMBER_VAL_MSG.format(key))
        return value

    @validates('cne_id')
    def validate_cne(self, key, value):
        try:
            int(value)
        except Exception:
            raise ValueError(ID_VAL_MSG)
        return value
