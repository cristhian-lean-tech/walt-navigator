from pydantic import BaseModel
from typing import List

class Embedding(BaseModel):
    id: str
    vector: List[float]
    metadata: dict

class EmbeddingCreate(BaseModel):
    vector: List[float]
    metadata: dict

class EmbeddingResponse(BaseModel):
    id: str
    vector: List[float]
    metadata: dict