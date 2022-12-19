def default_if_none(data, if_none, if_not_none=None):
    # Check if data is none.
    if data is None:
        return if_none
    elif if_not_none is None:
        return data
    else:
        return if_not_none(data)


def run_if_none(data, if_not_none=(lambda x: None)):
    # Check if data is none.
    if data is not None:
        if_not_none(data)


def false_if_error(expression) -> bool:
    try:
        expression()
        return True
    except:
        return False
