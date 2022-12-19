import time
from math import fsum

from utils.new.Schedule import Schedule as ScheduleMaker

GLOBAL_TASKS = 20
GLOBAL_SHIFTS = 20
GLOBAL_PEOPLE = 200

# Task/people/shifts: ms
complex_shifts_and_tasks_and_people = {
    '20/15/70': 5922.3,
    '20/15/200': 16449.4,
    '20/20/200': 53001.4, # ???
    '20/15/300': 24665.5,
    '10/10/10': 232.5,
    '25/25/25': 3866.3,
    '30/30/30': 6914.6,
    '35/35/35': 11186.8,
    '40/40/40': 17170.0,
    '45/45/45': 24780.8,
    '50/50/50': None,
}

people = [
    ("A" + str(count)) for count in range(0, GLOBAL_PEOPLE)
]


tasks = [
    {
        "name": "task_1",
        "qualified_people": people,
        "no_individual_with_tasks": [],
        "valid_shifts": {
            "setting_type": "SETTING",
            "setting_value": 'ALL'
        },
        "people_per_shift_task": {
            "setting_type": "DATA",
            "setting_value": {
                "max_amount": int(len(people) / 3) + 1,
                "min_amount": 1
            }
        },
        "per_task_cycle_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        },
        "per_person_cycle_settings": {
            "setting_type": "DATA",
            "setting_value": {
                'assigned_shifts_per_cycle': 1,
                'total_shifts_per_cycle': 3
            }
        },
        "sequential_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        }
    },
    {
        "name": "task_2",
        "qualified_people": people,
        "no_individual_with_tasks": [],
        "valid_shifts": {
            "setting_type": "SETTING",
            "setting_value": 'ALL'
        },
        "people_per_shift_task": {
            "setting_type": "DATA",
            "setting_value": {
                "max_amount": int(len(people) / 3) + 1,
                "min_amount": 1
            }
        },
        "per_task_cycle_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        },
        "per_person_cycle_settings": {
            "setting_type": "DATA",
            "setting_value": {
                'assigned_shifts_per_cycle': 1,
                'total_shifts_per_cycle': 3
            }
        },
        "sequential_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        }
    },
    {
        "name": "task_3",
        "qualified_people": people,
        "no_individual_with_tasks": [],
        "valid_shifts": {
            "setting_type": "SETTING",
            "setting_value": 'ALL'
        },
        "people_per_shift_task": {
            "setting_type": "DATA",
            "setting_value": {
                "max_amount": int(len(people) / 3) + 1,
                "min_amount": 1
            }
        },
        "per_task_cycle_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        },
        "per_person_cycle_settings": {
            "setting_type": "DATA",
            "setting_value": {
                'assigned_shifts_per_cycle': 1,
                'total_shifts_per_cycle': 3
            }
        },
        "sequential_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        }
    }
]

total_tasks = GLOBAL_TASKS



for i in range(3, total_tasks):
    tasks.append({
        "name": f"task_{i+1}",
        "qualified_people": people,
        "no_individual_with_tasks": [],
        "valid_shifts": {
            "setting_type": "SETTING",
            "setting_value": 'ALL'
        },
        "people_per_shift_task": {
            "setting_type": "DATA",
            "setting_value": {
                "max_amount": int(len(people) / 3) + 1,
                "min_amount": 1
            }
        },
        "per_task_cycle_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        },
        "per_person_cycle_settings": {
            "setting_type": "DATA",
            "setting_value": {
                'assigned_shifts_per_cycle': 1,
                'total_shifts_per_cycle': 3
            }
        },
        "sequential_settings": {
            "setting_type": "SETTING",
            "setting_value": None
        }
    })

# The schedule maker.
schedule_maker = ScheduleMaker(
    num_of_shifts_total=GLOBAL_SHIFTS,
    num_of_shifts_per_day=1,
    list_of_people=people
)

