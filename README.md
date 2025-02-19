# Streamlit UI

![ui](assets/ui.png)

This is MiADE project's prototype user interface for our automatic point-of-care clinical coding work. We are working to evaluate how a user interface should be designed to enable users to take advantage of language processing tools adding structure to data as they write unstructured notes.

> [!IMPORTANT]
> This interface is by default deployed with `miade-llm`, which requires setting API key environment varibles for the LLM providers. Docker Compose will load them from `lib/miade-llm/src/.env`. Remeber to put your API keys in that file.

## Downloading
After cloning this repository, install the submodules with:

```bash
git submodule init && git submodule update
```

## Building

> [!TIP]
> These instructions use the uv package manager, install uv: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv).

Build the custom component with npm:
```bash
npm install --prefix src/frontend
npm run --prefix src/frontend build
```

## Running

Run `miade-llm`:
```bash
cd lib/miade-llm/src
source .env && uv run langchain serve
```

Run the UI:
```bash
uv run streamlit run src/main.py -- -b http://localhost:8000
```
The data directory, where it saves documents, defaults to `data` in your working directory. `-b` is the `--backend` option; langserve defaults to running on port 8000.

To run with a custom data directory:
```bash
uv run streamlit run src/main.py -- -d <PATH/TO/CUSTOM/DIRECTORY> -b http://localhost:8000
```

This will serve the UI on port 8501.


## Docker
To deploy with docker compose:
```bash
docker-compose up
```
This will serve the UI on port 5000.
