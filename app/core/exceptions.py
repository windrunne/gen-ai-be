"""
Custom exceptions for the application
"""
from fastapi import HTTPException
from typing import Optional


class LLMLabException(Exception):
    """Base exception for LLM Lab application"""
    pass


class ExperimentNotFoundError(LLMLabException):
    """Raised when experiment is not found"""
    pass


class ResponseNotFoundError(LLMLabException):
    """Raised when response is not found"""
    pass


class LLMServiceError(LLMLabException):
    """Raised when LLM service fails"""
    pass


class ValidationError(LLMLabException):
    """Raised when validation fails"""
    pass


def raise_experiment_not_found(experiment_id: int) -> HTTPException:
    """Raise HTTP 404 for experiment not found"""
    raise HTTPException(
        status_code=404,
        detail=f"Experiment with id {experiment_id} not found"
    )


def raise_response_not_found(response_id: int) -> HTTPException:
    """Raise HTTP 404 for response not found"""
    raise HTTPException(
        status_code=404,
        detail=f"Response with id {response_id} not found"
    )
