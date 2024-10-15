import os

import dotenv

# Load environment variables
dotenv.load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]

from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings
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
            documents.append(
                Document(
                    page_content=character["character"].summary,
                    metadata={
                        "name": character["character"].name,
                        "source": "sqlite_database",
                        "character_id": character["character"].id,
                        "tag_1": "Summary",
                        "tag_2": "None",
                        "tag_3": "None",
                    },
                )
            )

            for section in character["details"]:
                documents.append(
                    Document(
                        page_content=section.text,
                        metadata={
                            "name": character["character"].name,
                            "source": "sqlite_database",
                            "character_id": character["character"].id,
                            "tag_1": section.tag_1,
                            "tag_2": section.tag_2 or "None",
                            "tag_3": section.tag_2 or "None",
                        },
                    )
                )

        return documents


def build():
    # Define filters for the database query
    filters = {
        "name": "Sasuke Uchiha",
        "get_details": "True",
    }  # Example filter to get Sasuke
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
        split_documents,
        persist_directory="data/vectordb",
        embedding=MistralAIEmbeddings(model="mistral-embed", api_key=api_key),
    )


def retrieve():
    vectordb = Chroma(
        persist_directory="data/vectordb",
        embedding_function=MistralAIEmbeddings(model="mistral-embed"),
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    # Define the query
    query = "What man does Sasuke love?"

    # Use the retriever to find the most relevant documents
    relevant_docs = retriever.invoke(query)
    # Print out the relevant documents
    print(relevant_docs)
    for doc in relevant_docs:
        print(doc.page_content)
        print("----")


# build()
retrieve()
