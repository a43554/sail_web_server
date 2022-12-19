import traceback

from ortools.sat.python import cp_model


# The scheduling dimension.
class MealScheduleObtain(cp_model.CpSolverSolutionCallback):

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
        # The possible schedules.
        self.schedule_data = {}

    # Print the solutions
    def on_solution_callback(self):
        try:
            # Increase the solution count.
            self.solution_count += 1
            # Create the schedule.
            store_schedule = {
                'menus': {},
                'schedule': {},
                'products': {},
                'totals': {}
            }
            # Iterate through each menu.
            for menu_name, menu_var in self.total_menu_variable_dict.items():
                # Store the amount of each menu.
                store_schedule['menus'][menu_name] = self.Value(menu_var)
            # Print the menu schedule.
            for idx, menu_data in enumerate(self.menu_variable_array):
                # Iterate through each menu.
                for menu_name, menu_var in menu_data.items():
                    # Check if menu var is valid.
                    if self.Value(menu_var) == 1:
                        # Add the schedule.
                        store_schedule['schedule'][idx] = menu_name
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
                # The product id.
                product_id = self.ingredient_data[ingredient_name]['product']
                # The products bought
                store_schedule['products'][product_id] = units_obtained
                # Increment the total weight.
                total_weight += units_obtained * self.ingredient_data[ingredient_name]['weight']
                # Increment the total cost.
                total_cost += (units_obtained * self.ingredient_data[ingredient_name]['price'])
            # Store the values.
            store_schedule['totals']['weight'] = total_weight
            store_schedule['totals']['cost'] = total_cost

            # Store the solution.
            self.schedule_data[self.solution_count - 1] = store_schedule

            # Check if enough solutions have been reached.
            if self.solution_count >= self.solution_limit:
                # Display the stop searching text.
                print('Stop search after %i solutions' % self.solution_limit)
                # Finish the search.
                self.StopSearch()
        except Exception as e:
            traceback.print_exc()
            raise e