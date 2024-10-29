## MistralAI-based NarutoVerse Chatbot

![Example Chat](./public/example.gif)

### Built With

The backend is written in Python 3.10.8, and uses the `FastAPI` framework for creating APIs, along
with `Uvicorn` as the ASGI server. On the frontend, the project is developed in `TypeScript` using
the `React`-based framework `Next.js`, along with `NextUI` as a modern component library.

### How does it work?

1. **Initialize database**:
   On backend startup, a local `SQLite` db is created and all characters from NarutoWiki are scraped
   and saved. If the database already exists, this step is skipped.
   **Important note**: I got explicit permission from Fandom.com to scrape these sites. To avoid
   overloading NarutoWiki with too many requests and for convenience, I have pushed a pre-built
   SQLite database with 100 characters to this repository.
2. **Embeddings**:
   When a character is selected, their wiki data is split into segments, embeddings are created,
   and stored in the `Chroma` vectorDB for RAG. If embeddings for that character already exist,
   this step is skipped. A dictionary stores the chat history for each client and each character
   belonging to the client.
3. **Conversational AI**:
   Using a LangChain graph, the user can then chat with the character. The graph workflow
   consists of the following steps:
    - Summarize the chat history
    - Characterize the user based on chat history
    - Run the RAG-LLM pipeline
        - Prompt LLM to generate a query optimized for RAG based on user input & chat history
        - Query the vectorDB which returns the 2 most relevant documents max
        - Generate a response to the user by combining the retrieved documents, a (summarized) chat history, and an
          instruction prompt including the user's (human) and character's (AI) personalities.

The character (AI) responds and the LLM-generated tokens are streamed chunk
by chunk to the frontend for a smooth ChatGPT-like experience.

### Run locally

To get a local copy up and running follow these simple steps.

### Backend

#### 1. Setup .env

Create an `.env` file, copy the contents of `.env-example` into the file, and add the missing values.

- Add `HF_TOKEN` from your [HuggingFace Account](https://huggingface.co/settings/tokens)
    - Accept [the terms](https://huggingface.co/mistralai/Mixtral-8x7B-v0.1) for using MistralAI
- Add `MISTRAL_API_KEY` from your [MistralAI Account](https://console.mistral.ai/api-keys/)

```shell
cd backend
touch .env
nano .env 
# ... add missing values
```

#### 2. Create a virtual environment

```shell
python3 -m venv .venv 
source .venv/bin/activate
```

#### 3. Install dependencies

Important: Your Python version needs to be `>=3.10.0` or else `Chroma` + `SQLite` may not work!

```shell
# For recommended poetry installation instructions, see https://python-poetry.org/docs/
# For running the demo locally, the following commands should suffice
# alternative: pip install -r requirements.txt (for convenience, requirements.txt is auto-generated from pyproject.toml and used by Railway, the backend deployment tool)
pip install poetry
poetry install --no-root
```

#### 4. Run the app

```shell
uvicorn app.app:app --port 8080
```

### Frontend

#### 1. Setup .env

Create an `.env.local` file and add the backend URL.

```shell
touch .env.local
nano .env.local
# add the following
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

#### 2. Install dependencies

```shell
cd frontend
yarn install
```

#### 3. Run the webapp

```shell
yarn dev
```
