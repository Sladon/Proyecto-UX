from .base import db, TABLENAMES, ID_VAL_MSG, NUMBER_VAL_MSG, VAL_MSG
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates
from sqlalchemy import ForeignKey
from datetime import date

from typing import Optional

TB = TABLENAMES['multi_prty']
PRTY_TB = TABLENAMES['prty']
PERSON_TB = TABLENAMES['person']
FORM_TB = TABLENAMES['form']

P_MIN, P_MAX = 0, 100
PERCENTAGE_RANGE_VAL = VAL_MSG.format(f': {P_MIN} <= valor <= {P_MAX}')
FINAL_VIG_YEAR_VAL = VAL_MSG.format('igual o mayor al inicial')


class MultiProperty(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey(f"{PRTY_TB['singular']}.id"))
    property: Mapped[PRTY_TB['tb']] = relationship(
        back_populates=TB['plural'], uselist=False)
    person_id: Mapped[int] = mapped_column(
        ForeignKey(f"{PERSON_TB['singular']}.id"))
    person: Mapped["Person"] = relationship(
        back_populates=TB['plural'], uselist=False)
    percentage: Mapped[float] = mapped_column(nullable=True)
    pages: Mapped[Optional[int]]
    inscription_date: Mapped[Optional[date]]
    inscription_number: Mapped[Optional[int]]
    initial_vigency_year: Mapped[int]
    final_vigency_year: Mapped[Optional[int]]
    
    form_id: Mapped[int] = mapped_column(
        ForeignKey(f"{FORM_TB['singular']}.id"))
    form: Mapped[FORM_TB['tb']] = relationship(back_populates=TB['plural'])

    @validates('percentage')
    def validate_percentage(self, key, value):
        return value
        if value is None:
            return value
        try:
            if value:
                float(value)
        except ValueError:
            raise ValueError(PERCENTAGE_RANGE_VAL.format(key))
        is_valid = P_MIN <= value <= P_MAX
        if not is_valid:
            raise ValueError(PERCENTAGE_RANGE_VAL.format(key))
        return value

    @validates('pages')
    def validate_number(self, key, value):
        try:
            int(value)
        except Exception:
            raise ValueError(NUMBER_VAL_MSG.format(key))
        return value

    @validates('final_vigency_year')
    def validate_final_vigency_year(self, key, value):
        if value is None:
            return value
        try:
            int(value)
        except Exception:
            raise ValueError(FINAL_VIG_YEAR_VAL.format(key))
        if value < self.initial_vigency_year:
            raise ValueError(FINAL_VIG_YEAR_VAL.format(key))
        return value
