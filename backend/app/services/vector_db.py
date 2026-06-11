from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from app.core.config import settings
import uuid

client = QdrantClient(
    host = settings.QDRANT_HOST,
    port = settings.QDRANT_PORT,
)

COLLECTION = settings.QDRANT_COLLECTION
VECTOR_DIM = settings.EMBEDDING_DIM

#Create collection
def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name = COLLECTION,
            vectors_config = VectorParams(
                size = VECTOR_DIM,
                distance = Distance.COSINE,
            ),
        )
        print(f"[QDRANT] create Collection '{COLLECTION}' successfully")
    else: 
        print(f"[QDRANT] Collection '{COLLECTION}' is existing")

#Save chunks + embedding to Qdrant

def upsert_chunks(
        doc_id: str,
        doc_name: str,
        chunks: list[str],
        embeddings: list[list[float]],
):
    points = [
        PointStruct(
            id = str(uuid.uuid4()),
            vector = embedding,
            payload = {
                "doc_id": doc_id,
                "doc_name": doc_name,
                "text": chunk,
                "chunk_index": i,
            },
        )
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    print(f"[Qdrant] save {len(points)} chunks for '{doc_name}'")

#Find semantics

def search(
        query_vector: list[float],
        top_k: int = 5,
        doc_id: str = None,
) -> list[dict]:
    
    query_filter = None
    if doc_id:
        query_filter = Filter(
            must = [FieldCondition(
                key = "doc_id",
                match = MatchValue(value = doc_id),
            )]
        )
    results = client.search(
        collection_name = COLLECTION,
        query_vector = query_vector,
        limit = top_k,
        query_filter = query_filter,
        with_payload = True,
    )

    return [
        {
            "text": r.payload["text"],
            "doc_name": r.payload["doc_name"],
            "doc_id": r.payload["doc_id"],
            "score": round(r.score,4),
        }
        for r in results
    ]

def delete_by_doc_id(doc_id: str):
    """Gọi khi user xóa file — xóa hết chunk liên quan trong Qdrant."""
    client.delete(
        collection_name=COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(
                key="doc_id",
                match=MatchValue(value=doc_id),
            )]
        ),
    )
    print(f"[Qdrant] deleted chunks of doc_id='{doc_id}'")


def get_collection_info() -> dict:
    info = client.get_collection(COLLECTION)
    return {
        "name":         COLLECTION,
        "total_points": info.points_count,
        "status":       info.status,
    }