for task in tasks:
    schedule_maker.quick_add_task(task)


solutions = {}
times = []
for i in range(0, 10):
    a = time.process_time_ns()
    solutions = schedule_maker.solve()
    b = time.process_time_ns()
    times.append((b - a) * 10**-6)
    print(times[i])

for sol_idx, solution in solutions.items():
    print(f"--------- Solution {sol_idx} ---------")
    for shift_idx, shift_data in solution.items():
        for task_name, assigned_people in shift_data.items():
            print(f"{task_name}\t|\t{assigned_people}", end='\t\t')
        print("")

print(f"\n\n{times}", end=' = ')
print(fsum(times) / len(times))




# Task/people/shifts: ms
solo_people = {
    '3/3/3': 6.8,
    '3/5/3': 8.7,
    '3/10/3': 13.7,
    '3/50/3': 54.8,
    '3/100/3': 113.1,
    '3/500/3': 950.5,
    '3/1000/3': 1953.2,
    '3/3000/3': 9205.1,
    '3/5000/3': 26210.1,
}

# Task/people/shifts: ms
solo_shifts = {
    '3/3/3': 6.8,
    '3/3/5': 9.4,
    '3/3/10': 17.6,
    '3/3/50': 90.9,
    '3/3/100': 170.1,
    '3/3/1000': 1848.7,
}

# Task/people/shifts: ms
solo_tasks = {
    '3/3/3': 6.8,
    '5/3/3': 10.7,
    '10/3/3': 17.6,
    '50/3/3': 81.8,
    '100/3/3': 193.3,
    '1000/3/3': 1808.5,
}

# Task/people/shifts: ms
people_and_shifts = {
    '3/3/3': 6.8,
    '3/5/5': 13.7,
    '3/10/10': 52.3,
    '3/50/50': 874.4,
    '3/100/100': 4003.6,
}

############### COMPLEX #################

# Task/people/shifts: ms
complex_solo_people = {
    '3/3/3':    7.4,
    '3/5/3':    10.6,
    '3/10/3':   16.8,
    '3/50/3':   73.6,
    '3/100/3':  190.9,
    '3/1000/3': 2607.7,
}

# Task/people/shifts: ms
complex_solo_shifts = {
    '3/3/3': 7.4,
    '3/3/5': 13.3,
    '3/3/10': 26.4,
    '3/3/50': 138.1,
    '3/3/100': 290.0,
    '3/3/1000': 3995.4,
}

# Task/people/shifts: ms
complex_solo_tasks = {
    '3/3/3': 7.4,
    '5/3/3': 10.6,
    '10/3/3': 20.4,
    '50/3/3': 105.4,
    '100/3/3': 203.9,
    '1000/3/3': 2015.3,
}

# Task/people/shifts: ms
complex_people_and_shifts = {
    '3/3/3': 7.4,
    '3/5/5': 18.8,
    '3/10/10': 83.0,
    '3/50/50': 1935.9,
    '3/100/100': 9008.7,
}

# Task/people/shifts: ms
complex_shifts_and_tasks = {
    '3/3/3': 7.4,
    '5/3/5': 19.6,
    '10/3/10': 92.5,
    '50/3/50': 2262.3,
    '100/3/100': 10324.8,
}

# Task/people/shifts: ms
complex_tasks_and_people = {
    '3/3/3': 7.4,
    '5/5/3': 18.9,
    '10/10/3': 64.6,
    '50/50/3': 2570.4,
    '100/100/3': 5231.2,
}

# Task/people/shifts: ms
complex_shifts_and_tasks_and_people = {
    '3/3/3': 7.4,
    '5/5/5': 28.9,
    '10/10/10': 232.5,
    '25/25/25': 3866.3,
    '30/30/30': 6914.6,
    '35/35/35': 11186.8,
    '40/40/40': 17170.0,
    '45/45/45': 24780.8,
    '50/50/50': None,
}