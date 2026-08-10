# AI Terminal Agent

An autonomous CLI agent that takes natural-language instructions, decides
which local tools to call, executes them, and reports back — built to learn
the core "tool use / function calling" loop behind modern AI agents.

Example:
python main.py "Find all log files in this directory and summarize error messages into a file"

The agent will figure out on its own to: list files → search for errors →
write a summary file, pausing to ask permission before the write.

## How it works

Every LLM "agent" is really the same loop:

1. Send the user's prompt + a list of available tools to the model
2. The model either answers directly, or asks to call a tool with specific arguments
3. The code executes that tool locally and returns the result as text
4. The result is sent back to the model
5. Repeat until the model gives a final answer (or a max-turn safety limit is hit)

This project implements that loop against two backends:
- **Claude (Anthropic API)** — `agent.py` was originally built for this; requires an API key and billing
- **Ollama (local, free)** — the current default, runs entirely offline

## Tools available to the agent

| Tool | Description |
|---|---|
| `list_files` | Recursively list files matching a glob pattern |
| `read_file` | Read a file's contents |
| `search_in_file` | Regex search within a single file |
| `write_file` | Write content to a file (asks for human confirmation first) |

All file tools are sandboxed to the project's working directory — the agent
cannot read or write anything outside it, even if asked to (tested against
path-traversal attempts like `../../etc/passwd`).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Option A: Run with Ollama (free, local)

```bash
brew install ollama          # or download from ollama.com
ollama pull qwen2.5:7b-instruct
```

`agent.py` is currently configured to use `qwen2.5:7b-instruct` via Ollama's
OpenAI-compatible API at `http://localhost:11434/v1`.

### Option B: Run with Claude (Anthropic API)

Requires an API key from console.anthropic.com and available credit.
Set `ANTHROPIC_API_KEY` as an environment variable and swap the client
in `agent.py` back to `anthropic.Anthropic()`.

## Usage

```bash
python main.py "your natural language instruction here"
```

Flags:
- `--no-confirm` — skip the human confirmation prompt before destructive actions
- `--quiet` — suppress the tool-call trace output

Run with no arguments for interactive mode (keeps prompting until you type `exit`).

## Findings: model comparison for tool-calling reliability

While building this, I compared two local Ollama models on the same task
(find log files, search for errors, write a summary):

- **llama3.1 (8B)** — correctly listed files, but then hallucinated a
  filename (`file1.log`) that was never returned by any tool call, instead
  of reusing the real filename (`logs/app.log`) from the earlier result.
- **qwen2.5:7b-instruct** — correctly tracked tool results across turns and
  used the real filename throughout, producing an accurate summary.

This was a useful hands-on lesson: tool-calling reliability varies
significantly between models of similar size, and smaller local models can
silently invent arguments instead of grounding them in prior tool output —
something to explicitly guard against in the system prompt and worth
testing before trusting a model with destructive actions.

## Safety design

- **Sandboxed filesystem access** — every file path is resolved and checked
  against the workspace root before use
- **Human-in-the-loop confirmation** — destructive actions (`write_file`)
  pause and require explicit `y` approval before executing
- **Max-turn limit** — the agent loop stops after 10 turns to prevent
  runaway tool-call loops
- **No uncaught exceptions** — every tool function catches errors and
  returns them as text, so the model can see and react to failures instead
  of crashing the program

## Project structure
├── tools.py # actual Python functions the agent can execute
├── tool_specs.py # JSON Schema descriptions of those tools for the model
├── agent.py # the core tool-use loop
├── main.py # CLI entry point
└── requirements.txt