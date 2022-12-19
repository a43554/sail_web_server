from ortools.sat.python import cp_model


# The scheduling dimension.
class MealScheduleDisplay(cp_model.CpSolverSolutionCallback):

    # The class constructor.
    def __init__(self, ingredient_data, menu_variable_array, total_menu_variable_dict, ingredient_variable_dict):
        # Call the super method.
        cp_model.CpSolverSolutionCallback.__init__(self)
        # The number of possible solutions.
        self.solution_count = 0
        # The max solution limit.
        self.solution_limit = 6
        # Store the number of days.
        self.ingredient_data = ingredient_data
        # Store the number of days.
        self.menu_variable_array = menu_variable_array
        # Store the number of shifts per day.
        self.total_menu_variable_dict = total_menu_variable_dict
        # Compute the total number of shifts.
        self.ingredient_variable_dict = ingredient_variable_dict

    # Print the solutions
    def on_solution_callback(self):
        # Increase the solution count.
        self.solution_count += 1
        # Print the totals.
        print(f"---------------------------SOLUTION: {self.solution_count}---------------------------",)
        # Print the totals.
        print("MENU TOTALS: ", end='|')
        # Iterate through each menu.
        for menu_name, menu_var in self.total_menu_variable_dict.items():
            # Print the data.
            print(f' {menu_name} = {self.Value(menu_var)} ', end='|')
        # Print the new line.
        print("")
        # Print the schedule.
        print("MENU SCHEDULE: ", end='|')
        # Print the menu schedule.
        for menu_data in self.menu_variable_array:
            # Iterate through each menu.
            for menu_name, menu_var in menu_data.items():
                # Check if menu var is valid.
                if self.Value(menu_var) == 1:
                    # Print the data.
                    print(f' {menu_name} ', end='|')
        # Print the new line.
        print("")
        # Variable to store the total weight.
        total_weight = 0
        # Variable to store the total cost.
        total_cost = 0.0
        # Print the schedule.
        print("INGREDIENT AMOUNT: ", end='|')
        # Iterate through each ingredient.
        for ingredient_name, ingredient_var in self.ingredient_variable_dict.items():
            # Store the amount of units obtained.
            units_obtained = self.Value(ingredient_var)
            # Print the data.
            print(f' {ingredient_name} = {units_obtained} ', end='|')
            # Increment the total weight.
            total_weight += units_obtained * self.ingredient_data[ingredient_name]['weight']
            # Increment the total cost.
            total_cost += (
                    units_obtained *
                    self.ingredient_data[ingredient_name]['price']
            )
        # Print the new line.
        print("")
        # Print the schedule.
        print(f"TOTAL WEIGHT: {total_weight}")
        print(f"TOTAL PRICE: {total_cost}")
        # Print the totals.
        print(f"-----------------------------------------------------------------",)
        # Check if enough solutions have been reached.
        if self.solution_count >= self.solution_limit:
            # Display the stop searching text.
            print('Stop search after %i solutions' % self.solution_limit)
            # Finish the search.
            self.StopSearch()
