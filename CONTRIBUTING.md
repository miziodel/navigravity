# Contributing to NaviGravity

First off, thank you for considering contributing to NaviGravity! 🎧

## The Social Contract

This software is released under the [MIT License](LICENSE), which gives you maximum freedom. You can use, modify, and distribute this software without restriction.

However, we have a "Gentlemen's Agreement" that we ask you to respect:

1.  **Attribution**: Please acknowledge the original authors in your derivative works.
2.  **Share Back**: If you fix a bug or add a cool feature, please share it via Pull Request.
3.  **Be Kind**: We are a community of music lovers. Let's build together with respect.

---

## 🏗️ Beta Testing & Bug Reporting

Since we are in **Preview Mode**, your feedback is critical.

### 🐛 Reporting Bugs
When opening an issue, please include:
1.  **Navidrome Version**: (e.g., `0.52.0`, Docker or Native).
2.  **MCP Client**: (Claude Desktop, Zed, Cursor, Antigravity, etc.).
3.  **Logs**:
    *   Please enable file logging by setting `NAVIDROME_LOG_FILE=logs/debug.log` in your `.env`.
    *   **Attach this log file** to your issue. Screenshots of the client console are often insufficient.

### 🧪 Feature Requests (The "Bliss" Philosophy)
If you want to add a new "Generation Mode" or Tool:
*   Ensure it respects the **Non-Destructive** principle (never modify user file tags).
*   Ensure it passes a **Quality Check** (don't generate 50 tracks from the same artist).

---

## 👩‍💻 Developer Guide

If you want to get your hands dirty with the code, here is how to start.

### 1. Setup
To get your development environment up and running:

```bash
# Clone the repository
git clone <repo>
cd navigravity

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode (Modern Setup)
pip install -e .[dev]
```

### 2. Workflow
1.  **Fork** the repository.
2.  **Create** a new branch (`git checkout -b feature/amazing-feature`).
3.  **Commit** your changes (`git commit -m 'Add some amazing feature'`).
4.  **Push** to the branch (`git push origin feature/amazing-feature`).
5.  **Open** a Pull Request.

### 3. Testing
We use `pytest` for quality assurance. Before submitting a PR, **ensure all tests pass**:

```bash
pytest
```
