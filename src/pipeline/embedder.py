from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, text):
        pass


class OpenAIEmbedder(BaseEmbedder):
    model = "text-embedding-3-small"

    def __init__(self, api_key):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def embed(self, text):
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
        )
        return response.data[0].embedding


def embed_chunks(chunks, embedder):
    for chunk in chunks:
        chunk["embedding"] = embedder.embed(chunk["content"])
