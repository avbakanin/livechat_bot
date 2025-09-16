"""
Dependency Injection Container for managing dependencies.
"""

import inspect
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

T = TypeVar('T')


class DIContainer:
    """Simple Dependency Injection Container."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._logger = logging.getLogger(__name__)
        
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register singleton service."""
        self._services[interface] = implementation
        self._logger.debug(f"Registered singleton {interface.__name__} -> {implementation.__name__}")
        
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register transient service."""
        self._factories[interface] = lambda: self._create_instance(implementation)
        self._logger.debug(f"Registered transient {interface.__name__} -> {implementation.__name__}")
        
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register service instance."""
        self._singletons[interface] = instance
        self._logger.debug(f"Registered instance {interface.__name__}")
        
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register factory function."""
        self._factories[interface] = factory
        self._logger.debug(f"Registered factory {interface.__name__}")
        
    def get(self, interface: Type[T]) -> T:
        """Get service instance."""
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
            
        # Check factories
        if interface in self._factories:
            return self._factories[interface]()
            
        # Check services (singleton)
        if interface in self._services:
            if interface not in self._singletons:
                self._singletons[interface] = self._create_instance(self._services[interface])
            return self._singletons[interface]
            
        raise ValueError(f"Service {interface.__name__} not registered")
        
    def _create_instance(self, implementation: Type[T]) -> T:
        """Create instance with dependency injection."""
        try:
            # Get constructor signature
            signature = inspect.signature(implementation.__init__)
            args = []
            
            # Resolve dependencies
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                    
                param_type = param.annotation
                if param_type == inspect.Parameter.empty:
                    # Try to resolve by parameter name
                    param_type = self._get_type_by_name(param_name)
                    
                if param_type and param_type != inspect.Parameter.empty:
                    args.append(self.get(param_type))
                else:
                    # Use default value if available
                    if param.default != inspect.Parameter.empty:
                        args.append(param.default)
                    else:
                        raise ValueError(f"Cannot resolve dependency {param_name}")
                        
            return implementation(*args)
            
        except Exception as e:
            self._logger.error(f"Error creating instance of {implementation.__name__}: {e}")
            raise
            
    def _get_type_by_name(self, name: str) -> Optional[Type]:
        """Get type by parameter name."""
        # Simple name-based resolution
        type_mapping = {
            'pool': 'asyncpg.Pool',
            'event_bus': 'core.event_bus.EventBus',
            'uow_factory': 'core.unit_of_work.UnitOfWorkFactory',
        }
        
        if name in type_mapping:
            # This is simplified - in real implementation would use proper type resolution
            return None
            
        return None
        
    def is_registered(self, interface: Type[T]) -> bool:
        """Check if service is registered."""
        return (
            interface in self._services or 
            interface in self._factories or 
            interface in self._singletons
        )


class ServiceLocator:
    """Service Locator pattern implementation."""
    
    def __init__(self, container: DIContainer):
        self._container = container
        
    def get_service(self, interface: Type[T]) -> T:
        """Get service from container."""
        return self._container.get(interface)
        
    def get_optional_service(self, interface: Type[T]) -> Optional[T]:
        """Get service if registered, None otherwise."""
        try:
            return self._container.get(interface)
        except ValueError:
            return None


# Global container instance
container = DIContainer()
service_locator = ServiceLocator(container)
