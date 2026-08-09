# Start here

## Local run
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
Open `http://127.0.0.1:8000`.

## Tests
```bash
pip install -e ".[dev]"
pytest -q
```

## Vercel
The project is Vercel-ready. Import the GitHub repository as a new Vercel project and keep framework/build/output settings on automatic/default.

## Research limitation
The MVP applies publication lags to revised FRED macro series, but it does not yet reconstruct ALFRED vintages. Treat historical performance as research evidence, not an investable track record.
