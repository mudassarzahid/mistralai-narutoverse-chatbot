from fastapi import HTTPException
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pydantic import TypeAdapter

from database.database import Database
from datamodels.models import Character, CharacterData, EmbeddingMapping
from utils.consts import MISTRAL_EMBED_MODEL, VECTOR_DB_DIR
from utils.exceptions import NotFoundError


class RAG:
    def __init__(self):
        self.db = Database()

    def load_character_data(self, character_id: int) -> list[Document]:
        # TODO: pydantic model for metadata
        # Fetch characters from the database
        character: Character = self.db.get_by_id(character_id, Character)

        # Convert characters to Langchain Document format
        documents = [
            Document(
                page_content=character.summary,
                metadata={
                    "character_id": character.id,
                    "source": "sqlite_database",
                    "name": character.name,
                    "tag_1": "Summary",
                    "tag_2": "null",
                    "tag_3": "null",
                },
            )
        ]

        character_data_list = TypeAdapter(list[CharacterData])
        for section in character_data_list.validate_python(character.data):
            documents.append(
                Document(
                    page_content=section.text,
                    metadata={
                        "character_id": character.id,
                        "source": "sqlite_database",
                        "name": character.name,
                        "tag_1": section.tag_1,
                        "tag_2": section.tag_2 or "null",
                        "tag_3": section.tag_2 or "null",
                    },
                )
            )

        return documents

    def build(self, character_id: int):
        documents = self.load_character_data(character_id)

        # Split the text into chunks for embedding
        text_splitter = CharacterTextSplitter(
            separator=".", chunk_size=256, chunk_overlap=64
        )

        split_documents = []
        for document in documents:
            split_documents.extend(text_splitter.split_documents([document]))

        # Create embeddings and save them in Chroma vector database
        try:
            Chroma.from_documents(
                split_documents,
                persist_directory=VECTOR_DB_DIR,
                embedding=MistralAIEmbeddings(model=MISTRAL_EMBED_MODEL),
            )
        except KeyError as error:
            print("It looks like MistralAI backend is unreachable...")

    def retriever(self, character_id: int) -> VectorStoreRetriever:
        # TODO: pydantic model for search_kwargs, Custom exception for db.get
        # TODO: Logging not printing
        try:
            print("check if vectors exist...")
            self.db.get_by_id(character_id, EmbeddingMapping, id_key="character_id")
        except NotFoundError:
            print("vectors don't exist... build....")
            self.build(character_id)
            self.db.create(EmbeddingMapping(character_id=character_id))

        vectordb = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=MistralAIEmbeddings(model=MISTRAL_EMBED_MODEL),
        )
        return vectordb.as_retriever(
            search_kwargs={"k": 2, "filter": {"character_id": character_id}}
        )
