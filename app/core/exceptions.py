from fastapi import HTTPException, status # type: ignore


class StudyAssistantException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DocumentProcessingError(StudyAssistantException):
    pass


class EmbeddingError(StudyAssistantException):
    pass


class VectorStoreError(StudyAssistantException):
    pass


class AuthenticationError(StudyAssistantException):
    pass


class ValidationError(StudyAssistantException):
    pass


def create_http_exception(status_code: int, detail: str):
    return HTTPException(
        status_code=status_code, 
        detail=detail
    )