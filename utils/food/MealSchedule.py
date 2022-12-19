from ortools.sat.python import cp_model

from utils.food.MealScheduleDisplay import MealScheduleDisplay


# The possible meal categories.
from utils.food.MealScheduleObtain import MealScheduleObtain


class MealType:
    BREAKFAST = 'BREAKFAST'
    LUNCH = 'LUNCH'
    DINNER = 'DINNER'


# The schedule class.
class MealSchedule:

    # The class constructor.
    def __init__(
            self, meal_times: list, num_of_people: int,
            possible_meals: dict, ingredient_data: dict,
            priority: str = 'NONE'
    ):
        # Call the super function.
        super().__init__()
        # Store the number of meals.
        self.meal_times = meal_times
        # Store the priority.
        self.priority = priority

        # [
        #     [MealType.BREAKFAST],
        #     [MealType.LUNCH],
        #     [MealType.DINNER],
        #     [MealType.BREAKFAST],
        #     [MealType.LUNCH],
        #     [MealType.DINNER],
        #     [MealType.LUNCH, MealType.DINNER],
        # ]
        # Store the number of people.
        self.num_of_people = num_of_people
        # Store the possible meals.
        self.possible_menus = possible_meals
        # {
        #     'MENU 1': {
        #         'meal_types': [MealType.DINNER, MealType.LUNCH, ],
        #         'ingredients': {
        #             'A': {'weight': 10},
        #             'B': {'weight': 5},
        #             'C': {'weight': 7}
        #         }
        #     },
        #     'MENU 2': {
        #         'meal_types': [MealType.DINNER, MealType.LUNCH, ],
        #         'ingredients': {
        #             'D': {'weight': 8},
        #             'B': {'weight': 6},
        #             'E': {'weight': 4}
        #         }
        #     },
        #     'MENU 3': {
        #         'meal_types': [MealType.BREAKFAST, ],
        #         'ingredients': {
        #             'D': {'weight': 12},
        #             'A': {'weight': 20}
        #         }
        #     },
        #     'MENU 4': {
        #         'meal_types': [MealType.DINNER, MealType.LUNCH, ],
        #         'ingredients': {
        #             'B': {'weight': 7},
        #             'E': {'weight': 4},
        #             'A': {'weight': 7}
        #         }
        #     },
        #     'MENU 5': {
        #         'meal_types': [MealType.DINNER, MealType.LUNCH, ],
        #         'ingredients': {
        #             'F': {'weight': 6},
        #             'E': {'weight': 4},
        #             'B': {'weight': 7},
        #             'C': {'weight': 8}
        #         }
        #     },
        #     'MENU 6': {
        #         'meal_types': [MealType.BREAKFAST, ],
        #         'ingredients': {
        #             'A': {'weight': 5},
        #             'F': {'weight': 10},
        #         }
        #     }
        # }
        # Store the ingredient data.
        self.ingredient_data = ingredient_data
        # {
        #     'A': {'price': 2.15, 'weight': 20, 'menus': ['MENU 1', 'MENU 3', 'MENU 4', 'MENU 6']},
        #     'B': {'price': 3.25, 'weight': 40, 'menus': ['MENU 1', 'MENU 2', 'MENU 4', 'MENU 5']},
        #     'C': {'price': 5.35, 'weight': 30, 'menus': ['MENU 1', 'MENU 5']},
        #     'D': {'price': 3.25, 'weight': 20, 'menus': ['MENU 2', 'MENU 3']},
        #     'E': {'price': 7.25, 'weight': 30, 'menus': ['MENU 2', 'MENU 4', 'MENU 5']},
        #     'F': {'price': 3.20, 'weight': 100, 'menus': ['MENU 5', 'MENU 6']}
        # }

        # Store the callback.
        self.display_results = None

        # The meal variable array.
        self.menu_variable_array = []
        # The total menu variable array.
        self.total_menu_variable_dict = {}
        # The ingredient variable dictionary.
        self.ingredient_variable_dict = {}

        # Create the model.
        self.model = None

    # Run the solver.
    def solve(self):

        # Create the model.
        self.model = cp_model.CpModel()

        # The variable array.
        self.menu_variable_array.clear()
        # The variable array.
        self.total_menu_variable_dict.clear()
        # The variable array.
        self.ingredient_variable_dict.clear()

        # Iterate through all menus.
        for menu in list(self.possible_menus.keys()):
            # Create the variable.
            self.total_menu_variable_dict[menu] = self.model.NewIntVar(0, len(self.meal_times), f'menu:{menu}')

        # Iterate through all meal times indexes.
        for meal_time_idx in range(len(self.meal_times)):
            # The dictionary of all meals.
            meal_dictionary = {}
            # Iterate through all menus.
            for menu in list(self.possible_menus.keys()):
                # Create the variable.
                meal_dictionary[menu] = self.model.NewBoolVar(f'idx:{meal_time_idx}menu:{menu}')
            # Append the meal dictionary to the array.
            self.menu_variable_array.append(meal_dictionary)

        # Iterate through all ingredients.
        for ingredient_name in list(self.ingredient_data.keys()):
            # Create the variable.
            self.ingredient_variable_dict[ingredient_name] = self.model.NewIntVar(
                0, 25, f'amount:{ingredient_name}'
            )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 1 -> No more than a meal per time slot.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_1()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 2 -> Sum of individual meal variables spread over all meal times must equal the total var value.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_2()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 3 -> There must be enough ingredients to make a meal.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_3()
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 4 -> Only meals of a certain type can exist in a meal slot.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_4()

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # RULE: 5 -> Don't repeat dish X more than once every Y meal times.
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.apply_rule_5()

        # Check if the weight should be minimized.
        if self.priority == "WEIGHT":
            # Minimize the max weight.
            self.model.Minimize(sum([
                (
                        self.ingredient_variable_dict[ingredient_name] * ingredient_data['weight']
                ) for ingredient_name, ingredient_data in self.ingredient_data.items()
            ]))
        # Check if the cost should be minimized.
        elif self.priority == "PRICE":
            # Minimize the max cost.
            self.model.Minimize(sum([
                (
                        self.ingredient_variable_dict[ingredient_name] * ing_data['price']
                ) for ingredient_name, ing_data in self.ingredient_data.items()
            ]))

        # Create the solver.
        solver = cp_model.CpSolver()
        # Set the linearization level.
        # solver.parameters.linearization_level = 0
        # Enumerate all solutions.
        # solver.parameters.enumerate_all_solutions = True
        # Prepare the printer
        self.display_results = MealScheduleObtain( # MealScheduleDisplay(
            self.ingredient_data,
            self.menu_variable_array,
            self.total_menu_variable_dict,
            self.ingredient_variable_dict
        )
        # Solve the problem.
        solver.Solve(self.model, self.display_results)

        # Check if weight should be minimized.
        if self.priority == "WEIGHT":
            # The list's result.
            list_result = list(self.display_results.schedule_data.values())
            # Re-order the dictionary.
            list_result.sort(key=(lambda item: item['totals']['weight']))
            # Return the ordered list.
            return dict([(idx, item) for idx, item in enumerate(list_result)])
        # Check if the cost should be minimized.
        elif self.priority == "PRICE":
            # The list's result.
            list_result = list(self.display_results.schedule_data.values())
            # Re-order the dictionary.
            list_result.sort(key=(lambda item: item['totals']['cost']))
            # Return the ordered list.
            return dict([(idx, item) for idx, item in enumerate(list_result)])
        # Return the results.
        return self.display_results.schedule_data

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 1 -> No more than a meal per time slot.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_1(self):
        # Iterate through all meal times indexes.
        for meal_time_idx in range(len(self.meal_times)):
            # Obtain all variables.
            variables = self.menu_variable_array[meal_time_idx].values()
            # Add the constraint.
            self.model.Add(sum(variables) == 1)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 2 -> Sum of individual menu variables spread over all meal times must equal the total var value.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_2(self):
        # Iterate through each menu.
        for menu_name, menu_value in self.possible_menus.items():
            # Obtain all variables for a single menu over all periods of time.
            single_menu_variables = [meal_time_data[menu_name] for meal_time_data in self.menu_variable_array]
            # Obtain the total menu occurrences variable.
            total_menu_occurrences_variable = self.total_menu_variable_dict[menu_name]
            # Add the constraint.
            self.model.Add(sum(single_menu_variables) == total_menu_occurrences_variable)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 3 -> There must be enough ingredients to make a meal.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_3(self):
        # Iterate through the menu ingredients.
        for ingredient_name, ingredient_data in self.ingredient_data.items():
            # Obtain all menu names that contain this ingredient.
            menu_names = ingredient_data['menus']
            # Obtain the ingredient weight per unit.
            weight_per_unit = ingredient_data['weight']
            # Obtain all menu sum variables for where this ingredient is present.
            menu_variables = [
                (
                    self.total_menu_variable_dict[menu_name],
                    self.possible_menus[menu_name]['ingredients'][ingredient_name]['weight']
                ) for menu_name in menu_names
            ]
            # Obtain the total.
            total_needed = [(weight * occurrences * self.num_of_people) for occurrences, weight in menu_variables]
            # Add a constraint.
            self.model.Add(
                self.ingredient_variable_dict[ingredient_name] * weight_per_unit >= sum(total_needed)
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 4 -> Only meals of a certain type can exist in a meal slot.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_4(self):
        # Iterate through all meal times.
        for idx, meal_slot_types in enumerate(self.meal_times):
            # The dictionary of all meals.
            meal_dictionary = self.menu_variable_array[idx]
            # Iterate through all menus.
            for menu_name, menu_variable in meal_dictionary.items():
                # Obtain the menu type.
                menu_types = self.possible_menus[menu_name]['meal_types']
                # Check if this menu slot allows this meal.
                if not any((menu_type in meal_slot_types) for menu_type in menu_types):
                    # No matching types, do not allow this variable to be filled.
                    self.model.Add(menu_variable == 0)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # RULE: 5 -> Don't repeat dish X more than once every Y meal times.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def apply_rule_5(self):
        # The number of meal time window.
        meal_time_window = 4
        # Iterate through each menu.
        for menu_name, _ in self.possible_menus.items():
            # Iterate through all shifts enumerated.
            for meal_time_index in range(0, len(self.menu_variable_array) - meal_time_window + 1):
                # The next N meal times.
                meal_times = self.menu_variable_array[meal_time_index: meal_time_index + meal_time_window]
                # Add the
                self.model.Add(sum(menu_var[menu_name] for menu_var in meal_times) <= 1)
