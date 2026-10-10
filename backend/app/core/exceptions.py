class BusinessRuleError(Exception):
    """Raised when an ERP business rule is violated."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
