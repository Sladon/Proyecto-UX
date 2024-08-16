from .base import db, TABLENAMES
from flaskr.helpers.utils import get_verification_digit, format_run
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates
from sqlalchemy import String

from typing import List

TB = TABLENAMES['person']
TRANS_TB = TABLENAMES['transaction']
MULT_PRTY_TB = TABLENAMES['multi_prty']

RUN_FORMAT_VAL_MSG = ("Formato del RUN invalido, formato: 123.456.789-0"
                      " o 123456789-0")
RUN_VER_VAL_MSG = "RUN invalido, el número verificador no corresponde"


class Person(db.Model):
    __tablename__ = TB['singular']
    id: Mapped[int] = mapped_column(primary_key=True)
    run: Mapped[str] = mapped_column(String(12), unique=True)

    transactions: Mapped[List[TRANS_TB['tb']]
                         ] = relationship(back_populates=TB['singular'])
    multi_properties: Mapped[List[MULT_PRTY_TB['tb']]
                             ] = relationship(back_populates=TB['singular'])

    @validates('run')
    def validate_run(self, key, value):
        is_valid = value.count('-') == 1
        if not is_valid:
            raise ValueError(RUN_FORMAT_VAL_MSG)
        value = value.replace(".", "")
        str_digits, verification_digit = value.split('-')

        digits = []
        for str_digit in str_digits:
            try:
                digit = int(str_digit)
                digits.append(digit)
            except ValueError:
                raise ValueError(RUN_FORMAT_VAL_MSG)

        num_sum = 0
        multiplier = 2
        for digit in reversed(digits):
            num_sum += digit * multiplier
            multiplier = 2 if multiplier == 7 else multiplier + 1

        remainder = num_sum % 11
        ver_digit = get_verification_digit(remainder)
        is_valid = ver_digit == verification_digit
        if not is_valid:
            raise ValueError(RUN_VER_VAL_MSG)
        return format_run(value)
