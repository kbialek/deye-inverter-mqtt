# Project Agents & Specialized Instructions

This file contains instructions for specialized skills and agent behaviors within this repository.

## General Rules

1.  **Read the Makefile:** Always read the `Makefile` at the start of a session or when encountering unfamiliar commands. It serves as the primary developer entry point and defines the build, test, and utility workflows for this project.
2.  **Python Environment:** Use `uv` to manage Python virtual environments and dependencies.
3.  **Code Quality:** Ensure all Python code is formatted using `make py-code-format` and passes linting via `make py-check-code`.

## Graphify (Codebase Navigation)

The project maintains a knowledge graph via `graphify` located at `graphify-out/`.

**When performing code navigation, architecture analysis, or answering questions about codebase relationships, follow these rules:**

1.  **Consult the Graph First:** Before performing broad file searches (like `grep` or `find`), consult the graph to understand the project structure.
2.  **Analyze High-Level Structure:** Read `graphify-out/GRAPH_REPORT.md` to identify "god nodes" (central modules/files) and the community structure (how the project is logically partitioned).
3.  **Use the Wiki:** If `graphify-out/wiki/index.md` exists, use it as your primary entry point for high-level navigation.
4.  **Prefer Graph Queries over Text Search:** Use `graphify query`, `graphify path`, or `graphify explain` to understand relationships. These commands traverse both extracted and inferred edges, providing semantic context that `grep` cannot.
5.  **Verify Paths:** Never guess a file path based on a component name. Use the graph to find the exact path, then use `read` to examine the file.
6.  **Maintain Freshness:** If you modify files or notice discrepancies, inform the user and run `graphify update .` to ensure the knowledge graph remains accurate.
