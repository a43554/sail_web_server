
# The class of a custom form error exception.
class FormErrorException(Exception):

    # The constructor for the custom exception.
    def __init__(self, exception_data):
        # Call the super constructor.
        super().__init__()
        # Store the exception data.
        self.exception_data = exception_data


# A warning exception.
class WarningException(Exception):
    pass