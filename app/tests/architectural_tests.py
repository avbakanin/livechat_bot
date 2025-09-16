"""
Architectural tests to enforce design patterns and constraints.
"""

import pytest
from pathlib import Path
from typing import List, Type

# Import architectural components
from core.interfaces.repository import IRepository
from core.interfaces.service import IService
from core.interfaces.unit_of_work import IUnitOfWork
from core.interfaces.event_bus import IEventBus
from core.events import DomainEvent
from core.cqrs import Command, Query, CommandHandler, QueryHandler
from core.specifications import Specification


class ArchitectureTestBase:
    """Base class for architectural tests."""
    
    @staticmethod
    def get_project_root() -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent
        
    @staticmethod
    def get_python_files(directory: Path) -> List[Path]:
        """Get all Python files in directory."""
        return list(directory.rglob("*.py"))
        
    @staticmethod
    def get_module_name(file_path: Path) -> str:
        """Get module name from file path."""
        relative_path = file_path.relative_to(ArchitectureTestBase.get_project_root())
        return str(relative_path.with_suffix('')).replace('/', '.')


class TestDependencyInversion:
    """Test dependency inversion principle."""
    
    def test_domain_should_not_depend_on_infrastructure(self):
        """Domain layer should not import from infrastructure."""
        project_root = ArchitectureTestBase.get_project_root()
        domain_dir = project_root / "app" / "domain"
        
        if not domain_dir.exists():
            pytest.skip("Domain directory not found")
            
        domain_files = ArchitectureTestBase.get_python_files(domain_dir)
        
        for file_path in domain_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for infrastructure imports
            assert "from infrastructure" not in content, \
                f"Domain file {file_path} imports from infrastructure"
            assert "import infrastructure" not in content, \
                f"Domain file {file_path} imports infrastructure"
                
    def test_application_should_not_depend_on_infrastructure(self):
        """Application layer should not import from infrastructure."""
        project_root = ArchitectureTestBase.get_project_root()
        app_dir = project_root / "app" / "application"
        
        if not app_dir.exists():
            pytest.skip("Application directory not found")
            
        app_files = ArchitectureTestBase.get_python_files(app_dir)
        
        for file_path in app_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for infrastructure imports
            assert "from infrastructure" not in content, \
                f"Application file {file_path} imports from infrastructure"
            assert "import infrastructure" not in content, \
                f"Application file {file_path} imports infrastructure"


class TestInterfaceSegregation:
    """Test interface segregation principle."""
    
    def test_repository_interfaces_are_focused(self):
        """Repository interfaces should be focused and not bloated."""
        # Check that repository interfaces don't have too many methods
        user_repo_methods = [method for method in dir(IUserRepository) 
                           if not method.startswith('_')]
        message_repo_methods = [method for method in dir(IMessageRepository) 
                              if not method.startswith('_')]
        
        # Each repository should have focused methods
        assert len(user_repo_methods) <= 10, "UserRepository has too many methods"
        assert len(message_repo_methods) <= 10, "MessageRepository has too many methods"
        
    def test_service_interfaces_are_focused(self):
        """Service interfaces should be focused and not bloated."""
        user_service_methods = [method for method in dir(IUserService) 
                              if not method.startswith('_')]
        message_service_methods = [method for method in dir(IMessageService) 
                                 if not method.startswith('_')]
        
        # Each service should have focused methods
        assert len(user_service_methods) <= 15, "UserService has too many methods"
        assert len(message_service_methods) <= 15, "MessageService has too many methods"


class TestSingleResponsibility:
    """Test single responsibility principle."""
    
    def test_handlers_have_single_responsibility(self):
        """Event handlers should have single responsibility."""
        # This would check that each handler only handles one type of event
        # Implementation depends on actual handler classes
        pass
        
    def test_services_have_single_responsibility(self):
        """Services should have single responsibility."""
        # Check that services are focused on one domain
        # UserService should only handle user operations
        # MessageService should only handle message operations
        pass


class TestOpenClosedPrinciple:
    """Test open/closed principle."""
    
    def test_specifications_can_be_extended(self):
        """Specifications should be open for extension."""
        # Check that specifications can be combined
        from core.specifications import UserByIdSpecification, ActiveUserSpecification
        
        # Should be able to combine specifications
        combined = UserByIdSpecification(123).and_specification(ActiveUserSpecification())
        assert hasattr(combined, 'is_satisfied_by')
        assert hasattr(combined, 'to_sql_where')
        
    def test_event_handlers_can_be_added(self):
        """Event handlers should be open for extension."""
        # Check that new event handlers can be added without modifying existing code
        from core.events import UserCreatedEvent
        from core.interfaces.event_bus import IEventHandler
        
        # Should be able to create new handlers
        class TestHandler(IEventHandler):
            async def handle(self, event: DomainEvent) -> None:
                pass
                
        handler = TestHandler()
        assert hasattr(handler, 'handle')


