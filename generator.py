"""
RAG-based Strudel code generator.
Uses semantic search to find relevant patterns, then generates new code with Claude.
"""

import anthropic
from embeddings import PatternSearcher
from strudel_context import FULL_CONTEXT


SYSTEM_PROMPT = f"""You are an expert Strudel (https://strudel.cc/) live coding musician, composer, and creative coder.

{FULL_CONTEXT}

---

## YOUR TASK

Generate COMPLETE, MUSICAL Strudel code that sounds good and runs directly in strudel.cc.

### CRITICAL REQUIREMENTS

1. **CREATE LONGER PATTERNS** - Use .slow(4), .slow(8), or /4, /8 notation for longer phrases
2. **LAYER MULTIPLE ELEMENTS** - Use stack() with drums + bass + chords + melody
3. **ADD MOVEMENT** - Use sine/perlin modulation on filters: .lpf(sine.range(400,2000).slow(8))
4. **VARY OVER TIME** - Use .every(), .sometimes() for evolution
5. **USE MUSICAL PROGRESSIONS** - Not just single chords, but progressions over multiple cycles
6. **CREATE PROPER MELODIES** - Stepwise motion, rhythmic variety, not just random notes

### OUTPUT FORMAT

Output ONLY valid Strudel code. No explanations, no markdown code blocks."""


def format_examples(patterns: list[tuple[dict, float]]) -> str:
    """Format retrieved patterns as examples for the prompt."""
    examples = []
    for pattern, score in patterns:
        example = f"""
---
Name: {pattern['name']}
Description: {pattern['description']}
Mood: {pattern['mood']}
Tags: {', '.join(pattern['tags'])}
Code:
```
{pattern['code']}
```
---"""
        examples.append(example)
    return "\n".join(examples)


def generate_strudel_code(
    prompt: str,
    searcher: PatternSearcher,
    num_examples: int = 6,
    model: str = "claude-sonnet-4-20250514",
    temperature: float = 0.8,
) -> dict:
    """
    Generate Strudel code based on a natural language prompt.

    Args:
        prompt: User's natural language description of desired music
        searcher: PatternSearcher instance for retrieving examples
        num_examples: Number of similar patterns to retrieve
        model: Claude model to use for generation
        temperature: Creativity parameter (higher = more creative)

    Returns:
        Dictionary with 'code', 'examples_used', and 'prompt'
    """
    # Retrieve similar patterns
    similar_patterns = searcher.search(prompt, top_k=num_examples)

    # Log what we're retrieving
    print(f"\n📝 User prompt: '{prompt}'")
    print(f"🔍 Retrieved patterns:")
    for p, score in similar_patterns:
        print(f"   [{score:.3f}] {p['name']} - {p['mood']}")

    # Format examples for context
    examples_text = format_examples(similar_patterns)

    # Build the generation prompt
    user_prompt = f"""Here are some example Strudel patterns for reference and syntax guidance:

{examples_text}

---

## YOUR REQUEST: "{prompt}"

---

## REQUIREMENTS FOR THIS GENERATION:

1. **MUST BE A COMPLETE TRACK** with multiple layers using stack():
   - Drums (kick, snare, hats)
   - Bass line (with filter movement)
   - Chords or pads (with effects)
   - Optional: melody or arpeggios

2. **MUST BE LONGER** - create phrases that span multiple cycles:
   - Use .slow(4) or .slow(8) on melodic elements
   - Use "/2" or "/4" in mini-notation for longer progressions
   - Example: `note("<c2 f2 g2 ab2>/2")` = 2-cycle bass line

3. **MUST HAVE MOVEMENT** - nothing should be static:
   - Filter sweeps: `.lpf(sine.range(400, 2000).slow(8))`
   - Gain modulation: `.gain(perlin.range(.4, .8).slow(4))`
   - Use .every() for periodic variations

4. **MUST BE MUSICAL**:
   - Use proper scales: `.scale("C:minor")` or `.scale("D:dorian")`
   - Create real melodies with stepwise motion and occasional leaps
   - Include harmonic progressions, not just single chords

5. **MUST INCLUDE EFFECTS**:
   - .room() for space
   - .delay() for echoes
   - .lpf() for warmth
   - .lpenv() for punch on basses

## EXAMPLE OF WHAT A GOOD OUTPUT LOOKS LIKE:

```
stack(
  s("bd*4, ~ cp, [~ hh]*4, ~ ~ ~ oh").bank("RolandTR909").gain(.8),

  note("<c2 c2 f2 g2>/2")
    .sound("sawtooth")
    .lpf(sine.range(200, 800).slow(8))
    .lpenv(3)
    .gain(.6),

  chord("<Cm7 Cm7 Fm9 Gsus4>/2")
    .voicing()
    .s("gm_epiano1")
    .room(.5)
    .gain(.35),

  n("<0 2 4 7 9 7 4 2>/4")
    .scale("C4:minor")
    .sound("triangle")
    .lpf(2000)
    .room(.4)
    .delay(.2)
    .every(4, fast(2))
    .gain(.3)
)
```

Now generate ORIGINAL code for: "{prompt}"

Output ONLY the Strudel code, no explanations."""

    # Call Claude
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=2048,  # Increased for longer, more complete tracks
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
    )

    generated_code = response.content[0].text

    # Clean up code (remove markdown code blocks if present)
    if generated_code.startswith("```"):
        lines = generated_code.split("\n")
        # Remove first and last lines (code block markers)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        generated_code = "\n".join(lines)

    return {
        "code": generated_code.strip(),
        "examples_used": [
            {"name": p["name"], "id": p["id"], "score": score}
            for p, score in similar_patterns
        ],
        "prompt": prompt,
    }


