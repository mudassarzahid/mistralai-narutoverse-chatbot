import os

import dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pydantic import TypeAdapter

from database.database import Database
from datamodels.models import Character, CharacterData

# Load environment variables
dotenv.load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]

db = Database()


class CharacterDataLoader:
    @staticmethod
    def load_character(character_id: int) -> list[Document]:
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
                })
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


def build(character_id: int):
    character_loader = CharacterDataLoader()
    documents = character_loader.load_character(character_id)

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
        persist_directory="database/vectordb",
        embedding=MistralAIEmbeddings(model="mistral-embed", api_key=api_key),
    )


def retrieve(character_id: int):
    vectordb = Chroma(
        persist_directory="database/vectordb",
        embedding_function=MistralAIEmbeddings(model="mistral-embed"),
    )
    retriever = vectordb.as_retriever(
        search_kwargs={'k': 3, 'filter': {'character_id': character_id}}
    )

    # Define the query
    query = "Where does Sasuke live?"

    # Use the retriever to find the most relevant documents
    relevant_docs = retriever.invoke(query)

    # Print out the relevant documents
    print(relevant_docs)
    for doc in relevant_docs:
        print(doc.metadata, doc.page_content)
        print("----")


# build(907)
retrieve(1055)
