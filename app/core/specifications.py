"""
Specification pattern for complex business rules and queries.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.interfaces.repository import IRepository


class Specification(ABC):
    """Base specification interface."""
    
    @abstractmethod
    def is_satisfied_by(self, entity: Any) -> bool:
        """Check if entity satisfies specification."""
        
    @abstractmethod
    def to_sql_where(self) -> str:
        """Convert to SQL WHERE clause."""
        
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get SQL parameters."""
        
    def and_specification(self, other: 'Specification') -> 'AndSpecification':
        """Combine with AND."""
        return AndSpecification(self, other)
        
    def or_specification(self, other: 'Specification') -> 'OrSpecification':
        """Combine with OR."""
        return OrSpecification(self, other)
        
    def not_specification(self) -> 'NotSpecification':
        """Negate specification."""
        return NotSpecification(self)


class CompositeSpecification(Specification):
    """Base class for composite specifications."""
    
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right


class AndSpecification(CompositeSpecification):
    """AND specification."""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        return self.left.is_satisfied_by(entity) and self.right.is_satisfied_by(entity)
        
    def to_sql_where(self) -> str:
        return f"({self.left.to_sql_where()}) AND ({self.right.to_sql_where()})"
        
    def get_parameters(self) -> Dict[str, Any]:
        params = self.left.get_parameters()
        params.update(self.right.get_parameters())
        return params


class OrSpecification(CompositeSpecification):
    """OR specification."""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        return self.left.is_satisfied_by(entity) or self.right.is_satisfied_by(entity)
        
    def to_sql_where(self) -> str:
        return f"({self.left.to_sql_where()}) OR ({self.right.to_sql_where()})"
        
    def get_parameters(self) -> Dict[str, Any]:
        params = self.left.get_parameters()
        params.update(self.right.get_parameters())
        return params


class NotSpecification(Specification):
    """NOT specification."""
    
    def __init__(self, spec: Specification):
        self.spec = spec
        
    def is_satisfied_by(self, entity: Any) -> bool:
        return not self.spec.is_satisfied_by(entity)
        
    def to_sql_where(self) -> str:
        return f"NOT ({self.spec.to_sql_where()})"
        
    def get_parameters(self) -> Dict[str, Any]:
        return self.spec.get_parameters()


# User Specifications
class UserByIdSpecification(Specification):
    """User by ID specification."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.id == self.user_id
        
    def to_sql_where(self) -> str:
        return "id = :user_id"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"user_id": self.user_id}


class UserByTelegramIdSpecification(Specification):
    """User by Telegram ID specification."""
    
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.telegram_id == self.telegram_id
        
    def to_sql_where(self) -> str:
        return "telegram_id = :telegram_id"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"telegram_id": self.telegram_id}


class ActiveUserSpecification(Specification):
    """Active user specification."""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.is_active if hasattr(entity, 'is_active') else True
        
    def to_sql_where(self) -> str:
        return "is_active = :is_active"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"is_active": True}


class PremiumUserSpecification(Specification):
    """Premium user specification."""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.subscription_status == 'premium'
        
    def to_sql_where(self) -> str:
        return "subscription_status = :subscription_status"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"subscription_status": "premium"}


# Message Specifications
class MessageByUserSpecification(Specification):
    """Message by user specification."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.user_id == self.user_id
        
    def to_sql_where(self) -> str:
        return "user_id = :user_id"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"user_id": self.user_id}


class MessageByDateRangeSpecification(Specification):
    """Message by date range specification."""
    
    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
        
    def is_satisfied_by(self, entity: Any) -> bool:
        return self.start_date <= entity.created_at <= self.end_date
        
    def to_sql_where(self) -> str:
        return "created_at BETWEEN :start_date AND :end_date"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "start_date": self.start_date,
            "end_date": self.end_date
        }


class MessageByRoleSpecification(Specification):
    """Message by role specification."""
    
    def __init__(self, role: str):
        self.role = role
        
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.role == self.role
        
    def to_sql_where(self) -> str:
        return "role = :role"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"role": self.role}


# Payment Specifications
class PaymentByUserSpecification(Specification):
    """Payment by user specification."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.user_id == self.user_id
        
    def to_sql_where(self) -> str:
        return "user_id = :user_id"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"user_id": self.user_id}


class PendingPaymentSpecification(Specification):
    """Pending payment specification."""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.payment_status == 'pending'
        
    def to_sql_where(self) -> str:
        return "payment_status = :payment_status"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"payment_status": "pending"}


class CompletedPaymentSpecification(Specification):
    """Completed payment specification."""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        return entity.payment_status == 'completed'
        
    def to_sql_where(self) -> str:
        return "payment_status = :payment_status"
        
    def get_parameters(self) -> Dict[str, Any]:
        return {"payment_status": "completed"}


class SpecificationRepository:
    """Repository with specification support."""
    
    def __init__(self, repository: IRepository):
        self.repository = repository
        
    async def find_by_specification(
        self, 
        specification: Specification,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Any]:
        """Find entities by specification."""
        # This would be implemented by the concrete repository
        # using the specification's SQL and parameters
