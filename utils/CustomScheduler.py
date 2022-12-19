from ortools.sat.python import cp_model
from functools import reduce


# Performs scheduling functions.
class CustomScheduler:
    # Print each solution.
    class PartialSolutionPrinter(cp_model.CpSolverSolutionCallback):

        # The constructor for the printer.
        def __init__(self, shifts, num_people, num_days, num_shifts, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_people = num_people
            self._num_days = num_days
            self._num_shifts = num_shifts
            self._solution_count = 0
            self._solution_limit = limit

        def on_solution_callback(self):
            # Increase the solution count.
            self._solution_count += 1
            # Print the solution number.
            print(
                '\n'
                +
                ''.join((['-' for _ in range(self._num_days * 32)]))
                +
                '\n'
                +
                f'Solution {self._solution_count}/{self._solution_limit}\t|'
                +
                ''.join(([f'\t\tDAY {i + 1}\t\t\t|' for i in range(self._num_days)]))
                +
                '\n'
                +
                ''.join((['-' for _ in range(self._num_days * 32)]))
            )
            # Loop for each shift.
            for s in range(self._num_shifts):
                # The format strings.
                start_string_time = (
                        str(int(24 * (s / self._num_shifts))).zfill(2)
                        + ':' +
                        str(int(24 * (s / self._num_shifts) * 60 % 60)).zfill(2)
                )
                # The format strings.
                end_string_time = (
                        str(int(24 * ((s + 1) / self._num_shifts))).zfill(2)
                        + ':' +
                        str(int(24 * ((s + 1) / self._num_shifts) * 60 % 60)).zfill(2)
                )
                # The first shift.
                display_str = f'| {start_string_time}-{end_string_time}\t|'
                # Loop for each day.
                for d in range(self._num_days):
                    # Loop for each person.
                    for p in range(self._num_people):
                        # Check if this person is working.
                        if self.Value(self._shifts[(p, d, s)]):
                            # Person is working, append their text.
                            display_str += f' PERSON {chr(ord("A") + p)}\t|'
                # Display the string.
                print(display_str)
            # Supply some spacing.
            print('\n')
            # Check if enough solutions have been reached.
            if self._solution_count >= self._solution_limit:
                # Display the stop searching text.
                print('Stop search after %i solutions' % self._solution_limit)
                # Finish the search.
                self.StopSearch()

            # for d in range(self._num_days):
            #     print('Day %i' % d)
            #     for n in range(self._num_people):
            #         is_working = False
            #         for s in range(self._num_shifts):
            #             if self.Value(self._shifts[(n, d, s)]):
            #                 is_working = True
            #                 turns = ['\t \t' for _ in range(0, self._num_shifts)]
            #                 turns[s] = '\tX\t'
            #                 print('Person %i must keep watch during shifts: %s' % (n, '|'.join(turns)))
            #         if not is_working:
            #             turns = ['\t \t' for _ in range(0, self._num_shifts)]
            #             print('Person %i must keep watch during shifts: %s' % (n, '|'.join(turns)))

        # Return the solution count.
        def solution_count(self):
            # Return the total amount of solutions.
            return self._solution_count

    # @staticmethod
    # # Create a sleep schedule.
    # def sleep_schedule(
    #         # The number of days to be scheduled.
    #         num_of_days: int,
    #         # The number of shifts for each day.
    #         num_of_shifts_per_day: int,
    #         # The number of people to fill out the shifts/days.
    #         num_of_people: int,
    # ):
    #     # Create an array for each variable.
    #     days_array = range(num_of_days)
    #     shifts_array = range(num_of_shifts_per_day)
    #     people_array = range(num_of_people)
    #     # Create the model.
    #     model = cp_model.CpModel()
    #     # Dictionary containing the information about the shifts.
    #     shifts = {}
    #     # Iterate through each person in the array.
    #     for p in people_array:
    #         # Iterate through each day in the array.
    #         for d in days_array:
    #             # Iterate through each shift in the array.
    #             for s in shifts_array:
    #                 # Store the value.
    #                 shifts[(p, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (p, d, s))
    #
    #     # # # # # # # # # # #
    #     # Condition - ONLY 1 PERSON PER SHIFT.
    #     #
    #     # Iterate through each day in the array.
    #     for d in days_array:
    #         # Iterate through each shift in the array.
    #         for s in shifts_array:
    #             # Add the condition to the array.
    #             model.Add(sum(shifts[(p, d, s)] for p in people_array) == 1)
    #
    #     # # # # # # # # # # #
    #     # Condition - ONLY 1 SHIFT PER PERSON IN A SINGLE DAY.
    #     #
    #     # Iterate through each person in the array.
    #     for p in people_array:
    #         # Iterate through each day in the array.
    #         for d in days_array:
    #             # Add the condition to the array.
    #             model.Add(sum(shifts[(p, d, s)] for s in shifts_array) <= 1)
    #
    #     # # # # # # # # # # #
    #     # Condition - PERSON A MUST NEVER HAVE THE FIRST SHIFT.
    #     #
    #     # Add the condition to the array.
    #     model.Add(sum(shifts[(0, d, 0)] for d in days_array) == 0)
    #
    #     # # # # # # # # # # #
    #     # Condition - ATTEMPT TO DISTRIBUTE EVENLY.
    #     #
    #     min_shifts_per_person = (num_of_shifts_per_day * num_of_days) // num_of_people
    #     # If perfect distribution is possible.
    #     if num_of_shifts_per_day * num_of_days % num_of_people == 0:
    #         # Both the max and minimum shifts should be the same.
    #         max_shifts_per_person = min_shifts_per_person
    #     # If perfect distribution is not possible.
    #     else:
    #         # The max amount of shifts should be one more than the minimum.
    #         max_shifts_per_person = min_shifts_per_person + 1
    #
    #     # Iterate through each person
    #     for p in people_array:
    #         # Store the number of shifts worked by this person.
    #         num_shifts_worked = []
    #         # Iterate through each day in the array.
    #         for d in days_array:
    #             # Iterate through each shift in the array.
    #             for s in shifts_array:
    #                 # Add this entry to the shifts worked.
    #                 num_shifts_worked.append(shifts[(p, d, s)])
    #         # Add the minimum condition to the model.
    #         model.Add(min_shifts_per_person <= sum(num_shifts_worked))
    #         # Add the maximum condition to the model.
    #         model.Add(sum(num_shifts_worked) <= max_shifts_per_person)
    #
    #     # Create the solver.
    #     solver = cp_model.CpSolver()
    #     # Set the linearization level.
    #     solver.parameters.linearization_level = 0
    #     # Enumerate all solutions.
    #     solver.parameters.enumerate_all_solutions = True
    #
    #     # Display the first five solutions.
    #     solution_printer = CustomScheduler.PartialSolutionPrinter(
    #         shifts, num_of_people, num_of_days, num_of_shifts_per_day, 5
    #     )
    #
    #     solver.Solve(model, solution_printer)
    #
    #     return False

    @staticmethod
    # Create a sleep schedule.
    def sleep_schedule(
            # The number of days to be scheduled.
            num_of_days: int,
            # The number of shifts for each day.
            num_of_shifts_per_day: int,
            # The number of people to fill out the shifts/days.
            num_of_people: int,
    ):
        # Create an array for each variable.
        days_array = range(num_of_days)
        shifts_array = range(num_of_shifts_per_day)
        people_array = range(num_of_people)
        # Create the model.
        model = cp_model.CpModel()
        # Dictionary containing the information about the shifts.
        shifts = {}
        # Iterate through each person in the array.
        for p in people_array:
            # Iterate through each day in the array.
            for d in days_array:
                # Iterate through each shift in the array.
                for s in shifts_array:
                    # Store the value.
                    shifts[(p, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (p, d, s))

        # Obtain the next shift.
        def get_next_shift(p, d, s):
            # Check if it's the last shift of a day.
            if (s + 1) < num_of_shifts_per_day:
                # Not last shift of the day.
                next_shift = shifts[(p, d, s + 1)]
            # Check if it's not the last day.
            elif (d + 1) < num_of_days:
                # Not last shift of the day.
                next_shift = shifts[(p, d + 1, 0)]
            # It's the last day.
            else:
                # Use the first day.
                next_shift = shifts[(p, 0, 0)]
            # Return the next shift.
            return next_shift

        # # # # # # # # # # #
        # Condition - ONLY 2 PERSON PER SHIFT.
        #
        # Iterate through each day in the array.
        for d in days_array:
            # Iterate through each shift in the array.
            for s in shifts_array:
                # Add the condition to the array.
                model.Add(sum(shifts[(p, d, s)] for p in people_array) == 2)

        # # # # # # # # # # # #
        # # Condition - ONLY 2 SHIFT PER PERSON IN A SINGLE DAY.
        # #
        # # Iterate through each person in the array.
        # for p in people_array:
        #     # Iterate through each day in the array.
        #     for d in days_array:
        #         # Add the condition to the array.
        #         model.Add(
        #             sum(shifts[(p, d, s)] for s in shifts_array) <= 2
        #         )

        # # # # # # # # # # #
        # Condition - SHIFTS MUST ALWAYS BE SPLIT.
        #
        # Iterate through each person in the array.
        for d in days_array:
            # Iterate through each shift in the array.
            for s in shifts_array:
                # Iterate through each person in the array.
                for p_idx_a in range(len(people_array) - 1):
                    # Iterate through each second person in the array.
                    for p_idx_b in range(p_idx_a + 1, len(people_array)):
                        # Perform the sum.
                        perform_sum = (
                            shifts[(p_idx_a, d, s)] +
                            get_next_shift(p_idx_a, d, s) +
                            shifts[(p_idx_b, d, s)] +
                            get_next_shift(p_idx_b, d, s)
                        )
                        # Append the sum to the list.
                        model.Add(perform_sum <= 3)

        # # # # # # # # # # #
        # Condition - SHIFTS MUST BE DONE IN A ROW.
        #
        # Iterate through each person in the array.
        for p in people_array:
            # Iterate through each day in the array.
            for d in days_array:
                # Iterate through each shift in the array.
                for s in shifts_array:
                    # Get the next shift.
                    next_shift = get_next_shift(p, d, s)
                    # Check if it's the first shift of a day.
                    if (s - 1) >= 0:
                        # Not first shift of the day.
                        previous_shift = shifts[(p, d, s - 1)]
                    # Check if it's not the first day.
                    elif (d - 1) >= 0:
                        # Not the first shift of the day.
                        previous_shift = shifts[(p, d - 1, num_of_shifts_per_day - 1)]
                    # It's the first day and shift.
                    else:
                        # Use the first day.
                        previous_shift = shifts[(p, num_of_days - 1, num_of_shifts_per_day - 1)]
                    # Add the condition to the array.
                    model.Add(
                        (previous_shift + next_shift + (-100 * shifts[(p, d, s)])) > -100
                    )

        # # # # # # # # # # #
        # Condition - SHIFTS MUST BE SPACED BY THE MAX SHIFTS IN A DAY.
        #
        # Iterate through each person in the array.
        for p in people_array:
            # Iterate through each day in the array.
            for d in days_array:
                # Iterate through each shift in the array.
                for s in shifts_array:
                    # The current shift sum.
                    true_s = s
                    true_d = d
                    # Sum the shifts.
                    list_of_shifts = []
                    # Loop through extra shifts.
                    for _ in range(0, num_of_shifts_per_day):
                        # Sum the shifts.
                        if (true_s + 1) < num_of_shifts_per_day:
                            # Not last shift of the day.
                            true_s += 1
                        # Check if it's not the last day.
                        elif (d + 1) < num_of_days:
                            # Not last shift of the day.
                            true_s = 0
                            true_d += 1
                        # It's the last day.
                        else:
                            true_s = 0
                            true_d = 0
                        # Not the first shift of the day.
                        list_of_shifts.append(shifts[(p, true_d, true_s)])
                    # Add the condition to the array.
                    model.Add(sum(list_of_shifts) <= 2)

        # # # # # # # # # # # #
        # # Condition - PERSON A MUST NEVER HAVE THE FIRST SHIFT.
        # #
        # # Add the condition to the array.
        model.Add(sum(shifts[(0, d, 0)] for d in days_array) == 0)

        # # # # # # # # # # #
        # Condition - ATTEMPT TO DISTRIBUTE EVENLY.
        #
        min_shifts_per_person = (num_of_shifts_per_day * num_of_days) // num_of_people
        # If perfect distribution is possible.
        if num_of_shifts_per_day * num_of_days % num_of_people == 0:
            # Both the max and minimum shifts should be the same.
            max_shifts_per_person = min_shifts_per_person
        # If perfect distribution is not possible.
        else:
            # The max amount of shifts should be one more than the minimum.
            max_shifts_per_person = min_shifts_per_person + 1

        # # Iterate through each person
        # for p in people_array:
        #     # Store the number of shifts worked by this person.
        #     num_shifts_worked = []
        #     # Iterate through each day in the array.
        #     for d in days_array:
        #         # Iterate through each shift in the array.
        #         for s in shifts_array:
        #             # Add this entry to the shifts worked.
        #             num_shifts_worked.append(shifts[(p, d, s)])
        #     # Add the minimum condition to the model.
        #     model.Add(min_shifts_per_person <= sum(num_shifts_worked))
        #     # Add the maximum condition to the model.
        #     model.Add(sum(num_shifts_worked) <= max_shifts_per_person)

        # Create the solver.
        solver = cp_model.CpSolver()
        # Set the linearization level.
        solver.parameters.linearization_level = 0
        # Enumerate all solutions.
        solver.parameters.enumerate_all_solutions = True

        # Display the first five solutions.
        solution_printer = CustomScheduler.PartialSolutionPrinter(
            shifts, num_of_people, num_of_days, num_of_shifts_per_day, 5
        )

        solver.Solve(model, solution_printer)

        return False


CustomScheduler.sleep_schedule(3, 6, 10)

# 4H Turns
# > 4 people -> 2 per turn
# option 1: "ladder" schedule
# option 2: classic schedule
