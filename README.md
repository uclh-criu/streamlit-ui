# Streamlit UI

![ui](assets/ui.png)

Build and install with [uv](https://github.com/astral-sh/uv) and npm:
```bash
uv venv
uv install .
npm install --prefix src/frontend
npm run --prefix src/frontend build
```

Run with:
```bash
uv run streamlit run src/main.py
```
