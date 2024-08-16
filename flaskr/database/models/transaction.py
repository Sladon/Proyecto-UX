from .base import db, TABLENAMES, VAL_MSG
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates
from sqlalchemy import ForeignKey

TB = TABLENAMES['transaction']
FORM_TB = TABLENAMES['form']
PERSON_TB = TABLENAMES['person']

P_MIN, P_MAX = 0, 100
PERCENTAGE_RANGE_VAL = VAL_MSG.format(f': {P_MIN} <= valor <= {P_MAX}')


class Transaction(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    form_id: Mapped[int] = mapped_column(
        ForeignKey(f"{FORM_TB['singular']}.id"))
    form: Mapped[FORM_TB['tb']] = relationship(back_populates=TB['plural'])
    person_id: Mapped[int] = mapped_column(ForeignKey("person.id"))
    person: Mapped[PERSON_TB['tb']] = relationship(back_populates=TB['plural'])
    percentage: Mapped[float] = mapped_column(nullable=True)
    is_buyer: Mapped[bool]

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
        is_valid = 0 <= value <= 100
        if not is_valid:
            raise ValueError(PERCENTAGE_RANGE_VAL.format(key))
        return value

class TransactionCopy:
    def __init__(self, form, person, percentage):
        self.form = form
        self.person = person
        self.percentage = percentage