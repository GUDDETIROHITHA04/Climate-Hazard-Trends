from datetime import date


def last_complete_year() -> int:
    return date.today().year - 1
