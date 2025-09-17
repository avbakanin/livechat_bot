"""
Core interfaces for dependency inversion and abstraction.
"""

from .event_bus import IEventBus
from .repository import IRepository
from .service import IService
from .unit_of_work import IUnitOfWork

__all__ = [
    "IRepository",
    "IUnitOfWork", 
    "IEventBus",
    "IService"
]
