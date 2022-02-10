from datetime import datetime, timedelta


class DateHandler:
    def __init__(self, date: datetime = None):
        self._current_date: datetime = date
        self._date_tuple = ()

    def parse_today_word(self) -> None:
        self._date_tuple = (self._current_date, None)

    def parse_tomorrow_word(self):
        self._date_tuple = (self._current_date + timedelta(days=1), None)

    def parse_double_date(self, string: str) -> None:
        self._get_full_date([string.split('-')[0], string.split('-')[1]])

    def parse_single_date(self, string: str) -> None:
        self._get_full_date([string, None])

    def get_current_date_object(self) -> datetime:
        return self._current_date

    def get_string(self) -> tuple:
        return \
            self._date_tuple[0].strftime("%d.%m.%Y"), \
            self._date_tuple[1].strftime("%d.%m.%Y") if self._date_tuple[1] else None

    def _get_full_date(self, dates: list) -> None:
        date_list = [self._parse_date_string(dates[0])]

        if self._is_date_less_current(date_list[0]):
            date_list[0] = self._add_year(date_list[0])

        if dates[1]:
            date_list.append(self._parse_date_string(dates[1]))
            if self._is_final_date_less(date_list[1], date_list[0]):
                date_list[1] = self._add_year(dates[1])

        self._date_tuple = (date_list[0], date_list[1] if dates[1] else None)

    def _parse_date_string(self, string: str) -> datetime:
        return datetime.strptime(f"{string}.{self._current_date.year}", "%d.%m.%Y")

    def _is_date_less_current(self, date: datetime) -> bool:
        return date.month - self._current_date.month < 0

    @staticmethod
    def _is_final_date_less(final_date: datetime, initial_date: datetime) -> bool:
        return (final_date - initial_date).days < 0

    @staticmethod
    def _add_year(date: datetime) -> datetime:
        return datetime(year=date.year + 1, month=date.month, day=date.day)
