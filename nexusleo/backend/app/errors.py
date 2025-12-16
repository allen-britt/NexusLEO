from __future__ import annotations

from enum import Enum


class ErrorToken(str, Enum):
    INVALID_REQUEST = "invalid_request"
    CASE_NOT_FOUND = "case_not_found"
    DOCUMENT_NOT_FOUND = "document_not_found"
    ACTIVITY_NOT_FOUND = "activity_not_found"
    NOT_AVAILABLE = "not_available"
    USER_NOT_FOUND = "user_not_found"
    SHIFT_NOT_FOUND = "shift_not_found"


ALL_ERROR_TOKENS: frozenset[str] = frozenset(token.value for token in ErrorToken)
