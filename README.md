## MistralAI-based NarutoVerse Chatbot

![Example Chat](./public/example.gif)

### Built With

The backend is written in Python **3.10.8** and uses `FastAPI` along with `Uvicorn`.
The frontend is written in TypeScript using `Next.js` (`React`).

### Run locally

To get a local copy up and running follow these simple steps.

#### Backend

##### 1. Setup .env

Create an `.env` file by copying `.env-example` and entering the missing values.

##### 2. Create a virtual environment

```shell
cd backend
python3 -m venv .venv 
source .venv/bin/activate
```

##### 3. Install dependencies

```shell
# For recommended poetry installation instructions, see https://python-poetry.org/docs/
# For running the demo locally, the following commands should suffice
pip install poetry
poetry install --no-root
```

##### 4. Run the app

```shell
uvicorn app.app:app --reload --port 8080
```

#### Frontend

##### 1. Install dependencies

```shell
cd frontend
yarn install
```

##### 3. Run the webapp

```shell
yarn dev
```
