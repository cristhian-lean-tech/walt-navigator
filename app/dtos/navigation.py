from dataclasses import dataclass

@dataclass
class NavigationDTO:
    content: str
    role: str

@dataclass
class NavigationResponseDTO:
    path: str
    description: str