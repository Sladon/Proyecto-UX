import re
from datetime import datetime


def convert_to_type(value, v_type):
    try:
        if v_type is datetime:
            return datetime.strptime(value, '%Y-%m-%d')
        return v_type(value)
    except Exception:
        return None


def get_verification_digit(remainder: int):
    if remainder == 0:
        return '0'
    elif remainder == 1:
        return 'K'
    return str(11-remainder)


def format_run(str_run) -> str:
    run, verificator = str_run.split("-")
    if '.' not in run:
        groups = [run[max(0, i-3):i] for i in range(len(run), 0, -3)]
        str_run = ".".join(groups[::-1])+'-'+verificator
    return str_run
