## MistralAI-based NarutoVerse Chatbot

![Example Chat](./public/example.gif)

### Built With

The backend is written in Python 3.10.8 and uses `FastAPI` along with `Uvicorn`.
The frontend is written in TypeScript using `Next.js` (`React`).

### How does it work?

1. **Initialize database**
   On backend startup, a local SQLite db is created and all characters from NarutoWiki are scraped
   and saved. If the database already exists, this step is skipped.
   **Important note**: I got explicit permission from Fandom.com to scrape these sites. To avoid
   overloading NarutoWiki with too many requests and for convenience, I have pushed a pre-built
   SQLite database with 50 characters to this repository.
2. **Embeddings**
   When a character is selected, their wiki data is split into segments, embeddings are created,
   and stored in the Chroma vectorDB for RAG. If embeddings for that character already exist,
   this step is skipped.
3. **Conversational AI**
   Using a LangChain graph, the user can then chat with the character. The graph workflow
   consists of the following steps:
    - Taking user input
    - Rephrasing the input by prompting LLM to generate a query optimized for RAG
    - Querying the vectorDB which returns the 2 most relevant documents
    - Generating a response to the user by combining:
        - The retrieved documents
        - An instruction prompt including the character's personality
        - A summary of the overall chat history

The character (bot) responds and the LLM-generated tokens are streamed chunk
by chunk to the frontend for a smooth ChatGPT-like experience.

### Run locally

To get a local copy up and running follow these simple steps.

### Backend

#### 1. Setup .env

Create an `.env` file by copying `.env-example` and entering the missing values.

#### 2. Create a virtual environment

```shell
cd backend
python3 -m venv .venv 
source .venv/bin/activate
```

#### 3. Install dependencies

```shell
# For recommended poetry installation instructions, see https://python-poetry.org/docs/
# For running the demo locally, the following commands should suffice
# alternative: pip install -r requirements.txt 
# (for convenience, requirements.txt is auto-generated from pyproject.toml 
# and used by Railway, the backend deployment tool)
pip install poetry
poetry install --no-root
```

#### 4. Run the app

```shell
uvicorn app.app:app --port 8080
```

### Frontend

#### 1. Install dependencies

```shell
cd frontend
yarn install
```

#### 2. Run the webapp

```shell
yarn dev
```

### Known problems and TODOs

1. **Injection of irrelevant context**
   The retrieved documents can sometimes introduce irrelevant context which
   the LLM includes into its response.
    - Possible solution: Add a classifier to decide if the retrieved documents are relevant
      (step between retrieving documents and generating LLM response). If not, don't use them.
2. **Confused dialogue**
   LLM sometimes misattributes statements, especially with long (summarized) chat histories and
   when pronouns like "I" and "You" are used, causing the character to confuse what the user
   said, what the system prompt said, and what the character said.
    - Possible solutions: Better prompting; substitute pronouns with explicit names to avoid
      confusion.