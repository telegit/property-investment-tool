# zillow-scraper

Web Application project.

## Setup

1. Activate virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Copy environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   python main.py
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
zillow-scraper/
├── main.py           # Entry point
├── requirements.txt  # Dependencies
├── .env.example     # Environment template
├── .gitignore
├── README.md
└── tests/           # Test files
```
