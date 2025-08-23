"""Validation models for army list rules checking."""

from typing import List

from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """Model representing a validation error."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    field: str = Field(..., description="Field that caused the error")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "code": "EXCEEDS_POINT_LIMIT",
                "message": "Army list exceeds 2000 point limit (current: 2150)",
                "field": "total_points",
            }
        }


class ValidationWarning(BaseModel):
    """Model representing a validation warning."""

    code: str = Field(..., description="Warning code")
    message: str = Field(..., description="Human-readable warning message")
    field: str = Field(..., description="Field that triggered the warning")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "code": "NO_BATTLELINE",
                "message": "Army has no Battleline units",
                "field": "units",
            }
        }


class ValidationResult(BaseModel):
    """Model representing the result of army list validation."""

    is_valid: bool = Field(..., description="Whether the list is valid")
    errors: List[ValidationError] = Field(
        default_factory=list, description="Validation errors"
    )
    warnings: List[ValidationWarning] = Field(
        default_factory=list, description="Validation warnings"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "is_valid": False,
                "errors": [
                    {
                        "code": "NO_WARLORD",
                        "message": "Army must have a Warlord",
                        "field": "units",
                    }
                ],
                "warnings": [
                    {
                        "code": "NO_BATTLELINE",
                        "message": "Army has no Battleline units",
                        "field": "units",
                    }
                ],
            }
        }
