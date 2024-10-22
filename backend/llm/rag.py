from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pydantic import TypeAdapter

from database.database import Database
from datamodels.models import Character, CharacterData, DocumentMetadata, EmbeddingLog
from utils.consts import MISTRAL_EMBED_MODEL, VECTOR_DB_DIR
from utils.exceptions import EmbeddingsNotCreatedError, NotFoundError
from utils.logger import get_logger

logger = get_logger()


class RAG:
    """RAG class for managing character embeddings and retrieval.

    This class handles loading character data, generating embeddings, and
    storing them in a Chroma vectorDB for later retrieval. It also manages
    the retriever for finding relevant documents during conversation.

    Attributes:
        db (Database): An instance of the NarutoWiki database.
    """

    def __init__(self):
        """Initialize the RAG class with the NarutoWiki database."""
        self.db = Database()

    def load_character_data(self, character_id: int) -> list[Document]:
        """Load character data and convert it into Langchain Document format.

        This function fetches character information from the database
        and converts them into `Document` format used by Langchain.
        The metadata is later used for filtering when retrieving
        relevant documents for the conversation.

        Args:
            character_id (int): The ID of the character.

        Returns:
            list[Document]: A list of Langchain `Document` objects
                representing the character's data.
        """
        character: Character = self.db.get_by_id(character_id, Character)
        documents = [
            Document(
                page_content=character.summary,
                metadata=DocumentMetadata(
                    character_id=character.id,
                    name=character.name,
                    tag_1="Summary",
                ).model_dump(),
            )
        ]

        character_data_list = TypeAdapter(list[CharacterData])
        for section in character_data_list.validate_python(character.data):
            documents.append(
                Document(
                    page_content=section.text,
                    metadata=DocumentMetadata(
                        character_id=character.id,
                        name=character.name,
                        tag_1=section.tag_1,
                        tag_2=section.tag_2 or "null",
                        tag_3=section.tag_2 or "null",
                    ).model_dump(),
                )
            )

        return documents

    def store_embeddings(self, character_id: int):
        """Create and store embeddings for a character in the vectorDB.

        This function fetches the character's data, splits it into smaller
        chunks, and generates embeddings for these chunks. The embeddings
        are then stored in a Chroma vectorDB.

        Args:
            character_id (int): The ID of the character for whom
                embeddings will be created.

        Raises:
            EmbeddingsNotCreatedError: If the MistralAI embedding
                backend is unreachable.
        """
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
        except KeyError:
            raise EmbeddingsNotCreatedError(
                f"Could not create embeddings for {split_documents=}, "
                f"likely because MistralAI backend is unreachable. "
                f"Try again in a few seconds!"
            )

    def retriever(self, character_id: int, k: int = 2) -> VectorStoreRetriever:
        """Return a retriever for a character based on stored embeddings.

        This function checks if embeddings exist for the character in the
        database. If embeddings already exist in the vectorDB they are not
        created again, unless the corresponding row in the log table is
        deleted. This is to improve performance when selecting a
        new character to chat. It then creates and returns a retriever
        for the character's data.

        Args:
            character_id (int): The ID of the character.
            k (int): Number of relevant documents to return.
                Defaults to 2.

        Returns:
            VectorStoreRetriever: A retriever that can search through
                the character's data using embeddings.
        """
        try:
            self.db.get_by_id(character_id, EmbeddingLog, id_key="character_id")
        except NotFoundError:
            logger.debug(f"Create vectorDB embeddings for {character_id=}.")
            self.store_embeddings(character_id)
            self.db.create(EmbeddingLog(character_id=character_id))

        vectordb = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=MistralAIEmbeddings(model=MISTRAL_EMBED_MODEL),
        )
        return vectordb.as_retriever(
            search_kwargs={"k": 2, "filter": {"character_id": character_id}}
        )
