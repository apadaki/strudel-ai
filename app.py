"""
Web interface for the Strudel AI Music Generator.
FastAPI backend with embedded HTML frontend.
"""

import os
import traceback

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from embeddings import PatternSearcher
from generator import generate_strudel_code, generate_variation


# Global searcher instance
searcher: PatternSearcher = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the pattern searcher on startup."""
    global searcher
    print("Initializing pattern searcher...")
    searcher = PatternSearcher()
    searcher.build_index()
    print("Ready!")
    yield


app = FastAPI(
    title="Strudel AI Music Generator",
    description="Generate Strudel live coding patterns using AI",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str
    num_examples: int = 4
    temperature: float = 0.8


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class VariationRequest(BaseModel):
    pattern_id: str
    variation_prompt: str = "make it more intense"


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface."""
    return HTML_TEMPLATE


@app.post("/api/generate")
async def generate(request: GenerateRequest):
    """Generate new Strudel code from a natural language prompt."""
    try:
        result = generate_strudel_code(
            prompt=request.prompt,
            searcher=searcher,
            num_examples=request.num_examples,
            temperature=request.temperature,
        )
        return result
    except Exception as e:
        print(f"ERROR in /api/generate: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search(request: SearchRequest):
    """Search for similar patterns."""
    try:
        results = searcher.search(request.query, top_k=request.top_k)
        return {
            "query": request.query,
            "results": [
                {
                    "pattern": pattern,
                    "score": score
                }
                for pattern, score in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/variation")
async def variation(request: VariationRequest):
    """Generate a variation of an existing pattern."""
    try:
        result = generate_variation(
            pattern_id=request.pattern_id,
            searcher=searcher,
            variation_prompt=request.variation_prompt,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patterns")
async def list_patterns():
    """List all available patterns."""
    return {
        "patterns": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "mood": p["mood"],
                "tags": p["tags"],
            }
            for p in searcher.patterns
        ]
    }


@app.get("/api/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get a specific pattern by ID."""
    for p in searcher.patterns:
        if p["id"] == pattern_id:
            return p
    raise HTTPException(status_code=404, detail="Pattern not found")


# Embedded HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strudel AI - Music Code Generator</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }

        header {
            text-align: center;
            margin-bottom: 2rem;
        }

        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d9ff, #ff00d9, #00ff9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            color: #888;
            font-size: 1rem;
        }

        .input-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .input-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #00d9ff;
            font-size: 0.9rem;
        }

        textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid rgba(0, 217, 255, 0.3);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            font-family: inherit;
            font-size: 1rem;
            resize: vertical;
            transition: border-color 0.3s;
        }

        textarea:focus {
            outline: none;
            border-color: #00d9ff;
        }

        .controls {
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .slider-group {
            flex: 1;
            min-width: 150px;
        }

        .slider-group input[type="range"] {
            width: 100%;
            accent-color: #00d9ff;
        }

        .slider-value {
            color: #888;
            font-size: 0.8rem;
        }

        button {
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-family: inherit;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }

        .btn-primary {
            background: linear-gradient(90deg, #00d9ff, #00ff9d);
            color: #1a1a2e;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 217, 255, 0.3);
        }

        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .output-section {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .output-title {
            color: #00ff9d;
            font-size: 0.9rem;
        }

        .output-actions {
            display: flex;
            gap: 0.5rem;
        }

        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
        }

        .code-output {
            padding: 1.5rem;
            font-size: 0.95rem;
            line-height: 1.6;
            white-space: pre-wrap;
            min-height: 200px;
            color: #f8f8f2;
        }

        .examples-used {
            padding: 1rem 1.5rem;
            background: rgba(0, 0, 0, 0.2);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .examples-title {
            color: #888;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }

        .example-tag {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            margin: 0.25rem;
            background: rgba(0, 217, 255, 0.2);
            border-radius: 4px;
            font-size: 0.75rem;
            color: #00d9ff;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(0, 217, 255, 0.3);
            border-top-color: #00d9ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .quick-prompts {
            margin-top: 1rem;
        }

        .quick-prompts-title {
            color: #888;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }

        .quick-prompt {
            display: inline-block;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            font-size: 0.8rem;
            color: #aaa;
            cursor: pointer;
            transition: all 0.2s;
        }

        .quick-prompt:hover {
            background: rgba(0, 217, 255, 0.2);
            border-color: rgba(0, 217, 255, 0.5);
            color: #fff;
        }

        .strudel-link {
            text-align: center;
            margin-top: 1.5rem;
            padding: 1rem;
            background: rgba(255, 0, 217, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(255, 0, 217, 0.2);
        }

        .strudel-link a {
            color: #ff00d9;
            text-decoration: none;
        }

        .strudel-link a:hover {
            text-decoration: underline;
        }

        .hidden {
            display: none;
        }

        footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #666;
            font-size: 0.8rem;
        }

        footer a {
            color: #00d9ff;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Strudel AI</h1>
            <p class="subtitle">Generate live coding music patterns with AI</p>
        </header>

        <div class="input-section">
            <div class="input-group">
                <label for="prompt">Describe the music you want to create</label>
                <textarea
                    id="prompt"
                    rows="3"
                    placeholder="e.g., something groovy and hypnotic for a late night coding session..."
                ></textarea>
            </div>

            <div class="controls">
                <div class="slider-group">
                    <label>Creativity: <span class="slider-value" id="temp-value">0.8</span></label>
                    <input type="range" id="temperature" min="0.1" max="1.5" step="0.1" value="0.8">
                </div>
                <button class="btn-primary" id="generate-btn" onclick="generate()">
                    Generate Music
                </button>
            </div>

            <div class="quick-prompts">
                <div class="quick-prompts-title">Try these:</div>
                <span class="quick-prompt" onclick="setPrompt('groovy hypnotic bass for late night coding')">hypnotic bass</span>
                <span class="quick-prompt" onclick="setPrompt('dark ambient horror soundscape')">dark ambient</span>
                <span class="quick-prompt" onclick="setPrompt('upbeat happy chiptune melody')">happy chiptune</span>
                <span class="quick-prompt" onclick="setPrompt('minimal techno with driving beat')">minimal techno</span>
                <span class="quick-prompt" onclick="setPrompt('relaxing meditation bells and pads')">meditation</span>
                <span class="quick-prompt" onclick="setPrompt('funky disco rhythm')">funky disco</span>
                <span class="quick-prompt" onclick="setPrompt('aggressive industrial noise')">industrial</span>
                <span class="quick-prompt" onclick="setPrompt('dreamy synthwave retrowave 80s')">synthwave</span>
            </div>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating your music...</p>
        </div>

        <div class="output-section hidden" id="output-section">
            <div class="output-header">
                <span class="output-title">Generated Strudel Code</span>
                <div class="output-actions">
                    <button class="btn-secondary btn-small" onclick="copyCode()">Copy</button>
                    <button class="btn-secondary btn-small" onclick="openInStrudel()">Open in Strudel</button>
                </div>
            </div>
            <pre class="code-output" id="code-output"></pre>
            <div class="examples-used" id="examples-used"></div>
        </div>

        <div class="strudel-link hidden" id="strudel-link">
            <p>Paste your code at <a href="https://strudel.cc/" target="_blank">strudel.cc</a> to hear it!</p>
        </div>

        <footer>
            <p>Powered by RAG + Claude | Patterns from <a href="https://strudel.cc/" target="_blank">Strudel</a></p>
        </footer>
    </div>

    <script>
        let generatedCode = '';

        const tempSlider = document.getElementById('temperature');
        const tempValue = document.getElementById('temp-value');
        tempSlider.addEventListener('input', () => {
            tempValue.textContent = tempSlider.value;
        });

        function setPrompt(text) {
            document.getElementById('prompt').value = text;
        }

        async function generate() {
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) {
                alert('Please enter a description');
                return;
            }

            const temperature = parseFloat(document.getElementById('temperature').value);
            const btn = document.getElementById('generate-btn');
            const loading = document.getElementById('loading');
            const output = document.getElementById('output-section');
            const strudelLink = document.getElementById('strudel-link');

            btn.disabled = true;
            loading.classList.add('active');
            output.classList.add('hidden');
            strudelLink.classList.add('hidden');

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt, temperature })
                });

                if (!response.ok) {
                    throw new Error('Generation failed');
                }

                const data = await response.json();
                generatedCode = data.code;

                document.getElementById('code-output').textContent = data.code;

                // Show examples used
                const examplesDiv = document.getElementById('examples-used');
                examplesDiv.innerHTML = '<div class="examples-title">Inspired by:</div>' +
                    data.examples_used.map(ex =>
                        `<span class="example-tag">${ex.name} (${(ex.score * 100).toFixed(0)}%)</span>`
                    ).join('');

                output.classList.remove('hidden');
                strudelLink.classList.remove('hidden');

            } catch (error) {
                alert('Error generating code: ' + error.message);
            } finally {
                btn.disabled = false;
                loading.classList.remove('active');
            }
        }

        function copyCode() {
            navigator.clipboard.writeText(generatedCode).then(() => {
                alert('Code copied to clipboard!');
            });
        }

        function openInStrudel() {
            // Encode the code for URL
            const encoded = encodeURIComponent(generatedCode);
            window.open(`https://strudel.cc/?code=${encoded}`, '_blank');
        }

        // Enter key to generate
        document.getElementById('prompt').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                generate();
            }
        });
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
