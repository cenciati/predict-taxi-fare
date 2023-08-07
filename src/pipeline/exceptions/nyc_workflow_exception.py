from typing import Optional


class NYCWorkflowException(Exception):
    """General or specific excpetion to be used in the NYC taxis
    workflow pipeline."""

    def __init__(
        self,
        message: Optional[
            str
        ] = 'New York City taxi workflow could not be completed.',
    ) -> None:
        self.message = message

    def __str__(self):
        return self.message
