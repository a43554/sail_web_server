from typing import Dict, List

from main.models import Plan, PlanAccess


# Execute operations on the progress dictionaries.
class ProgressOperations:
    # Dictionary used for parsing the path to update.
    PATH_REQUIREMENTS = {
        'general_info': [],
        'general_team': ['general_info'],
        'route_path': [],
        'route_duration': ['route_path',],
        'assignments_settings': [],
        'assignments_tasks_*': ['assignments_settings'],
        'assignments_options': ['general_team', 'assignments_tasks_*'],
        'assignments_schedule': ['assignments_options'],
        'meals_settings': ['general_team'],
        'meals_selection': ['meals_settings'],
        'meals_schedule': ['meals_selection']
    }

    # Get from progress array.
    @staticmethod
    def set_status_progress_from_target_str(
            target_section: str,
            progress_dictionary: Dict[str, str],
            status: str
    ):
        # Split the target section.
        target_section_array = target_section.split('_')
        # The target section array length.
        target_section_array_length = len(target_section_array)
        # Loop through each possible target.
        for possible_target in progress_dictionary.keys():
            # Split the string.
            possible_target_array = possible_target.split('_')
            # Check if the lengths match.
            if target_section_array_length == len(possible_target_array):
                # Correct section.
                is_correct_section = True
                # Iterate the arrays.
                for i in range(0, target_section_array_length):
                    # Obtain both strings.
                    actual_str, expected_str = target_section_array[i], possible_target_array[i]
                    # Check if the strings match.
                    if (expected_str != actual_str) and (actual_str != '*'):
                        # Is not correct section.
                        is_correct_section = False
                        # Break out.
                        break
                # Check if it is correct section.
                if is_correct_section:
                    # Return the status.
                    progress_dictionary[possible_target] = status

    # Check if the target section exists.
    @staticmethod
    def are_sections_equal(
            target_section: str,
            compare_section_to: str,
            progress_dictionary: Dict[str, str]
    ) -> bool:
        # Split the target section.
        target_section_array = target_section.split('_')
        # The target section array length.
        target_section_array_length = len(target_section_array)
        # Loop through each possible target.
        for possible_target in ProgressOperations.PATH_REQUIREMENTS.keys():
            # Split the string.
            possible_target_array = possible_target.split('_')
            # Check if the lengths match.
            if target_section_array_length == len(possible_target_array):
                # Correct section.
                is_correct_section = True
                # Iterate the arrays.
                for i in range(0, target_section_array_length):
                    # Obtain both strings.
                    actual_str, expected_str = target_section_array[i], possible_target_array[i]
                    # Check if the strings match.
                    if (expected_str != actual_str) and (expected_str != '*'):
                        # Is not correct section.
                        is_correct_section = False
                        # Break out.
                        break
                # Check if it is correct section.
                if is_correct_section and (possible_target == compare_section_to):
                    # Return the status.
                    return True
        # Raise an error.
        return False

    # Search progress array.
    @staticmethod
    def is_status_progress_from_target_str(
            target_section: str,
            progress_dictionary: Dict[str, str],
            status: str
    ) -> bool:
        # Split the target section.
        target_section_array = target_section.split('_')
        # The target section array length.
        target_section_array_length = len(target_section_array)
        # Loop through each possible target.
        for possible_target in progress_dictionary.keys():
            # Split the string.
            possible_target_array = possible_target.split('_')
            # Check if the lengths match.
            if target_section_array_length == len(possible_target_array):
                # Correct section.
                is_correct_section = True
                # Iterate the arrays.
                for i in range(0, target_section_array_length):
                    # Obtain both strings.
                    actual_str, expected_str = target_section_array[i], possible_target_array[i]
                    # Check if the strings match.
                    if (expected_str != actual_str) and (actual_str != '*'):
                        # Is not correct section.
                        is_correct_section = False
                        # Break out.
                        break
                # Check if it is correct section.
                if is_correct_section:
                    # Return the status.
                    return progress_dictionary[possible_target] == status
        # Raise an error.
        raise KeyError("No section found.")

    # Search progress array.
    @staticmethod
    def is_status_progress_from_all_targets_str(
            target_section: str,
            progress_dictionary: Dict[str, str],
            status: str
    ) -> bool:
        # The verdict.
        verdict = None
        # Split the target section.
        target_section_array = target_section.split('_')
        # The target section array length.
        target_section_array_length = len(target_section_array)
        # Loop through each possible target.
        for possible_target in progress_dictionary.keys():
            # Split the string.
            possible_target_array = possible_target.split('_')
            # Check if the lengths match.
            if target_section_array_length == len(possible_target_array):
                # Correct section.
                is_correct_section = True
                # Iterate the arrays.
                for i in range(0, target_section_array_length):
                    # Obtain both strings.
                    actual_str, expected_str = target_section_array[i], possible_target_array[i]
                    # Check if the strings match.
                    if (expected_str != actual_str) and (actual_str != '*'):
                        # Is not correct section.
                        is_correct_section = False
                        # Break out.
                        break
                # Check if it is correct section.
                if is_correct_section:
                    # Return the status.
                    verdict = (verdict is None or verdict) and (progress_dictionary[possible_target] == status)
        # Return the verdict.
        return verdict == True

    # Search progress array.
    @staticmethod
    def get_usages_from_target(
            target_section: str
    ) -> List[str]:
        # Split the target section.
        target_section_array = target_section.split('_')
        # The target section array length.
        target_section_array_length = len(target_section_array)
        # Search through all path sections.
        for section_name, section_requirements in ProgressOperations.PATH_REQUIREMENTS.items():
            # CHeck if any requirements contains this section.
            for req in section_requirements:
                # Split the string.
                possible_target_array = req.split('_')
                # Check if the lengths match.
                if target_section_array_length == len(possible_target_array):
                    # Correct section.
                    is_correct_section = True
                    # Iterate the arrays.
                    for i in range(0, target_section_array_length):
                        # Obtain both strings.
                        actual_str, expected_str = target_section_array[i], possible_target_array[i]
                        # Check if the strings match.
                        if (expected_str != actual_str) and (expected_str != '*'):
                            # Is not correct section.
                            is_correct_section = False
                            # Break out.
                            break
                    # Check if it is correct section.
                    if is_correct_section:
                        # Return the status.
                        yield section_name
        # Return.
        return

    # Unlock a section.
    @staticmethod
    def lock_section(
            target_section: str,
            progress_dictionary: Dict[str, str]
    ):
        # Set the section.
        ProgressOperations.set_status_progress_from_target_str(target_section, progress_dictionary, Plan.LOCK)
        # Get the requirements.
        for possible_chain_lock_section in ProgressOperations.get_usages_from_target(target_section):
            # Set the section.
            ProgressOperations.lock_section(possible_chain_lock_section, progress_dictionary)

    # Unlock a section.
    @staticmethod
    def unlock_section(
            target_section: str,
            progress_dictionary: Dict[str, str]
    ):
        # Set the section.
        ProgressOperations.set_status_progress_from_target_str(target_section, progress_dictionary, Plan.TODO)
        # Get the requirements.
        for possible_chain_lock_section in ProgressOperations.get_usages_from_target(target_section):
            # Get all requirements.
            chain_reqs = ProgressOperations.PATH_REQUIREMENTS[possible_chain_lock_section]
            # Check if the section can be completed.
            if not all(
                    ProgressOperations.is_status_progress_from_all_targets_str(req, progress_dictionary, Plan.DONE)
                    for
                    req
                    in
                    chain_reqs
            ):
                # Set the section.
                ProgressOperations.lock_section(possible_chain_lock_section, progress_dictionary)

    # Complete a section.
    @staticmethod
    def complete_section(
            target_section: str,
            progress_dictionary: Dict[str, str]
    ):
        # Set the section.
        ProgressOperations.set_status_progress_from_target_str(target_section, progress_dictionary, Plan.DONE)
        # Get the requirements.
        for possible_chain_unlock_section in ProgressOperations.get_usages_from_target(target_section):
            # Get all requirements.
            chain_reqs = ProgressOperations.PATH_REQUIREMENTS[possible_chain_unlock_section]
            # Check if the section can be completed.
            if all(
                    ProgressOperations.is_status_progress_from_all_targets_str(req, progress_dictionary, Plan.DONE)
                    for
                    req
                    in
                    chain_reqs
            ):
                # Set the section.
                ProgressOperations.unlock_section(possible_chain_unlock_section, progress_dictionary)
