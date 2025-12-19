"""
Comprehensive Strudel documentation context for LLM code generation.
This provides the full instruction set for generating high-quality Strudel patterns.
"""

STRUDEL_REFERENCE = """
# STRUDEL COMPLETE REFERENCE GUIDE

## OVERVIEW
Strudel is a JavaScript-based live coding environment for music, based on TidalCycles patterns.
Patterns loop continuously. One "cycle" = one loop iteration (default ~2 seconds at cps=0.5).

---

## MINI-NOTATION SYNTAX

### Basic Elements
- Space-separated = sequential events: `"c e g b"` (4 events per cycle)
- `[]` = subdivide time: `"c [e g]"` (c=half, e+g split other half)
- `<>` = alternate per cycle: `"<c e g>"` plays c, then e, then g over 3 cycles
- `~` = rest/silence
- `,` = play simultaneously: `"bd, hh"` = layered

### Modifiers
- `*N` = repeat N times: `"bd*4"` = 4 kicks per cycle
- `/N` = slow down: `"<c e g b>/2"` = plays over 2 cycles
- `@N` = elongate (weight): `"c@3 e"` = c takes 3 beats, e takes 1
- `!N` = replicate: `"bd!3"` = "bd bd bd" (same speed)
- `?` = 50% random drop: `"hh*8?"`
- `?0.2` = 20% drop chance
- `|` = random choice: `"bd | sd | hh"`

### Euclidean Rhythms
- `(hits, steps)` = distribute hits over steps: `"bd(3,8)"` = 3 kicks in 8 slots
- `(hits, steps, offset)` = with rotation: `"hh(5,8,2)"`

### Examples
- `"bd sd bd sd"` = basic 4/4 beat
- `"bd*4, hh*8, ~ sd"` = layered drums
- `"<[c e g] [d f a]>"` = alternating chords
- `"c@2 [e g]"` = c for 2 beats, e+g for 1

---

## SOUNDS & SAMPLES

### Drum Samples (use with s() or sound())
bd, sd, hh, oh, cp, rim, cr, rd, ht, mt, lt, perc, cb (cowbell)

### Sample Banks (use with .bank())
RolandTR909, RolandTR808, RolandTR707, RolandTR505, AkaiLinn, RhythmAce

### GM Sounds (General MIDI)
**Bass:** gm_acoustic_bass, gm_slap_bass_1, gm_synth_bass_1, gm_synth_bass_2
**Keys:** gm_epiano1, gm_epiano2, gm_clavinet, piano
**Guitar:** gm_acoustic_guitar_nylon, gm_electric_guitar_muted, gm_electric_guitar_clean
**Strings:** gm_string_ensemble_1, gm_synth_strings_1, gm_cello, gm_violin
**Brass:** gm_trumpet, gm_trombone, gm_french_horn
**Woodwind:** gm_flute, gm_clarinet, gm_oboe, gm_alto_sax
**Organ:** gm_rock_organ, gm_church_organ, gm_accordion
**Percussion:** gm_xylophone, gm_marimba, gm_vibraphone, gm_tubular_bells
**World:** gm_koto, gm_shamisen, gm_sitar

### Synth Waveforms
sawtooth, square, triangle, sine

### Noise
white, pink, brown, crackle

---

## NOTES & SCALES

### Note Syntax
- Letter names: `note("c3 e3 g3 b3")` - includes octave
- Sharps/flats: `note("c#4 bb3 f#3")`
- MIDI numbers: `note("60 64 67 71")` - middle C = 60

### Scale Degrees
Use n() with .scale() to map numbers to scale notes:
`n("0 2 4 6").scale("C:minor")` = C Eb G Bb

### Available Scales
major, minor, dorian, phrygian, lydian, mixolydian, locrian,
pentatonic, minor pentatonic, blues, chromatic, whole tone,
harmonic minor, melodic minor, bebop, bebop major, ritusen,
phrygian dominant (arabic/flamenco), pelog (gamelan)

### Chords
`chord("<Dm7 G7 C^7>").voicing().s("gm_epiano1")`
- Use .dict('ireal') for jazz voicings
- Chord symbols: m, M, 7, ^7 (maj7), m7, dim, aug, sus4, sus2

---

## TIME MANIPULATION - CRITICAL FOR LONGER MUSIC

### Making Patterns Longer
- `.slow(N)` = stretch over N cycles: `.slow(4)` = 4x longer
- `.slow(8)` = takes 8 cycles to complete (creates longer phrases)
- `/N` in mini-notation: `"<c e g b>/4"` = phrase over 4 cycles

### Speed Control
- `.fast(N)` = speed up N times
- `.hurry(N)` = speed up without pitch change

### Shifting
- `.early(N)` = shift earlier in time
- `.late(N)` = shift later (good for swing/humanize)

### Rhythm
- `.swing(N)` = add swing feel
- `.rev()` = reverse pattern
- `.palindrome()` = forward then backward

---

## LAYERING & ARRANGEMENT - KEY FOR FULL TRACKS

### stack() - Play Multiple Patterns Together
```javascript
stack(
  s("bd*4, ~ cp").bank("RolandTR909"),
  s("hh*8").gain(.4),
  note("<c2 f2 g2 c2>").sound("sawtooth").lpf(400),
  note("<[c4,e4,g4] [f4,a4,c5]>/2").sound("gm_epiano1").room(.4)
)
```

### arrange() - Sequence Sections Over Time
```javascript
arrange(
  [4, drums],      // 4 cycles of drums
  [8, fullTrack],  // 8 cycles of full track
  [4, breakdown]   // 4 cycles of breakdown
)
```

### layer() - Multiple Voices from Same Pattern
```javascript
note("<c3 e3 g3>").layer(
  x => x.sound("sawtooth").lpf(800),
  x => x.add(note(12)).sound("square").gain(.3)
)
```

---

## EFFECTS

### Filters
- `.lpf(freq)` = low-pass filter (200-20000 Hz)
- `.hpf(freq)` = high-pass filter
- `.lpq(amount)` = filter resonance (0-50)
- `.vowel("<a e i o u>")` = formant filter

### Envelope (ADSR)
- `.attack(seconds)` = fade in time
- `.decay(seconds)` = initial decay
- `.sustain(0-1)` = sustain level
- `.release(seconds)` = fade out time

### Filter Envelope - CREATES MOVEMENT
- `.lpenv(depth)` = filter envelope depth (-8 to 8)
- `.lpa(seconds)` = filter attack
- `.lpd(seconds)` = filter decay

### Space
- `.room(0-1)` = reverb amount
- `.roomsize(1-10)` = reverb size
- `.delay(0-1)` = delay amount
- `.delaytime(seconds)` = delay time
- `.delayfeedback(0-1)` = delay repeats

### Dynamics
- `.gain(0-1)` = volume
- `.velocity(0-1)` = note velocity
- `.compressor("-20:20:10:.002:.02")` = compression

### Modulation
- `.pan(0-1)` = stereo position (0.5 = center)
- `.phaser(speed)` = phaser effect
- `.leslie(speed)` = rotary speaker
- `.vib("rate:depth")` = vibrato

### Distortion
- `.shape(0-1)` = waveshaping distortion
- `.crush(1-16)` = bitcrusher (1=harsh, 16=subtle)
- `.coarse(1-32)` = sample rate reduction

---

## MODULATION SIGNALS - CREATE EVOLVING SOUNDS

### LFO Types (0-1 range)
- `sine` = smooth wave
- `saw` = rising ramp
- `tri` = triangle
- `square` = on/off
- `cosine` = shifted sine

### Noise
- `perlin` = smooth random (GREAT for organic movement)
- `rand` = random per event
- `irand(N)` = random integer 0 to N-1

### Using Signals
```javascript
.lpf(sine.range(400, 2000).slow(8))  // filter sweeps over 8 cycles
.gain(perlin.range(.3, .7).slow(4))  // organic volume changes
.pan(sine.slow(2))                    // auto-pan
```

### Key Methods
- `.range(min, max)` = scale output
- `.slow(N)` = slower modulation
- `.fast(N)` = faster modulation
- `.segment(N)` = quantize to N steps

---

## PATTERN TRANSFORMATIONS

### Conditional - Add Variation
- `.every(N, fn)` = apply every N cycles: `.every(4, fast(2))`
- `.sometimes(fn)` = random 50%: `.sometimes(rev)`
- `.sometimesBy(0.3, fn)` = 30% chance
- `.rarely(fn)` = 10% chance
- `.often(fn)` = 75% chance

### Structure
- `.ply(N)` = repeat each event N times
- `.chunk(N, fn)` = apply to Nth chunk
- `.jux(fn)` = apply to right channel only (stereo width)
- `.off(time, fn)` = delayed copy with modification

### Examples
```javascript
s("bd sd").every(4, fast(2))           // double-time every 4 cycles
note("c e g").off(1/8, add(12))        // octave echo
s("hh*8").jux(rev)                      // stereo hats
n("0 2 4 7").sometimes(add(7))          // random octave jumps
```

---

## CREATING LONGER, BETTER MUSIC

### Length Tips
1. Use `.slow()` liberally - `.slow(4)` makes a 4-cycle phrase
2. Stack multiple layers with different phrase lengths
3. Use `<>` angle brackets for things that change each cycle
4. Apply `.every()` for variation over time
5. Layer short and long elements together

### Melodic Tips
1. Use scales: `n("0 2 4 5 7").scale("C:minor")`
2. Create phrases with rests: `"0 2 ~ 4 5 ~ 7 ~"`
3. Use `<>` for melodic variation: `n("<0 2 4 7> <2 4 5 9>")`
4. Add octave jumps: `.sometimes(add(12))`
5. Humanize with `.late(perlin.range(0, 0.02))`

### Arrangement Tips
1. Build in layers - start simple, add complexity
2. Use different `.slow()` values for polyrhythmic interest
3. Add filter sweeps with `.lpf(sine.range(...).slow(16))`
4. Create breakdowns by using `.mask()` or `.gain()` modulation
5. Use effects that evolve: `room(perlin.range(.2,.6).slow(8))`

---

## FULL TRACK TEMPLATE

```javascript
// Set tempo
setcpm(120/4)

stack(
  // DRUMS - 1 cycle loop
  s("bd*4, ~ cp, [~ hh]*4").bank("RolandTR909"),

  // BASS - 4 cycle phrase
  note("<c2 c2 f2 g2>")
    .sound("sawtooth")
    .lpf(sine.range(200, 600).slow(8))
    .lpq(5)
    .gain(.6),

  // CHORDS - 8 cycle progression
  chord("<Cm7 Cm7 Fm7 G7>/2")
    .voicing()
    .s("gm_epiano1")
    .room(.4)
    .gain(.35),

  // MELODY - evolving over 16 cycles
  n("<0 2 4 7 9 7 4 2>/4")
    .scale("C4:minor")
    .off(1/8, x => x.add(12).gain(.3))
    .sound("triangle")
    .lpf(2000)
    .room(.5)
    .delay(.2)
    .every(4, fast(2))
)
```

---

## COMMON MISTAKES TO AVOID

1. DON'T make everything the same length - vary phrase lengths
2. DON'T forget `.slow()` - makes huge difference in feel
3. DON'T use only one octave - spread notes across range
4. DON'T skip effects - room, delay, lpf add polish
5. DON'T forget modulation - sine/perlin on filter = life
6. DON'T copy patterns exactly - transform them with every/sometimes
"""

