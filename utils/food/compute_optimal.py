from itertools import combinations

ingredient_data = {
    'A': {'price_per_weight': 0.50, 'weight': 50, 'menus': ['MENU 1', 'MENU 3', 'MENU 4']},
    'B': {'price_per_weight': 0.95, 'weight': 40, 'menus': ['MENU 1', 'MENU 2', 'MENU 4', 'MENU 5']},
    'C': {'price_per_weight': 0.35, 'weight': 30, 'menus': ['MENU 1', 'MENU 5']},
    'D': {'price_per_weight': 0.25, 'weight': 40, 'menus': ['MENU 2', 'MENU 3']},
    'E': {'price_per_weight': 0.25, 'weight': 40, 'menus': ['MENU 2', 'MENU 4', 'MENU 5']},
    'F': {'price_per_weight': 1.50, 'weight': 20, 'menus': ['MENU 5']}
}

meal_data = [
    {
        'menu': 'MENU 1',
        'ingredients': [
            {'name': 'A', 'weight': 10},
            {'name': 'B', 'weight': 5},
            {'name': 'C', 'weight': 7}
        ]
    },
    {
        'menu': 'MENU 2',
        'ingredients': [
            {'name': 'D', 'weight': 8},
            {'name': 'B', 'weight': 6},
            {'name': 'E', 'weight': 4}
        ]
    },
    {
        'menu': 'MENU 3',
        'ingredients': [
            {'name': 'D', 'weight': 12},
            {'name': 'A', 'weight': 20}
        ]
    },
    {
        'menu': 'MENU 4',
        'ingredients': [
            {'name': 'B', 'weight': 7},
            {'name': 'E', 'weight': 4},
            {'name': 'A', 'weight': 7}
        ]
    },
    {
        'menu': 'MENU 5',
        'ingredients': [
            {'name': 'F', 'weight': 6},
            {'name': 'E', 'weight': 4},
            {'name': 'B', 'weight': 7},
            {'name': 'C', 'weight': 8}
        ]
    }
]

test = list(ingredient_data.keys())
all_menu_combos = [
    list(menu_combinations) for s in range(1, len(test) + 1) for menu_combinations in combinations(test, s)
]

print("")