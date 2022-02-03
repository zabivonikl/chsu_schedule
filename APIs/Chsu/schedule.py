import datetime


class Schedule:
    def __init__(self, id_type: str, json: list):
        self._nullify_fields()
        self._response_json = json
        for self._couple in self._response_json:
            self._split_if_another_day()
            self._add_couple_to_string(id_type)

    def __iter__(self):
        return (i for i in self._response or ["Расписание не найдено.\n"])

    def _nullify_fields(self):
        self._response = []
        self._couple = {}
        self._current_date = datetime.datetime(1970, 1, 1)

    def _split_if_another_day(self):
        if not self._is_current_date():
            self._update_current_and_add_day()

    def _is_current_date(self):
        return self._current_date.strftime("%d.%m.%Y") == self._couple['dateEvent']

    def _update_current_and_add_day(self):
        self._current_date = datetime.datetime.strptime(self._couple['dateEvent'], "%d.%m.%Y")
        weekdays = ["Понедельник", "Вторник", "Среду", "Четверг", "Пятницу", "Субботу", "Воскресение"]
        self._response.append(
            f'\n==Расписание на {weekdays[self._current_date.weekday()].lower()}, '
            f'{self._current_date.strftime("%d.%m.%Y")}==\n'
        )

    def _add_couple_to_string(self, id_type):
        self._response[-1] += self._get_couple_time()
        self._response[-1] += self._get_discipline_string()
        self._response[-1] += self._get_professors_names() if id_type == 'student' \
            else self._get_groups_names()
        self._response[-1] += self._get_location()
        self._response[-1] += "\n"

    def _get_couple_time(self):
        return f"{self._couple['startTime']}-{self._couple['endTime']}\n"

    def _get_discipline_string(self):
        if self._couple["abbrlessontype"]:
            self._couple["abbrlessontype"] += "., "
        return f'''{self._couple["abbrlessontype"] or ''}{self._couple['discipline']['title']}\n'''

    def _get_professors_names(self):
        response = ""
        for professor in self._couple['lecturers']:
            response += f"{professor['fio']}, "
        return response[:-2] + "\n"

    def _get_groups_names(self):
        response = ""
        for group in self._couple['groups']:
            response += f"{group['title']}, "
        return response[:-2] + "\n"

    def _get_location(self):
        return "Онлайн\n" if self._couple['online'] == 1 else self._get_address()

    def _get_address(self):
        return f"{self._couple['build']['title']}, аудитория {self._couple['auditory']['title']}\n"
