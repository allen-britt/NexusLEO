from __future__ import annotations

from enum import Enum


class ErrorToken(str, Enum):
    INVALID_REQUEST = "invalid_request"
    CASE_NOT_FOUND = "case_not_found"
    DOCUMENT_NOT_FOUND = "document_not_found"
    ACTIVITY_NOT_FOUND = "activity_not_found"
    CATALOG_NOT_FOUND = "catalog_not_found"
    STATE_CONTEXT_REQUIRED = "state_context_required"
    CASE_STATE_NOT_SET = "case_state_not_set"
    CASE_FACTS_NOT_SET = "case_facts_not_set"
    NOT_AVAILABLE = "not_available"
    USER_NOT_FOUND = "user_not_found"
    SHIFT_NOT_FOUND = "shift_not_found"


ALL_ERROR_TOKENS: frozenset[str] = frozenset(token.value for token in ErrorToken)