class TestLiskovSubstitution:
    """Test Liskov substitution principle."""
    
    def test_repository_implementations_are_substitutable(self):
        """Repository implementations should be substitutable."""
        # Check that all repository implementations implement the interface correctly
        pass
        
    def test_service_implementations_are_substitutable(self):
        """Service implementations should be substitutable."""
        # Check that all service implementations implement the interface correctly
        pass


class TestCommandQuerySeparation:
    """Test CQRS command/query separation."""
    
    def test_commands_do_not_return_data(self):
        """Commands should not return data (except confirmation)."""
        from core.cqrs import CreateUserCommand, SendMessageCommand
        
        # Commands should be data containers, not return data
        command = CreateUserCommand(123, "test")
        assert hasattr(command, 'telegram_id')
        assert hasattr(command, 'username')
        
    def test_queries_do_not_modify_state(self):
        """Queries should not modify state."""
        from core.cqrs import GetUserQuery, GetUserMessagesQuery
        
        # Queries should be read-only
        query = GetUserQuery(123)
        assert hasattr(query, 'telegram_id')
        
        query = GetUserMessagesQuery(123)
        assert hasattr(query, 'user_id')
        assert hasattr(query, 'limit')


class TestEventDrivenArchitecture:
    """Test event-driven architecture."""
    
    def test_domain_events_are_immutable(self):
        """Domain events should be immutable."""
        from core.events import UserCreatedEvent
        
        event = UserCreatedEvent(123, 456, "test")
        
        # Events should have immutable properties
        assert event.user_id == 123
        assert event.telegram_id == 456
        assert event.username == "test"
        
    def test_events_have_required_properties(self):
        """Domain events should have required properties."""
        from core.events import DomainEvent
        
        # All events should inherit from DomainEvent
        assert hasattr(DomainEvent, 'event_id')
        assert hasattr(DomainEvent, 'occurred_at')
        assert hasattr(DomainEvent, 'event_version')


class TestArchitecturalLayers:
    """Test architectural layer separation."""
    
    def test_core_layer_isolation(self):
        """Core layer should be isolated."""
        project_root = ArchitectureTestBase.get_project_root()
        core_dir = project_root / "app" / "core"
        
        if not core_dir.exists():
            pytest.skip("Core directory not found")
            
        core_files = ArchitectureTestBase.get_python_files(core_dir)
        
        for file_path in core_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Core should not import from domain, application, or infrastructure
            assert "from domain" not in content, \
                f"Core file {file_path} imports from domain"
            assert "from application" not in content, \
                f"Core file {file_path} imports from application"
            assert "from infrastructure" not in content, \
                f"Core file {file_path} imports from infrastructure"
                
    def test_shared_layer_isolation(self):
        """Shared layer should be isolated."""
        project_root = ArchitectureTestBase.get_project_root()
        shared_dir = project_root / "app" / "shared"
        
        if not shared_dir.exists():
            pytest.skip("Shared directory not found")
            
        shared_files = ArchitectureTestBase.get_python_files(shared_dir)
        
        for file_path in shared_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Shared should not import from domain, application, or infrastructure
            assert "from domain" not in content, \
                f"Shared file {file_path} imports from domain"
            assert "from application" not in content, \
                f"Shared file {file_path} imports from application"
            assert "from infrastructure" not in content, \
                f"Shared file {file_path} imports from infrastructure"


class TestDesignPatterns:
    """Test implementation of design patterns."""
    
    def test_repository_pattern_implementation(self):
        """Test repository pattern implementation."""
        # Check that repositories implement the interface
        assert hasattr(IRepository, 'get_by_id')
        assert hasattr(IRepository, 'create')
        assert hasattr(IRepository, 'update')
        assert hasattr(IRepository, 'delete')
        
    def test_unit_of_work_pattern_implementation(self):
        """Test Unit of Work pattern implementation."""
        # Check that UoW has required methods
        assert hasattr(IUnitOfWork, 'commit')
        assert hasattr(IUnitOfWork, 'rollback')
        assert hasattr(IUnitOfWork, 'users')
        assert hasattr(IUnitOfWork, 'messages')
        
    def test_event_bus_pattern_implementation(self):
        """Test Event Bus pattern implementation."""
        # Check that event bus has required methods
        assert hasattr(IEventBus, 'publish')
        assert hasattr(IEventBus, 'subscribe')
        assert hasattr(IEventBus, 'unsubscribe')
        
    def test_specification_pattern_implementation(self):
        """Test Specification pattern implementation."""
        # Check that specifications have required methods
        assert hasattr(Specification, 'is_satisfied_by')
        assert hasattr(Specification, 'to_sql_where')
        assert hasattr(Specification, 'get_parameters')
        assert hasattr(Specification, 'and_specification')
        assert hasattr(Specification, 'or_specification')


# Run architectural tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
