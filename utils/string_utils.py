# Return a shortened string
def shorten_string(input_string: str, max_length: int, include_triple_dots: bool = True) -> str:
    # Return teh truncated string.
    return (
        input_string[:max_length] + ('...' if include_triple_dots else '')
    ) if len(input_string) > max_length else input_string
