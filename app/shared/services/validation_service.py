"""
Centralized validation service for common validation operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from shared.utils.datetime_utils import DateTimeUtils


class ValidationService:
    """Centralized validation service."""
    
    @staticmethod
    def validate_user_id(user_id: Any) -> bool:
        """Validate user ID."""
        return isinstance(user_id, int) and user_id > 0
    
    @staticmethod
    def validate_message_text(text: Optional[str], max_length: int = 2500) -> Dict[str, Any]:
        """Validate message text."""
        if not text:
            return {"is_valid": False, "error": "Message text is required"}
        
        if len(text.strip()) == 0:
            return {"is_valid": False, "error": "Message text cannot be empty"}
        
        if len(text) > max_length:
            return {
                "is_valid": False, 
                "error": f"Message too long. Maximum {max_length} characters",
                "current_length": len(text)
            }
        
        return {"is_valid": True}
    
    @staticmethod
    def validate_language(language: str) -> bool:
        """Validate language code."""
        supported_languages = ["en", "ru", "de", "es", "fr", "it", "pl", "sr", "tr"]
        return language in supported_languages
    
    @staticmethod
    def validate_gender_preference(gender: str) -> bool:
        """Validate gender preference."""
        valid_genders = ["female", "male"]
        return gender in valid_genders
    
    @staticmethod
    def validate_subscription_status(status: str) -> bool:
        """Validate subscription status."""
        valid_statuses = ["free", "premium"]
        return status in valid_statuses
    
    @staticmethod
    def validate_subscription_expiry(expires_at: Optional[datetime]) -> Dict[str, Any]:
        """Validate subscription expiry date."""
        if expires_at is None:
            return {"is_valid": True, "is_expired": False}
        
        is_expired = DateTimeUtils.is_expired(expires_at)
        return {
            "is_valid": True,
            "is_expired": is_expired,
            "expires_at": expires_at
        }
    
    @staticmethod
    def validate_personality_profile(profile: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Validate personality profile."""
        if profile is None:
            return {"is_valid": True, "profile": None}
        
        if not isinstance(profile, dict):
            return {"is_valid": False, "error": "Personality profile must be a dictionary"}
        
        # Check if all values are between 0 and 1
        for trait, value in profile.items():
            if not isinstance(value, (int, float)):
                return {"is_valid": False, "error": f"Trait '{trait}' must be a number"}
            
            if not 0 <= value <= 1:
                return {"is_valid": False, "error": f"Trait '{trait}' must be between 0 and 1"}
        
        return {"is_valid": True, "profile": profile}
    
    @staticmethod
    def validate_username(username: Optional[str]) -> Dict[str, Any]:
        """Validate username."""
        if username is None:
            return {"is_valid": True, "username": None}
        
        if not isinstance(username, str):
            return {"is_valid": False, "error": "Username must be a string"}
        
        if len(username) > 32:
            return {"is_valid": False, "error": "Username too long. Maximum 32 characters"}
        
        return {"is_valid": True, "username": username}
    
    @staticmethod
    def validate_name(name: Optional[str], field_name: str = "name") -> Dict[str, Any]:
        """Validate first/last name."""
        if name is None:
            return {"is_valid": True, field_name: None}
        
        if not isinstance(name, str):
            return {"is_valid": False, "error": f"{field_name.capitalize()} must be a string"}
        
        if len(name.strip()) == 0:
            return {"is_valid": False, "error": f"{field_name.capitalize()} cannot be empty"}
        
        if len(name) > 64:
            return {"is_valid": False, "error": f"{field_name.capitalize()} too long. Maximum 64 characters"}
        
        return {"is_valid": True, field_name: name.strip()}
    
    @staticmethod
    def validate_multiple_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
        """Validate multiple fields at once."""
        errors = []
        
        for field_name, value in fields.items():
            if field_name == "user_id":
                if not ValidationService.validate_user_id(value):
                    errors.append(f"Invalid user_id: {value}")
            
            elif field_name == "message_text":
                result = ValidationService.validate_message_text(value)
                if not result["is_valid"]:
                    errors.append(result["error"])
            
            elif field_name == "language":
                if not ValidationService.validate_language(value):
                    errors.append(f"Invalid language: {value}")
            
            elif field_name == "gender_preference":
                if not ValidationService.validate_gender_preference(value):
                    errors.append(f"Invalid gender preference: {value}")
            
            elif field_name == "subscription_status":
                if not ValidationService.validate_subscription_status(value):
                    errors.append(f"Invalid subscription status: {value}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }


# Global instance
validation_service = ValidationService()
