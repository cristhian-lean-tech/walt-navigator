from app.shared.const import CollectionName
from app.services.embdding import EmbeddingService
from app.shared.onboarding_faqs import ONBOARDING_FAQS
from app.shared.paths import PATHS

def load_faqs():
    embedding_service = EmbeddingService()
    collectionWasInitialized = embedding_service.exists_collection(CollectionName.FAQS)
    if collectionWasInitialized:
        return
    
    collection = embedding_service.get_collection(CollectionName.FAQS)
    ids = [item["id"] for item in ONBOARDING_FAQS]
    documents = [item["question"] for item in ONBOARDING_FAQS]
    metadata = [{"user_type": item["role"], "answer": item["answer"], "link": item["link"], "point_of_contact": item["point_of_contact"]} for item in ONBOARDING_FAQS]
    
    collection.add(
        ids=ids,
        embeddings=[embedding_service.generate_embedding(doc) for doc in documents],
        metadatas=metadata
    )

    print("Faqs loaded successfully")
   
def load_paths():
    embedding_service = EmbeddingService()
    was_collection_initialized = embedding_service.exists_collection(CollectionName.NAVIGATION)
    if was_collection_initialized:
        return
    
    collection = embedding_service.get_collection(CollectionName.NAVIGATION)
    ids = [item["path"] for item in PATHS]
    documents = [item["description"] for item in PATHS]
    metadata = [{"user_type": item["user_type"], "short_description": item["short_description"]} for item in PATHS]
    collection.add(
        ids=ids,
        embeddings=[embedding_service.generate_embedding(doc) for doc in documents],
        metadatas=metadata
    )

    print("Paths loaded successfully")