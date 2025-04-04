import openai
from fastapi import HTTPException

from app.core.config import settings
from app.db.chroma import chroma_client 
from app.shared.const import CollectionName


class EmbeddingService:

   def exists_collection(self, collection_name: CollectionName):
      try:
         chroma_client.get_collection(collection_name.value)
         return True
      except Exception as e:
         return False
    
   def get_collection(self, collection_name: CollectionName):
      collection = None
      try:
         collection = chroma_client.get_collection(collection_name.value)
      except Exception as e:
         collection = chroma_client.create_collection(collection_name.value)
      
      return collection
   
   def generate_embedding(self, text: str):
      response = openai.embeddings.create(
           model=settings.EMBEDDING_MODEL,           
           input=text
      )
       
      return response.data[0].embedding

   def get_embedding(self, doc_id: str, collection_name: CollectionName):
      try:
         collection = self.get_collection(collection_name)
         results = collection.query(
            query_embeddings=[doc_id],
            n_results=2
         )
         return results
      except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

   def save_embedding(self, content: str, collection_name: CollectionName):
      try:
         embedding = self.generate_embedding(content)
         collection = self.get_collection(collection_name)
         results = collection.add(
            ids=["doc_id"],  # Unique ID for the document
            embeddings=[embedding],
            metadatas=[{"text": content}]
         )
         return results
      except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
   
   def search_text(self, text: str, collection_name: CollectionName):
      try:
         collection = self.get_collection(collection_name)
         results = collection.query(
            query_embeddings=[self.generate_embedding(text)],
            n_results=2
         )

         output = []
         for id_value, metadata, distance in zip(results["ids"][0], results["metadatas"][0], results["distances"][0]):
            output.append({
                  "path": id_value,
                  "description": metadata["description"],
                  "score": round((1-distance), 2)
            })
         
         return [output for output in output]
      except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))