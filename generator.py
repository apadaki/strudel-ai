"""
RAG-based Strudel code generator.
Uses semantic search to find relevant patterns, then generates new code with Claude.
"""

import anthropic
from embeddings import PatternSearcher


SYSTEM_PROMPT = """You are an expert Strudel (https://strudel.cc/) live coding musician and creative coder.

Strudel is a JavaScript-based live coding environment for music, based on TidalCycles patterns.

## SAMPLE BANKS (use with .bank())
- RolandTR909, RolandTR808, RolandTR707, RolandTR505, RolandCompurhythm1000

## DRUM SAMPLES (use with s() or sound())
- bd (bass drum), sd (snare), hh (hi-hat), oh (open hi-hat)
- cp (clap), rim (rimshot), cr (crash), rd (ride)
- ht, mt, lt (high/mid/low tom), perc (percussion)

## GM SOUNDS (General MIDI - use with .sound())
- gm_acoustic_bass, gm_synth_bass_1, gm_synth_bass_2
- gm_epiano1, gm_epiano2 (electric piano)
- gm_acoustic_guitar_nylon, gm_electric_guitar_muted
- gm_xylophone, gm_marimba, gm_vibraphone
- gm_string_ensemble_1, gm_synth_strings_1
- gm_accordion, gm_rock_organ, gm_church_organ
- gm_violin, gm_cello, gm_flute, gm_trumpet

## SYNTH SOUNDS (use with .sound())
- sawtooth, square, triangle, sine (basic waveforms)
- piano (built-in piano sample)

## MINI-NOTATION
- `*N` - repeat N times: "bd*4" = four bass drums
- `[a b]` - subdivide: "[bd sd]" = both fit in one beat
- `<a b c>` - alternate each cycle: "<bd sd hh>" plays one per cycle
- `~` - rest/silence
- `@N` - elongate: "c@3 e" = c takes 3 beats, e takes 1
- `!N` - replicate: "bd!3" = "bd bd bd" (without speeding up)
- `,` - play simultaneously: "bd, hh" = layered
- `(n,k)` - Euclidean rhythm: "bd(3,8)" = 3 hits spread over 8 steps
- `?` - random remove (50%): "hh*8?"
- `|` - random choice: "bd | sd | hh"

## SCALES (use with .scale())
- n("0 2 4 6").scale("C:minor") - scale degrees to notes
- Common scales: major, minor, dorian, mixolydian, pentatonic, blues, ritusen

## CHORDS (use with chord() and .voicing())
- chord("<Dm7 G7 C^7>").voicing() - jazz chord voicings
- .dict('ireal') - use iReal chord dictionary

## EFFECTS
- .lpf(freq), .hpf(freq) - filters (freq in Hz)
- .lpq(amount), .hpq(amount) - filter resonance
- .room(0-1) - reverb amount
- .delay(0-1) - delay amount
- .gain(0-1) - volume
- .attack(sec), .decay(sec), .sustain(0-1), .release(sec) - ADSR envelope
- .crush(1-16) - bitcrusher
- .speed(amount) - playback speed (negative = reverse)
- .vowel("<a e i o u>") - formant filter

## MODULATION
- sine.range(min, max).slow(cycles) - sine LFO
- perlin.range(min, max).slow(cycles) - noise modulation
- rand - random value per event

## TEMPO
- setcps(0.5) - cycles per second (default)
- setcpm(120/4) - cycles per minute / 4

## STRUCTURE
- stack(...) - layer multiple patterns
- s("pattern").bank("BankName") - short form for sound()
- note("c3 e3 g3").sound("piano") - note with sound

When generating code:
1. Study the example patterns provided - they show correct syntax
2. Use ONLY valid sample names from the lists above
3. Layer sounds with stack() for fuller arrangements
4. Use effects tastefully to enhance the mood
5. Match the tempo and energy to the requested vibe
6. Keep code clean and runnable - no syntax errors

Output ONLY valid Strudel code that runs directly in strudel.cc. No explanations."""


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
    num_examples: int = 4,
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
    user_prompt = f"""Here are some example Strudel patterns for reference:

{examples_text}

Now compose ORIGINAL Strudel code for this request:
"{prompt}"

IMPORTANT - Be creative! You should:
- Invent NEW note sequences, melodies, and chord progressions
- Create DIFFERENT rhythmic patterns (don't copy the exact rhythms above)
- Choose your own tempo, key, and feel
- Mix and match techniques from different examples
- Adjust filter frequencies, envelope times, effect amounts creatively
- Add your own musical ideas - surprising variations, interesting textures

The examples show valid SYNTAX and available sounds - use them as a reference for what's possible, not as templates to copy. Generate something fresh that matches the vibe requested.

Output only the Strudel code, ready to paste into strudel.cc."""

    # Call Claude
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
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

Create a variation of the original pattern that: {variation_prompt}

Keep the core vibe but make it distinctly different. Output only the new Strudel code."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
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
