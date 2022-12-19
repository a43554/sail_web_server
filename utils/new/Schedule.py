import math
from typing import List, Any, Tuple, Union, Optional
from ortools.sat.python import cp_model

from utils.new.ScheduleObtain import ScheduleObtain
from utils.new.ScheduleOptions import ScheduleOptions


# The schedule class.
class Schedule:

    # The class constructor.
    def __init__(self, num_of_shifts_total: int, num_of_shifts_per_day: int, list_of_people: List):
        # Call the super function.
        super().__init__()
        # Store the number of days.
        self.num_of_days = math.ceil(num_of_shifts_total / num_of_shifts_per_day)
        # Store the number of shifts per day.
        self.num_of_shifts_per_day = num_of_shifts_per_day
        # Compute the total number of shifts.
        self.num_of_shifts_total = num_of_shifts_total
        # The list of people to participate.
        self.list_of_people_by_name = list_of_people
        # The list of people to participate.
        self.list_of_people_by_id = list_of_people
        # The dictionary mapping the list of people.
        self.dictionary_of_people = dict([(person, idx) for idx, person in enumerate(list_of_people)])
        # The task dictionary.
        self.task_dictionary = {}

        # The task's dictionary.
        self.TASKS = {}
        # The shift's dictionary.
        self.SHIFTS = {}
        # The people's dictionary.
        self.PEOPLE = {}
        # Combination of shift task.
        self.SHIFT_HAS_TASK = {}

        # Store the callback.
        self.display_results = None

        # Create the model.
        self.model = None

    # Add a task.
    def add_task(
            self,
            # The name of the current task.
            task_name: str,
            # All people that can work on this task. Possible values:
            # 1) List of Strings - with every individual that is qualified for the task.
            # 2) String - with the single individual with the qualifications.
            # 3) ScheduleOptions.ALL - Option to select everyone. [DEFAULT]
            list_of_qualified_people: Union[List[str], str] = ScheduleOptions.ALL,
            # Every single shift where it would be possible to execute this task. Possible values:
            # 1) List of Ints - with every shift that the task can be executed in.
            # 2) Int - The single shift where this task can be executed in.
            # 3) ScheduleOptions.ALL - Option to select every turn. [DEFAULT]
            list_of_possible_shifts: Union[List[int], int, str] = ScheduleOptions.ALL,
            # Every other task that cannot be executed at the same time by the same person. Possible values:
            # 1) List of Strings - with every task that the person doing the current task cannot also do.
            # 2) String - the single task that the other user cannot do at the same time as the current one.
            # 3) ScheduleOptions.ALL - Option to select all the tasks.
            # 3) ScheduleOptions.NONE - Option to make this task not occupy any other. [DEFAULT]
            list_of_task_the_qualified_person_cannot_overlap_with: Union[List[str], str] = ScheduleOptions.NONE,
            # The amount of people that must be present in order to complete this task. Possible values:
            # 1) Int - The amount of people present in order to complete this task in a shift. [DEFAULT = 1]
            # 2) Tuple of (Int, Int) - A Tuple containing both the min and max amount of people per task shift.
            # 3) ScheduleOptions.ALL - Option to make this task require every single person.
            people_per_task: Union[Tuple[int, int], int, str] = 1,
            # The task's shift cycle settings. Possible values:
            # 1) Tuple of (Int, Int) - A Tuple containing both the required amount of task assigned shifts that must
            #                          be completed and the amount of shifts that makes up a cycle.
            #                          within a given cycle.
            # 2) ScheduleOptions.NONE - Option not to apply task cycle settings. [DEFAULT]
            tasks_per_shift_cycle: Union[Tuple[int, int], str] = ScheduleOptions.NONE,
            # The task's people cycle settings. Possible values:
            # 1) Tuple of (Int, Int) - A Tuple containing both the required amount of tasks that EACH person
            #                          must complete and the amount of shifts that makes up a cycle.
            #                          within each cycle.
            # 2) ScheduleOptions.NONE - Option not to apply people cycle settings. [DEFAULT]
            people_per_shift_cycle: Union[Tuple[int, int], str] = ScheduleOptions.NONE,
            # Sequential task settings. Possible values:
            # 1) Tuple of (Int, Boolean) - A Tuple containing both the amount of shifts that must be done
            #                              sequentially and a boolean indicating whether the shifts can contain
            #                              the same people (TRUE) or if they must contain different people (FALSE).
            # 2) ScheduleOptions.NONE - Option not to apply sequential settings. [DEFAULT]
            shift_task_sequential_settings: Union[Tuple[int, int], str] = ScheduleOptions.NONE
    ):
        # Store the current task in the dictionary.
        self.task_dictionary[task_name] = {
            # The task's name.
            'name': task_name,
            # The full list of people qualified for this task.
            'qualified_people': list_of_qualified_people,
            # The full list of shifts possible for this task to occur in.
            'possible_shifts': list_of_possible_shifts,
            # The tasks that this task overlaps with within a shift must not have the same person.
            'no_individual_with_tasks': list_of_task_the_qualified_person_cannot_overlap_with,
            # Minimum and maximum amount of people per task.
            'min_max_people_per_task': people_per_task,
            # This Tasks' cycle settings.
            'per_task_cycle_settings': tasks_per_shift_cycle,
            # The cycle settings.
            'per_person_cycle_settings': people_per_shift_cycle,
            # The sequential settings.
            'sequential_settings': shift_task_sequential_settings
        }

    # Add the json task.
    def quick_add_task(self, data: dict):
        # Add the task
        self.task_dictionary[data['name']] = data

    # Run the solver.
    def solve(self):
        # The task's dictionary.
        self.TASKS = dict([
            (task['name'], {'info': task, 'shifts': {}, 'people': {}})
            for
            task
            in
            list(self.task_dictionary.values())
        ])
        # The shift's dictionary.
        self.SHIFTS = dict([
            (shift, {'info': shift, 'people': {}, 'tasks': {}})
            for
            shift
            in
            range(0, self.num_of_shifts_total)
        ])
        # The people's dictionary.
        self.PEOPLE = dict([
            (person, {'info': person, 'tasks': {}, 'shifts': {}})
            for
            person
            in
            list(self.dictionary_of_people.keys())
        ])

        self.SHIFT_HAS_TASK = dict([
            (task['name'], {'info': task, 'shifts': {}})
            for
            task
            in
            list(self.task_dictionary.values())
        ])

        # Create the model.
        self.model = cp_model.CpModel()

        # Iterate through all tasks.
        for task_id, task_data in self.TASKS.items():
            # Iterate through all shifts.
            for shift_id, shift_data in self.SHIFTS.items():
                # Get the shift-task link.
                shift_task_link = shift_data['tasks'].setdefault(task_id, {'info': task_data['info'], 'people': {}})
                # Get the task-shift link.
                task_shift_link = task_data['shifts'].setdefault(shift_id, {'info': shift_id, 'people': {}})
                # Iterate through all people.
                for person_id, person_data in self.PEOPLE.items():
                    # Create the variable.
                    variable = self.model.NewBoolVar(
                        f'shift:{shift_id}///task:{task_id}///person:{person_id}'
                    )
                    # Get the person-task link.
                    person_task_link = person_data['tasks'].setdefault(
                        task_id, {'info': task_data['info'], 'shifts': {}}
                    )
                    # Append the shift to the person-task link.
                    person_task_link['shifts'][shift_id] = {'info': shift_id, 'var': variable}

                    # Get the person-shift link.
                    person_shift_link = person_data['shifts'].setdefault(
                        shift_id, {'info': shift_id, 'tasks': {}}
                    )
                    # Append the task to the person-shift link.
                    person_shift_link['tasks'][task_id] = {'info': task_data['info'], 'var': variable}

                    # Append the person to the shift-task link.
                    shift_task_link['people'][person_id] = {'info': person_id, 'var': variable}

                    # Get the shift-person link.
                    shift_person_link = shift_data['people'].setdefault(
                        person_id, {'info': person_id, 'tasks': {}}
                    )
                    # Append the task to the shift-person link.
                    shift_person_link['tasks'][task_id] = {'info': task_data['info'], 'var': variable}

                    # Append the person to the task-shift link.
                    task_shift_link['people'][person_id] = {'info': person_id, 'var': variable}

                    # Get the task-person link.
                    task_person_link = task_data['people'].setdefault(
                        person_id, {'info': person_id, 'shifts': {}}
                    )
                    # Append the shift to the task-person link.
                    task_person_link['shifts'][shift_id] = {'info': shift_id, 'var': variable}
                # Add it to the add task.
                total_variable = self.model.NewBoolVar(f'shift:{shift_id}///task:{task_id}///Total')
                # Store it.
                self.SHIFT_HAS_TASK[task_id]["shifts"][shift_id] = total_variable
                # Obtain the variable sum.
                variable_sum = sum([
                    person_data['var'] for person_data in self.TASKS[task_id]['shifts'][shift_id]['people'].values()
                ])
                # Make sure the total matches.
                self.model.Add(variable_sum > 0).OnlyEnforceIf(total_variable)
                self.model.Add(variable_sum == 0).OnlyEnforceIf(total_variable.Not())

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 1 -> Tasks can only occur in their respective shifts
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_1()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 2 -> Tasks can only be performed by their respective people.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_2()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 3 -> Tasks that overlap must not be occupied by the same individual.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_3()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 4 -> Only a certain amount of people may occupy a single task.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_4()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 5 -> Tasks that require sequential shifts done by the same person must be enforced.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_5()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 6 -> Tasks that require sequential shifts may want to diversify the amount of people.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_6()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 7 -> Tasks that require only X shifts per cycle for a specific task must be enforced.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_7()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 8 -> Tasks that require only X shifts per cycle done by the same person must be enforced.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_8()

        # Create the solver.
        solver = cp_model.CpSolver()
        # Set the linearization level.
        solver.parameters.linearization_level = 0
        # Enumerate all solutions.
        solver.parameters.enumerate_all_solutions = True
        # Prepare the printer
        self.display_results = ScheduleObtain(self.num_of_days, self.num_of_shifts_per_day, self.SHIFTS)
        # Solve the problem.
        solver.Solve(self.model, self.display_results)
        # Return the list of results.
        return self.display_results.possible_schedules


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 1 -> Tasks can only occur in their respective shifts
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_1(self):
        # Iterate through each task.
        for task_id, task in self.TASKS.items():
            # Obtain all the possible shifts.
            possible_shifts = self.get_all_possible_shifts(task_id)
            # Iterate through each shift.
            for shift_id, shift in task['shifts'].items():
                # Iterate through each person.
                for person_id, person in shift['people'].items():
                    # Check if this shift should have this task.
                    if shift_id not in possible_shifts:
                        # Type is of list, and incorrect shift, variable should not be filled.
                        self.model.Add(person['var'] == 0)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 2 -> Tasks can only be performed by their respective people.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_2(self):
        # Iterate through each task.
        for task_id, task in self.TASKS.items():
            # Obtain all the qualified people.
            qualified_people = self.get_all_qualified_people(task_id)
            # Iterate through each shift.
            for shift_id, shift in task['shifts'].items():
                # Iterate through each person.
                for person_id, person in shift['people'].items():
                    # Check if this person should have this task.
                    if person_id not in qualified_people:
                        # Type is of list, and incorrect shift, variable should not be filled.
                        self.model.Add(person['var'] == 0)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 3 -> Tasks that overlap must not be occupied by the same individual.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_3(self):
        # Iterate through each shift.
        for shift_id, shift in self.SHIFTS.items():
            # Iterate through each task.
            for task_id, task in shift['tasks'].items():
                # Obtain the list of tasks not be overlapped with.
                no_overlaps = self.get_all_conflicting_tasks(task_id)
                # Check if the list is empty.
                if len(no_overlaps) == 0:
                    # List is empty, skip this task.
                    continue
                # Obtain all conflicting task names.
                conflicting_tasks = no_overlaps
                # Iterate through each person in this task/shift combination.
                for person_id, person in task['people'].items():
                    # Obtain all tasks related to this individual within this shift.
                    personal_tasks = shift['people'][person_id]['tasks']
                    # Iterate through the other conflicting tasks.
                    conflicting_variables = [
                        personal_tasks[conflict_task]['var'] for conflict_task in conflicting_tasks
                    ]
                    # Create the constraint expression.
                    constraint_expression = (
                            sum(conflicting_variable for conflicting_variable in conflicting_variables) == 0
                    )
                    # Obtain the task's assigned person.
                    self.model.Add(constraint_expression).OnlyEnforceIf(personal_tasks[task_id]['var'])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 4 -> Only a certain amount of people may occupy a single task.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_4(self):
        # Iterate through each shift.
        for shift_id, shift in self.SHIFTS.items():
            # Iterate through each task.
            for task_id, task in shift['tasks'].items():
                # Check if this shift should have this task.
                if shift_id not in self.get_all_possible_shifts(task_id):
                    # Skip this task for this shift.
                    continue
                # Perform the sum of all variables.
                variable_sum = sum(person['var'] for person_id, person in task['people'].items())
                # Obtain the maximum and minimum people per task.
                min_people_per_task, max_people_per_task = self.get_min_max_people_per_task(task_id)
                # Force that a task must have at least the minimum amount of people.
                self.model.Add(variable_sum >= min_people_per_task)
                # Force that a task must have at most the maximum amount of people.
                self.model.Add(variable_sum <= max_people_per_task)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 5 -> Tasks that require sequential shifts done by the same person must be enforced.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_5(self):
        # Iterate through each task.
        for task_id, task in self.TASKS.items():
            # Iterate through each person.
            for person_id, person in task['people'].items():
                # Check if this person should have this task.
                if person_id not in self.get_all_qualified_people(task_id):
                    # Skip this individual.
                    continue
                # Obtain a list of variables shift values for this person and task.
                shift_variables = (
                    [shift_item['var'] for shift_item in person['shifts'].values()]
                )
                # Obtain the sequential settings.
                sequential_settings = self.get_sequential_settings(task_id)
                # Check if sequential shifts are required.
                if sequential_settings is not None:
                    # Obtain the settings.
                    shifts_in_a_row, diversify_shifts = sequential_settings
                    # Check if sequential shifts cannot be equal.
                    if diversify_shifts:
                        # Iterate through all shifts enumerated.
                        for shift_idx in range(1, len(shift_variables) - shifts_in_a_row):
                            # The start of shifts.
                            previous_shift = shift_variables[shift_idx - 1]
                            # The next N shifts.
                            current_shifts = shift_variables[
                                             shift_idx: shift_idx + shifts_in_a_row
                                             ]
                            # The end of shifts.
                            after_shift = shift_variables[shift_idx + shifts_in_a_row]
                            # If all current shifts are occupied, previous shift must not be occupied.
                            # current_shifts => NOT previous_shift
                            self.model.AddBoolOr([previous_shift.Not()]).OnlyEnforceIf(current_shifts)
                            # Can't be partially assigned to the next shifts, if not assigned to the last or next one.
                            # NOT previous_shift AND current_shifts[0] => current_shifts
                            self.model.AddBoolAnd(
                                current_shifts
                            ).OnlyEnforceIf([previous_shift.Not(), current_shifts[0]])  # TODO APPLY TO ALL OCCURRENCES
                    # Sequential shifts can be equal.
                    else:
                        # Iterate through all shifts enumerated.
                        for shift_idx in range(0, len(shift_variables)):
                            # The start of shifts.
                            previous_shift = shift_variables[shift_idx - 1] if (shift_idx > 0) else 0
                            # The next N shifts.
                            current_shifts = shift_variables[
                                             shift_idx: shift_idx + shifts_in_a_row
                                             ]
                            # The end of shifts.
                            after_shift = shift_variables[
                                shift_idx + shifts_in_a_row
                                ] if (shift_idx < len(shift_variables) - shifts_in_a_row) else 0
                            # If previous shift was assigned, cannot be assigned to all the next shifts.
                            self.model.Add(
                                previous_shift + sum(current_shifts) != shifts_in_a_row + 1
                            )
                            # If assigned to all the next shifts, shift after that cannot be assigned to.
                            self.model.Add(
                                sum(current_shifts) + after_shift != shifts_in_a_row + 1
                            )
                            # Check if this index is smaller than 1.
                            if shift_idx < 1:
                                # Can't be partially assigned to the next shifts, if not assigned to the last/next one.
                                self.model.Add(
                                    sum(current_shifts) == shifts_in_a_row
                                ).OnlyEnforceIf(current_shifts[0])
                            # If not the first iteration.
                            else:
                                # Can't be partially assigned to the next shifts, if not assigned to the last/next one.
                                self.model.Add(
                                    sum(current_shifts) == shifts_in_a_row
                                ).OnlyEnforceIf([previous_shift.Not(), current_shifts[0]])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 6 -> Tasks that require sequential shifts may want to diversify the amount of people.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_6(self):
        # Iterate through each task.
        for task_id, task in self.TASKS.items():
            # Obtain the sequential settings.
            sequential_settings = self.get_sequential_settings(task_id)
            # Check to see if sequential shifts within this task must not differ.
            if sequential_settings is None:
                # Skip this task.
                continue
            # Obtain the settings.
            shifts_in_a_row, diversify_shifts = sequential_settings
            # Check if diversify is enabled.
            if not diversify_shifts:
                # Skip this task.
                continue
            # Create a tuple list with all the shifts
            shift_list = list(task['shifts'].items())
            # The list of possible shifts.
            possible_shifts = self.get_all_possible_shifts(task_id)
            # Iterate through all shifts.
            for shift_idx, shift_item in enumerate(shift_list[:-1]):
                # Obtain the current shift data.
                current_shift_id, current_shift = shift_item
                # Obtain the next shift data.
                next_shift_id, next_shift = shift_list[shift_idx + 1]
                # Check if these sequential shifts both have this task.
                if (
                        (current_shift_id not in possible_shifts) or (next_shift_id not in possible_shifts)
                ):
                    # Skip this task for this shift.
                    continue
                # Obtain all variables for this shift.
                current_vars = [person['var'] for person in current_shift['people'].values()]
                # Obtain all variables for the next shift.
                next_vars = [person['var'] for person in next_shift['people'].values()]
                # Apply the rules for differentiation.
                current_vars_prepared = [(current_vars[i] * (2 ** i)) for i in range(0, len(self.PEOPLE))]
                # Apply the rules for differentiation.
                next_vars_prepared = [(next_vars[i] * (2 ** i)) for i in range(0, len(self.PEOPLE))]
                # Apply the rule.
                self.model.Add(sum(current_vars_prepared) != sum(next_vars_prepared))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 7 -> Tasks that require only X shifts per cycle for a specific task must be enforced.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_7(self):
        # Iterate through each task.
        for task_id, task in self.SHIFT_HAS_TASK.items():
            # Obtain the task settings.
            task_cycle_settings = self.get_task_cycle_settings(task_id)
            # Check if cycles are enabled:
            if task_cycle_settings is None:
                # Skip, cycles not enabled.
                continue
            # Obtain the number of shifts per cycle.
            num_of_assigned_tasks, num_of_shifts_per_cycle = task_cycle_settings
            # This task's shifts.
            task_shifts = list(task['shifts'].values())
            # Iterate through each shift.
            for shift_idx in range(0, self.num_of_shifts_total - num_of_shifts_per_cycle + 1):
                # Grab N shifts at a time.
                n_shifts = task_shifts[shift_idx:shift_idx + num_of_shifts_per_cycle]
                # Amount must be exact.
                self.model.Add(sum(n_shifts) == num_of_assigned_tasks)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 8 -> Tasks that require only X shifts per cycle done by the same person must be enforced.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_8(self):
        # Iterate through each task.
        for task_id, task in self.TASKS.items():
            # Obtain the task settings.
            person_cycle_settings = self.get_people_cycle_settings(task_id)
            # Check if cycles are enabled:
            if person_cycle_settings is None:
                # Skip, cycles not enabled.
                continue
            # Obtain the number of shifts per cycle.
            num_of_assigned_shifts, num_of_shifts_per_cycle = person_cycle_settings
            # Iterate through each person.
            for person_id, person in task['people'].items():
                # Check if this person should have this task.
                if person_id not in self.get_all_qualified_people(task_id):
                    # Skip this individual.
                    continue
                # Obtain a list of variables shift values for this person and task.
                shift_variables = (
                    [shift_item['var'] for shift_item in person['shifts'].values()]
                )
                # Iterate through all shifts enumerated.
                for shift_idx in range(0, len(shift_variables) - num_of_shifts_per_cycle + 1):
                    # The next N shifts.
                    cycle_shifts = shift_variables[shift_idx: shift_idx + num_of_shifts_per_cycle]
                    # Amount must be exact.
                    self.model.Add(sum(cycle_shifts) == num_of_assigned_shifts)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # UTILITY FUNCTIONS
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Return the list of all valid shifts.
    def get_all_possible_shifts(self, task_id: str) -> List:
        # Obtain the task data.
        current_task_info = self.task_dictionary[task_id]
        # Get the shift info.
        shift_info = current_task_info['valid_shifts']
        # Make a decision based on the type.
        if type(shift_info) is list:
            # Return the list of shifts.
            return shift_info
        # Else, check if it's of type int.
        elif type(shift_info) is int:
            # Return a list with the int.
            return [shift_info]
        # Else, check if it's of type all.
        elif shift_info == ScheduleOptions.ALL:
            # Select every shift.
            return list(self.SHIFTS.keys())
        # Else, check if it's of type dict.
        elif type(shift_info) is dict:
            # Check if the type is single.
            if shift_info['setting_type'] == ScheduleOptions.SETTING:
                # Check the value.
                if shift_info['setting_value'] == ScheduleOptions.ALL:
                    # Select every shift.
                    return list(self.SHIFTS.keys())
                # Otherwise, raise an exception.
                else:
                    # Raise an exception.
                    raise KeyError("'Possible shifts' input is of invalid type")
            # Check if the type is dict.
            elif shift_info['setting_type'] == ScheduleOptions.DATA:
                # Check the value.
                if type(shift_info['setting_value']) is list:
                    # Select every shift.
                    return list(shift_info['setting_value'])
                # Otherwise, raise an exception.
                else:
                    # Raise an exception.
                    raise KeyError("'Possible shifts' input is of invalid type")
            # Otherwise, raise an exception.
            else:
                # Raise an exception.
                raise KeyError("'Possible shifts' input is of invalid type")
        # Otherwise, raise an exception.
        else:
            # Raise an exception.
            raise KeyError("'Possible shifts' input is of invalid type")

    # Return the list of all valid people.
    def get_all_qualified_people(self, task_id: str) -> List:
        # Obtain the task data.
        current_task_info = self.task_dictionary[task_id]
        # Get the shift info.
        qualified_people = current_task_info['qualified_people']
        # Make a decision based on the type.
        if type(qualified_people) is list:
            # Return the list of shifts.
            return qualified_people
        # Else, check if it's of type all.
        elif qualified_people == ScheduleOptions.ALL:
            # Select every person.
            return list(self.PEOPLE.keys())
        # Else, check if it's of type str.
        elif type(qualified_people) is str and (qualified_people in self.PEOPLE):
            # Return a list with the person.
            return [qualified_people]
        # Otherwise, raise an exception.
        else:
            # Raise an exception.
            raise KeyError("'Qualified people' input is of invalid type")

    # Return the list of all valid people.
    def get_all_conflicting_tasks(self, task_id: str) -> List:
        # Obtain the task data.
        current_task_info = self.task_dictionary[task_id]
        # Get the shift info.
        overlapping_tasks = current_task_info['no_individual_with_tasks']
        # Make a decision based on the type.
        if type(overlapping_tasks) is list:
            # Return the list of tasks, but only those in the info.
            return [task_id for task_id in overlapping_tasks if task_id in self.TASKS]
        # Else, check if it's of type all.
        elif overlapping_tasks == ScheduleOptions.ALL:
            # Select every task.
            return list(self.TASKS.keys())
        # Else, check if it's of type none.
        elif overlapping_tasks == ScheduleOptions.NONE:
            # Select no task.
            return []
        # Else, check if it's of type str.
        elif type(overlapping_tasks) is str and (overlapping_tasks in self.TASKS):
            # Return a list with the person.
            return [task_id for task_id in [overlapping_tasks] if task_id in self.TASKS]
        # Otherwise, raise an exception.
        else:
            # Raise an exception.
            raise KeyError("'Overlapping task' input is of invalid type")

    # Return the tuple of min and max people per task in a shift.
    def get_min_max_people_per_task(self, task_id: str) -> Tuple[int, int]:
        # Obtain the task data.
        current_task_info = self.task_dictionary[task_id]
        # Get the shift info.
        min_max_people_per_task = current_task_info['people_per_shift_task']
        # Make a decision based on the type.
        if type(min_max_people_per_task) is tuple:
            # Both tuple values.
            min_value, max_value = min_max_people_per_task
            # Check if any of the values is the all.
            if min_value == ScheduleOptions.NONE:
                # Set the first element as 0.
                min_value = 0
            # Check if any of the values is the all.
            elif min_value == ScheduleOptions.ALL:
                # Set the first element as 0.
                min_value = len(self.PEOPLE)
            # Check if any of the values is the all.
            if max_value == ScheduleOptions.NONE:
                # Set the first element as 0.
                max_value = 0
            # Check if any of the values is the all.
            elif max_value == ScheduleOptions.ALL:
                # Set the first element as 0.
                max_value = len(self.PEOPLE)
            # Return the tuple of people.
            return min_value, max_value
        # Else, check if it's of type all.
        elif min_max_people_per_task == ScheduleOptions.ALL:
            # Select every task.
            return len(self.PEOPLE), len(self.PEOPLE)
        # Else, check if it's of type str.
        elif type(min_max_people_per_task) is int:
            # Return a list with the person.
            return min_max_people_per_task, min_max_people_per_task
        # Else, check if it's of type dict.
        elif type(min_max_people_per_task) is dict:
            # Check if the type is single.
            if min_max_people_per_task['setting_type'] == ScheduleOptions.SETTING:
                # Check the value.
                if min_max_people_per_task['setting_value'] == ScheduleOptions.ALL:
                    # Select every shift.
                    return len(self.PEOPLE), len(self.PEOPLE)
                # Otherwise, raise an exception.
                else:
                    # Raise an exception.
                    raise KeyError("'Possible shifts' input is of invalid type")
            # Check if the type is dict.
            elif min_max_people_per_task['setting_type'] == ScheduleOptions.DATA:
                # Check the values.
                return (
                    min_max_people_per_task['setting_value']['min_amount'],
                    min_max_people_per_task['setting_value']['max_amount']
                )
            # Otherwise, raise an exception.
            else:
                # Raise an exception.
                raise KeyError("'Possible shifts' input is of invalid type")
        # Otherwise, raise an exception.
        else:
            # Raise an exception.
            raise KeyError("'Min/Max people per task' input is of invalid type")

    # Return the list of all shift task cycles.
    def get_task_cycle_settings(self, task_id: str) -> Optional[Tuple[int, int]]:
        # Obtain the task data.
        current_task_info = self.task_dictionary[task_id]
        # Get the shift info.
        task_cycle_settings = current_task_info['per_task_cycle_settings']
        # Make a decision based on the type.
        if type(task_cycle_settings) is tuple:
            # Return the tuple of people.
            return task_cycle_settings
        # Else, check if it's of type all.
        elif task_cycle_settings == ScheduleOptions.NONE:
            # Select nothing.
            return None
        # Else, check if it's of type dict.
        elif type(task_cycle_settings) is dict:
            # Check if the type is single.
            if task_cycle_settings['setting_type'] == ScheduleOptions.SETTING:
                # Check the value.
                if task_cycle_settings['setting_value'] == ScheduleOptions.NONE:
                    # Select every shift.
                    return None
                # Otherwise, raise an exception.
                else:
                    # Raise an exception.
                    raise KeyError("'Task cycle settings' input is of invalid type")
            # Check if the type is dict.
            elif task_cycle_settings['setting_type'] == ScheduleOptions.DATA:
                # Check the values.
                return (
                    task_cycle_settings['setting_value']['assigned_shifts_per_cycle'],
                    task_cycle_settings['setting_value']['total_shifts_per_cycle']
                )
            # Otherwise, raise an exception.
            else:
                # Raise an exception.
                raise KeyError("'Task cycle settings' input is of invalid type")
        # Otherwise, raise an exception.
        else:
            # Raise an exception.
            raise KeyError("'Task cycle settings' input is of invalid type")

    # Return the list of all valid people.
    def get_people_cycle_settings(self, task_id: str) -> Optional[Tuple[int, int]]:
        # Obtain the task data.
        current_task_info = self.task_dictionary[task_id]
        # Get the shift info.
        task_cycle_settings = current_task_info['per_person_cycle_settings']
        # Make a decision based on the type.
        if type(task_cycle_settings) is tuple:
            # Return the tuple of people.
            return task_cycle_settings
        # Else, check if it's of type all.
        elif task_cycle_settings == ScheduleOptions.NONE:
            # Select nothing.
            return None
        # Else, check if it's of type dict.
        elif type(task_cycle_settings) is dict:
            # Check if the type is single.
            if task_cycle_settings['setting_type'] == ScheduleOptions.SETTING:
                # Check the value.
                if task_cycle_settings['setting_value'] == ScheduleOptions.NONE:
                    # Select every shift.
                    return None
                # Otherwise, raise an exception.
                else:
                    # Raise an exception.
                    raise KeyError("'Task cycle settings' input is of invalid type")
            # Check if the type is dict.
            elif task_cycle_settings['setting_type'] == ScheduleOptions.DATA:
                # Check the values.
                return (
                    task_cycle_settings['setting_value']['assigned_shifts_per_cycle'],
                    task_cycle_settings['setting_value']['total_shifts_per_cycle']
                )
            # Otherwise, raise an exception.
            else:
                # Raise an exception.
                raise KeyError("'Task cycle settings' input is of invalid type")
        # Otherwise, raise an exception.
        else:
            # Raise an exception.
            raise KeyError("'Task cycle settings' input is of invalid type")

    # Return the list of all valid people.
    def get_sequential_settings(self, task_id: str) -> Optional[Tuple[int, int]]:
        # Obtain the task data.
        current_task_info = self.task_dictionary[task_id]
        # Get the shift info.
        sequential_settings = current_task_info['sequential_settings']
        # Make a decision based on the type.
        if type(sequential_settings) is tuple:
            # Return the tuple of people.
            return sequential_settings
        # Else, check if it's of type all.
        elif sequential_settings == ScheduleOptions.NONE:
            # Select nothing.
            return None
        # Else, check if it's of type dict.
        elif type(sequential_settings) is dict:
            # Check if the type is single.
            if sequential_settings['setting_type'] == ScheduleOptions.SETTING:
                # Check the value.
                if sequential_settings['setting_value'] == ScheduleOptions.NONE:
                    # Select every shift.
                    return None
                # Otherwise, raise an exception.
                else:
                    # Raise an exception.
                    raise KeyError("'Sequential settings' input is of invalid type")
            # Check if the type is dict.
            elif sequential_settings['setting_type'] == ScheduleOptions.DATA:
                # Check the values.
                return (
                    sequential_settings['setting_value']['number_of_sequential_shifts'],
                    sequential_settings['setting_value']['diversify_cast']
                )
            # Otherwise, raise an exception.
            else:
                # Raise an exception.
                raise KeyError("'Sequential settings' input is of invalid type")
        # Otherwise, raise an exception.
        else:
            # Raise an exception.
            raise KeyError("'Sequential settings' input is of invalid type")
