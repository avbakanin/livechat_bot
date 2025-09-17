"""
Factory patterns for object creation and configuration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar

from core.interfaces.repository import (
    IMessageRepository,
    IPaymentRepository,
    ISubscriptionRepository,
    IUserRepository,
)
from core.interfaces.service import (
    IMessageService,
    IPaymentService,
    ISubscriptionService,
    IUserService,
)

T = TypeVar('T')


class AbstractFactory(ABC):
    """Abstract factory interface."""
    
    @abstractmethod
    def create(self, *args, **kwargs) -> Any:
        """Create object."""


class ServiceFactory(AbstractFactory):
    """Factory for creating services."""
    
    def __init__(self, container):
        self.container = container
        
    def create_user_service(self) -> IUserService:
        """Create user service."""
        return self.container.get(IUserService)
        
    def create_message_service(self) -> IMessageService:
        """Create message service."""
        return self.container.get(IMessageService)
        
    def create_subscription_service(self) -> ISubscriptionService:
        """Create subscription service."""
        return self.container.get(ISubscriptionService)
        
    def create_payment_service(self) -> IPaymentService:
        """Create payment service."""
        return self.container.get(IPaymentService)


class RepositoryFactory(AbstractFactory):
    """Factory for creating repositories."""
    
    def __init__(self, connection):
        self.connection = connection
        
    def create_user_repository(self) -> IUserRepository:
        """Create user repository."""
        from infrastructure.repositories.user_repository import UserRepository
        return UserRepository(self.connection)
        
    def create_message_repository(self) -> IMessageRepository:
        """Create message repository."""
        from infrastructure.repositories.message_repository import MessageRepository
        return MessageRepository(self.connection)
        
    def create_subscription_repository(self) -> ISubscriptionRepository:
        """Create subscription repository."""
        from infrastructure.repositories.subscription_repository import (
            SubscriptionRepository,
        )
        return SubscriptionRepository(self.connection)
        
    def create_payment_repository(self) -> IPaymentRepository:
        """Create payment repository."""
        from infrastructure.repositories.payment_repository import PaymentRepository
        return PaymentRepository(self.connection)


class DomainObjectFactory(AbstractFactory):
    """Factory for creating domain objects."""
    
    @staticmethod
    def create_user(
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        gender_preference: str = "female",
        subscription_status: str = "free"
    ) -> 'User':
        """Create user domain object."""
        from shared.models.user import UserCreate
        return UserCreate(
            id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            gender_preference=gender_preference,
            subscription_status=subscription_status
        )
        
    @staticmethod
    def create_message(
        user_id: int,
        role: str,
        text: str
    ) -> 'Message':
        """Create message domain object."""
        from shared.models.message import MessageCreate
        return MessageCreate(
            user_id=user_id,
            role=role,
            text=text
        )
        
    @staticmethod
    def create_subscription(
        user_id: int,
        plan_type: str,
        duration_days: int
    ) -> 'Subscription':
        """Create subscription domain object."""
        from datetime import datetime, timedelta

        from shared.models.subscription import SubscriptionCreate
        
        expires_at = datetime.utcnow() + timedelta(days=duration_days)
        
        return SubscriptionCreate(
            user_id=user_id,
            plan_type=plan_type,
            expires_at=expires_at
        )
        
    @staticmethod
    def create_payment(
        user_id: int,
        amount: float,
        description: str,
        payment_status: str = "pending"
    ) -> 'Payment':
        """Create payment domain object."""
        from shared.models.payment import PaymentCreate
        return PaymentCreate(
            user_id=user_id,
            amount=amount,
            description=description,
            payment_status=payment_status
        )


class ConfigurationFactory(AbstractFactory):
    """Factory for creating configurations."""
    
    @staticmethod
    def create_openai_config(
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create OpenAI configuration."""
        return {
            "api_key": api_key,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "base_url": base_url
        }
        
    @staticmethod
    def create_database_config(
        host: str,
        port: int,
        database: str,
        user: str,
        password: str
    ) -> Dict[str, Any]:
        """Create database configuration."""
        return {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        
    @staticmethod
    def create_telegram_config(
        token: str,
        allowed_user_ids: set
    ) -> Dict[str, Any]:
        """Create Telegram configuration."""
        return {
            "token": token,
            "allowed_user_ids": allowed_user_ids
        }


class MiddlewareFactory(AbstractFactory):
    """Factory for creating middleware."""
    
    def __init__(self, container):
        self.container = container
        
    def create_access_middleware(self, allowed_ids: set):
        """Create access middleware."""
        from core.middleware import AccessMiddleware
        return AccessMiddleware(allowed_ids)
        
    def create_logging_middleware(self):
        """Create logging middleware."""
        from core.middleware import LoggingMiddleware
        return LoggingMiddleware()
        
    def create_service_middleware(self, user_service, message_service):
        """Create service middleware."""
        from core.middleware import ServiceMiddleware
        return ServiceMiddleware(user_service, message_service)
        
    def create_i18n_middleware(self):
        """Create i18n middleware."""
        from shared.middlewares.i18n_middleware import I18nMiddleware
        return I18nMiddleware()
        
    def create_fsm_middleware(self):
        """Create FSM middleware."""
        from shared.fsm.fsm_middleware import FSMMiddleware
        return FSMMiddleware()


class EventHandlerFactory(AbstractFactory):
    """Factory for creating event handlers."""
    
    def __init__(self, container):
        self.container = container
        
    def create_user_event_handlers(self):
        """Create user event handlers."""
        handlers = []
        
        # Add user created handler
        from application.event_handlers.user_event_handlers import UserCreatedHandler
        handlers.append(UserCreatedHandler(self.container))
        
        # Add user updated handler
        from application.event_handlers.user_event_handlers import UserUpdatedHandler
        handlers.append(UserUpdatedHandler(self.container))
        
        return handlers
        
    def create_message_event_handlers(self):
        """Create message event handlers."""
        handlers = []
        
        # Add message sent handler
        from application.event_handlers.message_event_handlers import MessageSentHandler
        handlers.append(MessageSentHandler(self.container))
        
        # Add limit exceeded handler
        from application.event_handlers.message_event_handlers import (
            MessageLimitExceededHandler,
        )
        handlers.append(MessageLimitExceededHandler(self.container))
        
        return handlers


class FactoryRegistry:
    """Registry for managing factories."""
    
    def __init__(self):
        self._factories: Dict[str, AbstractFactory] = {}
        
    def register_factory(self, name: str, factory: AbstractFactory):
        """Register factory."""
        self._factories[name] = factory
        
    def get_factory(self, name: str) -> AbstractFactory:
        """Get factory by name."""
        if name not in self._factories:
            raise ValueError(f"Factory {name} not registered")
        return self._factories[name]
        
    def create_service_factory(self, container) -> ServiceFactory:
        """Create and register service factory."""
        factory = ServiceFactory(container)
        self.register_factory("service", factory)
        return factory
        
    def create_repository_factory(self, connection) -> RepositoryFactory:
        """Create and register repository factory."""
        factory = RepositoryFactory(connection)
        self.register_factory("repository", factory)
        return factory


# Global factory registry
factory_registry = FactoryRegistry()
