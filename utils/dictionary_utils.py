from typing import Callable, TypeVar, Dict

K = TypeVar("K")
V = TypeVar("V")


# Check if key exists and matches element.
def in_and_predicate(input_dictionary: Dict[K, V], key: K, predicate: Callable[[V], bool]):
    # Return the result.
    return key in input_dictionary and predicate(input_dictionary[key])


# Check if key exists and matches element.
def in_and_equals(input_dictionary: Dict[K, V], key: K, target: V):
    # Return the result.
    return key in input_dictionary and input_dictionary[key] == target


# Check if key exists and does not match element.
def not_in_or_differs(input_dictionary: Dict[K, V], key: K, target: V):
    # Return the result.
    return key not in input_dictionary or input_dictionary[key] != target
