print("EMBEDDINGS.PY IMPORTED")
from sentence_transformers import (
    SentenceTransformer
)

class EmbeddingModel:
    _model = None
    @classmethod
    def get_model(cls):
    
        print("LOADING SENTENCE TRANSFORMER")
    
        if cls._model is None:
        
            cls._model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
    
        print("MODEL LOADED")
    
        return cls._model

    @classmethod
    def embed_documents(
        cls,
        texts
    ):

        model = cls.get_model()

        return model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

    @classmethod
    def embed_query(
        cls,
        query
    ):

        model = cls.get_model()

        return model.encode(
            query,
            normalize_embeddings=True
        ).tolist()