def generate_variation(
    pattern_id: str,
    searcher: PatternSearcher,
    variation_prompt: str = "Create a variation",
    model: str = "claude-sonnet-4-20250514",
) -> dict:
    """
    Generate a variation of an existing pattern.

    Args:
        pattern_id: ID of the pattern to create a variation of
        searcher: PatternSearcher instance
        variation_prompt: How to vary the pattern
        model: Claude model to use

    Returns:
        Dictionary with generated code and metadata
    """
    # Find the original pattern
    original = None
    for p in searcher.patterns:
        if p["id"] == pattern_id:
            original = p
            break

    if original is None:
        raise ValueError(f"Pattern '{pattern_id}' not found")

    # Get similar patterns for additional context
    similar = searcher.get_similar_patterns(pattern_id, top_k=3)

    user_prompt = f"""Here is an original Strudel pattern:

Name: {original['name']}
Description: {original['description']}
Code:
```
{original['code']}
```

And some related patterns for inspiration:
{format_examples(similar)}

---

## CREATE A VARIATION

Your task: {variation_prompt}

Requirements:
1. Keep the core vibe/mood but make it distinctly different
2. Make it LONGER - use .slow() to extend phrases
3. Add LAYERS - if original is simple, add bass/chords/melody
4. Add MOVEMENT - filter sweeps, modulation, .every() variations
5. Include proper effects - room, delay, lpf

Output ONLY the Strudel code, no explanations."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.9,
    )

    generated_code = response.content[0].text

    # Clean up code
    if generated_code.startswith("```"):
        lines = generated_code.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        generated_code = "\n".join(lines)

    return {
        "code": generated_code.strip(),
        "original_pattern": original["name"],
        "variation_prompt": variation_prompt,
    }


def demo():
    """Demo the code generation."""
    print("Initializing pattern searcher...")
    searcher = PatternSearcher()
    searcher.build_index()

    prompts = [
        "something groovy and hypnotic for a late night coding session",
        "dark atmospheric ambient for a horror game",
        "upbeat happy chiptune melody",
    ]

    print("\n" + "="*60)
    print("CODE GENERATION DEMO")
    print("="*60)

    for prompt in prompts:
        print(f"\n🎵 Prompt: '{prompt}'")
        print("-" * 50)

        result = generate_strudel_code(prompt, searcher)

        print("Examples used:")
        for ex in result["examples_used"]:
            print(f"  - {ex['name']} (score: {ex['score']:.3f})")

        print("\nGenerated code:")
        print("-" * 30)
        print(result["code"])
        print("-" * 30)


if __name__ == "__main__":
    demo()
