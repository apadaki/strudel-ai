# Strudel AI Music Generator

Generate [Strudel](https://strudel.cc/) live coding patterns using RAG (Retrieval Augmented Generation).

## How it Works

1. **Pattern Database**: 30 curated Strudel patterns with rich descriptions (mood, tempo, tags)
2. **Semantic Search**: Uses local sentence-transformers for embeddings (no API key needed!)
3. **Code Generation**: Uses Claude to generate new Strudel code based on retrieved patterns

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your-key-here

# Run the web app
python app.py
```

Then open http://localhost:8000

## Project Structure

```
strudel-ai/
├── patterns.json      # Curated pattern database (30 patterns)
├── embeddings.py      # Local embedding + semantic search
├── generator.py       # RAG code generation with Claude
├── app.py             # FastAPI web interface
└── requirements.txt
```

## API Endpoints

- `GET /` - Web interface
- `POST /api/generate` - Generate new code from prompt
- `POST /api/search` - Search similar patterns
- `POST /api/variation` - Generate variation of existing pattern
- `GET /api/patterns` - List all patterns

## Example Usage

```python
from embeddings import PatternSearcher
from generator import generate_strudel_code

searcher = PatternSearcher()
searcher.build_index()

result = generate_strudel_code(
    "something groovy and hypnotic",
    searcher
)
print(result["code"])
```

## Adding Patterns

Edit `patterns.json` to add more patterns. Each pattern needs:
- `id`: Unique identifier
- `name`: Human-readable name
- `description`: Rich description of the sound/mood
- `tags`: Array of relevant tags
- `tempo`: slow/medium/fast/none
- `mood`: Description of the mood/feeling
- `code`: Valid Strudel code

After adding patterns, delete `embeddings_cache.pkl` to rebuild the index.

## Tech Stack

- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2) - runs locally, no API needed
- **Generation**: Claude (Anthropic API)
- **Web**: FastAPI + vanilla JS
