import math
from typing import Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.http import HttpResponseNotFound
from scheduling.models.ScheduleModel import Schedule
from scheduling.models.TaskModel import Task


# The page for displaying a schedule.
class TaskSchedulePage(LoginRequiredMixin, APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]
    # The template's name.
    template_name = 'demos/main/plan/schedules/schedule_page.html'
    # The login url.
    login_url = '/login'

    # Obtain the shift date string.
    @staticmethod
    def obtain_shift_date_string(shift: int, shifts_per_day: int) -> str:
        # Obtain the day.
        day = math.floor(shift / shifts_per_day)
        # Obtain the shift of day.
        shift_number_of_day = (shift % shifts_per_day)
        # Obtain the start time.
        start_string_time = (
                str(int(24 * (shift_number_of_day / shifts_per_day))).zfill(2)
                + ':' +
                str(int(24 * (shift_number_of_day / shifts_per_day) * 60 % 60)).zfill(2)
        )
        # Obtain the end time.
        end_string_time = (
                str(int(24 * ((shift_number_of_day + 1) / shifts_per_day))).zfill(2)
                + ':' +
                str(int(24 * ((shift_number_of_day + 1) / shifts_per_day) * 60 % 60)).zfill(2)
        )
        # Obtain the day.
        day_string = str(day).zfill(2)
        # Return the string.
        return f"{start_string_time}\n{end_string_time}"

    # The GET method for this class.
    def get(self, request, schedule_id: str):
        # Attempt to get a schedule.
        schedule = Schedule.objects.filter(name=schedule_id).first()
        # Check if not schedule was found.
        if schedule is None:
            # Raise the 404 exception.
            return HttpResponseNotFound(f'No schedule with ID \'{schedule_id}\' was found.')
        # Obtain the solution values.
        shift_values = list(list(schedule.last_solutions.values())[0].values())
        # The crew members.
        crew = [handler.name for handler in schedule.handlers.all()]
        # The amount of shifts per day.
        shifts_per_day = schedule.total_shifts_per_day
        # Obtain the times.
        times = [
            [
                self.obtain_shift_date_string(i, shifts_per_day)
            ] for i in range(schedule.total_shift_amount)
        ]
        # Map the context.
        context = {
            # Store the solutions.
            'schedule_data': {
                # Store the tasks.
                'tasks': [Task.objects.get(name=t_name).display_name for t_name in list(shift_values[0].keys())],
                # The name of the various people.
                'crew': crew,
                # The various shifts.
                'shifts': [[times[idx]] + list(shift_data.values()) for idx, shift_data in enumerate(shift_values)],
                # The shift info by crew member.
                'shifts_by_crew': [
                    [times[idx]] + [
                        [
                            Task.objects.get(name=t_name).display_name for t_name, t_crew in task_info.items() if crew_member in t_crew
                        ] for crew_member in crew
                    ] for idx, task_info in enumerate(shift_values)
                ]
            }
        }
        # Return the response with the html content.
        return Response(context)
