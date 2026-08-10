

import os
import re
import glob

WORKSPACE_ROOT = os.path.abspath(os.getcwd())


def _safe_path(path: str) -> str:
    candidate = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))
    if not candidate.startswith(WORKSPACE_ROOT):
        raise PermissionError(
            f"Refusing to access '{path}': outside workspace root {WORKSPACE_ROOT}"
        )
    return candidate


def list_files(pattern: str = "*") -> str:
    try:
        matches = glob.glob(os.path.join(WORKSPACE_ROOT, "**", pattern), recursive=True)
        files = [os.path.relpath(m, WORKSPACE_ROOT) for m in matches if os.path.isfile(m)]
        if not files:
            return f"No files matched pattern '{pattern}'."
        return "\n".join(sorted(files))
    except Exception as e:
        return f"Error listing files: {e}"


def read_file(path: str, max_chars: int = 8000) -> str:
    try:
        full_path = _safe_path(path)
        if not os.path.isfile(full_path):
            return f"Error: '{path}' is not a file."
        with open(full_path, "r", errors="replace") as f:
            content = f.read(max_chars + 1)
        if len(content) > max_chars:
            content = content[:max_chars] + "\n...[truncated]"
        return content
    except Exception as e:
        return f"Error reading '{path}': {e}"


def search_in_file(path: str, pattern: str) -> str:
    try:
        full_path = _safe_path(path)
        regex = re.compile(pattern, re.IGNORECASE)
        hits = []
        with open(full_path, "r", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if regex.search(line):
                    hits.append(f"{i}: {line.rstrip()}")
        if not hits:
            return f"No matches for '{pattern}' in {path}."
        return "\n".join(hits[:200])
    except Exception as e:
        return f"Error searching '{path}': {e}"


def write_file(path: str, content: str, overwrite: bool = False) -> str:
    try:
        full_path = _safe_path(path)
        if os.path.exists(full_path) and not overwrite:
            return (
                f"Error: '{path}' already exists. Call write_file again with "
                f"overwrite=true if you really want to replace it."
            )
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return f"Wrote {len(content)} characters to {path}."
    except Exception as e:
        return f"Error writing '{path}': {e}"


TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "search_in_file": search_in_file,
    "write_file": write_file,
}