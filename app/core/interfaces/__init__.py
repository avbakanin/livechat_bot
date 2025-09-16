"""
Core interfaces for dependency inversion and abstraction.
"""

from .repository import IRepository
from .unit_of_work import IUnitOfWork
from .event_bus import IEventBus
from .service import IService

__all__ = [
    "IRepository",
    "IUnitOfWork", 
    "IEventBus",
    "IService"
]
