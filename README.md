# SCRIPTOR
### A Programming Language Written Like a Movie

> *Every valid Scriptor program reads like a short film. The compiler is the audience.*

CS 420 — Programming Languages | Spring 2026

**Authors:** Miguel Reese & Mark Gugg

---

## Overview

Scriptor is a general-purpose interpreted programming language where all syntax is written in Hollywood screenplay format. Variables are **characters**, functions are **scenes**, loops are **montages**, and conditionals are **meanwhile** cuts. The goal is to make programming syntax feel narrative and approachable — every program tells a story.

---

## Requirements

- Python 3.8 or higher
- No external dependencies

---

## Running a Program

```bash
python3 interpreter.py <file.scp>
```

**Examples:**

```bash
python3 interpreter.py hello_world.scp
python3 interpreter.py fizzbuzz.scp
python3 interpreter.py cinema_report.scp
```

---

## Running All Programs

Run every `.scp` file in the directory at once:

```bash
for f in *.scp; do
  echo ""; echo "▶ $f"; python3 interpreter.py "$f"
done
```

---

## Language Reference

### Program Structure

Every Scriptor program follows this skeleton:

```
SCRIPT: <Title>

OPENING CREDITS        ← optional global variables

SCENE: <Name> (CAST: <param> AS <type>)
  ...                  ← reusable function/block

DIRECTOR'S CUT         ← required entry point
  ...
FADE OUT.              ← end of program
```

---

### Keyword Mapping

| Scriptor Keyword | Programming Concept |
|---|---|
| `SCENE` | Function / block |
| `CHARACTER` | Variable declaration |
| `SAYS` | print to stdout |
| `SHOUTS` | print to stderr (error/emphasis) |
| `MEANWHILE` | if statement |
| `OTHERWISE` | else |
| `MONTAGE` | for loop |
| `CUT TO` | function call |
| `DIRECTOR'S CUT` | main() / entry point |
| `OPENING CREDITS` | global scope |
| `PLOT TWIST` | try / catch |
| `FADE OUT` | end of program |
| `RETURN` | return a value from a scene |

---

### Data Types (Roles)

| Role | Type | Example |
|---|---|---|
| `HERO` | integer / number | `42`, `3.14` |
| `NARRATOR` | string | `"Hello"` |
| `VILLAIN` | boolean | `VILLAIN_TRUE`, `VILLAIN_FALSE` |
| `EXTRA` | null / void | *(no value)* |

---

### Declaring Variables

```
CHARACTER name AS NARRATOR = "Alice"
CHARACTER score AS HERO = 100
CHARACTER passing AS VILLAIN = VILLAIN_TRUE
```

---

### Output

```
name SAYS LINE          ← character speaks their own value:  name: "Alice"
SAYS "Some text"        ← bare print:  Some text
SAYS score              ← bare print of a variable:  100
SHOUTS "Critical error" ← prints to stderr
```

---

### Conditionals

```
MEANWHILE score >= 80
  SAYS "You passed."
OTHERWISE
  SAYS "Try again."
```

Nested:

```
MEANWHILE score >= 90
  SAYS "A grade"
OTHERWISE
  MEANWHILE score >= 80
    SAYS "B grade"
  OTHERWISE
    SAYS "Below B"
```

---

### Loops

```
MONTAGE i FROM 1 TO 10
  SAYS i
END MONTAGE
```

Counts down:

```
MONTAGE i FROM 5 TO 1
  SAYS i
END MONTAGE
```

The loop variable steps by `+1` or `-1` automatically based on direction.

---

### Scenes (Functions)

Define a scene:

```
SCENE: Greet (CAST: name AS NARRATOR)
  SAYS "Hello,"
  name SAYS LINE
```

Call a scene:

```
CUT TO Greet("World")
```

Return a value:

``
SCENE: Double (CAST: n AS HERO)
  CHARACTER result AS HERO = n * 2
  RETURN result
``

Capture a return value:

```
CHARACTER doubled AS HERO = Double(5)
```

---

### Error Handling

```
PLOT TWIST
  CUT TO RiskyScene(input)
OTHERWISE
  SAYS "Something went wrong."
```

