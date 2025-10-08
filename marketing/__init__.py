# Import all feature classes from models.py to make them available at package level
from .models import (
    CustomerInteraction,
    CustomerInteractionDocument,
    CustomerInteractionSearch,
    ProductArea,
    UserEventType,
    StructuredOutput,
    User,
    Event,
    UserEventAnalysis,
    EventType,
)

__all__ = [
    "CustomerInteraction",
    "CustomerInteractionDocument",
    "CustomerInteractionSearch",
    "ProductArea",
    "UserEventType",
    "StructuredOutput",
    "User",
    "Event",
    "UserEventAnalysis",
    "EventType",
]
