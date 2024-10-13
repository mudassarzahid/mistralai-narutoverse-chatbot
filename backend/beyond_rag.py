import os

import dotenv

# Load environment variables
dotenv.load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]

from typing import List
from langchain_mistralai import MistralAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter

from database.database import get_characters
from datamodels.models import Character


class CharacterDataLoader:
    def __init__(self, filters: dict[str, str], limit: int = None):
        self.filters = filters
        self.limit = limit

    def load_characters(self) -> List[Document]:
        # Fetch characters from the database
        characters = get_characters(self.filters, Character, self.limit)

        # Convert characters to Langchain Document format
        documents = []
        for character in characters:
            data = character.model_dump(
                exclude_none=True, exclude={"id", "image_url", "href"}
            )
            string = ""
            for key, value in data.items():
                string += (
                    f"{key.replace('_', ' ').replace(' Ii', 'II').title()}: {value}\n"
                )
            metadata = {"source": "sqlite_database", "character_id": character.id}
            documents.append(Document(page_content=string[:-1], metadata=metadata))

        return documents


def build():
    # Define filters for the database query
    filters = {"name": "Sasuke Uchiha"}  # Example filter to get Sasuke
    limit = 10  # Set a limit if needed

    # Initialize the character data loader
    character_loader = CharacterDataLoader(filters=filters, limit=limit)

    # Load character documents from the database
    documents = character_loader.load_characters()

    # Split the text into chunks for embedding
    text_splitter = CharacterTextSplitter(
        separator=".", chunk_size=1024, chunk_overlap=128
    )

    split_documents = []
    for document in documents:
        split_documents.extend(text_splitter.split_documents([document]))

    # Create embeddings using OpenAI and store them in Chroma vector database
    Chroma.from_documents(
        [split_documents[0]],
        persist_directory="data/vectordb",
        embedding=MistralAIEmbeddings(model="mistral-embed"),  # api_key=api_key),
    )


def retrieve():
    vectordb = Chroma(
        persist_directory="data/vectordb",
        embedding_function=MistralAIEmbeddings(model="mistral-embed")
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 10})

    # Define the query
    query = "Sasuke"

    # Use the retriever to find the most relevant documents
    relevant_docs = retriever.invoke(query)
    # Print out the relevant documents
    print(relevant_docs)
    for doc in relevant_docs:
        print(doc.page_content)


retrieve()
