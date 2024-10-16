from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pydantic import TypeAdapter

from consts import MISTRAL_API_KEY, MISTRAL_EMBED_MODEL, VECTOR_DB_DIR
from database.database import Database
from datamodels.models import Character, CharacterData

db = Database()


class RAG:

    @staticmethod
    def load_character_data(character_id: int) -> list[Document]:
        # TODO: pydantic model for metadata
        # Fetch characters from the database
        character: Character = db.get_by_id(character_id, Character)

        # Convert characters to Langchain Document format
        documents = [
            Document(
                page_content=character.summary,
                metadata={
                    "character_id": character.id,
                    "source": "sqlite_database",
                    "name": character.name,
                    "tag_1": "Summary",
                    "tag_2": "None",
                    "tag_3": "None",
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
                        "tag_2": section.tag_2 or "None",
                        "tag_3": section.tag_2 or "None",
                    },
                )
            )

        return documents

    def build(self, character_id: int):
        documents = self.load_character_data(character_id)

        # Split the text into chunks for embedding
        text_splitter = CharacterTextSplitter(
            separator=".", chunk_size=1024, chunk_overlap=128
        )

        split_documents = []
        for document in documents:
            split_documents.extend(text_splitter.split_documents([document]))

        # Create embeddings and save them in Chroma vector database
        Chroma.from_documents(
            split_documents,
            persist_directory=VECTOR_DB_DIR,
            embedding=MistralAIEmbeddings(
                model=MISTRAL_EMBED_MODEL, api_key=MISTRAL_API_KEY
            ),
        )

    @staticmethod
    def retriever(character_id: int) -> VectorStoreRetriever:
        # TODO: pydantic model for search_kwargs
        vectordb = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=MistralAIEmbeddings(model=MISTRAL_EMBED_MODEL),
        )
        return vectordb.as_retriever(
            search_kwargs={"k": 3, "filter": {"character_id": character_id}}
        )
