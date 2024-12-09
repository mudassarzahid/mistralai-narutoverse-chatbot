## NarutoVerse Chatbot

![Example Chat](./public/example.gif)
<p align="center">Example chat showcasing the Chatbot's ability to impersonate the character's personality, reference specific plot points
thanks to querying the RAG database, and overall engage in a coherent conversation.</p>


### Built With

The backend is written in Python 3.10.8, and uses the `FastAPI` framework for creating APIs, along
with `Uvicorn` as the ASGI server. The frontend is developed in `TypeScript` using the `React`-based
framework `Next.js`, along with `NextUI` as a modern component library.

### How does it work?

1. **Initialize database**:
   On backend startup, a local `SQLite` db is created and all characters from NarutoWiki are scraped and saved. If the
   database already exists, this step is skipped.
   **Important note**: I got explicit permission from Fandom.com to scrape these sites. To avoid overloading NarutoWiki
   with too many requests and for convenience, I have pushed a pre-built SQLite database with 100 NarutoVerse characters
   to this repository.
2. **Embeddings**:
   When the client selects the character they want to chat with on the frontend, their wiki data is split into segments,
   embeddings are created, and stored in the `Chroma` vectorDB for RAG. If embeddings for that character already exist,
   this step is skipped. A dictionary stores the chat history for each client and each character belonging to the
   client. This makes it possible for multiple clients to chat with the same character simultaneously.
3. **Conversational AI**:
   Using a `LangChain` graph, the client can then chat with the character. The graph workflow consists of the following
   steps:
    - Summarize the chat history
    - Characterize the client based on chat history, allowing the character to develop an understanding of the client
      and make the conversation feel more personalized
    - Run the RAG-LLM pipeline
        - Prompt LLM to generate a query optimized for RAG based on client input & chat history
        - Query the vectorDB which returns at most the 2 most relevant documents
        - Generate a response to the client by combining the retrieved documents, a (summarized) chat history, and an
          instruction prompt including the client's (human) and character's (AI) personalities.

The character (AI) responds and the LLM-generated tokens are streamed chunk by chunk to the frontend for a smooth
ChatGPT-like experience.

### Run locally

To get a local copy up and running follow these simple steps.

### Backend

#### 1. Create `.env` file

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

#### 2. Create a virtual environment and activate it

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

#### 4. Run the backend

```shell
uvicorn app.app:app --port 8080
```

### Frontend

#### 1. Create .env.local file

Create an `.env.local` file and add the backend URL.

```shell
touch .env.local
nano .env.local
# add the following line
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

#### 2. Install dependencies

```shell
cd frontend
yarn install
```

#### 3. Run the frontend

```shell
yarn dev
```

#### 4. Open `http://localhost:3000/` in your browser and start chatting!
