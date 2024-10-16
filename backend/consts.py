import os

import dotenv

dotenv.load_dotenv()
MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
MISTRAL_EMBED_MODEL = os.environ["MISTRAL_EMBED_MODEL"]
MISTRAL_LANGUAGE_MODEL = os.environ["MISTRAL_LANGUAGE_MODEL"]
VECTOR_DB_DIR = os.path.join("database", "vectordb")
