class ScheduleParser:
    def __init__(self):
        self._response_json = None

    def _init_(self):
        self._nullify_fields()

    def _nullify_fields(self):
        self._response = []
        self._lesson = {}
        self._current_date = ""

    def parse_json(self, id_type, json):
        self._nullify_fields()
        self._response_json = json
        for self._lesson in self._response_json:
            self._split_if_another_day()
            self._add_lesson_to_string(id_type)
        return self._response

    def _split_if_another_day(self):
        if not self._is_current_date():
            self._update_current_and_add_day()

    def _is_current_date(self):
        return self._current_date == self._lesson['dateEvent']

    def _update_current_and_add_day(self):
        self._current_date = self._lesson['dateEvent']
        self._response.append(f'\n=====Расписание на {self._current_date}=====\n')

    def _add_lesson_to_string(self, id_type):
        self._response[len(self._response) - 1] += self._get_lesson_time()
        self._response[len(self._response) - 1] += self._get_discipline_string()
        self._response[len(self._response) - 1] += self._get_professors_names() if id_type == 'student' \
            else self._get_groups_names()
        self._response[len(self._response) - 1] += self._get_location()
        self._response[len(self._response) - 1] += "\n"

    def _get_lesson_time(self):
        return f"{self._lesson['startTime']}-{self._lesson['endTime']}\n"

    def _get_discipline_string(self):
        return f"{self._lesson['abbrlessontype'] or ''}., {self._lesson['discipline']['title']}\n"

    def _get_professors_names(self):
        response = ""
        for professor in self._lesson['lecturers']:
            response += f"{professor['fio']}, "
        return response[:-2] + "\n"

    def _get_groups_names(self):
        response = ""
        for group in self._lesson['groups']:
            response += f"{group['title']}, "
        return response[:-2] + "\n"

    def _get_location(self):
        return "Онлайн\n" if self._lesson['online'] == 1 else self._get_address()

    def _get_address(self):
        return f"{self._lesson['build']['title']}, аудитория {self._lesson['auditory']['title']}\n"

    @staticmethod
    def get_empty_response():
        return ["На текущий промежуток времени расписание не найдено\n"]
