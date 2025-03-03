from chromadb import PersistentClient
from chromadb.config import Settings



chroma_client = PersistentClient(path="./data/chroma")

# def save_embedding(embedding_id: str, content: list, collection_name: CollectionName):
#     collection = chroma_client.get_or_create_collection(collection_name.value)
#     collection.add(
#         documents=[embedding_id],
#         embeddings=[content],
#         metadatas=[{"id": embedding_id}],
#     )

# def get_embedding(embedding_id: str, collection_name: CollectionName):
#     collection = chroma_client.get_collection(collection_name.value)
#     results = collection.query(
#         query_embeddings=[embedding_id],
#         n_results=1
#     )

#     return results['documents'][0] if results['documents'] else None