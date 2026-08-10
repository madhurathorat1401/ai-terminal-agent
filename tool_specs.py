"""
tool_specs.py

JSON Schema descriptions of the tools in tools.py, in the format the
Anthropic Messages API expects.
"""

TOOLS = [
    {
        "name": "list_files",
        "description": (
            "Recursively list files in the current workspace directory that match "
            "a glob pattern, e.g. '*.log' or '*.py'. Use this first to discover "
            "what files exist before reading them."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match, e.g. '*.log'. Defaults to '*' (all files).",
                }
            },
            "required": [],
        },
    },
    {
        "name": "read_file",
        "description": "Read and return the text contents of a single file, given its path relative to the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path to the file."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_in_file",
        "description": (
            "Search a single file for lines matching a regex pattern (case-insensitive) "
            "and return matching line numbers and text. Useful for finding errors, "
            "specific keywords, or patterns without reading the whole file."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path to the file."},
                "pattern": {"type": "string", "description": "Regex pattern to search for, e.g. 'error|exception'."},
            },
            "required": ["path", "pattern"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write text content to a file at the given relative path, creating parent "
            "directories if needed. Fails if the file already exists unless overwrite=true. "
            "Use this to save summaries, reports, or generated output."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path of the file to write."},
                "content": {"type": "string", "description": "Full text content to write."},
                "overwrite": {
                    "type": "boolean",
                    "description": "Set true to overwrite an existing file. Defaults to false.",
                },
            },
            "required": ["path", "content"],
        },
    },
]