COMPOSITION_GUIDELINES = """
# MUSIC COMPOSITION GUIDELINES FOR STRUDEL

## Creating Compelling Melodies

### Melodic Principles
1. **Stepwise motion with occasional leaps** - mostly move by 1-2 scale degrees, with occasional 3-5 leaps for interest
2. **Rhythmic variety** - mix long and short notes, use rests
3. **Repetition with variation** - repeat phrases but change endings
4. **Call and response** - create question/answer phrases
5. **Climax and resolution** - build tension, then release

### Melodic Patterns That Work
- Ascending/descending scales: `n("0 1 2 3 4 3 2 1")`
- Arpeggios: `n("0 2 4 7 4 2")`
- Pentatonic runs: `n("0 2 4 7 9 7 4 2").scale("C:pentatonic")`
- Motifs with development: `n("<0 2 4 2> <0 2 5 4>")`

## Creating Grooves

### Drum Pattern Principles
1. **Kick on 1 and 3** (or variations for genre)
2. **Snare/clap on 2 and 4** for backbeat
3. **Hi-hats for subdivision** - 8ths or 16ths
4. **Ghost notes** - quieter hits between main beats
5. **Fills** - use `.every()` for periodic variations

### Genre-Specific Drums
**House/Techno:** `s("bd*4, ~ cp, hh*8")`
**Hip-hop:** `s("bd [~ bd] ~ bd, ~ sd, hh*8")`
**DnB:** `s("bd ~ [bd bd] ~, ~ sd ~ sd")`
**Trap:** `s("bd ~ ~ bd, ~ ~ ~ ~ sd, hh*16")`

## Harmonic Movement

### Chord Progressions That Work
- **I-V-vi-IV** (pop): `chord("<C G Am F>")`
- **ii-V-I** (jazz): `chord("<Dm7 G7 C^7>")`
- **i-VI-III-VII** (epic): `chord("<Am F C G>")`
- **i-iv-v-i** (minor): `chord("<Cm Fm Gm Cm>")`

### Bass Lines
1. Follow chord roots
2. Add passing tones between roots
3. Use octave jumps for energy
4. Syncopation adds groove

## Texture & Space

### Layering Principles
1. **Low frequencies** - one bass element only
2. **Mid frequencies** - chords, leads, pads (most content)
3. **High frequencies** - hats, percussion, sparkle
4. **Space** - leave room, not everything at once

### Dynamic Arrangement
1. **Intro** - minimal elements, build anticipation
2. **Verse** - core groove, less intense
3. **Chorus/Drop** - full energy, all layers
4. **Breakdown** - strip back, create tension
5. **Build** - gradually add elements back
"""

# Combined context for the generator
FULL_CONTEXT = STRUDEL_REFERENCE + "\n\n" + COMPOSITION_GUIDELINES
