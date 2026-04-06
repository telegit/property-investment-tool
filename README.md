# property-investment-tool

Real estate investment analyzer — market valuations, cap rates, cash flow estimates, and multi-zip comparisons powered by RapidAPI.

## Setup

1. Activate virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Copy environment file and add your RapidAPI key:
   ```bash
   cp .env.example .env
   # Edit .env and set RAPIDAPI_KEY=your_key
   ```

4. Run the app:
   ```bash
   uv run streamlit run main.py
   ```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black .
ruff check .
```

## Project Structure

```
property-investment-tool/
├── main.py           # Streamlit dashboard
├── market_client.py  # RapidAPI client
├── requirements.txt  # Dependencies
├── .env.example      # Environment template
├── README.md
└── tests/
```