--

### Arithmetic & Comparison

| Operator | Meaning |
|---|---|
| `+` `-` `*` `/` `%` | Arithmetic |
| `==` `!=` `<` `>` `<=` `>=` | Comparison |

---

### Scoping Rules

- Variables declared inside a `SCENE` are **local** to that scene.
- Variables in `OPENING CREDITS` are **global** and readable from any scene.
- Assigning to a global variable from inside a scene **updates the global**.
- `DIRECTOR'S CUT` runs in global scope.

---

## Programs

### 1. Hello World — `hello_world.scp`

The simplest Scriptor program. Declares a NARRATOR and prints it.

```
SCRIPT: Hello World

DIRECTOR'S CUT
  CHARACTER lead AS NARRATOR = "Hello, World!"
  lead SAYS LINE
FADE OUT.
```

**Run:**
```bash
python3 interpreter.py hello_world.scp
```

**Output:**
```
==================================================
  SCRIPT: Hello World
==================================================

  lead: "Hello, World!"

==================================================
  FADE OUT.
==================================================
```

---

### 2. Simple Math — `math.scp`

Arithmetic with HERO integers.

```
SCRIPT: Simple Math

DIRECTOR'S CUT
  CHARACTER a AS HERO = 10
  CHARACTER b AS HERO = 5
  CHARACTER total AS HERO = a + b
  CHARACTER diff AS HERO = a - b
  SAYS "Sum:"
  total SAYS LINE
  SAYS "Difference:"
  diff SAYS LINE
FADE OUT.
```

**Run:**
```bash
python3 interpreter.py math.scp
```

**Output:**
```
  Sum:
  total: "15"
  Difference:
  diff: "5"
```

---

### 3. Personal Greeting — `greeting.scp`

Defines a SCENE, passes a NARRATOR argument, calls it with CUT TO.

```
SCRIPT: Personal Greeting

SCENE: Greet (CAST: name AS NARRATOR)
  SAYS "Welcome to the show,"
  name SAYS LINE

DIRECTOR'S CUT
  CHARACTER guest AS NARRATOR = "Alice"
  CUT TO Greet(guest)
FADE OUT.
```

**Run:**
```bash
python3 interpreter.py greeting.scp
```

**Output:**
```
  Welcome to the show,
  name: "Alice"
```

---

### 4. The Countdown — `countdown.scp`

Demonstrates MONTAGE (loop) counting down, and SHOUTS for emphasis.

```
SCRIPT: The Countdown

OPENING CREDITS
  CHARACTER count AS HERO = 10

SCENE: Launch Sequence
  MONTAGE count FROM 10 TO 1
    SAYS count
  END MONTAGE
  SHOUTS "We have liftoff!"

DIRECTOR'S CUT
  CUT TO Launch Sequence
FADE OUT.
```

**Run:**
```bash
python3 interpreter.py countdown.scp
```

**Output:**
```
  10
  9
  8
  ...
  1
  !! We have liftoff! !!
```

---

### 5. The Audition — `audition.scp`

Functions with parameters and MEANWHILE/OTHERWISE conditionals.

```
SCRIPT: The Audition

SCENE: Audition (CAST: score AS HERO)
  MEANWHILE score >= 80
    SAYS "You got the part."
  OTHERWISE
    SAYS "Better luck next time."

DIRECTOR'S CUT
  CHARACTER applicant AS HERO = 92
  CUT TO Audition(applicant)
FADE OUT.
```

**Run:**
```bash
python3 interpreter.py audition.scp
```

**Output:**
```
  You got the part.
```

---

### 6. FizzBuzz — `fizzbuzz.scp`

Classic FizzBuzz 1–30 using modulo, nested conditionals, and a MONTAGE loop.

