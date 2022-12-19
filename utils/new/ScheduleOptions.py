# All the schedule options.
class ScheduleOptions:
    # The option to select everything.
    ALL = 'ALL'
    # The option to select nothing.
    NONE = None

    # The option to indicate a setting.
    SETTING = 'SETTING'
    # The option to indicate data.
    DATA = 'DATA'

    @staticmethod
    # Get the default settings.
    def get_default_settings() -> dict:
        # Return the dictionary.
        return {
            # The full list of shifts possible for this task to occur in.
            'valid_shifts': {
                # The setting type.
                'setting_type': ScheduleOptions.SETTING,
                # The list of shifts.
                'setting_value': ScheduleOptions.ALL
            },
            # Minimum and maximum amount of people per task.
            'people_per_shift_task': {
                # The setting type.
                'setting_type': ScheduleOptions.DATA,
                # The value of the setting.
                'setting_value': {
                    # The minimum amount.
                    'min_amount': 0,
                    # The maximum amount.
                    'max_amount': 1
                }
            },
            # This Tasks' cycle settings.
            'per_task_cycle_settings': {
                # The setting type.
                'setting_type': ScheduleOptions.DATA,
                # The value of the setting.
                'setting_value': {
                    # The assigned shifts per cycle.
                    'assigned_shifts_per_cycle': 2,
                    # The total shifts per cycle.
                    'total_shifts_per_cycle': 6
                }
            },
            # The cycle settings.
            'per_person_cycle_settings': {
                # The setting type.
                'setting_type': ScheduleOptions.DATA,
                # The value of the setting.
                'setting_value': {
                    # The assigned shifts per cycle.
                    'assigned_shifts_per_cycle': 2,
                    # The total shifts per cycle.
                    'total_shifts_per_cycle': 6
                }
            },
            # The sequential settings.
            'sequential_settings': {
                # The setting type.
                'setting_type': ScheduleOptions.DATA,
                # The value of the setting.
                'setting_value': {
                    # The number of sequential shifts.
                    'number_of_sequential_shifts': 2,
                    # If shifts cannot have the same cast.
                    'diversify_cast': False
                }
            }
        }