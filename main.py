#!/usr/bin/env python3
"""
main.py

CLI entry point.
"""

import sys
import argparse

from agent import run_agent


def main():
    parser = argparse.ArgumentParser(description="Autonomous AI terminal agent")
    parser.add_argument("prompt", nargs="*", help="Natural language instruction")
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip human confirmation before destructive actions (use with care)",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress tool-call trace output")
    args = parser.parse_args()

    confirm = not args.no_confirm
    verbose = not args.quiet

    if args.prompt:
        prompt = " ".join(args.prompt)
        answer = run_agent(prompt, confirm=confirm, verbose=verbose)
        print(f"\n=== Result ===\n{answer}")
        return

    print("AI Terminal Agent. Type a request, or 'exit' to quit.")
    while True:
        try:
            prompt = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not prompt:
            continue
        if prompt.lower() in ("exit", "quit"):
            break
        answer = run_agent(prompt, confirm=confirm, verbose=verbose)
        print(f"\n=== Result ===\n{answer}")


if __name__ == "__main__":
    sys.exit(main() or 0)