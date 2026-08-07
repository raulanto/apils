class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    status_code: int = 400

    def __init__(self, message: str, details: list[dict] | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    status_code = 422

class FileProcessingDomainError(DomainError):
    code = "FILE_PROCESSING_ERROR"
    status_code = 400
