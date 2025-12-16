from enum import Enum

class CollectionName(Enum):
    NAVIGATION = "navigation"
    FAQS = "faqs"

class IntentType(str, Enum):
    """Intent classification types for FAQ routing."""
    IN_SCOPE = "IN_SCOPE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    SMALL_TALK = "SMALL_TALK"