import math

from ortools.sat.python import cp_model
from tabulate import tabulate


# The scheduling dimension.
class ScheduleDisplay(cp_model.CpSolverSolutionCallback):

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

    # Print the solutions
    def on_solution_callback(self):
        # Increase the solution count.
        self.solution_count += 1
        # The list of all shift strings.
        shift_strings = []
        # The full list of tasks.
        full_task_list = [task for task in list(self.list_of_shifts.values())[0]['tasks']]
        # Construct the first row string.
        shift_strings.append(full_task_list)
        # Split the days.
        previous_day = 0
        # Iterate through every shift.
        for shift in range(self.num_of_shifts_total):
            # Obtain the shift date string.
            shift_date_str = self.obtain_shift_date_string(shift)
            # Obtain the shift tasks string.
            list_of_shift_tasks_strs = self.obtain_shift_tasks_string(shift)
            # Join the result.
            full_shift_string = [shift_date_str] + list_of_shift_tasks_strs
            # Obtain the day.
            current_day = math.floor(shift / self.num_of_shifts_per_day)
            # Check if the last day changed.
            if previous_day != current_day:
                # Update the previous day.
                previous_day = current_day
                # Append an empty array.
                shift_strings.append([' ' for _ in range(len(full_task_list) + 1)])
            # Append to the shift strings.
            shift_strings.append(full_shift_string)
        # Print the result.
        print(tabulate(shift_strings, headers="firstrow", tablefmt="fancy_grid"))
        # Check if enough solutions have been reached.
        if self.solution_count >= self.solution_limit:
            # Display the stop searching text.
            print('Stop search after %i solutions' % self.solution_limit)
            # Finish the search.
            self.StopSearch()

    # Obtain the shift date string.
    def obtain_shift_date_string(self, shift: int) -> str:
        # Obtain the day.
        day = math.floor(shift / self.num_of_shifts_per_day)
        # Obtain the shift of day.
        shift_number_of_day = (shift % self.num_of_shifts_per_day)
        # Obtain the start time.
        start_string_time = (
                str(int(24 * (shift_number_of_day / self.num_of_shifts_per_day))).zfill(2)
                + ':' +
                str(int(24 * (shift_number_of_day / self.num_of_shifts_per_day) * 60 % 60)).zfill(2)
        )
        # Obtain the end time.
        end_string_time = (
                str(int(24 * ((shift_number_of_day + 1) / self.num_of_shifts_per_day))).zfill(2)
                + ':' +
                str(int(24 * ((shift_number_of_day + 1) / self.num_of_shifts_per_day) * 60 % 60)).zfill(2)
        )
        # Obtain the day.
        day_string = str(day).zfill(2)
        # Return the string.
        return f"Day {day_string} <> {start_string_time} - {end_string_time}"

    # Obtain the shift tasks string.
    def obtain_shift_tasks_string(self, shift: int) -> list:
        # Obtain the task data for each shift.
        tasks = self.list_of_shifts[shift]['tasks']
        # The string for all tasks.
        list_of_tasks = []
        # Iterate through each task
        for task_id, task in tasks.items():
            # Obtain the person data for each shift-task.
            people = task['people']
            # Iterate through each person and obtain a string with all participants.
            list_of_tasks.append('[' + ','.join([
                (f'{person_id}' if self.Value(person['var']) == 1 else '_') for person_id, person in people.items()
            ]) + ']')
        # Join and return the string.
        return list_of_tasks
