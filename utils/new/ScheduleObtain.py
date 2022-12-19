import math

from ortools.sat.python import cp_model
from tabulate import tabulate


# The scheduling dimension.
class ScheduleObtain(cp_model.CpSolverSolutionCallback):

    # The class constructor.
    def __init__(self, num_of_days: int, num_of_shifts_per_day: int, list_of_shifts: dict):
        # Call the super method.
        cp_model.CpSolverSolutionCallback.__init__(self)
        # The number of possible solutions.
        self.solution_count = 0
        # The max solution limit.
        self.solution_limit = 2
        # Store the number of days.
        self.num_of_days = num_of_days
        # Store the number of shifts per day.
        self.num_of_shifts_per_day = num_of_shifts_per_day
        # Compute the total number of shifts.
        self.num_of_shifts_total = num_of_days * num_of_shifts_per_day
        # The list of all shifts.
        self.list_of_shifts = list_of_shifts
        # The possible schedules.
        self.possible_schedules = {}

    # Print the solutions
    def on_solution_callback(self):
        # Increase the solution count.
        self.solution_count += 1
        # The json data.
        shifts = {}
        # Iterate through every shift.
        for shift in range(self.num_of_shifts_total):
            # Obtain the shift tasks string.
            shifts[shift] = self.obtain_shift_tasks_dictionary(shift)
        # Append the result to the solution list.
        self.possible_schedules[self.solution_count - 1] = shifts
        # Check if enough solutions have been reached.
        if self.solution_count >= self.solution_limit:
            # Display the stop searching text.
            print('Stop search after %i solutions' % self.solution_limit)
            # Finish the search.
            self.StopSearch()

    # Obtain the shift tasks string.
    def obtain_shift_tasks_dictionary(self, shift: int) -> dict:
        # Obtain the task data for each shift.
        tasks = self.list_of_shifts[shift]['tasks']
        # The string for all tasks.
        dict_of_tasks = {}
        # Iterate through each task
        for task_id, task in tasks.items():
            # Obtain the person data for each shift-task.
            people = task['people']
            # Iterate through each person and obtain a string with all participants.
            dict_of_tasks[task_id] = [
                (person_id if self.Value(person['var']) == 1 else None) for person_id, person in people.items()
            ]
        # Join and return the string.
        return dict_of_tasks