```
SCRIPT: FizzBuzz

OPENING CREDITS
  CHARACTER limit AS HERO = 30

SCENE: CheckFizzBuzz (CAST: n AS HERO)
  CHARACTER rem3 AS HERO = n % 3
  CHARACTER rem5 AS HERO = n % 5
  MEANWHILE rem3 == 0
    MEANWHILE rem5 == 0
      SAYS "FizzBuzz"
    OTHERWISE
      SAYS "Fizz"
  OTHERWISE
    MEANWHILE rem5 == 0
      SAYS "Buzz"
    OTHERWISE
      SAYS n

DIRECTOR'S CUT
  SAYS "=== FizzBuzz: 1 to 30 ==="
  MONTAGE i FROM 1 TO limit
    CUT TO CheckFizzBuzz(i)
  END MONTAGE
  SAYS "=== Scene. ==="

FADE OUT.
```

**Run:**
```bash
python3 interpreter.py fizzbuzz.scp
```

**Output:**
```
  === FizzBuzz: 1 to 30 ===
  1
  2
  Fizz
  4
  Buzz
  Fizz
  7
  8
  Fizz
  Buzz
  11
  Fizz
  13
  14
  FizzBuzz
  ...
  === Scene. ===
```

---

### 7. The Grand Cinema Report — `cinema_report.scp`

The most complex program. Demonstrates:
- Multiple interdependent scenes
- Global state accumulation across scene calls
- Scene return values via `RETURN`
- Nested `MEANWHILE`/`OTHERWISE` (multi-tier verdict system)
- `PLOT TWIST` error handling wrapping scene calls
- A batch of `CUT TO` calls building a final report

**Run:**
```bash
python3 interpreter.py cinema_report.scp
```

**Output (abridged):**
```
  === OPENING WEEKEND REPORT ===
  --- Screening #1
    Gross Revenue: $5760
    Verdict: Solid Performer
  --- Screening #4
    Gross Revenue: $8960
    Verdict: BLOCKBUSTER HIT
  ...
  === FINAL SUMMARY ===
  Total Revenue: $28660
  VERDICT: GREENLIGHT THE SEQUEL!
```

---

## Interpreter Architecture

```
interpreter.py
├── tokenize()       Lexer — regex-based, handles multi-word keywords
│                    (CUT TO, DIRECTOR'S CUT, OPENING CREDITS, etc.)
├── Parser           Recursive descent — produces an AST
│   ├── parse_program()
│   ├── parse_scene()
│   ├── parse_block()
│   ├── parse_statement()
│   ├── parse_meanwhile()
│   ├── parse_montage()
│   ├── parse_cut_to()
│   └── parse_expr() / parse_atom()
└── Interpreter      Tree-walk executor
    ├── _eval()      Evaluates expressions (literals, identifiers, binops, calls)
    ├── _exec()      Executes statements
    ├── _call_scene() Dispatches scene calls with local scope
    └── _resolve()   Two-level scope lookup (local → global)
```

**Key design decisions:**
- Scene-local scope starts empty (only params); globals are read via `_resolve` and written directly to `self.globals` on assignment
- `RETURN` is implemented via a `ReturnSignal` exception caught in `_call_scene`
- `PLOT TWIST` uses a native Python `try/except` block
- `SHOUTS` goes to `stderr`; stdout is flushed first to preserve output ordering

---

## Known Limitations

- **Sequential `MEANWHILE` ambiguity** — two `MEANWHILE` blocks at the same indentation level nest rather than run in sequence (no explicit end-block marker). Use `MEANWHILE`/`OTHERWISE` chains instead of sequential `MEANWHILE` blocks.
- **No arrays or maps** — the screenplay metaphor doesn't extend cleanly to data structures.
- **No string interpolation** — concatenate with `+` between NARRATOR values.
- **Single file only** — no `SEQUEL TO` (import) support yet.

---

## File Index

| File | Description |
|---|---|
| `interpreter.py` | Lexer, parser, and interpreter |
| `hello_world.scp` | Simplest program — NARRATOR and SAYS |
| `math.scp` | Arithmetic with HERO integers |
| `greeting.scp` | Scene with CAST parameter and CUT TO |
| `countdown.scp` | MONTAGE loop + SHOUTS |
| `audition.scp` | Conditionals with MEANWHILE/OTHERWISE |
| `fizzbuzz.scp` | FizzBuzz 1–30 with modulo and nested conditionals |
| `cinema_report.scp` | Complex multi-scene program with global state |
