"""
agent.py

The core execution loop ("state machine") that turns a natural-language
request into a sequence of tool calls.

This version talks to a LOCAL Ollama model via its OpenAI-compatible API
instead of the Anthropic API -- no API key, no cost, runs on your machine.
"""

import json
from openai import OpenAI

from tool_specs import TOOLS
from tools import TOOL_FUNCTIONS

MODEL = "qwen2.5:7b-instruct"
MAX_TURNS = 10

SYSTEM_PROMPT = """You are a terminal assistant with access to tools for
reading, searching, and writing files in the user's current workspace
directory. You cannot access anything outside that directory.

Guidelines:
- Use list_files first if you don't already know what files exist.
- CRITICAL: only ever call read_file or search_in_file on filenames that were
  literally returned by a previous list_files call. Never guess, assume, or
  invent a filename that wasn't explicitly shown to you in a tool result.
- Prefer search_in_file over read_file when looking for a specific pattern
  in a large file, to save context.
- When asked to summarize or extract information into a new file, actually
  call write_file -- don't just print the summary in your response.
- Before taking a destructive action (overwriting a file), briefly explain
  what you're about to do.
- Be concise in your final answer: report what you did and where output
  was saved, not a play-by-play of every tool call.
"""

DESTRUCTIVE_TOOLS = {"write_file"}

# Ollama's OpenAI-compatible tool schema wraps each tool spec slightly
# differently than Anthropic's. Convert once, here.
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }
    for t in TOOLS
]


def execute_tool(name: str, tool_input: dict) -> str:
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return f"Error: unknown tool '{name}'"
    try:
        return fn(**tool_input)
    except TypeError as e:
        return f"Error: bad arguments for '{name}': {e}"


def run_agent(user_prompt: str, confirm: bool = True, verbose: bool = True) -> str:
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for turn in range(MAX_TURNS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=OPENAI_TOOLS,
        )

        choice = response.choices[0]
        msg = choice.message

        if not msg.tool_calls:
            return msg.content or "(no response)"

        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                tool_input = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                tool_input = {}

            if verbose:
                print(f"[tool call] {name}({json.dumps(tool_input)})")

            if name in DESTRUCTIVE_TOOLS and confirm:
                ans = input(f"  -> Allow '{name}' with {tool_input}? [y/N] ").strip().lower()
                if ans != "y":
                    result_text = "User declined to run this tool. Do not retry it; explain that to the user instead."
                else:
                    result_text = execute_tool(name, tool_input)
            else:
                result_text = execute_tool(name, tool_input)

            if verbose:
                preview = result_text if len(result_text) < 300 else result_text[:300] + "...[truncated]"
                print(f"[tool result] {preview}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_text,
                }
            )

    return "Stopped: reached max turns without a final answer."