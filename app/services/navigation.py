import json

from app.shared.const import CollectionName
from .embdding import EmbeddingService
from app.shared.paths import PATHS
from app.shared.forms import FORMS

class NavigationService():
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def suggest_routes(self, content: str, role: str) -> any:
      result = self.embedding_service.search_text(content, CollectionName.NAVIGATION)

      detected_benefit = self._detect_benefit(content)
      if detected_benefit:
        result["benefit"] = detected_benefit

        return {"message": f"Great! You're requesting {detected_benefit}. Let's start. When would you like to begin?"}

      return result
    
    def init_database(self):
        databseWasInitialized = self.embedding_service.exists_collection(CollectionName.NAVIGATION)
        if databseWasInitialized:
            return
        
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        ids = [item["path"] for item in PATHS]
        documents = [item["description"] for item in PATHS]
        metadatas = [{"description": item["description"]} for item in PATHS]

        collection.add(
            ids=ids,
            embeddings=[self.embedding_service.generate_embedding(doc) for doc in documents],
            metadatas=metadatas
        )
    
    def cleanup_database(self):
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        collection.delete()


    def _detect_benefit(self, content: str) -> str or None:
        for benefit in FORMS.keys():
           if benefit in content.lower():
               return benefit            
        return None
